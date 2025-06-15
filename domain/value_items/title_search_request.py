from typing import Optional

from pydantic import BaseModel


class TitleSearchRequest(BaseModel):
    model_config = {"frozen": True}
    search_text: Optional[str] = None

    def __eq__(self, other):
        if not isinstance(other, TitleSearchRequest):
            return False
        return self.search_text == other.search_text

    def __hash__(self):
        return hash(self.search_text)
