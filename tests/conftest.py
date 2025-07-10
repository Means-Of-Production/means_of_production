import decimal
from datetime import timedelta

import pytest

from domain import (
    ID,
    Location,
    Money,
    MOPServer,
    Person,
    PersonName,
    PhysicalLocation,
    WaitingListType,
)
from domain.entities.libraries.simple_library import SimpleLibrary
from domain.value_items import URL, FeeSchedule
from domain.value_items.fee_schedules.per_day_fee_schedule import PerDayFeeSchedule


@pytest.fixture
def fee_schedule() -> FeeSchedule:
    return PerDayFeeSchedule(
        daily_charge=Money(amount=decimal.Decimal(10.0), currency_name="EUR")
    )


@pytest.fixture
def library_location() -> Location:
    return PhysicalLocation(
        street_address="Gran Via De Les Corts Catalanes 888",
        city="Barcelona",
        state="Barcelona",
        country="España",
        zip_code="08013",
    )


@pytest.fixture
def administrator() -> Person:
    return Person(
        person_id=ID.generate(),
        name=PersonName(
            first_name="Testy",
            last_name="Administrator",
        ),
        emails=["admin@testlibrary.com", "anotheremail@gmail.com"],
    )


@pytest.fixture
def simple_library(
    administrator: Person,
    library_location: PhysicalLocation,
    fee_schedule: FeeSchedule,
) -> SimpleLibrary:
    return SimpleLibrary(
        library_id=ID.generate(),
        name="Test Library",
        administrator=administrator,
        location=library_location,
        waiting_list_type=WaitingListType.NONE,
        max_fines_before_suspension=Money(
            amount=decimal.Decimal(100.0), currency_name="EUR"
        ),
        fee_schedule=fee_schedule,
        default_loan_time=timedelta(days=14),
        mop_server=MOPServer(
            id=ID.generate(), base_url=URL.parse("https://meansofp.org")
        ),
    )
