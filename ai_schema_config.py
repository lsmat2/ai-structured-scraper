from typing import Optional, List
from pydantic import BaseModel

class DailyHours(BaseModel):
    day: str  # e.g. "Monday"
    open_hour: int  # 0–23
    open_minute: Optional[int] = None  # 0–59
    close_hour: int  # 0–23
    close_minute: Optional[int] = None  # 0–59

    class Config:
        extra = "forbid"

class PromotionData(BaseModel):
    title: str
    description: Optional[str] = None
    hours: Optional[List[DailyHours]] = None

    class Config:
        extra = "forbid"

class EventData(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: str  # ISO8601 or plain string
    end_date: str
    hours: Optional[List[DailyHours]] = None

    class Config:
        extra = "forbid"

class MenuItem(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: str

    class Config:
        extra = "forbid"

class PlaceDataExtraction(BaseModel):
    name: str
    street: str
    city: str
    state_code: str
    zip: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    hours: Optional[List[DailyHours]] = None
    amenity: Optional[str] = None
    cuisine: Optional[List[str]] = None
    price_level: Optional[str] = None
    rating: Optional[float] = None
    description: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    profile_image_url: Optional[str] = None
    image_urls: Optional[List[str]] = None
    primary_type: Optional[str] = None
    secondary_types: Optional[List[str]] = None

    promotion_data: Optional[List[PromotionData]] = None
    menu_data: Optional[List[MenuItem]] = None
    event_data: Optional[List[EventData]] = None

    class Config:
        extra = "forbid"
