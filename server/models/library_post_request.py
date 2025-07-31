from typing import Union

from pydantic import RootModel

from .distributed_library import DistributedLibrary
from .simple_library import SimpleLibrary


class LibraryPostRequest(RootModel[Union[SimpleLibrary, DistributedLibrary]]):
    pass
