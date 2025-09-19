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

SCHEMA_DESCRIPTION = """You are an expert at structured data extraction. You will be given unstructured
text from a business's website and should convert it into the provided schema.

Focus on identifying business hours, contact information, descriptions, events,
promotions, menu items, amenities, cuisines, and secondary types.

#### Hours
Represent hours using integers for time fields:
daily_hours = {
    day: "Monday" | "Tuesday" | "Wednesday" | "Thursday" |
         "Friday" | "Saturday" | "Sunday";
    open_hour: number; // 0-23
    open_minute?: number; // 0-59
    close_hour: number; // 0-23
    close_minute?: number; // 0-59
}

If a business is open 24 hours, set both open_hour and close_hour to 0.

#### Promotions
promotion_data = [
{
    title: string;
    description?: string;
    hours?: daily_hours[];
}, ...
]

#### Events
event_data = [
{
    title: string;
    description?: string;
    start_date: string;
    end_date: string;
    hours?: daily_hours[];
}, ...
]

#### Menu Items
menu_data = [
{
    name: string;
    description?: string;
    price: number;
    category: string;
}, ...
]

#### Notes
- Each promotion, event, and menu item should be a distinct entry.
- If an item has multiple time slots, represent each slot as a separate entry.
- Events are one-time or date-bound, while promotions are recurring or ongoing.
- If an item spans an entire day and no specific times are given, use open_hour = 0 and close_hour = 0.
- Do not invent fields not defined in the schema. Only use the properties described above.
- If certain information is not available, omit that field. If hours information is not specified, assume it spans the entire day.
- Ensure the final output is valid JSON and adheres to the schema."""