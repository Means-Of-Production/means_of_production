from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel


class Location(ABC, BaseModel):
    @abstractmethod
    def contains(self, other: Location) -> bool:
        raise NotImplementedError()
