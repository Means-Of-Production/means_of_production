import pytest

from domain.value_items import LoanStatus, ThingStatus


class TestSimpleLibraryEndToEnd:
    @pytest.mark.asyncio
    async def test_borrow_and_return(self, simple_library, person_one, item_one):
        loan = await simple_library.borrow(thing=item_one, borrower=person_one)

        assert loan
        assert loan.status == LoanStatus.BORROWED
        assert item_one.status == ThingStatus.BORROWED
