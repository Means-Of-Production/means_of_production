from typing import List

from pydantic import RootModel

from .thing import Thing


class LibraryLibraryIdThingsGetResponse(RootModel[List[Thing]]):
    pass