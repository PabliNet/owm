from requests import get, RequestException

from owm.i18n import msg
from owm.models import Weather
from owm.exceptions import OWMError
from owm.cache import (
    build_alias_cache_path, build_cache_path,
    is_cache_valid, read_cache, write_cache
)

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(
    lat: float,
    lon: float,
    api_key: str,
    lang: str = "en",
    units: str = "metric",
    cache_seconds: int = 600,
    terminal: str | None = None,
    alias: str | None = None,
) -> Weather:
    if alias:
        cache_path = build_alias_cache_path(alias, lang)
    else:
        cache_path = build_cache_path(lat, lon, lang)

    if is_cache_valid(cache_path, cache_seconds):
        cached = read_cache(cache_path)
        if cached is not None:
            try:
                return Weather.from_api(cached, lang)
            except ValueError:
                pass  # caché obsoleto — caer a la API

    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": units,
        "lang": lang[:2],
    }

    try:
        response = get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
    except RequestException as exc:
        # Sin conexión: intentar usar el caché aunque haya expirado
        cached = read_cache(cache_path)
        if cached is not None:
            try:
                return Weather.from_api(cached, lang)
            except ValueError:
                pass
        if terminal and terminal.lower() == 'conky':
            print('--')
            raise SystemExit(0)
        raise OWMError(
            msg(lang, 'weather_connection_error').format(exc=exc)
        ) from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise OWMError(
            msg(lang, 'weather_invalid_json')
        ) from exc

    try:
        weather = Weather.from_api(data, lang)
    except ValueError as exc:
        raise OWMError(
            msg(lang, 'weather_unexpected_format')
        ) from exc

    write_cache(cache_path, data)
    return weather
