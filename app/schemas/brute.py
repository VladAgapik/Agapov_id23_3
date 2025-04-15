from pydantic import BaseModel

class BruteRequest(BaseModel):
    hash: str
    charset: str
    max_length: int
