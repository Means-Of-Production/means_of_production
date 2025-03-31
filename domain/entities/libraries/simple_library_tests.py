import unittest
from datetime import datetime, timedelta

from people import Person, Borrower
from value_items import (
    PersonName, ThingTitle, PhysicalLocation, ThingStatus, DueDate, LoanStatus
)
from value_items.exceptions import BorrowerNotInGoodStandingError, InvalidThingStatusToBorrowError
from value_items.mop_server import MOPServer
from value_items.fee_status import FeeStatus
from thing import Thing
from loans import Loan
from factories import WaitingListFactory, MoneyFactory, SimpleTimeBasedFeeSchedule
from value_items.money import USDMoney
from libraries.simple_library import SimpleLibrary
from libraries.library_fee import LibraryFee
from value_items.time_interval import TimeInterval

def create_library(waiting_list_factory=None):
    return SimpleLibrary(
        "testLib1",
        "testLibrary",
        Person("1", PersonName("Test", "McTesterson")),
        PhysicalLocation(0, 0),
        waiting_list_factory or WaitingListFactory(),
        USDMoney(100),
        [],
        MoneyFactory(),
        MOPServer.localhost,
        SimpleTimeBasedFeeSchedule(MoneyFactory()),
        TimeInterval.from_days(14),
    )

def create_borrower(library, name="libraryMember"):
    borrower = Borrower(name, library.administrator, library, [])
    library.add_borrower(borrower)
    return borrower

def create_thing(library, status=ThingStatus.READY, purchase_cost=None):
    return Thing("item", ThingTitle("title"), library.location, library, status, "", [], purchase_cost)

def get_due_date(num_days=1):
    return DueDate(datetime.now() + timedelta(days=num_days))

class TestSimpleLibrary(unittest.TestCase):
    
    def test_lists_items_it_has(self):
        library = create_library()
        item = create_thing(library)
        library.add_item(item)

        self.assertEqual(len(list(library.available_titles)), 1)
        self.assertEqual(list(library.available_titles)[0].name, "title")
    
    def test_item_marked_damaged_is_no_longer_available(self):
        library = create_library()
        item = create_thing(library, ThingStatus.DAMAGED)
        library.add_item(item)

        self.assertEqual(len(list(library.available_titles)), 0)
        self.assertEqual(len(list(library.all_titles)), 1)
    
    def test_borrowed_item_is_no_longer_available(self):
        library = create_library()
        borrower = create_borrower(library)
        item = create_thing(library)
        library.add_item(item)

        loan = library.borrow(item, borrower, DueDate())

        self.assertIsNotNone(loan)
        self.assertEqual(len(list(library.available_titles)), 0)
        self.assertEqual(len(list(library.all_titles)), 1)
    
    def test_cannot_borrow_damaged_item(self):
        library = create_library()
        borrower = create_borrower(library)
        item = create_thing(library, ThingStatus.DAMAGED, USDMoney(100))
        library.add_item(item)

        with self.assertRaises(InvalidThingStatusToBorrowError):
            library.borrow(item, borrower, DueDate(datetime(2022, 12, 12)))
    
    def test_cannot_borrow_if_too_many_fees(self):
        library = create_library()
        borrower = create_borrower(library)
        item = create_thing(library)
        library.add_item(item)

        loan = Loan("loan", item, borrower, DueDate())
        borrower.apply_fee(LibraryFee(USDMoney(120), loan, FeeStatus.OUTSTANDING))

        with self.assertRaises(BorrowerNotInGoodStandingError):
            library.borrow(item, borrower, DueDate(datetime(2022, 12, 12)))
    
    def test_can_borrow_and_return_on_time(self):
        library = create_library()
        borrower = create_borrower(library)
        item = create_thing(library)
        library.add_item(item)

        loan = library.borrow(item, borrower, get_due_date())
        self.assertIsNotNone(loan)
        self.assertEqual(loan.item.status, ThingStatus.BORROWED)
        
        finished = library.finish_return(library.start_return(loan))
        self.assertEqual(finished.status, LoanStatus.RETURNED)
        self.assertEqual(finished.item.status, ThingStatus.READY)
    
if __name__ == '__main__':
    unittest.main()
