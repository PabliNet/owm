# owm — Python API

[English](#english) | [Español](#español)

---

## English

`owm` can be used as a Python library to query weather and geocoding data
programmatically.

### Installation

```bash
pip install owm
```

### get_weather()

```python
from owm.weather import get_weather
```

Fetches current weather for a given location. Returns a `Weather` object.
Results are cached locally to avoid unnecessary API calls.

```python
weather = get_weather(
    lat=-34.61,
    lon=-58.38,
    api_key="YOUR_KEY",
    lang="es",           # optional, default: "es"
    units="metric",      # optional: "metric" or "imperial", default: "metric"
    cache_seconds=300,   # optional, default: 300
    terminal=None,       # optional: "conky" prints "--" on connection error
)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `lat` | `float` | Latitude |
| `lon` | `float` | Longitude |
| `api_key` | `str` | OpenWeatherMap API key |
| `lang` | `str` | Language code (e.g. `"en"`, `"es"`) |
| `units` | `str` | `"metric"` or `"imperial"` |
| `cache_seconds` | `int` | Cache validity in seconds |
| `terminal` | `str \| None` | Terminal type (e.g. `"conky"`) |

**Returns:** `Weather`

**Raises:** `OWMError` on connection or API errors.

---

### city_name_to_list()

```python
from owm.geocode import city_name_to_list
```

Searches for cities by name using the OpenWeatherMap Geocoding API.
Returns up to 5 results.

```python
cities = city_name_to_list(
    city="Buenos Aires",
    api_key="YOUR_KEY",
    lang="es",  # optional, default: "es"
)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `city` | `str` | City name to search |
| `api_key` | `str` | OpenWeatherMap API key |
| `lang` | `str` | Language code for localized names |

**Returns:** `list[City]`

**Raises:** `CityNotFoundError` if no results are found.

---

### Weather

```python
from owm.models import Weather
```

Dataclass returned by `get_weather()`. All temperature values are in the
units requested. Times are returned both as UTC `datetime` and as
local `datetime` based on the city's timezone offset.

| Attribute | Type | Description |
|-----------|------|-------------|
| `city_name` | `str` | City name |
| `country` | `str` | Country code (e.g. `"AR"`) |
| `description` | `str` | Weather description (e.g. `"clear sky"`) |
| `temperature` | `float` | Temperature |
| `feels_like` | `float` | Feels like temperature |
| `humidity` | `int` | Relative humidity (%) |
| `pressure` | `int` | Atmospheric pressure (hPa) |
| `wind_speed` | `float` | Wind speed |
| `wind_deg` | `float \| None` | Wind direction in degrees |
| `wind_direction` | `str` | Wind direction as compass point (e.g. `"NE"`) |
| `visibility` | `int \| None` | Visibility in metres |
| `icon` | `str` | OWM icon code (e.g. `"01d"`) |
| `city_id` | `int \| None` | OWM city ID |
| `sunrise` | `datetime` | Sunrise time (UTC) |
| `sunset` | `datetime` | Sunset time (UTC) |
| `sunrise_local` | `datetime` | Sunrise time (local) |
| `sunset_local` | `datetime` | Sunset time (local) |
| `sunrise_str` | `str` | Sunrise time formatted as `HH:MM` |
| `sunset_str` | `str` | Sunset time formatted as `HH:MM` |
| `tz_offset` | `int` | Timezone offset in seconds from UTC |

---

### City

```python
from owm.models import City
```

Dataclass returned by `city_name_to_list()`.

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `str` | City name |
| `country` | `str` | Country code (e.g. `"AR"`) |
| `lat` | `float` | Latitude |
| `lon` | `float` | Longitude |
| `state` | `str \| None` | State or province (if available) |
| `city_id` | `int \| None` | OWM city ID (if available) |

---

### Exceptions

```python
from owm.exceptions import OWMError, CityNotFoundError
```

| Exception | Description |
|-----------|-------------|
| `OWMError` | Base exception for all owm errors |
| `CityNotFoundError` | Raised when no city matches the search query |

---

### Example

```python
from owm.weather import get_weather
from owm.geocode import city_name_to_list
from owm.exceptions import OWMError, CityNotFoundError

API_KEY = "YOUR_KEY"

# Geocoding
try:
    cities = city_name_to_list("Tokyo", api_key=API_KEY, lang="en")
    for city in cities:
        print(f"{city.name}, {city.country} ({city.lat}, {city.lon})")
except CityNotFoundError as e:
    print(e)

# Weather
try:
    weather = get_weather(lat=35.68, lon=139.69, api_key=API_KEY, lang="en")
    print(f"{weather.city_name}: {weather.temperature}°C, {weather.description}")
    print(f"Humidity: {weather.humidity}%")
    print(f"Sunrise: {weather.sunrise_str} / Sunset: {weather.sunset_str}")
except OWMError as e:
    print(e)
```

---

## Español

`owm` puede usarse como librería de Python para consultar datos de clima
y geolocalización de forma programática.

### Instalación

```bash
pip install owm
```

### get_weather()

```python
from owm.weather import get_weather
```

Obtiene el clima actual para una ubicación dada. Devuelve un objeto `Weather`.
Los resultados se cachean localmente para evitar llamadas innecesarias a la API.

```python
weather = get_weather(
    lat=-34.61,
    lon=-58.38,
    api_key="TU_KEY",
    lang="es",           # opcional, por defecto: "es"
    units="metric",      # opcional: "metric" o "imperial", por defecto: "metric"
    cache_seconds=300,   # opcional, por defecto: 300
    terminal=None,       # opcional: "conky" imprime "--" si no hay conexión
)
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `lat` | `float` | Latitud |
| `lon` | `float` | Longitud |
| `api_key` | `str` | API key de OpenWeatherMap |
| `lang` | `str` | Código de idioma (ej. `"en"`, `"es"`) |
| `units` | `str` | `"metric"` o `"imperial"` |
| `cache_seconds` | `int` | Segundos de validez del caché |
| `terminal` | `str \| None` | Tipo de terminal (ej. `"conky"`) |

**Devuelve:** `Weather`

**Lanza:** `OWMError` en caso de errores de conexión o de la API.

---

### city_name_to_list()

```python
from owm.geocode import city_name_to_list
```

Busca ciudades por nombre usando la API de Geocoding de OpenWeatherMap.
Devuelve hasta 5 resultados.

```python
cities = city_name_to_list(
    city="Buenos Aires",
    api_key="TU_KEY",
    lang="es",  # opcional, por defecto: "es"
)
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `city` | `str` | Nombre de la ciudad a buscar |
| `api_key` | `str` | API key de OpenWeatherMap |
| `lang` | `str` | Código de idioma para nombres localizados |

**Devuelve:** `list[City]`

**Lanza:** `CityNotFoundError` si no se encuentran resultados.

---

### Weather

```python
from owm.models import Weather
```

Dataclass devuelto por `get_weather()`. Los valores de temperatura están en
las unidades solicitadas. Las horas se devuelven tanto en UTC como en hora
local según el offset de zona horaria de la ciudad.

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `city_name` | `str` | Nombre de la ciudad |
| `country` | `str` | Código de país (ej. `"AR"`) |
| `description` | `str` | Descripción del clima (ej. `"cielo claro"`) |
| `temperature` | `float` | Temperatura |
| `feels_like` | `float` | Sensación térmica |
| `humidity` | `int` | Humedad relativa (%) |
| `pressure` | `int` | Presión atmosférica (hPa) |
| `wind_speed` | `float` | Velocidad del viento |
| `wind_deg` | `float \| None` | Dirección del viento en grados |
| `wind_direction` | `str` | Dirección del viento como punto cardinal (ej. `"NE"`) |
| `visibility` | `int \| None` | Visibilidad en metros |
| `icon` | `str` | Código de ícono de OWM (ej. `"01d"`) |
| `city_id` | `int \| None` | ID de la ciudad en OWM |
| `sunrise` | `datetime` | Hora de amanecer (UTC) |
| `sunset` | `datetime` | Hora de ocaso (UTC) |
| `sunrise_local` | `datetime` | Hora de amanecer (local) |
| `sunset_local` | `datetime` | Hora de ocaso (local) |
| `sunrise_str` | `str` | Amanecer formateado como `HH:MM` |
| `sunset_str` | `str` | Ocaso formateado como `HH:MM` |
| `tz_offset` | `int` | Offset de zona horaria en segundos desde UTC |

---

### City

```python
from owm.models import City
```

Dataclass devuelto por `city_name_to_list()`.

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `name` | `str` | Nombre de la ciudad |
| `country` | `str` | Código de país (ej. `"AR"`) |
| `lat` | `float` | Latitud |
| `lon` | `float` | Longitud |
| `state` | `str \| None` | Provincia o estado (si está disponible) |
| `city_id` | `int \| None` | ID de la ciudad en OWM (si está disponible) |

---

### Excepciones

```python
from owm.exceptions import OWMError, CityNotFoundError
```

| Excepción | Descripción |
|-----------|-------------|
| `OWMError` | Excepción base para todos los errores de owm |
| `CityNotFoundError` | Se lanza cuando ninguna ciudad coincide con la búsqueda |

---

### Ejemplo

```python
from owm.weather import get_weather
from owm.geocode import city_name_to_list
from owm.exceptions import OWMError, CityNotFoundError

API_KEY = "TU_KEY"

# Geolocalización
try:
    cities = city_name_to_list("Tokio", api_key=API_KEY, lang="es")
    for city in cities:
        print(f"{city.name}, {city.country} ({city.lat}, {city.lon})")
except CityNotFoundError as e:
    print(e)

# Clima
try:
    weather = get_weather(lat=35.68, lon=139.69, api_key=API_KEY, lang="es")
    print(f"{weather.city_name}: {weather.temperature}°C, {weather.description}")
    print(f"Humedad: {weather.humidity}%")
    print(f"Amanecer: {weather.sunrise_str} / Ocaso: {weather.sunset_str}")
except OWMError as e:
    print(e)
```
