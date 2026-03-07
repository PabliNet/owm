# owm

[English](#english) | [Español](#español)

[![GitHub](https://img.shields.io/badge/GitHub-PabliNet%2Fowm-blue?logo=github)](https://github.com/PabliNet/owm)

---

## English

A command-line client for [OpenWeatherMap](https://openweathermap.org/) that lets you query current weather and geocoding data directly from the terminal.

### Installation

### APT (Debian/Ubuntu)

```bash
# 1. Add the APT repository
echo "deb https://pablinet.github.io/apt ./" > /etc/apt/sources.list.d/pablinet.list

# 2. Add the APT key
# With curl:
curl -fsSL https://pablinet.github.io/apt/pablinet.gpg -o /etc/apt/trusted.gpg.d/pablinet.gpg
# Or with wget:
wget -O /etc/apt/trusted.gpg.d/pablinet.gpg https://pablinet.github.io/apt/pablinet.gpg

# 3. Update and install
apt update && apt install owm
```

### pip

```bash
pip install owm
```

### Requirements

- Python 3.10+
- An [OpenWeatherMap API key](https://home.openweathermap.org/api_keys) (free tier works)

### Usage

```bash
owm [options]
# or
python3 -m owm [options]
```

### Modes

**Weather mode** — requires `--geo` or `--lat`/`--lon`, plus at least one output flag:

```bash
owm --geo=-34.61,-58.38 --key=YOUR_KEY -t
owm --lat=-34.61 --lon=-58.38 --key=YOUR_KEY -t --description

# With imperial units
owm --geo=40.71,-74.01 --key=YOUR_KEY --units=imperial -t --wind

# Using python3 -m
python3 -m owm --geo=-34.61,-58.38 --key=YOUR_KEY -t --humidity
```

**Geocoding mode** — search cities by name:

```bash
owm --city=Madrid --key=YOUR_KEY
owm --city="Buenos Aires" --key=YOUR_KEY

# Using python3 -m
python3 -m owm --city=Paris --key=YOUR_KEY
```

### All flags

#### Configuration

| Flag | Description |
|------|-------------|
| `--key KEY` | OpenWeatherMap API key (or `OWM_API_KEY` env var) |
| `--city CITY` | Search city by name (geocoding mode) |
| `--geo LAT,LON` | Coordinates as `LAT,LON` (or `OWM_GEO` env var) |
| `--lat LAT` | Latitude (use with `--lon`, or `OWM_GEO` env var) |
| `--lon LON` | Longitude (use with `--lat`, or `OWM_GEO` env var) |
| `--units UNITS` | Unit system: `metric` (default) or `imperial` (or `OWM_UNITS` env var) |
| `--lang LANG` | Language for weather description (or `LANG` env var, default: `en`) |
| `--time SECONDS` | Cache validity in seconds (or `OWM_SECONDS` env var, default: 300) |
| `--space SPACE` | Separator between output fields (default: space) |
| `-h, --help` | Show help and exit |
| `-v, --version` | Show version and exit |

#### Output (weather mode only)

| Flag | Description |
|------|-------------|
| `--temp` | Temperature |
| `--feels-like` | Feels like temperature |
| `--temp-feels-like` | Temperature or feels-like, alternating every 5 seconds |
| `--description` | Weather description |
| `--humidity` | Relative humidity |
| `--pressure` | Atmospheric pressure |
| `--wind` | Wind speed and direction |
| `--icon` | Weather icon code |
| `--visibility` | Visibility |
| `--sunrise` | Sunrise time |
| `--sunset` | Sunset time |
| `--name` | City name |
| `--id` | OWM city ID |

### Environment variables

| Variable | Equivalent flag |
|----------|----------------|
| `OWM_API_KEY` | `--key` |
| `OWM_GEO` | `--geo` / `--lat` + `--lon` |
| `OWM_UNITS` | `--units` |
| `OWM_SECONDS` | `--time` |
| `LANG` | `--lang` |

Example:

```bash
export OWM_API_KEY=your_api_key
export OWM_GEO=-34.61,-58.38
export OWM_UNITS=metric

owm --temp --description
owm --temp-feels-like --humidity --space=" | "
python3 -m owm --wind --pressure --units=imperial
```

### Examples

```bash
# Temperature and description, pipe-separated
owm --geo=-34.61,-58.38 --key=YOUR_KEY --description --temp --space=" | "
# 18°C | scattered clouds

# Metric vs imperial
owm --geo=40.71,-74.01 --key=YOUR_KEY --temp --units=metric
# 22°C
owm --geo=40.71,-74.01 --key=YOUR_KEY --temp --units=imperial
# 71.6°F

# Full weather report
owm --lat=48.85 --lon=2.35 --key=YOUR_KEY --temp --feels-like --humidity --wind --pressure
python3 -m owm --lat=48.85 --lon=2.35 --key=YOUR_KEY --temp --feels-like --humidity --wind --pressure

# Geocoding
owm --city=Tokyo --key=YOUR_KEY
python3 -m owm --city="New York" --key=YOUR_KEY

# Sunrise and sunset
owm --geo=-34.61,-58.38 --key=YOUR_KEY --sunrise --sunset --space=" / "
```

### Changes in 0.4.0

The flags `-d`, `-i`, `-l`, `-n`, `-p`, `-t` and `-w` have been removed. The flags `-h` and `-v` have been replaced by `--help` and `--version` respectively starting from version 0.4.0.

---

## Español

Un cliente de línea de comandos para [OpenWeatherMap](https://openweathermap.org/) que permite consultar el clima actual y datos de geolocalización directamente desde la terminal.

### Instalación

### APT (Debian/Ubuntu)

```bash
# 1. Agregar el repositorio APT
echo "deb https://pablinet.github.io/apt ./" > /etc/apt/sources.list.d/pablinet.list

# 2. Agregar la clave APT
# Con curl:
curl -fsSL https://pablinet.github.io/apt/pablinet.gpg -o /etc/apt/trusted.gpg.d/pablinet.gpg
# O con wget:
wget -O /etc/apt/trusted.gpg.d/pablinet.gpg https://pablinet.github.io/apt/pablinet.gpg

# 3. Actualizar e instalar
apt update && apt install owm
```

### pip

```bash
pip install owm
```

### Requisitos

- Python 3.10+
- Una [API key de OpenWeatherMap](https://home.openweathermap.org/api_keys) (el plan gratuito funciona)

### Uso

```bash
owm [opciones]
# o
python3 -m owm [opciones]
```

### Modos

**Modo clima** — requiere `--geo` o `--lat`/`--lon`, más al menos un flag de salida:

```bash
owm --geo=-34.61,-58.38 --key=TU_KEY -t
owm --lat=-34.61 --lon=-58.38 --key=TU_KEY -t --description

# Con unidades imperiales
owm --geo=40.71,-74.01 --key=TU_KEY --units=imperial -t --wind

# Usando python3 -m
python3 -m owm --geo=-34.61,-58.38 --key=TU_KEY -t --humidity
```

**Modo geolocalización** — buscar ciudades por nombre:

```bash
owm --city=Madrid --key=TU_KEY
owm --city="Buenos Aires" --key=TU_KEY

# Usando python3 -m
python3 -m owm --city=Paris --key=TU_KEY
```

### Todos los flags

#### Configuración

| Flag | Descripción |
|------|-------------|
| `--key KEY` | API key de OpenWeatherMap (o variable `OWM_API_KEY`) |
| `--city CITY` | Buscar ciudad por nombre (modo geolocalización) |
| `--geo LAT,LON` | Coordenadas en formato `LAT,LON` (o variable `OWM_GEO`) |
| `--lat LAT` | Latitud (usar junto con `--lon`, o variable `OWM_GEO`) |
| `--lon LON` | Longitud (usar junto con `--lat`, o variable `OWM_GEO`) |
| `--units UNITS` | Sistema de unidades: `metric` (por defecto) o `imperial` (o variable `OWM_UNITS`) |
| `--lang LANG` | Idioma de la descripción del clima (o variable `LANG`, por defecto: `en`) |
| `--time SECONDS` | Segundos de validez del caché (o variable `OWM_SECONDS`, por defecto: 300) |
| `--space SPACE` | Separador entre campos de salida (por defecto: espacio) |
| `-h, --help` | Mostrar ayuda y salir |
| `-v, --version` | Mostrar versión y salir |

#### Salidas (solo modo clima)

| Flag | Descripción |
|------|-------------|
| `--temp` | Temperatura |
| `--feels-like` | Sensación térmica |
| `--temp-feels-like` | Temperatura o sensación térmica, alternando cada 5 segundos |
| `--description` | Descripción del clima |
| `--humidity` | Humedad relativa |
| `--pressure` | Presión atmosférica |
| `--wind` | Velocidad y dirección del viento |
| `--icon` | Código de ícono del clima |
| `--visibility` | Visibilidad |
| `--sunrise` | Hora de salida del sol |
| `--sunset` | Hora de puesta del sol |
| `--name` | Nombre de la ciudad |
| `--id` | ID de la ciudad en OWM |

### Variables de entorno

| Variable | Flag equivalente |
|----------|-----------------|
| `OWM_API_KEY` | `--key` |
| `OWM_GEO` | `--geo` / `--lat` + `--lon` |
| `OWM_UNITS` | `--units` |
| `OWM_SECONDS` | `--time` |
| `LANG` | `--lang` |

Ejemplo:

```bash
export OWM_API_KEY=tu_api_key
export OWM_GEO=-34.61,-58.38
export OWM_UNITS=metric

owm --temp --description
owm --temp-feels-like --humidity --space=" | "
python3 -m owm --wind --pressure --units=imperial
```

### Ejemplos

```bash
# Temperatura y descripción separadas por pipe
owm --geo=-34.61,-58.38 --key=TU_KEY --description --temp --space=" | "
# 18°C | nubes dispersas

# Métrico vs imperial
owm --geo=40.71,-74.01 --key=TU_KEY --temp --units=metric
# 22°C
owm --geo=40.71,-74.01 --key=TU_KEY --temp --units=imperial
# 71.6°F

# Reporte completo
owm --lat=48.85 --lon=2.35 --key=TU_KEY --temp --feels-like --humidity --wind --pressure
python3 -m owm --lat=48.85 --lon=2.35 --key=TU_KEY --temp --feels-like --humidity --wind --pressure

# Geolocalización
owm --city=Tokio --key=TU_KEY
python3 -m owm --city="Nueva York" --key=TU_KEY

# Salida y puesta del sol
owm --geo=-34.61,-58.38 --key=TU_KEY --sunrise --sunset --space=" / "
```

### Cambios en la versión 0.4.0

Los flags `-d`, `-i` `-l`, `-n`, `-p`, `-t` y `-w` fueron eliminados. Los flags `-h` y `-v` fueron reemplazados por `--help` y `--version` respectivamente a partir de la versión 0.4.0.
