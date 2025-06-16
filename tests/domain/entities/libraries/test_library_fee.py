from domain.entities.libraries.library_fee import LibraryFee
from domain.value_items import ID, FeeStatus, Money


def test_library_fee_creation():
    # Create a library fee
    fee_id = ID.generate()
    library_id = ID.generate()
    charged_for_id = ID.generate()
    amount = Money(amount=10.50, currency_name="USD")

    fee = LibraryFee(
        library_fee_id=fee_id,
        library_id=library_id,
        amount=amount,
        status=FeeStatus.OUTSTANDING,
        charged_for_id=charged_for_id,
    )

    # Verify the fee was created correctly
    assert fee.library_fee_id == fee_id
    assert fee.library_id == library_id
    assert fee.amount == amount
    assert fee.status == FeeStatus.OUTSTANDING
    assert fee.charged_for_id == charged_for_id

    # Test entity_id property
    assert fee.entity_id == fee_id


def test_library_fee_status_change():
    # Create a library fee with OUTSTANDING status
    fee = LibraryFee(
        library_fee_id=ID.generate(),
        library_id=ID.generate(),
        amount=Money(amount=10.50, currency_name="USD"),
        status=FeeStatus.OUTSTANDING,
        charged_for_id=ID.generate(),
    )

    # Verify initial status
    assert fee.status == FeeStatus.OUTSTANDING

    # Change status to PAID
    fee.status = FeeStatus.PAID

    # Verify status was updated
    assert fee.status == FeeStatus.PAID
