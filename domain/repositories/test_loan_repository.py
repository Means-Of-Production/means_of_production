from unittest.mock import Mock
from domain import Person, PersonName, Borrower, LibraryRepository, Loan
from loan_repository import LoanRepository

def test_get_loans_for_person_filters_by_borrower():
    # Create mock person
    person = Person(person_id="personId", name=PersonName("Testy", "McTesterson"))
    borrower = Mock(spec=Borrower)
    borrower.person = person

    other_person = Person("anotherPerson", PersonName("Billy", "Jean"))
    other_borrower = Mock(spec=Borrower)
    other_borrower.person = other_person

    # Create mock library repository
    library_repository = Mock(spec=LibraryRepository)

    # Create mock loans
    loan1 = Mock(spec=Loan)
    loan1.borrower = borrower

    loan2 = Mock(spec=Loan)
    loan2.borrower = other_borrower

    # Initialize LoanRepository
    under_test = LoanRepository(library_repository)
    under_test.add(loan1)
    under_test.add(loan2)

    # Run method and check results
    res = list(under_test.get_loans_for_person(person))
    assert len(res) == 1
