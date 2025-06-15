from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, Dict, Iterable

from domain.entities.borrower import Borrower
from domain.entities.thing import Thing
from domain.entities.waiting_lists.base_waiting_list import BaseWaitingList
from domain.entities.waiting_lists.first_come_first_serve_waiting_list import (
    FirstComeFirstServeWaitingList,
)
from domain.entities.waiting_lists.reservation import Reservation
from domain.value_items import ID, Money


class AuctionBid:
    amount_bid: Money
    made_by: Borrower
    made_for: Borrower

    def __init__(self, amount_bid: Money, made_by: Borrower, made_for: Borrower):
        self.amount_bid = amount_bid
        self.made_by = made_by
        self.made_for = made_for


class AuctionableWaitingList(BaseWaitingList):
    waiting_list_id: ID
    _item: Thing
    ends: datetime
    is_active: bool = True
    started: datetime

    _backup_list: FirstComeFirstServeWaitingList
    _bids_by_for_id: Dict[ID, list[AuctionBid]] = {}

    @property
    def entity_id(self) -> ID:
        return self.waiting_list_id

    def add(self, borrower: Borrower) -> AuctionableWaitingList:
        self._backup_list.add(borrower)
        return self

    def add_bid(self, bid: AuctionBid) -> AuctionableWaitingList:
        if not bid.made_for.entity_id:
            from domain.value_items.exceptions import EntityNotAssignedIdError

            raise EntityNotAssignedIdError("")

        if bid.made_for.entity_id not in self._bids_by_for_id:
            self._bids_by_for_id[bid.made_for.entity_id] = []

        self._bids_by_for_id[bid.made_for.entity_id].append(bid)

        return self

    def get_bids(self) -> Iterable[AuctionBid]:
        result = []
        for bids in self._bids_by_for_id.values():
            result.extend(bids)
        return result

    def get_winning_borrower(self) -> Borrower:
        top_amount = self.money_factory.get_empty_money()
        top_borrower_id = None

        for borrower_id, bids in self._bids_by_for_id.items():
            amount = self.money_factory.get_empty_money()
            for bid in bids:
                amount = amount.add(bid.amount_bid)

            if amount.greater_than(top_amount):
                top_amount = amount
                top_borrower_id = borrower_id

        for bid in self.get_bids():
            if bid.made_for.entity_id and bid.made_for.entity_id == top_borrower_id:
                return bid.made_for

        raise ValueError("No winning borrower found")

    def is_on_list(self, borrower: Borrower) -> bool:
        return False

    def find_next_borrower(self) -> Optional[Borrower]:
        if not self._bids_by_for_id:
            return self._backup_list.find_next_borrower()

        return self.get_winning_borrower()

    def get_largest_amount(self) -> Money:
        amount = self.money_factory.get_empty_money()
        winner = self.get_winning_borrower()

        if not winner.entity_id:
            from domain.value_items.exceptions import EntityNotAssignedIdError

            raise EntityNotAssignedIdError("")

        winner_bids = self._bids_by_for_id.get(winner.entity_id, [])
        for bid in winner_bids:
            amount = amount.add(bid.amount_bid)

        return amount

    def process_reservation_expired(
        self, reservation: Reservation
    ) -> "AuctionableWaitingList":
        raise NotImplementedError("Method not implemented")

    def get_reservation_time(self) -> timedelta:
        raise NotImplementedError("Method not implemented")

    def cancel(self, borrower: Borrower) -> "AuctionableWaitingList":
        if not borrower.entity_id:
            from domain.value_items.exceptions import EntityNotAssignedIdError

            raise EntityNotAssignedIdError("")

        self._backup_list.cancel(borrower)

        if borrower.entity_id in self._bids_by_for_id:
            del self._bids_by_for_id[borrower.entity_id]

        # Delete any bids for OR by this borrower
        for borrower_id, bids in list(self._bids_by_for_id.items()):
            updated_bids = []
            for bid in bids:
                if bid.made_by.entity_id != borrower.entity_id:
                    updated_bids.append(bid)

            if updated_bids:
                self._bids_by_for_id[borrower_id] = updated_bids
            else:
                del self._bids_by_for_id[borrower_id]

        return self
