# app/agents/time_agent.py
from datetime import datetime
from zoneinfo import ZoneInfo
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
import re

tf = TimezoneFinder()
geolocator = Nominatim(user_agent="time_agent")

async def run(query: str) -> str:
    q = query.lower()

    # Try to extract a location name from the query
    location = None
    if " in " in q:
        location = q.split(" in ", 1)[1].strip()

    # Clean up punctuation (remove trailing ? ! , . etc.)
    if location:
        location = re.sub(r"[^\w\s]", "", location).strip()

    tz_name = None
    if location:
        try:
            geo = geolocator.geocode(location)
            if geo:
                tz_name = tf.timezone_at(lng=geo.longitude, lat=geo.latitude)
        except Exception:
            pass

    if tz_name is None:
        tz_name = "Asia/Kolkata"  # default fallback

    try:
        now = datetime.now(ZoneInfo(tz_name))
        if location:
            return f"The current time in {location.title()} is {now.strftime('%H:%M:%S %Z')}."
        else:
            return f"The current time is {now.strftime('%H:%M:%S %Z')}."
    except Exception:
        return "Sorry, I couldn't determine the time right now."
