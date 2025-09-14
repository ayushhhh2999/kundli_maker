from typing import Any, Dict, Optional
from pydantic import BaseModel

class KundliResponse(BaseModel):
    status: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    errors: Optional[Any] = None

class KundliRequest(BaseModel):
    ayanamsa: int
    coordinates: str  # "lat,long"
    datetime: str 
    email:str