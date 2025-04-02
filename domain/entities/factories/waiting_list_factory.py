from __future__ import annotations  # Enables forward references
from typing import TYPE_CHECKING
from datetime import datetime, timedelta
from typing import Optional
from domain.entities.thing import Thing
from domain.entities.waiting_lists.waiting_list import WaitingList
from domain.entities.waiting_lists.first_come_first_serve_waiting_list import FirstComeFirstServeWaitingList
from domain.value_items.time_interval import TimeInterval
from domain.entities.factories.money_factory import MoneyFactory

if TYPE_CHECKING:
    from domain.entities.waiting_lists.auctionable_waiting_list import AuctionableWaitingList

class IWaitingListFactory:
    """Interface for waiting list factories."""
    
    @property
    def supports_auctions(self) -> bool:
        raise NotImplementedError

    def create_list(self, item: Thing) -> WaitingList:
        """Creates a waiting list for a given item."""
        raise NotImplementedError


class WaitingListFactory(IWaitingListFactory):
    """Factory to create different types of waiting lists based on auction support."""

    def __init__(
        self,
        supports_auctions: bool = False,
        default_auction_time: Optional[TimeInterval] = None,
        money_factory: Optional[MoneyFactory] = None
    ):
        self._supports_auctions = supports_auctions
        self.default_auction_time = default_auction_time
        self.money_factory = money_factory

        if self._supports_auctions and (not self.default_auction_time or not self.money_factory):
            raise ValueError("Dependencies for auctionable waiting list were not provided!")

    @property
    def supports_auctions(self) -> bool:
        """Indicates whether auctions are supported."""
        return self._supports_auctions

    def create_list(self, item: Thing) -> WaitingList:
        """Creates a waiting list for the given item."""
        if self._supports_auctions:
            if not self.default_auction_time or not self.money_factory:
                raise ValueError("Dependencies for auctionable waiting list were not provided!")

            return AuctionableWaitingList(
                item, 
                self.default_auction_time.from_now(), 
                self.money_factory, 
                datetime.now()
            )
        else:
            return FirstComeFirstServeWaitingList(item)
