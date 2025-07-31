from typing import List

from pydantic import RootModel

from .thing import Thing


class ThingsGetResponse(RootModel[List[Thing]]):
    pass