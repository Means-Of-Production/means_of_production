from typing import List, Union

from pydantic import RootModel

from .distributed_library import DistributedLibrary
from .simple_library import SimpleLibrary


class LibraryGetResponse(RootModel[List[Union[SimpleLibrary, DistributedLibrary]]]):
    pass