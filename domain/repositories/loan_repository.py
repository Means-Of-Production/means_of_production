from __future__ import annotations
from typing import Iterable, TYPE_CHECKING
from .base_in_memory_repository import BaseInMemoryRepository
from domain.value_items.location.physical_location import PhysicalLocation

if TYPE_CHECKING:
    from domain.entities.libraries.library import Library
    from domain.repositories.library_repository import LibraryRepository
    from domain.entities.loans.loan import Loan
    from domain.entities.people.person import Person

class LoanRepository(BaseInMemoryRepository):
    def __init__(self, library_repository: 'LibraryRepository'):
        super().__init__()
        self.library_repository = library_repository

    def create(self, entity: 'Loan') -> 'Loan':
        return Loan(
            self.new_id(),
            entity.item,
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

    def get_loans_for_library(self, library: 'Library') -> Iterable['Loan']:
        for loan in self.get_all():
            if loan.borrower.library.id == library.id:
                yield loan