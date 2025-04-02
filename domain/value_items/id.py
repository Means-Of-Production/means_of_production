from pydantic import BaseModel

class ID(BaseModel):
    value: str
    
    def __str__(self):
        return self.value