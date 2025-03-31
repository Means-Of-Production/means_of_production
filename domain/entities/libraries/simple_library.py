from datetime import datetime, timedelta
from typing import List, Optional, Iterable
from dataclasses import dataclass

# Constants for item and loan statuses
class ThingStatus:
    READY = "READY"
    BORROWED = "BORROWED"

class LoanStatus:
    BORROWED = "BORROWED"
    RETURN_STARTED = "RETURN_STARTED"
    WAITING_ON_LENDER_ACCEPTANCE = "WAITING_ON_LENDER_ACCEPTANCE"

# Exception classes
class InvalidThingStatusToBorrowError(Exception):
    pass

class BorrowerNotInGoodStandingError(Exception):
    pass

# Data classes for core entities
@dataclass
class PhysicalLocation:
    address: str

@dataclass
class ThingTitle:
    name: str

@dataclass
class DueDate:
    date: datetime

@dataclass
class Thing:
    title: ThingTitle
    status: str = ThingStatus.READY

@dataclass
class Borrower:
    name: str
    fines_due: float = 0.0

@dataclass
class Loan:
    item: Thing
    borrower: Borrower
    due_date: DueDate
    status: str
    return_date: Optional[datetime] = None

# Base Library class
class BaseLibrary:
    def __init__(self, id: str, name: str, admin: str, max_fines: float, default_loan_days: int = 14):
        self.id = id
        self.name = name
        self.admin = admin
        self.max_fines = max_fines
        self.default_loan_days = default_loan_days
        self.loans: List[Loan] = []

    def can_borrow(self, borrower: Borrower) -> bool:
        return borrower.fines_due <= self.max_fines

    def add_loan(self, loan: Loan):
        self.loans.append(loan)

# Simple Library implementation
class SimpleLibrary(BaseLibrary):
    def __init__(self, id: str, name: str, admin: str, location: PhysicalLocation, max_fines: float):
        super().__init__(id, name, admin, max_fines)
        self.location = location
        self.items: List[Thing] = []

    def add_item(self, item: Thing) -> Thing:
        self.items.append(item)
        return item

    def get_all_things(self) -> Iterable[Thing]:
        return self.items

    def borrow(self, item: Thing, borrower: Borrower, until: Optional[DueDate] = None) -> Loan:
        if item.status != ThingStatus.READY:
            raise InvalidThingStatusToBorrowError(f"Item status is {item.status}")
        
        if not self.can_borrow(borrower):
            raise BorrowerNotInGoodStandingError("Borrower is not in good standing")
        
        until = until or DueDate(datetime.now() + timedelta(days=self.default_loan_days))
        loan = Loan(item=item, borrower=borrower, due_date=until, status=LoanStatus.BORROWED)
        
        item.status = ThingStatus.BORROWED
        self.add_loan(loan)
        return loan

    def start_return(self, loan: Loan) -> Loan:
        loan.status = LoanStatus.WAITING_ON_LENDER_ACCEPTANCE
        loan.return_date = datetime.now()
        return loan
