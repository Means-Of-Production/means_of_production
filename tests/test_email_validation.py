from domain.entities.people.person import Person
from domain.value_items import ID, PersonName


def test_person_with_email():
    # Create a person with an email
    person = Person(
        person_id=ID.generate(),
        name=PersonName(first_name="Test", last_name="User"),
        emails=["test@example.com"],
    )

    # Verify the email was set correctly
    assert len(person.emails) == 1
    assert person.emails[0] == "test@example.com"


if __name__ == "__main__":
    test_person_with_email()
    print("Email validation test passed!")
