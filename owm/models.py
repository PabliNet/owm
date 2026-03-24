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
    grnd_level: Optional[int] = None
    sea_level: Optional[int] = None
    temp_max: Optional[float] = None
    temp_min: Optional[float] = None

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
            grnd_level=main_data.get("grnd_level"),
            sea_level=main_data.get("sea_level"),
            temp_max=main_data.get("temp_max"),
            temp_min=main_data.get("temp_min"),
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

    @property
    def timezone_str(self) -> str:
        '''Offset UTC formateado, ej: UTC -3, UTC +5:30, UTC 0.'''
        total_minutes = self.tz_offset // 60
        sign = '+' if total_minutes >= 0 else '-'
        total_minutes = abs(total_minutes)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        if sign == '+' and hours == 0 and minutes == 0:
            return 'UTC 0'
        if minutes == 0:
            return f'UTC {sign}{hours}'
        return f'UTC {sign}{hours}:{minutes:02d}'
