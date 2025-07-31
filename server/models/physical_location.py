from typing import Optional

from pydantic import BaseModel, Field


class PhysicalLocation(BaseModel):
    latitude: Optional[float] = Field(None, description='Latitude coordinate')
    longitude: Optional[float] = Field(None, description='Longitude coordinate')
    street_address: str = Field(..., description='Street address')
    city: str = Field(..., description='City')
    state: str = Field(..., description='State or province')
    zip_code: str = Field(..., description='Postal or ZIP code')
    country: str = Field(..., description='Country')