# owm

[English](#english) | [Español](#español)

[![GitHub](https://img.shields.io/badge/GitHub-PabliNet%2Fowm-blue?logo=github)](https://github.com/PabliNet/owm)

---

## English

A command-line client for [OpenWeatherMap](https://openweathermap.org/) that lets you query current weather and geocoding data directly from the terminal.

### Installation

#### APT (Debian/Ubuntu)

```bash
# 1. Add the APT repository
echo "deb https://pablinet.github.io/apt ./" > /etc/apt/sources.list.d/pablinet.list

# 2. Add the APT key
# With curl:
curl -fsSL https://pablinet.github.io/apt/pablinet.gpg -o /etc/apt/trusted.gpg.d/pablinet.gpg
# Or with wget:
wget -O /etc/apt/trusted.gpg.d/pablinet.gpg https://pablinet.github.io/apt/pablinet.gpg

# 3. Update and install
apt update && apt install python3-owm
```

#### pip

```bash
pip install owm
```

### Requirements

- Python 3.13+
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
owm --lat=-34.61 --lon=-58.38 --key=YOUR_KEY -t -d

# With imperial units
owm --geo=40.71,-74.01 --key=YOUR_KEY --units=imperial -t -w

# Using python3 -m
python3 -m owm --geo=-34.61,-58.38 --key=YOUR_KEY -t -u
```

**Geocoding mode** — search cities by name:

```bash
owm --city=Madrid --key=YOUR_KEY
owm --city="Buenos Aires" --key=YOUR_KEY

# Using python3 -m
python3 -m owm --city=Paris --key=YOUR_KEY
```

### All flags

#### Authentication

| Flag | Description |
|------|-------------|
| `--key KEY` | OpenWeatherMap API key (or `OWM_API_KEY` env var) |

#### Geolocation

| Flag | Description |
|------|-------------|
| `--city CITY` | Search city by name (geocoding mode) |
| `--geo LAT,LON` | Coordinates as `LAT,LON` (or `OWM_GEO` env var) |
| `--lat LAT` | Latitude (use with `--lon`, or `OWM_GEO` env var) |
| `--lon LON` | Longitude (use with `--lat`, or `OWM_GEO` env var) |

#### Configuration

| Flag | Description |
|------|-------------|
| `--clear-cache` | Clear the weather cache |
| `--lang LANG` | Language for weather description (or `LANG` env var, default: `en`) |
| `--terminal TERMINAL` | Terminal type, e.g. `conky` (or `WINDOW_TERMINAL` env var) |
| `--time SECONDS` | Cache validity in seconds (or `OWM_SECONDS` env var, default: 300) |
| `--units UNITS` | Unit system: `metric` (default) or `imperial` (or `OWM_UNITS` env var) |
| `-h, --help` | Show help and exit |
| `-v, --version` | Show version and exit |

#### Output (weather mode only)

| Flag | Short | Description |
|------|-------|-------------|
| `--visibility` | `-b` | Visibility |
| `--description` | `-d` | Weather description (lowercase) |
| `--desc-cap` | `-D` | Weather description (capitalized) |
| `--icon` | `-i` | Weather icon code |
| `--id` | | OWM city ID |
| `--feels-like` | `-l` | Feels like temperature |
| `--last-update` | | Last cache update time |
| `--name` | `-n` | City name |
| `--pressure` | `-p` | Atmospheric pressure |
| `--space SPACE` | | Separator between output fields (default: space) |
| `--sunrise` | `-r` | Sunrise time |
| `--sunset` | `-s` | Sunset time |
| `--temp` | `-t` | Temperature |
| `--toggle` | `-T` | Temperature or feels-like, alternating every 5 seconds |
| `--humidity` | `-u` | Relative humidity |
| `--wind` | `-w` | Wind speed and direction |

### Python API

See [API.md](API.md) for documentation on using `owm` as a Python library.

### Inline literals

Any argument that does not start with `-` is printed as-is in the position it appears. This allows custom formatting:

```bash
owm --geo=-34.61,-58.38 --key=YOUR_KEY -n " | " -t "°C " -u "%" --space=""
# Buenos Aires | 21°C 80%
```

### Environment variables

| Variable | Equivalent flag |
|----------|----------------|
| `OWM_API_KEY` | `--key` |
| `OWM_GEO` | `--geo` / `--lat` + `--lon` |
| `OWM_UNITS` | `--units` |
| `OWM_SECONDS` | `--time` |
| `LANG` | `--lang` |
| `WINDOW_TERMINAL` | `--terminal` |

Example:

```bash
export OWM_API_KEY=your_api_key
export OWM_GEO=-34.61,-58.38
export OWM_UNITS=metric

owm -t -d
owm -T -u --space=" | "
python3 -m owm -w -p --units=imperial
```

### Examples

```bash
# Temperature and description, pipe-separated
owm --geo=-34.61,-58.38 --key=YOUR_KEY -d " | " -t --space=""
# scattered clouds | 18°C

# Metric vs imperial
owm --geo=40.71,-74.01 --key=YOUR_KEY -t --units=metric
# 22°C
owm --geo=40.71,-74.01 --key=YOUR_KEY -t --units=imperial
# 71.6°F

# Full weather report
owm --lat=48.85 --lon=2.35 --key=YOUR_KEY -t -l -u -w -p
python3 -m owm --lat=48.85 --lon=2.35 --key=YOUR_KEY -t -l -u -w -p

# Geocoding
owm --city=Tokyo --key=YOUR_KEY
python3 -m owm --city="New York" --key=YOUR_KEY

# Sunrise and sunset
owm --geo=-34.61,-58.38 --key=YOUR_KEY --sunrise --sunset --space=" / "

# Conky integration (prints -- when no data available)
owm --geo=-34.61,-58.38 --key=YOUR_KEY --terminal=conky -T
```

### Changes in 0.5.0

Short flags `-b`, `-d`, `-D`, `-i`, `-l`, `-n`, `-p`, `-r`, `-s`, `-t`, `-T`, `-u` and `-w` have been added. `--toggle` replaces `--temp-feels-like`. The flags `-h` and `-v` have been replaced by `--help` and `--version` respectively starting from version 0.4.0.

---

## Español

Un cliente de línea de comandos para [OpenWeatherMap](https://openweathermap.org/) que permite consultar el clima actual y datos de geolocalización directamente desde la terminal.

### Instalación

#### APT (Debian/Ubuntu)

```bash
# 1. Agregar el repositorio APT
echo "deb https://pablinet.github.io/apt ./" > /etc/apt/sources.list.d/pablinet.list

# 2. Agregar la clave APT
# Con curl:
curl -fsSL https://pablinet.github.io/apt/pablinet.gpg -o /etc/apt/trusted.gpg.d/pablinet.gpg
# O con wget:
wget -O /etc/apt/trusted.gpg.d/pablinet.gpg https://pablinet.github.io/apt/pablinet.gpg

# 3. Actualizar e instalar
apt update && apt install python3-owm
```

#### pip

```bash
pip install owm
```

### Requisitos

- Python 3.13+
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
owm --lat=-34.61 --lon=-58.38 --key=TU_KEY -t -d

# Con unidades imperiales
owm --geo=40.71,-74.01 --key=TU_KEY --units=imperial -t -w

# Usando python3 -m
python3 -m owm --geo=-34.61,-58.38 --key=TU_KEY -t -u
```

**Modo geolocalización** — buscar ciudades por nombre:

```bash
owm --city=Madrid --key=TU_KEY
owm --city="Buenos Aires" --key=TU_KEY

# Usando python3 -m
python3 -m owm --city=Paris --key=TU_KEY
```

### Todos los flags

#### Autenticación

| Flag | Descripción |
|------|-------------|
| `--key KEY` | API key de OpenWeatherMap (o variable `OWM_API_KEY`) |

#### Geolocalización

| Flag | Descripción |
|------|-------------|
| `--city CITY` | Buscar ciudad por nombre (modo geolocalización) |
| `--geo LAT,LON` | Coordenadas en formato `LAT,LON` (o variable `OWM_GEO`) |
| `--lat LAT` | Latitud (usar junto con `--lon`, o variable `OWM_GEO`) |
| `--lon LON` | Longitud (usar junto con `--lat`, o variable `OWM_GEO`) |

#### Configuración

| Flag | Descripción |
|------|-------------|
| `--clear-cache` | Eliminar el caché del clima |
| `--lang LANG` | Idioma de la descripción del clima (o variable `LANG`, por defecto: `en`) |
| `--terminal TERMINAL` | Tipo de terminal, ej. `conky` (o variable `WINDOW_TERMINAL`) |
| `--time SECONDS` | Segundos de validez del caché (o variable `OWM_SECONDS`, por defecto: 300) |
| `--units UNITS` | Sistema de unidades: `metric` (por defecto) o `imperial` (o variable `OWM_UNITS`) |
| `-h, --help` | Mostrar ayuda y salir |
| `-v, --version` | Mostrar versión y salir |

#### Salidas (solo modo clima)

| Flag | Corto | Descripción |
|------|-------|-------------|
| `--visibility` | `-b` | Visibilidad |
| `--description` | `-d` | Descripción del clima en minúsculas |
| `--desc-cap` | `-D` | Descripción del clima con primera letra en mayúscula |
| `--icon` | `-i` | Código de ícono del clima |
| `--id` | | ID de la ciudad en OWM |
| `--feels-like` | `-l` | Sensación térmica |
| `--last-update` | | Hora de la última actualización del caché |
| `--name` | `-n` | Nombre de la ciudad |
| `--pressure` | `-p` | Presión atmosférica |
| `--space SPACE` | | Separador entre campos de salida (por defecto: espacio) |
| `--sunrise` | `-r` | Hora de salida del sol |
| `--sunset` | `-s` | Hora de puesta del sol |
| `--temp` | `-t` | Temperatura |
| `--toggle` | `-T` | Temperatura o sensación térmica, alternando cada 5 segundos |
| `--humidity` | `-u` | Humedad relativa |
| `--wind` | `-w` | Velocidad y dirección del viento |

### API de Python

Consultá [API.md](API.md) para documentación sobre el uso de `owm` como librería de Python.

### Literales intercalados

Cualquier argumento que no empiece con `-` se imprime tal cual en la posición en que aparece. Esto permite formatear la salida libremente:

```bash
owm --geo=-34.61,-58.38 --key=TU_KEY -n " | " -t "°C " -u "%" --space=""
# Buenos Aires | 21°C 80%
```

### Variables de entorno

| Variable | Flag equivalente |
|----------|-----------------|
| `OWM_API_KEY` | `--key` |
| `OWM_GEO` | `--geo` / `--lat` + `--lon` |
| `OWM_UNITS` | `--units` |
| `OWM_SECONDS` | `--time` |
| `LANG` | `--lang` |
| `WINDOW_TERMINAL` | `--terminal` |

Ejemplo:

```bash
export OWM_API_KEY=tu_api_key
export OWM_GEO=-34.61,-58.38
export OWM_UNITS=metric

owm -t -d
owm -T -u --space=" | "
python3 -m owm -w -p --units=imperial
```

### Ejemplos

```bash
# Temperatura y descripción separadas por pipe
owm --geo=-34.61,-58.38 --key=TU_KEY -d " | " -t --space=""
# nubes dispersas | 18°C

# Métrico vs imperial
owm --geo=40.71,-74.01 --key=TU_KEY -t --units=metric
# 22°C
owm --geo=40.71,-74.01 --key=TU_KEY -t --units=imperial
# 71.6°F

# Reporte completo
owm --lat=48.85 --lon=2.35 --key=TU_KEY -t -l -u -w -p
python3 -m owm --lat=48.85 --lon=2.35 --key=TU_KEY -t -l -u -w -p

# Geolocalización
owm --city=Tokio --key=TU_KEY
python3 -m owm --city="Nueva York" --key=TU_KEY

# Salida y puesta del sol
owm --geo=-34.61,-58.38 --key=TU_KEY --sunrise --sunset --space=" / "

# Integración con Conky (imprime -- cuando no hay datos disponibles)
owm --geo=-34.61,-58.38 --key=TU_KEY --terminal=conky -T
```

### Cambios en la versión 0.5.0

Se agregaron los flags cortos `-b`, `-d`, `-D`, `-i`, `-l`, `-n`, `-p`, `-r`, `-s`, `-t`, `-T`, `-u` y `-w`. `--toggle` reemplaza a `--temp-feels-like`. Los flags `-h` y `-v` fueron reemplazados por `--help` y `--version` respectivamente a partir de la versión 0.4.0.
