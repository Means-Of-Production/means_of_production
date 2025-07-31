from datetime import timedelta

import pytest
from freezegun import freeze_time

from domain.value_items import LoanStatus, ThingStatus


class TestSimpleLibraryEndToEnd:
    @pytest.mark.asyncio
    async def test_borrow_and_return(self, simple_library, person_one, item_one):
        loan = await simple_library.borrow(thing=item_one, borrower=person_one)

        assert loan
        assert loan.status == LoanStatus.BORROWED
        assert item_one.status == ThingStatus.BORROWED

        # return the item
        loan = await simple_library.start_return(loan)
        assert loan.status == LoanStatus.WAITING_ON_LENDER_ACCEPTANCE

        loan = await simple_library.finish_library_return(loan, person_one)
        assert loan.status == LoanStatus.RETURNED
        assert item_one.status == ThingStatus.READY

    @pytest.mark.asyncio
    async def test_borrow_and_return_overdue(
        self, simple_library, person_one, item_one
    ):
        assert not person_one.fees
        with freeze_time() as frozen_datetime:
            loan = await simple_library.borrow(thing=item_one, borrower=person_one)

            assert loan.due_date
            assert loan.status == LoanStatus.BORROWED
            assert item_one.status == ThingStatus.BORROWED

            # use freezegun to move the time forward past the due date
            past_due = loan.due_date.date + timedelta(days=1)
            frozen_datetime.move_to(past_due)

            assert loan.status == LoanStatus.OVERDUE
            assert item_one.status == ThingStatus.BORROWED

            loan = await simple_library.start_return(loan)
            assert loan.status == LoanStatus.WAITING_ON_LENDER_ACCEPTANCE

            loan = await simple_library.finish_library_return(loan, person_one)
            assert loan.status == LoanStatus.OVERDUE
            assert item_one.status == ThingStatus.READY

            # check we were assigned a fee
            assert len(person_one.fees) == 1
