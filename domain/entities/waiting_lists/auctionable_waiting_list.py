from __future__ import annotations
from typing import List, Dict, Optional, Iterable
from datetime import datetime

# Clean package-level imports
from domain.entities import (
    Thing,
    WaitingList,
    FirstComeFirstServeWaitingList,
    Reservation,
    AuctionBid,
    Borrower,
    MoneyFactory
)
from domain.value_items import (
    Money,
    TimeInterval,
    EntityNotAssignedIdError
)


class AuctionableWaitingList(WaitingList):
    def __init__(
        self,
        item: Thing,
        ends: datetime,
        money_factory: MoneyFactory,
        started: datetime,
        is_active: bool = True,
        current_reservation: Optional[Reservation] = None,
        expired_reservations: Optional[List[Reservation]] = None
    ):
        super().__init__(item, current_reservation, expired_reservations or [])
        self.backup_list = FirstComeFirstServeWaitingList(item)
        self.bids_by_for_id: Dict[str, List[AuctionBid]] = {}
        self.money_factory = money_factory

        self.started = started
        self.ends = ends
        self.is_active = is_active

    def add(self, borrower: Borrower) -> "AuctionableWaitingList":
        self.backup_list.add(borrower)
        return self

    def add_bid(self, bid: AuctionBid) -> "AuctionableWaitingList":
        if not bid.made_for.id:
            raise EntityNotAssignedIdError("Bid must be assigned an ID.")
        
        if bid.made_for.id not in self.bids_by_for_id:
            self.bids_by_for_id[bid.made_for.id] = []
        
        self.bids_by_for_id[bid.made_for.id].append(bid)
        return self

    def get_bids(self) -> Iterable[AuctionBid]:
        """Returns all bids."""
        return [bid for bids in self.bids_by_for_id.values() for bid in bids]

    def get_winning_borrower(self) -> Borrower:
        """Determines the borrower with the highest total bid amount."""
        top_borrower_id: Optional[str] = None
        top_amount: Money = self.money_factory.get_empty_money()

        for borrower_id, bids in self.bids_by_for_id.items():
            total_bid = self.money_factory.get_empty_money()
            for bid in bids:
                total_bid.add(bid.amount_bid)

            if total_bid.greater_than(top_amount):
                top_amount = total_bid
                top_borrower_id = borrower_id

        if top_borrower_id:
            return next(
                bid.made_for for bid in self.get_bids() if bid.made_for.id == top_borrower_id
            )
        else:
            raise ValueError("No winning borrower found.")

    def is_on_list(self, borrower: Borrower) -> bool:
        return False  # Auctions don't work like a regular waiting list

    def find_next_borrower(self) -> Optional[Borrower]:
        """Finds the next borrower based on highest bid or falls back to backup list."""
        if not self.bids_by_for_id:
            return self.backup_list.find_next_borrower()
        
        return self.get_winning_borrower()

    def get_largest_amount(self) -> Money:
        """Gets the highest bid amount placed."""
        amount = self.money_factory.get_empty_money()
        winner = self.get_winning_borrower()

        if not winner.id:
            raise EntityNotAssignedIdError("Winning borrower must have an ID.")

        winner_bids = self.bids_by_for_id.get(winner.id, [])
        for bid in winner_bids:
            amount.add(bid.amount_bid)

        return amount

    def process_reservation_expired(self, reservation: Reservation) -> "AuctionableWaitingList":
        raise NotImplementedError("Method not implemented.")

    def get_reservation_time(self) -> TimeInterval:
        raise NotImplementedError("Method not implemented.")

    def cancel(self, borrower: Borrower) -> "AuctionableWaitingList":
        """Removes a borrower from the waiting list and deletes their bids."""
        if not borrower.id:
            raise EntityNotAssignedIdError("Borrower must have an ID.")

        self.backup_list.cancel(borrower)

        if borrower.id in self.bids_by_for_id:
            del self.bids_by_for_id[borrower.id]

        # Remove bids made by this borrower
        for bid_list in self.bids_by_for_id.values():
            bid_list[:] = [bid for bid in bid_list if bid.made_by.id != borrower.id]

        return self
