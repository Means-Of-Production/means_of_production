from typing import List

from pydantic import RootModel

from .thing import Thing


class ThingsSearchSearchTermGetResponse(RootModel[List[Thing]]):
    pass
