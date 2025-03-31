import pytest
from unittest.mock import AsyncMock, MagicMock
from title_search_service import TitleSearchService
from domain.value_items.title_search_result import TitleSearchResult
from domain.value_items.thing_title import ThingTitle
from entities.libraries import Library
from entities import Thing
from entities.people import Person
from repositories.library_repository import LibraryRepository
from value_items.title_search_request import TitleSearchRequest


@pytest.mark.asyncio
async def test_removes_duplicate_titles():
    title1 = ThingTitle("hash1")
    title2 = ThingTitle("another")

    thing1 = MagicMock(spec=Thing)
    thing1.title = title1

    thing2 = MagicMock(spec=Thing)
    thing2.title = title2

    library = MagicMock(spec=Library)
    library.id = "first"
    library.get_available_things = AsyncMock(return_value=[thing1, thing2])

    thing3 = MagicMock(spec=Thing)
    thing3.title = title1

    second_library = MagicMock(spec=Library)
    second_library.id = "second"
    second_library.get_available_things = AsyncMock(return_value=[thing3])

    library_repo = MagicMock(spec=LibraryRepository)
    library_repo.get_libraries_person_can_use = AsyncMock(return_value=[library, second_library])

    under_test = TitleSearchService(library_repo)

    person = MagicMock(spec=Person)
    search_request = TitleSearchRequest()

    # Act
    res = await under_test.find(person, search_request)
    res = list(res)

    # Assertions
    assert res is not None
    assert len(res) == 2

    res_title1_lib1 = res[0].get_for_library(library)
    assert len(list(res_title1_lib1.things)) == 1

    res_title1_lib2 = res[0].get_for_library(second_library)
    assert len(list(res_title1_lib2.things)) == 1

    res_title2_lib1 = res[1].get_for_library(library)
    assert len(list(res_title2_lib1.things)) == 1


@pytest.mark.asyncio
async def test_iterates_all_library_results():
    title1 = ThingTitle("hash1")
    title2 = ThingTitle("another")

    thing1 = MagicMock(spec=Thing)
    thing1.title = title1

    thing2 = MagicMock(spec=Thing)
    thing2.title = title2

    library = MagicMock(spec=Library)
    library.id = "first"
    library.get_available_things = AsyncMock(return_value=[thing1, thing2])

    thing3 = MagicMock(spec=Thing)
    thing3.title = title1

    second_library = MagicMock(spec=Library)
    second_library.id = "second"
    second_library.get_available_things = AsyncMock(return_value=[thing3])

    library_repo = MagicMock(spec=LibraryRepository)
    library_repo.get_libraries_person_can_use = AsyncMock(return_value=[library, second_library])

    under_test = TitleSearchService(library_repo)

    person = MagicMock(spec=Person)
    search_request = TitleSearchRequest()

    # Act
    res = await under_test.find(person, search_request)
    res = list(res)

    # Assertions
    assert res is not None
    assert len(res) == 2

    library_results_title_one = list(res[0].library_results)
    assert len(library_results_title_one) == 2

    library_results_title_two = list(res[1].library_results)
    assert len(library_results_title_two) == 1
