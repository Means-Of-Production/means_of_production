import pytest
from datetime import datetime, timedelta, UTC

# Domain and value objects
from domain.entities.people.person_borrower import PersonBorrower
from domain.entities.people.person import PersonName
from domain.entities.waiting_lists.waiting_list import WaitingList
from domain.entities.thing import Thing
from domain.entities.waiting_lists.reservation import ReservationStatus
from domain.value_items import ID, ThingTitle, Money
from domain.value_items.location import Location
from domain.value_items.thing_status import ThingStatus


# Dummy concrete implementation of the abstract WaitingList for testing
class SimpleWaitingList(WaitingList):
    borrowers: list[PersonBorrower] = []

    # Add borrower if not already on list
    def add(self, borrower: PersonBorrower) -> WaitingList:  # type: ignore
        if not self.is_on_list(borrower):
            self.borrowers.append(borrower)
        return self

    # Return the first borrower on the list
    def find_next_borrower(self):
        return self.borrowers[0] if self.borrowers else None

    # Check if borrower is already in the waiting list
    def is_on_list(self, borrower: PersonBorrower) -> bool:  # type: ignore
        return borrower in self.borrowers

    # Mark reservation as expired and clear the current reservation
    def process_reservation_expired(self, reservation):
        self.expired_reservations.append(reservation)
        self.clear_current_reservation()
        return self

    # Remove a borrower from the list
    def cancel(self, borrower: PersonBorrower) -> WaitingList:  # type: ignore
        self.borrowers = [b for b in self.borrowers if b != borrower]
        return self

    # Define the reservation duration (2 days)
    def get_reservation_time(self) -> timedelta:
        return timedelta(days=2)


# ---------- Fixtures ----------

# Reusable test fixture for a sample borrower
@pytest.fixture
def borrower():
    return PersonBorrower(
        person_id=ID.generate(),
        library_id=ID.generate(),
        name=PersonName(first_name="Alice", last_name="Test"),
        emails=[],
        verification_flags=[],
    )


# Reusable test fixture for a sample Thing (e.g., a Laptop)
@pytest.fixture
def thing():
    return Thing(
        thing_id=ID.generate(),
        title=ThingTitle(name="Laptop"),
        description="Work laptop",
        owner_id=ID.generate(),
        storage_location=Location(name="Shelf A", latitude=0.0, longitude=0.0),
        image_urls=[],
        purchase_cost=Money(amount=1000, currency_name="EUR"),  # type: ignore
    )


# ---------- Tests ----------

# Test adding a borrower to the waiting list
def test_add_borrower_to_list(borrower, thing):
    wl = SimpleWaitingList(item=thing)
    wl.add(borrower)
    assert wl.is_on_list(borrower)
    assert borrower in wl.borrowers


# Test that a reservation is properly created and status set to ASSIGNED
def test_reserve_item_for_next_borrower_sets_status(borrower, thing):
    wl = SimpleWaitingList(item=thing)
    wl.add(borrower)

    reservation = wl.reserve_item_for_next_borrower()

    assert reservation.holder == borrower
    assert reservation.item == thing
    assert reservation.status == ReservationStatus.ASSIGNED
    assert wl.current_reservation == reservation
    assert not wl.is_on_list(borrower)
    assert thing.status == ThingStatus.RESERVED


# Test that trying to reserve when one already exists raises an error
def test_reserve_raises_if_current_reservation_exists(borrower, thing):
    wl = SimpleWaitingList(item=thing)
    wl.add(borrower)
    wl.reserve_item_for_next_borrower()

    with pytest.raises(ValueError, match="already has a reservation"):
        wl.reserve_item_for_next_borrower()


# Test that trying to reserve with no borrowers raises an error
def test_reserve_raises_if_no_borrowers(thing):
    wl = SimpleWaitingList(item=thing)

    with pytest.raises(ValueError, match="No borrower is waiting"):
        wl.reserve_item_for_next_borrower()


# Test that processing an expired reservation works as expected
def test_process_reservation_expired(borrower, thing):
    wl = SimpleWaitingList(item=thing)
    wl.add(borrower)
    reservation = wl.reserve_item_for_next_borrower()

    wl.process_reservation_expired(reservation)

    assert reservation in wl.expired_reservations
    assert wl.current_reservation is None
