import unittest
from unittest.mock import MagicMock
from domain.entities import Person, ILibrary, IBorrower, PersonName
from library_repository import LibraryRepository


class TestLibraryRepository(unittest.TestCase):
    def test_gets_libraries_via_person(self):
        # Arrange
        person_name = PersonName("Testy", "McTesterson")
        person = Person("test", person_name, [])

        mock_lib1 = MagicMock(spec=ILibrary)
        mock_borrower1 = MagicMock(spec=IBorrower)
        mock_borrower1.person = person
        mock_lib1.borrowers = [mock_borrower1]

        mock_lib2 = MagicMock(spec=ILibrary)
        mock_borrower2 = MagicMock(spec=IBorrower)
        mock_borrower2.person = Person("nope", person_name, [])
        mock_lib2.borrowers = [mock_borrower2]

        under_test = LibraryRepository([mock_lib1, mock_lib2])

        # Act
        res = list(under_test.get_libraries_person_can_use(person))

        # Assert
        self.assertIsNotNone(res)
        self.assertEqual(len(res), 1)


if __name__ == "__main__":
    unittest.main()
