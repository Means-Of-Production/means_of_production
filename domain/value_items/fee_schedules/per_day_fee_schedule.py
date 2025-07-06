import decimal
from datetime import datetime

from domain import Money
from domain.value_items.fee_schedules.fee_schedule import FeeSchedule


class PerDayFeeSchedule(FeeSchedule):
    daily_charge: Money
    
    def fee_for_overdue_item(self, loan) -> Money:
        if not loan.due_date:
            return Money(amount=decimal.Decimal(0), currency_name=self.daily_charge.currency_name)
        num_days = (datetime.now().date() - loan.due_date).days
        return self.daily_charge * num_days