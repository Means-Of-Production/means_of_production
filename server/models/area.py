from pydantic import BaseModel, Field

from .physical_location import PhysicalLocation


class Area(BaseModel):
    center: PhysicalLocation
    radius: float = Field(..., description="Radius of the area in kilometers")
