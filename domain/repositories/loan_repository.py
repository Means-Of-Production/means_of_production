from typing import Iterable

from domain.entities import Library, Loan, Person
from domain.repositories.base_in_memory_repository import BaseInMemoryRepository
from domain.repositories.library_repository import LibraryRepository


class LoanRepository(BaseInMemoryRepository):
    def __init__(self, library_repository: LibraryRepository):
        super().__init__()
        self.library_repository = library_repository

    def get_id_field_name(self) -> str:
        return "loan_id"

    def get_loans_for_person(self, person: Person) -> Iterable[Loan]:
        for loan in self.get_all():
            if loan.borrower.person == person:
                yield loan

    def get_loans_for_library(self, library: Library) -> Iterable[Loan]:
        for loan in self.get_all():
            if loan.borrower.library.id == library.entity_id:
                yield loan
