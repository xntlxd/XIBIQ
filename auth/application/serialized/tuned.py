from pydantic import BaseModel

class TunedModel(BaseModel):
    class Config:
        """Tells pydantic to convert even non dict obj to json"""
        orm_mode = True