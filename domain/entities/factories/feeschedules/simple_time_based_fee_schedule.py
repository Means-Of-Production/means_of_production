from domain.entities.factories.money_factory import MoneyFactory
from domain.entities.loans.loan import Loan
from domain.value_items.money import Money
from domain.entities.factories.feeschedules.fee_schedule import FeeSchedule


class SimpleTimeBasedFeeSchedule(FeeSchedule):
    """
    Basic fee generator that charges late fees based on the item's cost,
    split up over a set amount of time (default is one year to full cost).
    """

    def __init__(
        self,
        money_factory: MoneyFactory,
        default_item_cost: Money = None,
        num_years: int = 1,
    ):
        self.num_years = num_years
        self.money_factory = money_factory
        self.default_item_cost = (
            default_item_cost if default_item_cost else money_factory.get_empty_money()
        )

    def _base_cost(self, loan: Loan) -> Money:
        """Returns the item's purchase cost if available; otherwise, uses the default cost."""
        return (
            loan.item.purchase_cost
            if loan.item.purchase_cost
            else self.default_item_cost
        )

    def fees_for_damaged_item(self, loan: Loan) -> Money:
        """Returns the full purchase cost of the item as the damage fee."""
        return self._base_cost(loan)

    def fees_for_overdue_item(self, loan: Loan) -> Money:
        """Calculates overdue fees based on the time overdue and total cost."""
        if loan.date_returned and loan.due_date:
            time_overdue = (
                loan.date_returned - loan.due_date
            ).total_seconds() * 1000  # Convert to milliseconds

            if time_overdue < 0:
                time_overdue = 0

            years = time_overdue / 31_536_000_000  # Convert milliseconds to years
            ratio = years / self.num_years

            return self._base_cost(loan).multiply(ratio)

        return self.money_factory.get_empty_money()
