import pytest
from datetime import timedelta
from unittest.mock import Mock, MagicMock

# Domain entities and value objects
from domain.entities.borrower import Borrower
from domain.entities.waiting_lists.reservation import Reservation
from domain.entities.waiting_lists.null_waiting_list import NullWaitingList
from domain.entities.thing import Thing  # Required for NullWaitingList instantiation


class TestNullWaitingList:
    # Fixture to create a mock Thing instance for testing
    @pytest.fixture
    def mock_thing(self) -> Thing:
        # MagicMock ensures compatibility with Pydantic if validation is used
        return MagicMock(spec=Thing)

    # Fixture to create a NullWaitingList instance with the mocked Thing
    @pytest.fixture
    def null_waiting_list(self, mock_thing: Thing) -> NullWaitingList:
        return NullWaitingList(item=mock_thing)

    # Fixture for a mock Borrower object
    @pytest.fixture
    def mock_borrower(self) -> Borrower:
        return Mock(spec=Borrower)

    # Fixture for a mock Reservation object
    @pytest.fixture
    def mock_reservation(self) -> Reservation:
        return Mock(spec=Reservation)

    # Test that calling add() returns the same instance (null pattern)
    def test_add_borrower_returns_self(
        self, null_waiting_list: NullWaitingList, mock_borrower: Borrower
    ):
        result = null_waiting_list.add(mock_borrower)
        assert result is null_waiting_list  # Should return itself

    # Test that find_next_borrower() always returns None for NullWaitingList
    def test_find_next_borrower_always_returns_none(
        self, null_waiting_list: NullWaitingList
    ):
        assert null_waiting_list.find_next_borrower() is None

    # Test that is_on_list() always returns False for any borrower
    def test_is_on_list_always_returns_false(
        self, null_waiting_list: NullWaitingList, mock_borrower: Borrower
    ):
        assert not null_waiting_list.is_on_list(mock_borrower)

    # Test that process_reservation_expired() returns the same instance
    def test_process_reservation_expired_returns_self(
        self, null_waiting_list: NullWaitingList, mock_reservation: Reservation
    ):
        result = null_waiting_list.process_reservation_expired(mock_reservation)
        assert result is null_waiting_list

    # Test that cancel() returns the same instance (no operation)
    def test_cancel_returns_self(
        self, null_waiting_list: NullWaitingList, mock_borrower: Borrower
    ):
        result = null_waiting_list.cancel(mock_borrower)
        assert result is null_waiting_list

    # Test that get_reservation_time() returns a zero-duration timedelta
    def test_get_reservation_time_returns_zero_delta(
        self, null_waiting_list: NullWaitingList
    ):
        assert null_waiting_list.get_reservation_time() == timedelta(days=0)

    # Test that chaining multiple operations does not affect the object
    def test_multiple_operations_chain_correctly(
        self, null_waiting_list: NullWaitingList, mock_borrower: Borrower
    ):
        result = (
            null_waiting_list
            .add(mock_borrower)
            .cancel(mock_borrower)
            .process_reservation_expired(Mock(spec=Reservation))
        )
        # Assert the object remains unchanged and consistent
        assert result is null_waiting_list
        assert result.find_next_borrower() is None
