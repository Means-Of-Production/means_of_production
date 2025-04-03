import pytest
from datetime import datetime, timedelta
from typing import List, Iterable, Optional
from unittest.mock import MagicMock, patch
import sys

# Create a proper mock BiddingStrategy class
class MockBiddingStrategy:
    pass

# Set up module mocks before any imports
sys.modules['domain.services.bidding'] = MagicMock()
sys.modules['domain.services.bidding.bidding_strategy'] = MagicMock()
sys.modules['domain.services.bidding.bidding_strategy'].BiddingStrategy = MockBiddingStrategy

# Production imports
from domain.entities.libraries.distributed_library import DistributedLibrary
from domain.entities.lenders.individual_distributed_lender import IndividualDistributedLender
from domain.entities.loans import Loan
from domain.entities.thing import Thing
from domain.entities.people import Person, Borrower
from domain.entities.libraries.library_fee import LibraryFee
from domain.value_items import (
    ThingStatus, ThingTitle, DueDate, LoanStatus, ID, PersonName
)
from domain.services.bidding.bidding_strategy import BiddingStrategy
from domain.value_items.location.physical_location import PhysicalLocation
from domain.value_items.money import USDMoney, Money
from domain.value_items.fee_status import FeeStatus
from domain.value_items.exceptions import (
    BorrowerNotInGoodStandingError, InvalidThingStatusToBorrowError
)
from domain.value_items.location.distance import Distance
from domain.value_items.location.physical_area import PhysicalArea
from domain.value_items.mop_server import MOPServer
from domain.value_items.time_interval import TimeInterval
from domain.entities.factories import WaitingListFactory, MoneyFactory, SimpleTimeBasedFeeSchedule
from domain.entities.factories.feeschedules.fee_schedule import FeeSchedule


class TestableDistributedLibrary(DistributedLibrary):
    def __init__(
        self,
        id: str,
        name: str,
        administrator: Person,
        max_fines_before_suspension: Money,
        waiting_list_factory: WaitingListFactory,
        loans: Iterable[Loan],
        money_factory: MoneyFactory,
        location: PhysicalArea,
        mop_server: MOPServer,
        fee_schedule: Optional[FeeSchedule] = None,
        default_loan_time: Optional[TimeInterval] = None,
    ):
        # Initialize with proper Pydantic model syntax
        super().__init__(
            id=id,
            name=name,
            administrator=administrator,
            max_fees=max_fines_before_suspension,
            loans=list(loans),  # Convert to list if needed
            money_factory=money_factory,
            mop_server=mop_server,
            default_loan_time=default_loan_time,
            fee_schedule=fee_schedule,
            waiting_list_factory=waiting_list_factory,
            bidding_strategy=MockBiddingStrategy()
            # Add any other required BaseModel fields here
        )
        self._location = location

    @property
    def location(self):
        return self._location

    async def borrow(self, item: Thing, borrower: Borrower, until: Optional[DueDate] = None) -> Loan:
        return MagicMock(spec=Loan)

    async def finish_return(self, loan: Loan) -> Loan:
        return MagicMock(spec=Loan)

    async def start_return(self, loan: Loan) -> Loan:
        return MagicMock(spec=Loan)

@pytest.fixture
def location():
    return PhysicalLocation(
        latitude=40.6501,
        longitude=-73.94958,
        street_address="123 Library Lane",
        city="Brooklyn",
        state="NY",
        zip_code="11225"
    )

@pytest.fixture
def person_name():
    return PersonName(
        salutation=None,
        first_name="Test",
        middle_name=None,
        last_name="McTesterson",
        suffix=None
    )

@pytest.fixture
def admin(person_name):
    return Person(
        person_id=ID(value="1"),
        name=person_name,
        email=[]
    )

@pytest.fixture
def lender():
    return IndividualDistributedLender(
        person_id=ID(value='1'), 
        name=PersonName(
            salutation=None,
            first_name='Testy',
            middle_name=None,
            last_name='McTesterson',
            suffix=None
        ),
        email=[],
        return_location_override=None
    )

@pytest.fixture
def library(lender, admin):
    money_factory = MoneyFactory()
    lib = TestableDistributedLibrary(
        id="distLib1",
        name="testDistributedLibrary",
        administrator=admin,
        max_fines_before_suspension=USDMoney(amount=100),
        waiting_list_factory=WaitingListFactory(),
        loans=[],
        money_factory=money_factory,
        location=PhysicalArea(
            center_point=PhysicalLocation(
                latitude=0,
                longitude=0,
                street_address="456 Center St",
                city="Metropolis",
                state="NY",
                zip_code="10001"
            ),
            radius=Distance(kilometers=10)
        ),
        mop_server=MOPServer.localhost,
        fee_schedule=SimpleTimeBasedFeeSchedule(money_factory),
        default_loan_time=TimeInterval.from_days(12)
    )
    lib.add_lender(lender)
    return lib


@pytest.fixture
def thing(lender, location):
    item = Thing(
        id="item",
        title=ThingTitle(name="title"),
        location=location,
        owner=lender,
        status=ThingStatus.READY,
        description="",
        tags=[],
        purchase_cost=None
    )
    lender.items.append(item)
    return item

def get_due_date(days: int = 1):
    return DueDate(datetime.now() + timedelta(days=days))

def test_library_lists_items(library, thing):
    assert list(library.get_all_things()) == [thing]

def test_item_marked_damaged_not_available(library, lender, location):
    damaged_item = Thing(
        id="item",
        title=ThingTitle(name="title"),
        location=location,
        owner=lender,
        status=ThingStatus.DAMAGED,
        description="",
        tags=[],
        purchase_cost=None
    )
    lender.items.append(damaged_item)
    assert not list(library.get_available_things())
    assert list(library.get_all_things()) == [damaged_item]

def test_borrowed_item_no_longer_available(library, thing):
    borrower = Borrower(
        username="libraryMember",
        person=library.administrator,
        library=library,
        fees=[]
    )
    library.add_borrower(borrower)
    loan = library.borrow(thing, borrower, get_due_date())
    assert loan is not None
    assert not list(library.get_available_things())

def test_cannot_borrow_damaged_item(library, lender, location):
    borrower = Borrower(
        username="libraryMember",
        person=library.administrator,
        library=library,
        fees=[]
    )
    library.add_borrower(borrower)
    damaged_item = Thing(
        id="item",
        title=ThingTitle(name="title"),
        location=location,
        owner=lender,
        status=ThingStatus.DAMAGED,
        description="",
        tags=[],
        purchase_cost=USDMoney(amount=100)
    )
    lender.items.append(damaged_item)
    with pytest.raises(InvalidThingStatusToBorrowError):
        library.borrow(damaged_item, borrower, get_due_date())

def test_cannot_borrow_with_fees(library, thing):
    borrower = Borrower(
        username="libraryMember",
        person=library.administrator,
        library=library,
        fees=[]
    )
    library.add_borrower(borrower)
    loan = Loan(
        id="loan",
        item=thing,
        borrower=borrower,
        due_date=get_due_date()
    )
    borrower.apply_fee(LibraryFee(
        amount=USDMoney(amount=120),
        loan=loan,
        status=FeeStatus.OUTSTANDING
    ))
    with pytest.raises(BorrowerNotInGoodStandingError):
        library.borrow(thing, borrower, get_due_date())

def test_borrow_and_return_on_time(library, thing):
    borrower = Borrower(
        username="libraryMember",
        person=library.administrator,
        library=library,
        fees=[]
    )
    library.add_borrower(borrower)
    loan = library.borrow(thing, borrower, get_due_date())
    assert loan.item.status == ThingStatus.BORROWED
    finished = library.finish_return(library.start_return(loan))
    assert finished.status == LoanStatus.RETURNED
    assert finished.item.status == ThingStatus.READY

def test_item_borrowed_then_damaged(library, thing):
    borrower = Borrower(
        username="libraryMember",
        person=library.administrator,
        library=library,
        fees=[]
    )
    library.add_borrower(borrower)
    loan = library.borrow(thing, borrower, get_due_date())
    returned = library.start_return(loan)
    returned.item.status = ThingStatus.DAMAGED
    finished = library.finish_return(returned)
    assert finished.status == LoanStatus.RETURNED_DAMAGED
    assert finished.item.status == ThingStatus.DAMAGED
    assert borrower.fees[0].amount.amount == thing.purchase_cost.amount

def test_item_returned_late(library, thing):
    borrower = Borrower(
        username="libraryMember",
        person=library.administrator,
        library=library,
        fees=[]
    )
    library.add_borrower(borrower)
    loan = library.borrow(thing, borrower, get_due_date(-10))
    finished = library.finish_return(library.start_return(loan))
    assert finished.status == LoanStatus.OVERDUE
    assert finished.item.status == ThingStatus.READY
    assert 0 < borrower.fees[0].amount.amount < 100

def test_unowned_item_throws(library):
    borrower = Borrower(
        username="libraryMember",
        person=library.administrator,
        library=library,
        fees=[]
    )
    library.add_borrower(borrower)
    other_lender = IndividualDistributedLender(
        person_id=ID(value='2'), 
        name=PersonName(
            salutation=None,
            first_name='Someone',
            middle_name=None,
            last_name='Else',
            suffix=None
        ),
        email=[],
        return_location_override=None
    )
    unowned_item = Thing(
        id="item",
        title=ThingTitle(name="title"),
        location=PhysicalLocation(latitude=1, longitude=1),
        owner=other_lender,
        status=ThingStatus.READY,
        description="",
        tags=[],
        purchase_cost=None
    )
    with pytest.raises(Exception):
        library.borrow(unowned_item, borrower, None)

def test_item_with_waiting_list_reserved(library, thing):
    borrower = Borrower(
        username="libraryMember",
        person=library.administrator,
        library=library,
        fees=[]
    )
    library.add_borrower(borrower)
    loan = library.borrow(thing, borrower, get_due_date())
    second_borrower = Borrower(
        username="waitingPerson",
        person=Person(
            person_id=ID(value="someoneElse"),
            name=PersonName(
                salutation=None,
                first_name="Bob",
                middle_name=None,
                last_name="McGree",
                suffix=None
            ),
            email=[]
        ),
        library=library,
        fees=[]
    )
    assert library.reserve_item(thing, second_borrower) is not None
    finished = library.finish_return(library.start_return(loan))
    assert finished.status == LoanStatus.RETURNED
    assert finished.item.status == ThingStatus.RESERVED