from operator import itemgetter


class TestSimpleLibraryEndToEnd:
    def test_borrow_and_return(self, simple_library, person_one, item_one):
        loan = simple_library.borrow(thing=item_one, borrower=person_one)

        assert loan
