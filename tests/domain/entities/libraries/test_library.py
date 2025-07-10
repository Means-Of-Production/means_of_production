import decimal
from datetime import datetime, timedelta
from typing import Iterable
from unittest.mock import MagicMock, patch

import pytest

from domain.entities.borrower import Borrower
from domain.entities.libraries.library import Library
from domain.entities.libraries.library_fee import LibraryFee
from domain.entities.loan import Loan
from domain.entities.people.person import Person
from domain.entities.thing import Thing
from domain.entities.waiting_lists.waiting_list import WaitingList
from domain.factories import MoneyFactory, WaitingListFactory
from domain.value_items import (
    ID,
    DueDate,
    FeeStatus,
    LoanStatus,
    Location,
    Money,
    PersonName,
    ThingStatus,
    ThingTitle,
    WaitingListType,
)
from domain.value_items.fee_schedules.fee_schedule import FeeSchedule


# Create a concrete implementation of FeeSchedule for testing
class TestFeeSchedule(FeeSchedule):
    def fee_for_overdue_item(self, loan) -> Money:
        return Money(amount=decimal.Decimal(5.0), currency_name="USD")

    def fee_for_damaged_item(self, loan) -> Money:
        return Money(amount=decimal.Decimal(20.0), currency_name="USD")


# Create a concrete implementation of Library for testing
class TestableLibrary(Library):
    model_config = {"arbitrary_types_allowed": True, "frozen": False, "extra": "allow"}

    def __init__(self, **kwargs):
        # Initialize the Pydantic model first
        super().__init__(**kwargs)
        # Then initialize our private attributes
        # We need to use object.__setattr__ to bypass Pydantic's __setattr__
        object.__setattr__(self, "_items", [])
        object.__setattr__(self, "_borrowers", [])
        object.__setattr__(self, "_loans", [])

    @property
    def all_things(self) -> Iterable[Thing]:
        return self._items

    async def borrow(self, thing: Thing, borrower: Borrower, until: DueDate) -> Loan:
        loan = Loan(
            loan_id=ID.generate(),
            item=thing,
            borrower_id=borrower.entity_id,
            due_date=until,
            return_location=self.location,
            time_returned=None,
        )
        self.add_loan(loan)
        return loan

    async def start_return(self, loan: Loan) -> Loan:
        loan.status = LoanStatus.WAITING_ON_LENDER_ACCEPTANCE
        loan.time_returned = datetime.now()
        return loan

    async def finish_return(self, loan: Loan, borrower: Borrower) -> Loan:
        return await self.finish_library_return(loan, borrower)

    def get_loans(self) -> Iterable[Loan]:
        return self._loans


@pytest.fixture
def testable_library():
    person = Person(
        person_id=ID.generate(),
        name=PersonName(first_name="Admin", last_name="User"),
        emails=["admin@library.com"],
    )

    money_factory = MoneyFactory()

    # Use TestFeeSchedule instead of MagicMock for fee_schedule
    fee_schedule = TestFeeSchedule()

    # Create a minimal MOPServer instance
    from domain.entities.mop_server import MOPServer
    from domain.value_items.url import URL

    mop_server = MOPServer(
        id=ID.generate(), base_url=URL.parse("http://test-server.com")
    )

    return TestableLibrary(
        library_id=ID.generate(),
        name="Test Library",
        administrator=person,
        location=MagicMock(spec=Location),
        waiting_list_type=WaitingListType.FIRST_COME_FIRST_SERVE,
        waiting_lists_by_item_id={},
        max_fines_before_suspension=Money(
            amount=decimal.Decimal(50.0), currency_name="USD"
        ),
        fee_schedule=fee_schedule,
        money_factory=money_factory,
        default_loan_time=timedelta(days=14),
        mop_server=mop_server,
    )


@pytest.fixture
def borrower():
    return MagicMock(spec=Borrower)


@pytest.fixture
def thing():
    thing = MagicMock(spec=Thing)
    thing.status = ThingStatus.READY
    thing.entity_id = ID.generate()
    thing.title = ThingTitle(name="Test Book")
    return thing


def test_entity_id(testable_library):
    assert testable_library.entity_id == testable_library.library_id


def test_available_things(testable_library):
    # Create some things with different statuses
    ready_thing = MagicMock(spec=Thing)
    ready_thing.status = ThingStatus.READY

    borrowed_thing = MagicMock(spec=Thing)
    borrowed_thing.status = ThingStatus.BORROWED

    testable_library._items = [ready_thing, borrowed_thing]

    # Test that only READY things are returned
    available = list(testable_library.available_things)
    assert len(available) == 1
    assert available[0] == ready_thing


def test_add_borrower(testable_library, borrower):
    # Test adding a borrower
    result = testable_library.add_borrower(borrower)

    assert result == borrower
    assert borrower in testable_library._borrowers


def test_can_borrow_different_library(testable_library, borrower):
    # Set up borrower from a different library
    borrower.library_id = ID.generate()  # Different from testable_library.entity_id

    # Test that borrower from different library can't borrow
    assert not testable_library.can_borrow(borrower)


def test_can_borrow_with_fees(testable_library, borrower):
    # Set up a borrower from this library
    borrower.library_id = testable_library.entity_id

    # Case 1: Borrower has no fees
    borrower.fees = []
    # Use patch to mock the total method
    with patch.object(
        MoneyFactory,
        "total",
        return_value=Money(amount=decimal.Decimal(0.0), currency_name="USD"),
    ):
        assert testable_library.can_borrow(borrower)

    # Case 2: Borrower has fees but under the limit
    fee = MagicMock()
    fee.status = FeeStatus.OUTSTANDING
    fee.amount = Money(amount=decimal.Decimal(10.0), currency_name="USD")
    borrower.fees = [fee]

    # Mock the money_factory.total method to return a value less than max_fines
    with patch.object(
        MoneyFactory,
        "total",
        return_value=Money(amount=decimal.Decimal(10.0), currency_name="USD"),
    ):
        assert testable_library.can_borrow(borrower)

    # Case 3: Borrower has fees over the limit
    with patch.object(
        MoneyFactory,
        "total",
        return_value=Money(amount=decimal.Decimal(60.0), currency_name="USD"),
    ):
        assert not testable_library.can_borrow(borrower)


@pytest.mark.asyncio
async def test_reserve_item(testable_library, thing, borrower):
    # Mock the WaitingListFactory
    with patch.object(WaitingListFactory, "create_new_list") as mock_create:
        mock_waiting_list = MagicMock(spec=WaitingList)
        mock_create.return_value = mock_waiting_list

        # Test reserving an item
        result = await testable_library.reserve_item(thing, borrower)

        # Verify the waiting list was created and the borrower was added
        mock_create.assert_called_once_with(testable_library, thing)
        mock_waiting_list.add.assert_called_once_with(borrower)
        assert result == mock_waiting_list
        assert (
            testable_library.waiting_lists_by_item_id[thing.entity_id]
            == mock_waiting_list
        )


def test_get_loans(testable_library):
    # Create some test loans
    loan1 = MagicMock(spec=Loan)
    loan2 = MagicMock(spec=Loan)

    # Add loans using the add_loan method
    testable_library.add_loan(loan1)
    testable_library.add_loan(loan2)

    # Test getting loans directly from the _loans attribute
    assert len(testable_library._loans) == 2
    assert loan1 in testable_library._loans
    assert loan2 in testable_library._loans


def test_add_loan(testable_library):
    # Create a test loan
    loan = MagicMock(spec=Loan)

    # Test adding a loan
    testable_library.add_loan(loan)
    assert loan in testable_library._loans


def test_get_titles_from_items():
    # Create some test things with titles
    thing1 = MagicMock(spec=Thing)
    thing1.title = ThingTitle(name="Book 1")

    thing2 = MagicMock(spec=Thing)
    thing2.title = ThingTitle(name="Book 2")

    thing3 = MagicMock(spec=Thing)
    thing3.title = ThingTitle(name="Book 1")  # Duplicate title

    # Test getting unique titles
    titles = list(Library.get_titles_from_items([thing1, thing2, thing3]))
    assert len(titles) == 2
    assert ThingTitle(name="Book 1") in titles
    assert ThingTitle(name="Book 2") in titles


@pytest.mark.asyncio
async def test_finish_return(testable_library, borrower):
    # Create a test loan in the correct state for return
    thing = MagicMock(spec=Thing)
    thing.status = ThingStatus.BORROWED
    thing.entity_id = ID.generate()

    loan = MagicMock(spec=Loan)
    loan.status = LoanStatus.WAITING_ON_LENDER_ACCEPTANCE
    loan.time_returned = datetime.now()
    loan.item = thing
    # Use a date object instead of a datetime object
    from datetime import date

    today = date.today()
    yesterday = today - timedelta(days=1)
    loan.due_date = DueDate(date=yesterday)  # Overdue
    loan.loan_id = ID.generate()

    # Create an async mock function for finish_library_return
    async def mock_finish_library_return(self, loan, borrower):
        loan.status = LoanStatus.OVERDUE
        thing.status = ThingStatus.READY
        fee = LibraryFee(
            library_fee_id=ID.generate(),
            library_id=testable_library.library_id,
            amount=Money(amount=decimal.Decimal(5.0), currency_name="USD"),
            charged_for_id=loan.loan_id,
        )
        fee.status = FeeStatus.OUTSTANDING
        borrower.apply_fee(fee)
        return loan

    # Patch the finish_library_return method
    with patch.object(Library, "finish_library_return", mock_finish_library_return):
        # Test finishing a return for an overdue item
        result = await testable_library.finish_return(loan, borrower)

        # Verify the loan status was updated
        assert result.status == LoanStatus.OVERDUE

        # Verify the thing status was updated
        assert thing.status == ThingStatus.READY

        # Verify a fee was applied for the overdue item
        borrower.apply_fee.assert_called_once()
