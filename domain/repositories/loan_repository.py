from typing import Iterable
from .base_in_memory_repository import BaseInMemoryRepository
from domain import ILibrary, ILibraryRepository, ILoan, ILoanRepository, Loan, Person, PhysicalLocation


class LoanRepository(BaseInMemoryRepository, ILoanRepository):
    def __init__(self, library_repository: ILibraryRepository):
        super().__init__()
        self.library_repository = library_repository

    def create(self, entity: ILoan) -> ILoan:
        return Loan(
            self.new_id(),
            entity.item,
            entity.borrower,
            entity.due_date,
            entity.status,
            entity.return_location if isinstance(entity.return_location, PhysicalLocation) else None,
            entity.date_returned
        )

    def get_loans_for_person(self, person: Person) -> Iterable[ILoan]:
        for loan in self.get_all():
            if loan.borrower.person == person:
                yield loan

    def get_loans_for_library(self, library: ILibrary) -> Iterable[ILoan]:
        for loan in self.get_all():
            if loan.borrower.library.id == library.id:
                yield loan
