from domain.entities.factories.money_factory import MoneyFactory
from domain.entities.loans.loan import Loan
from domain.value_items.money import Money
from domain.entities.factories.feeschedules.fee_schedule import FeeSchedule


class NoFeeSchedule(FeeSchedule):
    """A Fee Schedule that does not charge any fees."""

    def __init__(self, money_factory: MoneyFactory):
        self.money_factory = money_factory

    def fees_for_damaged_item(self, loan: Loan) -> Money:
        """Returns zero fee for damaged items."""
        return self.money_factory.get_empty_money()

    def fees_for_overdue_item(self, loan: Loan) -> Money:
        """Returns zero fee for overdue items."""
        return self.money_factory.get_empty_money()
