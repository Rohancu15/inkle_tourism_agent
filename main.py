import requests
import difflib

# ============= Geocoding Agent (LocationIQ) =============

LOCATIONIQ_URL = "https://us1.locationiq.com/v1/search"

def geocode_place(place_name: str):
    """
    Child tool used by both agents.
    Returns (lat, lon, display_name) or (None, None, None) if place seems invalid.
    """
    API_KEY = "pk.1f4a34091a15db5f434b3c1afaa7064e"  

    params = {
        "key": API_KEY,
        "q": place_name,
        "format": "json",
        "limit": 1
    }

    try:
        response = requests.get(LOCATIONIQ_URL, params=params, timeout=10)
        data = response.json()
    except Exception:
        return None, None, None

    if not data or "error" in data:
        return None, None, None

    lat = float(data[0]["lat"])
    lon = float(data[0]["lon"])
    display_name = data[0]["display_name"]

    # Validate: avoid random far-off matches for nonsense input
    user_query = place_name.lower()
    detected_place = display_name.split(",")[0].lower()
    match_score = difflib.SequenceMatcher(None, user_query, detected_place).ratio()

    if match_score < 0.55:
        return None, None, None

    return lat, lon, display_name


# ============= Child Agent 1: Weather Agent =============

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

class WeatherAgent:
    def get_weather(self, place_name: str) -> str:
        lat, lon, resolved_name = geocode_place(place_name)
        if lat is None or lon is None:
            return "I don’t know this place exists."

        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": "true",
            "hourly": "precipitation_probability",
            "forecast_days": 1
        }

        try:
            response = requests.get(OPEN_METEO_URL, params=params, timeout=10)
            data = response.json()
        except Exception:
            return f"I couldn't fetch weather for {place_name} right now."

        current = data.get("current_weather", {})
        temp = current.get("temperature")

        hourly = data.get("hourly", {})
        rain_probs = hourly.get("precipitation_probability", [])
        chance_of_rain = max(rain_probs) if rain_probs else None

        if temp is None:
            return f"I couldn't fetch weather for {place_name} right now."

        if chance_of_rain is None:
            return f"In {place_name} it’s currently {temp}°C."

        # Exactly in assignment style
        return f"In {place_name} it’s currently {temp}°C with a chance of {chance_of_rain}% to rain."


# ============= Child Agent 2: Places Agent =============

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

class PlacesAgent:
    def get_places(self, place_name: str, max_places: int = 5) -> str:
        lat, lon, resolved_name = geocode_place(place_name)
        if lat is None or lon is None:
            return "I don’t know this place exists."

        query = f"""
        [out:json][timeout:25];
        (
            node["tourism"="attraction"](around:30000,{lat},{lon});
            node["tourism"="museum"](around:30000,{lat},{lon});
            node["leisure"="park"](around:30000,{lat},{lon});
            node["historic"="monument"](around:30000,{lat},{lon});
            node["historic"="temple"](around:30000,{lat},{lon});
            node["amenity"="place_of_worship"](around:30000,{lat},{lon});
        );
        out body;
        """

        try:
            response = requests.post(
                OVERPASS_URL,
                data={"data": query},
                headers={"User-Agent": "InkleTourismAgent/1.0"},
                timeout=30
            )
            data = response.json()
        except Exception:
            return f"I couldn't fetch tourist places for {place_name} right now."

        elements = data.get("elements", [])
        names: list[str] = []

        for el in elements:
            tags = el.get("tags", {})
            name = tags.get("name")
            if name and name not in names:
                names.append(name)
            if len(names) >= max_places:
                break

        if not names:
            return f"In {place_name} I couldn’t find popular tourist attractions from the API."

        # Assignment style: list of up to 5 places
        places_list = "\n".join(names)
        return f"In {place_name} these are the places you can go,\n{places_list}"


# ============= Parent Agent: TourismAgent (Orchestrator) =============

class TourismAgent:
    """
    Parent agent that orchestrates the child agents.
    It does NOT use its own knowledge; it delegates to the tools.
    """

    def __init__(self):
        self.weather_agent = WeatherAgent()
        self.places_agent = PlacesAgent()

    def plan_trip(self, place: str, want_weather: bool, want_places: bool) -> str:
        place = (place or "").strip()
        if not place:
            return "Please enter a place you want to visit."

        responses = []

        if want_weather:
            responses.append(self.weather_agent.get_weather(place))

        if want_places:
            responses.append(self.places_agent.get_places(place))

        # If user didn't specify, default to just places (trip planning)
        if not want_weather and not want_places:
            responses.append(self.places_agent.get_places(place))

        # Combine like examples (weather sentence + places block)
        return " And ".join(responses)
