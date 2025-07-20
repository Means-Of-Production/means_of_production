import pytest
from datetime import datetime, timedelta

# Import domain models and helper classes
from domain.entities.waiting_lists.reservation import Reservation, ReservationStatus
from domain.entities.people.person import PersonName
from domain.entities import Thing
from domain.value_items import ID, Money, ThingTitle
from domain.entities.people.person_borrower import PersonBorrower
from domain.value_items.location import Location
from domain.value_items.exceptions import InvalidReservationStateTransitionError

# Fixture for creating a sample borrower
@pytest.fixture
def borrower():
    return PersonBorrower(
        library_id=ID.generate(),
        person_id=ID.generate(),
        name=PersonName(first_name="John", last_name="Doe"),
        emails=[],
        verification_flags=[],
    )

# Fixture for creating a sample item (Thing)
@pytest.fixture
def item_one():
    return Thing(
        thing_id=ID.generate(),
        title=ThingTitle(name="Test Item"),
        description="Test Description",
        owner_id=ID.generate(),
        storage_location=Location(name="Main Shelf", latitude=0.0, longitude=0.0),
        image_urls=[],
        purchase_cost=Money(amount=10, currency_name="EUR"),  # type: ignore
    )

# Test: Ensure reservation starts with ASSIGNED status by default
def test_initial_status(borrower, item_one):
    r = Reservation(
        reservation_id=ID.generate(),
        holder=borrower,
        item=item_one,
        good_until=datetime.now() + timedelta(days=1),
    )
    assert r.status == ReservationStatus.ASSIGNED

# Test: Transition from ASSIGNED to BORROWER_NOTIFIED is valid
def test_valid_status_transition_to_borrower_notified(borrower, item_one):
    r = Reservation(
        reservation_id=ID.generate(),
        holder=borrower,
        item=item_one,
        good_until=datetime.now() + timedelta(days=1),
    )
    r.transition_to(ReservationStatus.BORROWER_NOTIFIED)
    assert r.status == ReservationStatus.BORROWER_NOTIFIED

# Test: Transition from ASSIGNED to CANCELLED is valid
def test_valid_transition_to_cancelled_from_assigned(borrower, item_one):
    r = Reservation(
        reservation_id=ID.generate(),
        holder=borrower,
        item=item_one,
        good_until=datetime.now() + timedelta(days=1),
    )
    r.transition_to(ReservationStatus.CANCELLED)
    assert r.status == ReservationStatus.CANCELLED

# Test: Transition from BORROWER_NOTIFIED to CANCELLED is valid
def test_valid_transition_to_cancelled_from_borrower_notified(borrower, item_one):
    r = Reservation(
        reservation_id=ID.generate(),
        holder=borrower,
        item=item_one,
        good_until=datetime.now() + timedelta(days=1),
        status=ReservationStatus.BORROWER_NOTIFIED,
    )
    r.transition_to(ReservationStatus.CANCELLED)
    assert r.status == ReservationStatus.CANCELLED

# Test: Full valid transition flow from ASSIGNED -> BORROWER_NOTIFIED -> BORROWED
def test_valid_full_lifecycle_transition(borrower, item_one):
    r = Reservation(
        reservation_id=ID.generate(),
        holder=borrower,
        item=item_one,
        good_until=datetime.now() + timedelta(days=1),
    )
    r.transition_to(ReservationStatus.BORROWER_NOTIFIED)
    r.transition_to(ReservationStatus.BORROWED)
    assert r.status == ReservationStatus.BORROWED

# Parametrized test for various valid transitions
@pytest.mark.parametrize("from_status,to_status", [
    (ReservationStatus.BORROWER_NOTIFIED, ReservationStatus.BORROWED),
    (ReservationStatus.BORROWER_NOTIFIED, ReservationStatus.CANCELLED),
    (ReservationStatus.ASSIGNED, ReservationStatus.BORROWER_NOTIFIED),
    (ReservationStatus.ASSIGNED, ReservationStatus.CANCELLED),
])
def test_valid_transitions(from_status, to_status, borrower, item_one):
    r = Reservation(
        reservation_id=ID.generate(),
        holder=borrower,
        item=item_one,
        good_until=datetime.now() + timedelta(days=1),
        status=from_status,
    )
    r.transition_to(to_status)
    assert r.status == to_status

# Parametrized test to verify invalid transitions raise correct error
@pytest.mark.parametrize("from_status,to_status", [
    (ReservationStatus.BORROWER_NOTIFIED, ReservationStatus.ASSIGNED),
    (ReservationStatus.BORROWED, ReservationStatus.ASSIGNED),
    (ReservationStatus.EXPIRED, ReservationStatus.BORROWED),
])
def test_invalid_transitions_raise(from_status, to_status, borrower, item_one):
    r = Reservation(
        reservation_id=ID.generate(),
        holder=borrower,
        item=item_one,
        good_until=datetime.now() + timedelta(days=1),
        status=from_status,
    )
    with pytest.raises(InvalidReservationStateTransitionError):
        r.transition_to(to_status)
