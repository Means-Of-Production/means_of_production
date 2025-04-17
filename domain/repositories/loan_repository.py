from typing import Iterable
from domain.entities import Loan, Person
from domain.value_items import PhysicalLocation
from domain.repositories import BaseInMemoryRepository, LibraryRepository
from domain.entities.libraries import Library

class LoanRepository(BaseInMemoryRepository):
    def __init__(self, library_repository: LibraryRepository):
        super().__init__()
        self.library_repository = library_repository

    def create(self, entity: 'Loan') -> 'Loan':
        return Loan(
            loan_id=self.new_id(),
            item=entity.item,
            entity.borrower,
            entity.due_date,
            entity.status,
            entity.return_location if isinstance(entity.return_location, PhysicalLocation) else None,
            entity.date_returned
        )

    def get_loans_for_person(self, person: 'Person') -> Iterable['Loan']:
        for loan in self.get_all():
            if loan.borrower.person == person:
                yield loan

    def get_loans_for_library(self, library: Library) -> Iterable[Loan]:
        for loan in self.get_all():
            if loan.borrower.library.id == library.entity_id:
                yield loan