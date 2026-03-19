from pathlib import Path

from owm.weather import get_weather
from owm.models import Weather, City
from owm.exceptions import OWMError, CityNotFoundError
from owm.geocode import city_name_to_list
from owm.conversions import temperature, pressure, wind, visibility, icons

__all__ = [
    'get_weather',
    'Weather',
    'City',
    'OWMError',
    'CityNotFoundError',
    'city_name_to_list',
    'temperature',
    'pressure',
    'wind',
    'visibility',
    'icons',
]

try:
    from importlib.metadata import version, PackageNotFoundError
    __version__ = version('owm')
except PackageNotFoundError:
    try:
        __version__ = (Path(__file__).parent / 'VERSION').read_text().strip()
    except FileNotFoundError:
        FILE = Path(__file__).resolve().parent.parent / 'VERSION'
        if FILE.exists():
            with open(FILE, 'r') as f:
                __version__ = f.read().strip()
        else:
            __version__ = 'unknown'
