import decimal
import pytest
from uuid import UUID

from domain.entities.thing import Thing
from domain.entities.waiting_lists.first_come_first_serve_waiting_list import (
    FirstComeFirstServeWaitingList
)
from domain.entities.people.person_borrower import PersonBorrower
from domain.entities.people.person import PersonName
from domain.value_items.borrower_verification_flags import BorrowerVerificationFlags
from domain.value_items import (
    ID,
    Location,
    Money,
    ThingStatus,
    ThingTitle,
    ReservationStatus
)
from domain.value_items.exceptions import InvalidThingStateTransitionError


def create_sample_borrower(first_name: str, last_name: str = "Doe") -> PersonBorrower:
    """Helper to create a properly initialized borrower"""
    return PersonBorrower(
        person_id=ID.generate(),
        library_id=ID.generate(),
        name=PersonName(first_name=first_name, last_name=last_name),
        emails=[f"{first_name.lower()}@example.com"],
        verification_flags=[BorrowerVerificationFlags.EMAIL]
    )


@pytest.fixture
def sample_thing() -> Thing:
    """Fixture providing a properly initialized Thing"""
    return Thing(
        thing_id=ID.generate(),
        title=ThingTitle(name="Sample Book"),
        description="Test Description",
        owner_id=ID.generate(),
        storage_location=Location(name="Main Library", latitude=0, longitude=0),
        purchase_cost=Money(amount=decimal.Decimal("10.00"), currency_name="USD"),
    )


@pytest.fixture
def waiting_list(sample_thing: Thing) -> FirstComeFirstServeWaitingList:
    """Fixture providing a waiting list with a sample thing"""
    return FirstComeFirstServeWaitingList(
        waiting_list_id=ID.generate(),
        item=sample_thing,
        members=[],
        reservation_days=3
    )


def test_reservation_borrow_flow(waiting_list: FirstComeFirstServeWaitingList, sample_thing: Thing):
    person1 = create_sample_borrower("Alice", "Anderson")
    person2 = create_sample_borrower("Bob", "Brown")
    person3 = create_sample_borrower("Charlie", "Clark")

    # 1. person1 borrows the item
    sample_thing.status = ThingStatus.BORROWED
    assert sample_thing.status == ThingStatus.BORROWED

    # 2. person2 reserves it (adds to waiting list and reserves next)
    waiting_list.add(person2)
    reservation = waiting_list.reserve_item_for_next_borrower()
    assert reservation is not None
    assert reservation.holder == person2
    assert sample_thing.status == ThingStatus.RESERVED

    # 3. person1 returns the item (status becomes READY)
    sample_thing.status = ThingStatus.READY
    assert sample_thing.status == ThingStatus.READY

    # 4. person3 attempts to borrow but cannot
    # Add person3 to waiting list
    waiting_list.add(person3)
    assert waiting_list.is_on_list(person3)

    # person3 tries to reserve next but should fail because person2 still has reservation
    with pytest.raises(ValueError, match="This item already has a reservation"):
        waiting_list.reserve_item_for_next_borrower()

    # 5. person2 borrows (item status BORROWED)
    sample_thing.status = ThingStatus.BORROWED
    assert sample_thing.status == ThingStatus.BORROWED


    # Phase 6: Clear current reservation before reserving for Charlie
    waiting_list.clear_current_reservation()
    reservation = waiting_list.reserve_item_for_next_borrower()
    assert reservation.holder == person3
    assert sample_thing.status == ThingStatus.RESERVED

    # Phase 7: Invalid transition to DAMAGED
    with pytest.raises(InvalidThingStateTransitionError):
        sample_thing.status = ThingStatus.DAMAGED



def test_waiting_list_operations(waiting_list, sample_thing):
    """Test waiting list add and cancel operations"""
    person = create_sample_borrower("Test", "User")

    # Add person to list
    waiting_list.add(person)
    assert waiting_list.is_on_list(person)
    assert len(waiting_list.members) == 1

    # Remove person from list
    waiting_list.cancel(person)
    assert not waiting_list.is_on_list(person)
    assert len(waiting_list.members) == 0


def test_state_transitions(sample_thing):
    """Test allowed and disallowed Thing state transitions"""

    # Ready → Borrowed
    sample_thing.status = ThingStatus.BORROWED
    assert sample_thing.status == ThingStatus.BORROWED

    # Borrowed → Ready
    sample_thing.status = ThingStatus.READY
    assert sample_thing.status == ThingStatus.READY

    # Ready → Reserved
    sample_thing.status = ThingStatus.RESERVED
    assert sample_thing.status == ThingStatus.RESERVED

    # Reserved → Borrowed
    sample_thing.status = ThingStatus.BORROWED
    assert sample_thing.status == ThingStatus.BORROWED

    # Invalid transition: Ready → Damaged (if not allowed)
    sample_thing.status = ThingStatus.READY
    with pytest.raises(InvalidThingStateTransitionError):
        sample_thing.status = ThingStatus.DAMAGED
