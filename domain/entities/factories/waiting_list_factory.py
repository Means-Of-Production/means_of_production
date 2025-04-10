from typing import Optional
from datetime import datetime

from domain.entities.thing import Thing
from domain.entities.waiting_lists.first_come_first_serve_waiting_list import FirstComeFirstServeWaitingList
from domain.entities.waiting_lists.auctionable_waiting_list import AuctionableWaitingList
from domain.value_items.time_interval import TimeInterval
from domain.entities.factories.money_factory import MoneyFactory


class WaitingListFactory:
    def __init__(
        self,
        supports_auctions: bool = False,
        default_auction_time: Optional[TimeInterval] = None,
        money_factory: Optional[MoneyFactory] = None
    ):
        self.supports_auctions = supports_auctions
        self.default_auction_time = default_auction_time
        self.money_factory = money_factory

        if self.supports_auctions and (not self.default_auction_time or not self.money_factory):
            raise ValueError("Dependencies for auctionable waiting list were not provided!")

    def create_list(self, item: Thing):
        if self.supports_auctions:
            if not self.default_auction_time or not self.money_factory:
                raise ValueError("Dependencies for auctionable waiting list were not provided!")
            return AuctionableWaitingList(
                item=item,
                auction_end_time=self.default_auction_time.from_now(),
                money_factory=self.money_factory,
                created_at=datetime.now()
            )
        else:
            return FirstComeFirstServeWaitingList(item)
