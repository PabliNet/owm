from requests import get, RequestException
from urllib.parse import urlencode

from owm.i18n import msg
from owm.exceptions import OWMError, CityNotFoundError
from owm.models import City

BASE_URL = "https://api.openweathermap.org/geo/1.0/direct"


def city_name_to_list(city: str, api_key: str, lang: str = "en") -> list[City]:
    params = {
        "q": city,
        "limit": 5,
        "appid": api_key,
        "lang": lang,
    }

    url = f"{BASE_URL}?{urlencode(params)}"

    try:
        response = get(url, timeout=10)
        response.raise_for_status()
    except RequestException as exc:
        raise OWMError(
            msg(lang, 'weather_connection_error').format(exc=exc)
        ) from exc

    data = response.json()

    if not data:
        raise CityNotFoundError(msg(lang, "city_not_found"))

    results: list[City] = []
    for d in data:
        results.append(
            City(
                name=d.get("local_names", {}).get(lang) or d.get("name"),
                state=d.get("state"),
                country=d.get("country"),
                lat=d.get("lat"),
                lon=d.get("lon"),
            )
        )

    return results
