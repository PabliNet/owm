from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timezone, timedelta

from owm.i18n import msg


@dataclass(slots=True)
class City:
    name: str
    country: str
    lat: float
    lon: float
    state: Optional[str] = None
    city_id: Optional[int] = None


@dataclass(slots=True)
class Weather:
    city_name: str
    country: str
    description: str
    feels_like: float
    humidity: int
    icon: str
    pressure: int
    sunrise: datetime
    sunset: datetime
    temperature: float
    tz_offset: int
    wind_deg: Optional[float]
    wind_speed: float
    visibility: Optional[int] = None
    city_id: Optional[int] = None

    @classmethod
    def from_api(cls, data: dict, lang: str = 'en') -> "Weather":
        try:
            sys_data = data["sys"]
            main_data = data["main"]
            weather_data = data["weather"][0]
            wind_data = data.get("wind", {})
        except (KeyError, IndexError) as exc:
            raise ValueError(
                msg(lang, 'weather_invalid_api_structure')
            ) from exc

        sunrise_utc = datetime.fromtimestamp(
            sys_data["sunrise"], tz=timezone.utc
        )
        sunset_utc = datetime.fromtimestamp(
            sys_data["sunset"], tz=timezone.utc
        )

        return cls(
            city_name=data["name"],
            country=sys_data["country"],
            description=weather_data["description"],
            icon=weather_data["icon"],
            temperature=main_data["temp"],
            feels_like=main_data["feels_like"],
            humidity=main_data["humidity"],
            pressure=main_data["pressure"],
            sunrise=sunrise_utc,
            sunset=sunset_utc,
            tz_offset=data.get("timezone", 0),
            wind_deg=wind_data.get("deg"),
            wind_speed=wind_data.get("speed", 0.0),
            visibility=data.get("visibility"),
            city_id=data.get("id"),
        )

    @property
    def local_timezone(self):
        return timezone(timedelta(seconds=self.tz_offset))

    @property
    def sunrise_local(self) -> datetime:
        return self.sunrise.astimezone(self.local_timezone)

    @property
    def sunset_local(self) -> datetime:
        return self.sunset.astimezone(self.local_timezone)

    @property
    def sunrise_str(self) -> str:
        return self.sunrise_local.strftime("%H:%M")

    @property
    def sunset_str(self) -> str:
        return self.sunset_local.strftime("%H:%M")

    def wind_direction(self, lang: str = 'en') -> str:
        if self.wind_deg is None:
            return "N/A"
        directions = msg(lang, 'wind_directions').split()
        index = round(self.wind_deg / 45) % 8
        return directions[index]
