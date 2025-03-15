from unittest.mock import MagicMock
from domain.entities import Person, Library, Borrower, PersonName
from library_repository import LibraryRepository

def test_gets_libraries_via_person():
    # Arrange
    person_name = PersonName("Testy", "McTesterson")
    person = Person("test", person_name, [])

    mock_lib1 = MagicMock(spec=Library)
    mock_borrower1 = MagicMock(spec=Borrower)
    mock_borrower1.person = person
    mock_lib1.borrowers = [mock_borrower1]

    mock_lib2 = MagicMock(spec=Library)
    mock_borrower2 = MagicMock(spec=Borrower)
    mock_borrower2.person = Person("nope", person_name, [])
    mock_lib2.borrowers = [mock_borrower2]

    under_test = LibraryRepository([mock_lib1, mock_lib2])

    # Act
    res = list(under_test.get_libraries_person_can_use(person))

    # Assert
    assert res is not None
    assert len(res) == 1
