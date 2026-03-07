from requests import get, RequestException

from owm.models import Weather
from owm.exceptions import OWMError
from owm.cache import build_cache_path, is_cache_valid, read_cache, write_cache

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(
    lat: float,
    lon: float,
    api_key: str,
    lang: str = "es",
    units: str = "metric",
    cache_seconds: int = 600,
) -> Weather:
    cache_path = build_cache_path(lat, lon, lang)

    if is_cache_valid(cache_path, cache_seconds):
        cached = read_cache(cache_path)
        if cached is not None:
            try:
                return Weather.from_api(cached)
            except ValueError:
                pass  # stale/corrupt cache — fall through to API

    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric",
        "lang": lang,
    }

    try:
        response = get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
    except RequestException as exc:
        raise OWMError(f"Error connecting to weather service: {exc}") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise OWMError("Invalid JSON response from weather API") from exc

    try:
        weather = Weather.from_api(data)
    except ValueError as exc:
        raise OWMError("Unexpected response format from weather API") from exc

    write_cache(cache_path, data)
    return weather
