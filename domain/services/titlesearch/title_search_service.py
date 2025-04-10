import unittest
from unittest.mock import AsyncMock, MagicMock, create_autospec
from typing import List
from domain.entities import Thing, Person
from domain.entities.libraries import Library
from domain.repositories import LibraryRepository
from domain.services import TitleSearchService
from domain.value_items import ThingTitle
from domain.value_items.title_search_request import TitleSearchRequest


class TitleSearchServiceTests(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.title1 = ThingTitle("hash1")
        self.title2 = ThingTitle("another")

        self.thing1 = create_autospec(Thing)
        self.thing1.title = self.title1

        self.thing2 = create_autospec(Thing)
        self.thing2.title = self.title2

        self.thing3 = create_autospec(Thing)
        self.thing3.title = self.title1

        self.library1 = create_autospec(Library)
        self.library1.id = "first"
        self.library1.get_available_things = MagicMock(return_value=[self.thing1, self.thing2])

        self.library2 = create_autospec(Library)
        self.library2.id = "second"
        self.library2.get_available_things = MagicMock(return_value=[self.thing3])

        self.library_repo = create_autospec(LibraryRepository)
        self.library_repo.get_libraries_person_can_use = AsyncMock(return_value=[self.library1, self.library2])

        self.title_search_service = TitleSearchService(self.library_repo)
        self.person = create_autospec(Person)

    async def test_removes_duplicate_titles(self):
        search_request = TitleSearchRequest()

        results = await self.title_search_service.find(self.person, search_request)
        results_list = list(results)

        self.assertIsNotNone(results_list)
        self.assertEqual(len(results_list), 2)

        res_title1_lib1 = results_list[0].get_for_library(self.library1)
        self.assertEqual(len(list(res_title1_lib1.things)), 1)

        res_title1_lib2 = results_list[0].get_for_library(self.library2)
        self.assertEqual(len(list(res_title1_lib2.things)), 1)

        res_title2_lib1 = results_list[1].get_for_library(self.library1)
        self.assertEqual(len(list(res_title2_lib1.things)), 1)

    async def test_iterates_all_library_results(self):
        search_request = TitleSearchRequest()

        results = await self.title_search_service.find(self.person, search_request)
        results_list = list(results)

        self.assertIsNotNone(results_list)
        self.assertEqual(len(results_list), 2)

        lib_results_title1 = list(results_list[0].library_results)
        self.assertEqual(len(lib_results_title1), 2)

        lib_results_title2 = list(results_list[1].library_results)
        self.assertEqual(len(lib_results_title2), 1)


if __name__ == "__main__":
    unittest.main()
