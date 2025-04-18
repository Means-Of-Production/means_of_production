from datetime import datetime
from typing import Iterable, Optional

from domain.entities import (
    Thing,
    Loan,
    Lender,
    BaseLibrary,
    MoneyFactory,
    FeeSchedule,
    WaitingListFactory,
    Borrower,
    Person,
)

from domain.value_items import (
    ThingStatus,
    Money,
    DueDate,
    LoanStatus,
    PhysicalArea,
    MOPServer,
    TimeInterval,
    BorrowerNotInGoodStandingError,
    InvalidThingStatusToBorrowError, ID,
)


class DistributedLibrary(BaseLibrary):
    def __init__(
        self,
        library_id: ID,
        name: str,
        administrator: Person,
        max_fees: Money,
        waiting_list_factory: WaitingListFactory,
        loans: Iterable[Loan],
        money_factory: MoneyFactory,
        location: PhysicalArea,
        mop_server: MOPServer,
        fee_schedule: Optional[FeeSchedule] = None,
        default_loan_time: Optional[TimeInterval] = None,
    ):
        super().__init__(
            library_id,
            name,
            administrator,
            max_fees,
            loans,
            money_factory,
            mop_server,
            default_loan_time,
            fee_schedule,
            waiting_list_factory,
        )
        self._lenders: list[Lender] = []
        self.location = location

    def get_all_things(self) -> Iterable[Thing]:
        """Returns all items from all lenders."""
        return (item for lender in self._lenders for item in lender.items)

    def _get_owner_of_item(self, item: Thing) -> Lender:
        """Finds the lender who owns the given item."""
        for lender in self._lenders:
            if any(lender_item.id == item.id for lender_item in lender.items):
                return lender
        raise ValueError(f"Cannot find an owner for {item.title.name}")

    async def borrow(
        self, item: Thing, borrower: Borrower, until: Optional[DueDate] = None
    ) -> Loan:
        """Allows a borrower to borrow an item if they meet eligibility criteria."""
        if item.status != ThingStatus.READY:
            raise InvalidThingStatusToBorrowError(item.status)
        if not self.can_borrow(borrower):
            raise BorrowerNotInGoodStandingError()

        lender = self._get_owner_of_item(item)
        until = until or DueDate(date=self.default_loan_time.from_now())
        item.status = ThingStatus.BORROWED

        return Loan(
            None,
            item,
            borrower,
            until,
            LoanStatus.BORROWED,
            lender.preferred_return_location(item),
            None,
        )

    async def finish_return(self, loan: Loan) -> Loan:
        """Finalizes the return process for a loan."""
        owner = self._get_owner_of_item(loan.item)
        return await super().finish_return(await owner.finish_return(loan))

    async def start_return(self, loan: Loan) -> Loan:
        """Initiates the return process for a borrower."""
        owner = self._get_owner_of_item(loan.item)
        updated = owner.start_return(loan)
        loan.date_returned = datetime.now()
        loan.status = LoanStatus.WAITING_ON_LENDER_ACCEPTANCE
        return updated

    def add_lender(self, lender: Lender) -> None:
        """Adds a new lender to the library."""
        self._lenders.append(lender)
