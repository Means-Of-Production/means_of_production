import decimal
from datetime import datetime

from domain import Money
from domain.value_items.fee_schedules.fee_schedule import FeeSchedule


class PerDayFeeSchedule(FeeSchedule):
    daily_charge: Money

    def fee_for_overdue_item(self, loan) -> Money:
        if not loan.due_date or not loan.due_date.date:
            return Money(amount=decimal.Decimal(0), currency=self.daily_charge.currency)
        num_days = (datetime.now().date() - loan.due_date.date).days
        return self.daily_charge * num_days
