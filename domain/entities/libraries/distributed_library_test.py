import pytest
from datetime import datetime, timedelta

from domain.entities.libraries.distributed_library import DistributedLibrary
from domain.entities.libraries.library_fee import LibraryFee
from domain.entities.lenders.individual_distributed_lender import IndividualDistributedLender
from domain.entities.people import Borrower, Person
from domain.entities.loans import Loan
from domain.entities.thing import Thing

from value_items import (
    PhysicalLocation, ThingStatus, ThingTitle, DueDate, LoanStatus
)
from value_items.money import USDMoney
from value_items.fee_status import FeeStatus
from value_items.exceptions import (
    BorrowerNotInGoodStandingError, InvalidThingStatusToBorrowError
)
from value_items.location import Distance, PhysicalArea
from value_items.mop_server import MOPServer
from value_items.time_interval import TimeInterval
from factories import WaitingListFactory, MoneyFactory, SimpleTimeBasedFeeSchedule


@pytest.fixture
def location():
    return PhysicalLocation(40.6501, -73.94958)

@pytest.fixture
def lender():
    return IndividualDistributedLender("testLender", Person("1", "Testy McTesterson"), [], [])

@pytest.fixture
def library(lender):
    money_factory = MoneyFactory()
    admin = Person("1", "Test McTesterson")
    lib = DistributedLibrary(
        "distLib1", "testDistributedLibrary", admin, USDMoney(100),
        WaitingListFactory(), [], money_factory,
        PhysicalArea(PhysicalLocation(0, 0), Distance.from_kilometers(10)),
        MOPServer.localhost, SimpleTimeBasedFeeSchedule(money_factory),
        TimeInterval.from_days(12)
    )
    lib.add_lender(lender)
    return lib

@pytest.fixture
def thing(lender, location):
    item = Thing("item", ThingTitle("title"), location, lender, ThingStatus.READY, "", [], None)
    lender.add_item(item)
    return item

# Helper Function
def get_due_date(days: int = 1):
    return DueDate(datetime.now() + timedelta(days=days))

# Test Cases
def test_library_lists_items(library, thing):
    assert list(library.get_all_things()) == [thing]

def test_item_marked_damaged_not_available(library, lender, location):
    damaged_item = Thing("item", ThingTitle("title"), location, lender, ThingStatus.DAMAGED, "", [], None)
    lender.add_item(damaged_item)
    assert not list(library.get_available_things())
    assert list(library.get_all_things()) == [damaged_item]

def test_borrowed_item_no_longer_available(library, thing):
    borrower = Borrower("libraryMember", library.administrator, library, [])
    library.add_borrower(borrower)
    loan = library.borrow(thing, borrower, get_due_date())
    assert loan is not None
    assert not list(library.get_available_things())

def test_cannot_borrow_damaged_item(library, lender, location):
    borrower = Borrower("libraryMember", library.administrator, library, [])
    library.add_borrower(borrower)
    damaged_item = Thing("item", ThingTitle("title"), location, lender, ThingStatus.DAMAGED, "", [], USDMoney(100))
    lender.add_item(damaged_item)
    with pytest.raises(InvalidThingStatusToBorrowError):
        library.borrow(damaged_item, borrower, get_due_date())

def test_cannot_borrow_with_fees(library, thing):
    borrower = Borrower("libraryMember", library.administrator, library, [])
    library.add_borrower(borrower)
    loan = Loan("loan", thing, borrower, get_due_date())
    borrower.apply_fee(LibraryFee(USDMoney(120), loan, FeeStatus.OUTSTANDING))
    with pytest.raises(BorrowerNotInGoodStandingError):
        library.borrow(thing, borrower, get_due_date())

def test_borrow_and_return_on_time(library, thing):
    borrower = Borrower("libraryMember", library.administrator, library, [])
    library.add_borrower(borrower)
    loan = library.borrow(thing, borrower, get_due_date())
    assert loan.item.status == ThingStatus.BORROWED
    finished = library.finish_return(library.start_return(loan))
    assert finished.status == LoanStatus.RETURNED
    assert finished.item.status == ThingStatus.READY

def test_item_borrowed_then_damaged(library, thing):
    borrower = Borrower("libraryMember", library.administrator, library, [])
    library.add_borrower(borrower)
    loan = library.borrow(thing, borrower, get_due_date())
    returned = library.start_return(loan)
    returned.item.status = ThingStatus.DAMAGED
    finished = library.finish_return(returned)
    assert finished.status == LoanStatus.RETURNED_DAMAGED
    assert finished.item.status == ThingStatus.DAMAGED
    assert borrower.fees[0].amount.amount == thing.purchase_cost.amount

def test_item_returned_late(library, thing):
    borrower = Borrower("libraryMember", library.administrator, library, [])
    library.add_borrower(borrower)
    loan = library.borrow(thing, borrower, get_due_date(-10))
    finished = library.finish_return(library.start_return(loan))
    assert finished.status == LoanStatus.OVERDUE
    assert finished.item.status == ThingStatus.READY
    assert 0 < borrower.fees[0].amount.amount < 100

def test_unowned_item_throws(library):
    borrower = Borrower("libraryMember", library.administrator, library, [])
    library.add_borrower(borrower)
    other_lender = IndividualDistributedLender("otherLender", Person("2", "Someone Else"), [], [])
    unowned_item = Thing("item", ThingTitle("title"), PhysicalLocation(1, 1), other_lender, ThingStatus.READY, "", [], None)
    with pytest.raises(Exception):
        library.borrow(unowned_item, borrower, None)

def test_item_with_waiting_list_reserved(library, thing):
    borrower = Borrower("libraryMember", library.administrator, library, [])
    library.add_borrower(borrower)
    loan = library.borrow(thing, borrower, get_due_date())
    second_borrower = Borrower("waitingPerson", Person("someoneElse", "Bob McGree"), library)
    assert library.reserve_item(thing, second_borrower) is not None
    finished = library.finish_return(library.start_return(loan))
    assert finished.status == LoanStatus.RETURNED
    assert finished.item.status == ThingStatus.RESERVED
