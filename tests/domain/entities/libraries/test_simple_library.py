from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from domain.entities.borrower import Borrower
from domain.entities.libraries.simple_library import SimpleLibrary
from domain.entities.loan import Loan
from domain.entities.mop_server import MOPServer
from domain.entities.people.person import Person
from domain.entities.thing import Thing
from domain.factories import MoneyFactory
from domain.value_items import (
    ID,
    URL,
    DueDate,
    LoanStatus,
    Location,
    Money,
    PersonName,
    ThingStatus,
    ThingTitle,
    WaitingListType,
)
from domain.value_items.exceptions import (
    BorrowerNotInGoodStandingError,
    InvalidThingStatusToBorrowError,
)
from domain.value_items.fee_schedules.fee_schedule import FeeSchedule


# Create a concrete implementation of FeeSchedule for testing
class TestFeeSchedule(FeeSchedule):
    def fee_for_overdue_item(self, loan) -> Money:
        return Money(amount=5.0, currency_name="USD")

    def fee_for_damaged_item(self, loan) -> Money:
        return Money(amount=20.0, currency_name="USD")


@pytest.fixture
def person():
    return Person(
        person_id=ID.generate(),
        name=PersonName(first_name="Admin", last_name="User"),
        email=["admin@library.com"],
    )


@pytest.fixture
def simple_library(person):
    money_factory = MoneyFactory()
    fee_schedule = TestFeeSchedule()
    mop_server = MOPServer(id=ID.generate(), base_url=URL.parse("https://example.com"))

    return SimpleLibrary(
        library_id=ID.generate(),
        name="Test Simple Library",
        administrator=person,
        location=MagicMock(spec=Location),
        _borrowers=[],
        _loans=[],
        waiting_list_type=WaitingListType.FIRST_COME_FIRST_SERVE,
        waiting_lists_by_item_id={},
        max_fines_before_suspension=Money(amount=50.0, currency_name="USD"),
        fee_schedule=fee_schedule,
        money_factory=money_factory,
        default_loan_time=timedelta(days=14),
        mop_server=mop_server,
        _items=[],
    )


@pytest.fixture
def borrower():
    borrower = MagicMock(spec=Borrower)
    borrower.entity_id = ID.generate()
    return borrower


@pytest.fixture
def thing():
    thing = MagicMock(spec=Thing)
    thing.status = ThingStatus.READY
    thing.entity_id = ID.generate()
    thing.title = ThingTitle(name="Test Book")
    return thing


def test_entity_id(simple_library):
    assert simple_library.entity_id == simple_library.library_id


def test_add_item(simple_library, thing):
    # Test adding an item
    result = simple_library.add_item(thing)

    assert result == thing
    assert thing in simple_library._items


def test_all_things(simple_library, thing):
    # Add an item
    simple_library.add_item(thing)

    # Test getting all things
    things = list(simple_library.all_things)
    assert len(things) == 1
    assert thing in things


def test_items(simple_library, thing):
    # Add an item
    simple_library.add_item(thing)

    # Test getting items
    items = list(simple_library.items)
    assert len(items) == 1
    assert thing in items


@pytest.mark.asyncio
async def test_borrow_success(simple_library, thing, borrower):
    # Set up borrower in good standing
    borrower.library_id = simple_library.entity_id
    simple_library.can_borrow = MagicMock(return_value=True)

    # Test borrowing an item
    due_date = DueDate(date=datetime.now() + timedelta(days=14))
    loan = await simple_library.borrow(thing, borrower, due_date)

    # Verify the loan was created correctly
    assert loan.item == thing
    assert loan.borrower_id == borrower.entity_id
    assert loan.due_date == due_date
    assert loan.return_location == simple_library.location
    assert loan.status == LoanStatus.BORROWED

    # Verify the thing status was updated
    assert thing.status == ThingStatus.BORROWED

    # Verify the loan was added to the library
    assert loan in simple_library._loans


@pytest.mark.asyncio
async def test_borrow_with_default_due_date(simple_library, thing, borrower):
    # Set up borrower in good standing
    borrower.library_id = simple_library.entity_id
    simple_library.can_borrow = MagicMock(return_value=True)

    # Test borrowing an item without specifying a due date
    loan = await simple_library.borrow(thing, borrower)

    # Verify a default due date was set
    assert loan.due_date is not None
    # Due date should be approximately default_loan_time in the future
    assert loan.due_date.date > datetime.now()
    assert (
        loan.due_date.date
        < datetime.now() + simple_library.default_loan_time + timedelta(seconds=5)
    )


@pytest.mark.asyncio
async def test_borrow_unavailable_thing(simple_library, borrower):
    # Create a thing that's already borrowed
    borrowed_thing = MagicMock(spec=Thing)
    borrowed_thing.status = ThingStatus.BORROWED

    # Test borrowing an unavailable item
    with pytest.raises(InvalidThingStatusToBorrowError):
        await simple_library.borrow(borrowed_thing, borrower)


@pytest.mark.asyncio
async def test_borrow_borrower_not_in_good_standing(simple_library, thing, borrower):
    # Set up borrower not in good standing
    simple_library.can_borrow = MagicMock(return_value=False)

    # Test borrowing when borrower is not in good standing
    with pytest.raises(BorrowerNotInGoodStandingError):
        await simple_library.borrow(thing, borrower)


@pytest.mark.asyncio
async def test_start_return(simple_library):
    # Create a loan
    loan = MagicMock(spec=Loan)

    # Test starting a return
    result = await simple_library.start_return(loan)

    # Verify the loan status was updated
    assert result.status == LoanStatus.WAITING_ON_LENDER_ACCEPTANCE
    assert result.time_returned is not None


def test_all_titles(simple_library):
    # Create some test things with titles
    thing1 = MagicMock(spec=Thing)
    thing1.title = ThingTitle(name="Book 1")

    thing2 = MagicMock(spec=Thing)
    thing2.title = ThingTitle(name="Book 2")

    thing3 = MagicMock(spec=Thing)
    thing3.title = ThingTitle(name="Book 1")  # Duplicate title

    # Add the things to the library
    simple_library._items = [thing1, thing2, thing3]

    # Test getting all titles
    titles = list(simple_library.all_titles)
    assert len(titles) == 2
    assert ThingTitle(name="Book 1") in titles
    assert ThingTitle(name="Book 2") in titles


def test_available_titles(simple_library):
    # Create some things with different statuses
    ready_thing1 = MagicMock(spec=Thing)
    ready_thing1.status = ThingStatus.READY
    ready_thing1.title = ThingTitle(name="Book 1")

    ready_thing2 = MagicMock(spec=Thing)
    ready_thing2.status = ThingStatus.READY
    ready_thing2.title = ThingTitle(name="Book 2")

    borrowed_thing = MagicMock(spec=Thing)
    borrowed_thing.status = ThingStatus.BORROWED
    borrowed_thing.title = ThingTitle(name="Book 3")

    # Add the things to the library
    simple_library._items = [ready_thing1, ready_thing2, borrowed_thing]

    # Test getting available titles
    titles = list(simple_library.available_titles)
    assert len(titles) == 2
    assert ThingTitle(name="Book 1") in titles
    assert ThingTitle(name="Book 2") in titles
    assert ThingTitle(name="Book 3") not in titles


def test_preferred_return_location(simple_library):
    # Test getting the preferred return location
    assert simple_library.preferred_return_location == simple_library.location
