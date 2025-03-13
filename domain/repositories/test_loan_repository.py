import unittest
from unittest.mock import Mock
from meansofproduction.domain import Person, PersonName, IBorrower, ILibraryRepository, ILoan
from loan_repository import LoanRepository

class TestLoanRepository(unittest.TestCase):
    def test_get_loans_for_person_filters_by_borrower(self):
        # Create mock person
        person = Person("personId", PersonName("Testy", "McTesterson"))
        borrower = Mock(spec=IBorrower)
        borrower.person = person
        
        other_person = Person("anotherPerson", PersonName("Billy", "Jean"))
        other_borrower = Mock(spec=IBorrower)
        other_borrower.person = other_person
        
        # Create mock library repository
        library_repository = Mock(spec=ILibraryRepository)
        
        # Create mock loans
        loan1 = Mock(spec=ILoan)
        loan1.borrower = borrower
        
        loan2 = Mock(spec=ILoan)
        loan2.borrower = other_borrower
        
        # Initialize LoanRepository
        under_test = LoanRepository(library_repository)
        under_test.add(loan1)
        under_test.add(loan2)
        
        # Run method and check results
        res = list(under_test.get_loans_for_person(person))
        self.assertEqual(len(res), 1)

if __name__ == "__main__":
    unittest.main()