import pytest

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
        loan = await simple_library.borrow(thing=item_one, borrower=person_one)

        assert loan.due_date
        # todo use freezegun to move the time forward past the due date
