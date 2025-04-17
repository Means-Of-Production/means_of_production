from __future__ import annotations
from typing import TYPE_CHECKING

# Import non-circular dependencies at runtime
from .entity import Entity
from domain.value_items import ThingTitle

# Use TYPE_CHECKING for potentially circular imports
if TYPE_CHECKING:
    from .libraries.distributed_library import DistributedLibrary
    from .lenders.individual_distributed_lender import IndividualDistributedLender
    from .waiting_lists.first_come_first_serve_waiting_list import (
        FirstComeFirstServeWaitingList,
    )
    from .waiting_lists.reservation import Reservation
    from .waiting_lists.auction_bid import AuctionBid
    from .libraries.simple_library import SimpleLibrary
    from .loans import Loan
    from .waiting_lists import WaitingList
    from .factories.feeschedules.fee_schedule import FeeSchedule
    from .libraries.base_library import BaseLibrary
    from .lenders.lender import Lender
    from .thing import Thing
    from .people import Person, Borrower
    from .libraries.library_fee import LibraryFee
    from .factories import (
        WaitingListFactory,
        MoneyFactory,
        NoFeeSchedule,
        AuctionableWaitingList,
        SimpleTimeBasedFeeSchedule,
    )


# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == "DistributedLibrary":
        from .libraries.distributed_library import DistributedLibrary

        return DistributedLibrary
    elif name == "IndividualDistributedLender":
        from .lenders.individual_distributed_lender import IndividualDistributedLender

        return IndividualDistributedLender
    elif name == "FirstComeFirstServeWaitingList":
        from .waiting_lists.first_come_first_serve_waiting_list import (
            FirstComeFirstServeWaitingList,
        )

        return FirstComeFirstServeWaitingList
    elif name == "Reservation":
        from .waiting_lists.reservation import Reservation

        return Reservation
    elif name == "AuctionBid":
        from .waiting_lists.auction_bid import AuctionBid

        return AuctionBid
    elif name == "SimpleLibrary":
        from .libraries.simple_library import SimpleLibrary

        return SimpleLibrary
    elif name == "Loan":
        from .loans import Loan

        return Loan
    elif name == "WaitingList":
        from .waiting_lists import WaitingList

        return WaitingList
    elif name == "FeeSchedule":
        from .factories.feeschedules.fee_schedule import FeeSchedule

        return FeeSchedule
    elif name == "BaseLibrary":
        from .libraries.base_library import BaseLibrary

        return BaseLibrary
    elif name == "Lender":
        from .lenders.lender import Lender

        return Lender
    elif name == "Thing":
        from .thing import Thing

        return Thing
    elif name == "Person":
        from .people import Person

        return Person
    elif name == "Borrower":
        from .people import Borrower

        return Borrower
    elif name == "LibraryFee":
        from .libraries.library_fee import LibraryFee

        return LibraryFee
    elif name == "WaitingListFactory":
        from .factories import WaitingListFactory

        return WaitingListFactory
    elif name == "MoneyFactory":
        from .factories import MoneyFactory

        return MoneyFactory
    elif name == "NoFeeSchedule":
        from .factories import NoFeeSchedule

        return NoFeeSchedule
    elif name == "AuctionableWaitingList":
        from .factories import AuctionableWaitingList

        return AuctionableWaitingList
    elif name == "SimpleTimeBasedFeeSchedule":
        from .factories import SimpleTimeBasedFeeSchedule

        return SimpleTimeBasedFeeSchedule
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "Thing",
    "Borrower",
    "Person",
    "Lender",
    "LibraryFee",
    "Loan",
    "AuctionableWaitingList",
    "FirstComeFirstServeWaitingList",
    "Reservation",
    "AuctionBid",
    "WaitingList",
    "FeeSchedule",
    "WaitingListFactory",
    "MoneyFactory",
    "NoFeeSchedule",
    "DistributedLibrary",
    "IndividualDistributedLender",
    "SimpleTimeBasedFeeSchedule",
    "SimpleLibrary",
    "Entity",
    "ThingTitle",
    "BaseLibrary",
]
