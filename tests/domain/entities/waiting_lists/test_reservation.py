import pytest
from datetime import datetime, timedelta

from domain.entities.waiting_lists.reservation import Reservation, ReservationStatus
from domain.entities.people.person_borrower import PersonBorrower
from domain.entities.people.person import PersonName
from domain.entities.thing import Thing
from domain.value_items import ID, Money, ThingTitle, Location
from domain.value_items.exceptions import InvalidReservationStateTransitionError


@pytest.fixture
def sample_borrower():
    return PersonBorrower(
        person_id=ID.generate(),
        library_id=ID.generate(),
        name=PersonName(first_name="Jane", last_name="Doe"),
        emails=["jane.doe@example.com"],
        verification_flags=[],
    )


@pytest.fixture
def sample_item():
    return Thing(
        thing_id=ID.generate(),
        title=ThingTitle(name="Effective Python"),
        description="A book about Python best practices.",
        owner_id=ID.generate(),
        storage_location=Location(name="Main Branch", latitude=0.0, longitude=0.0),
        purchase_cost=Money(amount=30, currency_name="USD"), # type: ignore
        image_urls=[],
    )


@pytest.fixture
def new_reservation(sample_borrower, sample_item):
    # Create a fresh reservation with default ASSIGNED status
    return Reservation(
        reservation_id=ID.generate(),
        holder=sample_borrower,
        item=sample_item,
        good_until=datetime.utcnow() + timedelta(days=5),
    )


def test_reservation_initial_state(new_reservation, sample_borrower, sample_item):
    assert new_reservation.status == ReservationStatus.ASSIGNED
    assert new_reservation.holder == sample_borrower
    assert new_reservation.item == sample_item
    assert new_reservation.good_until > datetime.utcnow()


def test_full_lifecycle_success(new_reservation):
    # ASSIGNED -> BORROWER_NOTIFIED
    new_reservation.transition_to(ReservationStatus.BORROWER_NOTIFIED)
    assert new_reservation.status == ReservationStatus.BORROWER_NOTIFIED

    # BORROWER_NOTIFIED -> BORROWED
    new_reservation.transition_to(ReservationStatus.BORROWED)
    assert new_reservation.status == ReservationStatus.BORROWED

    # Once borrowed, can't notify again or cancel - expect errors
    with pytest.raises(InvalidReservationStateTransitionError):
        new_reservation.transition_to(ReservationStatus.BORROWER_NOTIFIED)
    with pytest.raises(InvalidReservationStateTransitionError):
        new_reservation.transition_to(ReservationStatus.CANCELLED)


def test_expire_and_cancel_flows(new_reservation):
    # ASSIGNED -> CANCELLED directly allowed
    new_reservation.transition_to(ReservationStatus.CANCELLED)
    assert new_reservation.status == ReservationStatus.CANCELLED

    # Reset for next test
    new_reservation._status = ReservationStatus.ASSIGNED

    # ASSIGNED -> BORROWER_NOTIFIED -> CANCELLED allowed
    new_reservation.transition_to(ReservationStatus.BORROWER_NOTIFIED)
    new_reservation.transition_to(ReservationStatus.CANCELLED)
    assert new_reservation.status == ReservationStatus.CANCELLED

    # Reset for expiry test
    new_reservation._status = ReservationStatus.BORROWER_NOTIFIED

    # BORROWER_NOTIFIED -> EXPIRED allowed
    new_reservation.transition_to(ReservationStatus.EXPIRED)
    assert new_reservation.status == ReservationStatus.EXPIRED


def test_invalid_status_transitions(new_reservation):
    # Try invalid transition ASSIGNED -> BORROWED directly (skip notification)
    with pytest.raises(InvalidReservationStateTransitionError):
        new_reservation.transition_to(ReservationStatus.BORROWED)

    # Move to BORROWED
    new_reservation.transition_to(ReservationStatus.BORROWER_NOTIFIED)
    new_reservation.transition_to(ReservationStatus.BORROWED)

    # Try invalid transition BORROWED -> ASSIGNED
    with pytest.raises(InvalidReservationStateTransitionError):
        new_reservation.transition_to(ReservationStatus.ASSIGNED)

    # Try invalid transition BORROWED -> CANCELLED
    with pytest.raises(InvalidReservationStateTransitionError):
        new_reservation.transition_to(ReservationStatus.CANCELLED)


def test_good_until_date_in_future(new_reservation):
    # Ensure good_until is always in the future at creation
    assert new_reservation.good_until > datetime.utcnow()
