import decimal
from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from domain.entities.borrower import Borrower
from domain.entities.thing import Thing
from domain.entities.waiting_lists.auctionable_waiting_list import (
    AuctionableWaitingList,
    AuctionBid,
)
from domain.entities.waiting_lists.first_come_first_serve_waiting_list import (
    FirstComeFirstServeWaitingList,
)
from domain.entities.waiting_lists.reservation import Reservation
from domain.value_items import ID, Money, ReservationStatus, ThingTitle
from domain.value_items.exceptions import EntityNotAssignedIdError


@pytest.fixture
def thing():
    thing = MagicMock(spec=Thing)
    thing.entity_id = ID.generate()
    thing.title = ThingTitle(name="Test Book")
    return thing


@pytest.fixture
def borrower():
    borrower = MagicMock(spec=Borrower)
    borrower.entity_id = ID.generate()
    return borrower


@pytest.fixture
def another_borrower():
    borrower = MagicMock(spec=Borrower)
    borrower.entity_id = ID.generate()
    return borrower


@pytest.fixture
def third_borrower():
    borrower = MagicMock(spec=Borrower)
    borrower.entity_id = ID.generate()
    return borrower


@pytest.fixture
def backup_list(thing):
    backup_list = MagicMock(spec=FirstComeFirstServeWaitingList)
    backup_list.waiting_list_id = ID.generate()
    backup_list.item = thing
    backup_list.members = []
    backup_list.reservation_days = 3
    return backup_list


@pytest.fixture
def waiting_list(thing, backup_list):
    waiting_list = AuctionableWaitingList(
        waiting_list_id=ID.generate(),
        item=thing,
        currency_name="USD",
        started=datetime.now(),
        ends=datetime.now() + timedelta(days=7),
    )
    waiting_list._backup_list = backup_list
    return waiting_list


@pytest.fixture
def money():
    return Money(amount=decimal.Decimal(10.0), currency_name="USD")


@pytest.fixture
def another_money():
    return Money(amount=decimal.Decimal(20.0), currency_name="USD")


@pytest.fixture
def bid(money, borrower, another_borrower):
    return AuctionBid(
        amount_bid=money,
        made_by=borrower,
        made_for=another_borrower,
    )


@pytest.fixture
def reservation(thing, borrower):
    # Create a mock Reservation object
    mock_reservation = MagicMock(spec=Reservation)
    mock_reservation.reservation_id = ID.generate()
    mock_reservation.holder = borrower
    mock_reservation.item = thing
    mock_reservation.good_until = MagicMock()
    mock_reservation.status = ReservationStatus.ASSIGNED
    return mock_reservation


def test_auction_bid_initialization(money, borrower, another_borrower):
    # Test initializing an AuctionBid
    bid = AuctionBid(
        amount_bid=money,
        made_by=borrower,
        made_for=another_borrower,
    )

    # Verify the bid properties
    assert bid.amount_bid == money
    assert bid.made_by == borrower
    assert bid.made_for == another_borrower


def test_entity_id(waiting_list):
    # Test the entity_id property
    assert waiting_list.entity_id == waiting_list.waiting_list_id


def test_add(waiting_list, borrower, backup_list):
    # Mock the backup_list.add method
    backup_list.add = MagicMock(return_value=backup_list)

    # Test adding a borrower
    result = waiting_list.add(borrower)

    # Verify the backup_list.add method was called with the borrower
    backup_list.add.assert_called_once_with(borrower)

    # Verify the method returns self for chaining
    assert result == waiting_list


def test_add_bid(waiting_list, bid):
    # Test adding a bid
    result = waiting_list.add_bid(bid)

    # Verify the bid was added to _bids_by_for_id
    assert bid in waiting_list._bids_by_for_id[bid.made_for.entity_id]

    # Verify the method returns self for chaining
    assert result == waiting_list


def test_add_bid_no_entity_id(waiting_list, money, borrower):
    # Create a borrower with no entity_id
    no_id_borrower = MagicMock(spec=Borrower)
    no_id_borrower.entity_id = None

    # Create a bid with a borrower that has no entity_id
    bid = AuctionBid(
        amount_bid=money,
        made_by=borrower,
        made_for=no_id_borrower,
    )

    # Test adding a bid with a borrower that has no entity_id
    with pytest.raises(EntityNotAssignedIdError):
        waiting_list.add_bid(bid)


def test_get_bids(waiting_list, bid, money, borrower, another_borrower, third_borrower):
    # Add a bid
    waiting_list.add_bid(bid)

    # Add another bid
    another_bid = AuctionBid(
        amount_bid=money,
        made_by=borrower,
        made_for=third_borrower,
    )
    waiting_list.add_bid(another_bid)

    # Test getting all bids
    bids = waiting_list.get_bids()

    # Verify both bids are returned
    assert bid in bids
    assert another_bid in bids


def test_get_winning_borrower(
    waiting_list, money, another_money, borrower, another_borrower, third_borrower
):
    # Add a bid for another_borrower
    bid1 = AuctionBid(
        amount_bid=money,
        made_by=borrower,
        made_for=another_borrower,
    )
    waiting_list.add_bid(bid1)

    # Add a higher bid for third_borrower
    bid2 = AuctionBid(
        amount_bid=another_money,
        made_by=borrower,
        made_for=third_borrower,
    )
    waiting_list.add_bid(bid2)

    # Test getting the winning borrower
    winner = waiting_list.get_winning_borrower()

    # Verify the borrower with the highest bid is returned
    assert winner == third_borrower


def test_get_winning_borrower_multiple_bids(
    waiting_list, money, another_money, borrower, another_borrower, third_borrower
):
    # Add a bid for another_borrower
    bid1 = AuctionBid(
        amount_bid=money,
        made_by=borrower,
        made_for=another_borrower,
    )
    waiting_list.add_bid(bid1)

    # Add another bid for another_borrower
    bid2 = AuctionBid(
        amount_bid=money,
        made_by=borrower,
        made_for=another_borrower,
    )
    waiting_list.add_bid(bid2)

    # Add a bid for third_borrower
    bid3 = AuctionBid(
        amount_bid=money,
        made_by=borrower,
        made_for=third_borrower,
    )
    waiting_list.add_bid(bid3)

    # Test getting the winning borrower
    winner = waiting_list.get_winning_borrower()

    # Verify the borrower with the highest total bid is returned
    assert winner == another_borrower


def test_get_winning_borrower_no_bids(waiting_list):
    # Test getting the winning borrower when there are no bids
    with pytest.raises(ValueError, match="No winning borrower found"):
        waiting_list.get_winning_borrower()


def test_is_on_list(waiting_list, borrower):
    # Test is_on_list method
    assert waiting_list.is_on_list(borrower) is False


def test_find_next_borrower_with_bids(waiting_list, money, borrower, another_borrower):
    # Add a bid
    bid = AuctionBid(
        amount_bid=money,
        made_by=borrower,
        made_for=another_borrower,
    )
    waiting_list.add_bid(bid)

    # Test finding the next borrower
    next_borrower = waiting_list.find_next_borrower()

    # Verify the winning borrower is returned
    assert next_borrower == another_borrower


def test_find_next_borrower_no_bids(waiting_list, backup_list, borrower):
    # Set up the backup_list to return a borrower when find_next_borrower is called
    backup_list.find_next_borrower.return_value = borrower

    # Test finding the next borrower when there are no bids
    next_borrower = waiting_list.find_next_borrower()

    # Verify the backup_list.find_next_borrower method was called
    backup_list.find_next_borrower.assert_called_once()

    # Verify the borrower from the backup list is returned
    assert next_borrower == borrower


def test_get_largest_amount(
    waiting_list, money, another_money, borrower, another_borrower
):
    # Add a bid
    bid1 = AuctionBid(
        amount_bid=money,
        made_by=borrower,
        made_for=another_borrower,
    )
    waiting_list.add_bid(bid1)

    # Add another bid for the same borrower
    bid2 = AuctionBid(
        amount_bid=another_money,
        made_by=borrower,
        made_for=another_borrower,
    )
    waiting_list.add_bid(bid2)

    # Test getting the largest amount
    largest_amount = waiting_list.get_largest_amount()

    # Verify the sum of the bids is returned
    expected_amount = money.amount + another_money.amount
    assert largest_amount.amount == expected_amount
    assert largest_amount.currency_name == money.currency_name


def test_get_largest_amount_no_entity_id(waiting_list, money, borrower):
    # Since we can't directly mock the get_winning_borrower method on a Pydantic model,
    # we'll use monkeypatch to patch the method for the duration of the test

    # Create a borrower with no entity_id
    no_id_borrower = MagicMock(spec=Borrower)
    no_id_borrower.entity_id = None

    # Create a subclass of AuctionableWaitingList that overrides get_winning_borrower
    class TestAuctionableWaitingList(AuctionableWaitingList):
        def get_winning_borrower(self):
            return no_id_borrower

    # Create an instance of our test class with the same attributes as the original
    test_list = TestAuctionableWaitingList(
        waiting_list_id=waiting_list.waiting_list_id,
        item=waiting_list.item,
        currency_name=waiting_list.currency_name,
        started=waiting_list.started,
        ends=waiting_list.ends,
    )
    test_list._backup_list = waiting_list._backup_list

    # Add a bid to the test list
    bid = AuctionBid(
        amount_bid=money,
        made_by=borrower,
        made_for=borrower,  # Use a valid borrower for the bid
    )
    test_list._bids_by_for_id = {borrower.entity_id: [bid]}

    # Test getting the largest amount
    with pytest.raises(EntityNotAssignedIdError):
        test_list.get_largest_amount()


def test_process_reservation_expired(waiting_list, reservation):
    # Test process_reservation_expired method
    with pytest.raises(NotImplementedError, match="Method not implemented"):
        waiting_list.process_reservation_expired(reservation)


def test_get_reservation_time(waiting_list):
    # Test get_reservation_time method
    with pytest.raises(NotImplementedError, match="Method not implemented"):
        waiting_list.get_reservation_time()


def test_cancel(waiting_list, borrower, backup_list):
    # Set up the backup_list to return itself when cancel is called
    backup_list.cancel.return_value = backup_list

    # Add a bid
    bid = AuctionBid(
        amount_bid=Money(amount=decimal.Decimal(10.0), currency_name="USD"),
        made_by=borrower,
        made_for=borrower,
    )
    waiting_list.add_bid(bid)

    # Test canceling a borrower
    result = waiting_list.cancel(borrower)

    # Verify the backup_list.cancel method was called with the borrower
    backup_list.cancel.assert_called_once_with(borrower)

    # Verify the borrower's bids were removed
    assert borrower.entity_id not in waiting_list._bids_by_for_id

    # Verify the method returns self for chaining
    assert result == waiting_list


def test_cancel_no_entity_id(waiting_list):
    # Create a borrower with no entity_id
    no_id_borrower = MagicMock(spec=Borrower)
    no_id_borrower.entity_id = None

    # Test canceling a borrower with no entity_id
    with pytest.raises(EntityNotAssignedIdError):
        waiting_list.cancel(no_id_borrower)


def test_cancel_bids_made_by_borrower(
    waiting_list, money, borrower, another_borrower, backup_list
):
    # Set up the backup_list to return itself when cancel is called
    backup_list.cancel.return_value = backup_list

    # Add a bid made by borrower for another_borrower
    bid = AuctionBid(
        amount_bid=money,
        made_by=borrower,
        made_for=another_borrower,
    )
    waiting_list.add_bid(bid)

    # Verify the bid was added correctly
    assert another_borrower.entity_id in waiting_list._bids_by_for_id
    assert bid in waiting_list._bids_by_for_id[another_borrower.entity_id]

    # Test canceling the borrower who made the bid
    waiting_list.cancel(borrower)

    # Verify the bid was removed
    # After cancellation, the entry should be removed from the dictionary
    assert another_borrower.entity_id not in waiting_list._bids_by_for_id
