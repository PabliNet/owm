# owm — OpenWeatherMap CLI

A command-line tool to retrieve current weather information from OpenWeatherMap, designed for use in terminals, panels, and status bars.

---

## Installation

### Install from GitHub

**Clone the repository**

```bash
git clone https://github.com/pablinet/owm.git
```

**Make the script executable**

```bash
chmod +x owm/owm
```

**Copy it to /usr/local/bin as root or with `sudo`**

```bash
cp owm/owm /urs/local/bin
```

### Install from APT (Debian/Ubuntu)

Run the following commands as root or with `sudo`:

**1. Add the APT repository:**

```bash
echo "deb https://pablinet.github.io/apt ./" > /etc/apt/sources.list.d/pablinet.list
```

**2. Add the APT key:**

With `curl`:
```bash
curl -fsSL https://pablinet.github.io/apt/pablinet.gpg -o /etc/apt/trusted.gpg.d/pablinet.gpg
```

Or with `wget`:
```bash
wget -O /etc/apt/trusted.gpg.d/pablinet.gpg https://pablinet.github.io/apt/pablinet.gpg
```

**3. Update and install:**

```bash
apt update && apt install owm
```

---

## Requirements

A valid [OpenWeatherMap API key](https://openweathermap.org/api) is required.

---

## Authentication

You can provide your API key in two ways:

**Via command-line argument:**
```bash
owm --city="Buenos Aires" --key=YOUR_API_KEY
```

**Via environment variable:**

```bash
export OWM_API_KEY="your_key"
```

---

## Usage

```
owm --city="CITY"
owm --geo=LAT,LON
owm --lat=LAT --lon=LON

owm [LOCATION] [WEATHER OPTIONS] [GENERAL OPTIONS]
```

---

## Location Options

One location option is required.

| Option | Description |
|--------|-------------|
| `--city="CITY"` | Specify city name |
| `--geo=LAT,LON` | Specify geographic coordinates |
| `--lat=LAT` | Latitude in decimal degrees |
| `--lon=LON` | Longitude in decimal degrees |

> Coordinates must be in decimal format. Use negative values for South and West hemispheres.

---

## Weather Data Options

Short options must be combined into a single argument (e.g. `-tld`, not `-t -l -d`).

| Option | Description |
|--------|-------------|
| `-n` | City name |
| `-i` | Weather icon |
| `-d` | Weather description |
| `-t` | Current temperature |
| `-l` | Feels like temperature |
| `-p` | Atmospheric pressure |
| `-v` | Visibility |
| `-w` | Wind speed |

---

## Special Modes

### `--temp-feelslike`

Alternates between temperature and feels-like every 5 seconds, only if the values differ.. This is a standalone mode and **cannot** be combined with other weather options (`-n -i -d -t -l -p -v -w`), `--help`, or `--version`.
### `--icon-temp-feelslike`

**Output format:**

| Language | Temperature | Feels Like |
|----------|-------------|------------|
| Spanish | `T24°C` | `S29°C` |
| English | `T24°C` | `L29°C` |

Displays the weather icon and alternates between temperature and feels-like every 5 seconds, only if the values differ. This is a standalone mode and **cannot** be combined with other weather options (`-n -i -d -t -l -p -v -w`), `--help`, or `--version`.

**Output format:**

| Language | Temperature | Feels Like |
|----------|-------------|------------|
| Spanish | `☀T24°C` | `☀S29°C` |
| English | `☀T24°C` | `☀L29°C` |

---

## General Options

 **`--units=UNIT`**
Unit system: `metric` (°C, m/s), `imperial` (°F, mph), `standard` (K, m/s). <br />Via environment variable: `export OWM_UNITS=60000` (10 minutes). 

**`--lang=LANG`**
Response language (e.g. `es`, `en`)

**`--time=SECONDS`**
Refresh interval in seconds. Minimum: 300 (5 minutes). Useful for panels or status bars.
Via environment variable: `export OWM_SECONDS=60000` (10 minutes).

**`--space=SEP` **
Output separator string. Default: single space.
Example: `--space=" \| "`.

**`--window=conky`**
Indicates execution inside Conky.  Can also be set via `export WINDOW_TERMINAL=$(ps -o comm= -p $PPID)`.

**`--help`** 
Display help and exit.

**`--version` **
Output version information and exit.


## Examples

**Basic usage with city name**
```bash
owm --city="Puerto Iguazú" --key=0123456789
```

**Coordinates with temperature and feels-like**
```bash
owm --geo=-25.6346782,-54.58287530604622 -tl --key=0123456789
```

**Latitude/longitude with metric units**
```bash
owm --lat=-25.6346782 --lon=-54.58287530604622 -t --units=metric
```

**Coordinates with no separator between values**
```bash
owm --geo=-25.6346782,-54.58287530604622 -tl --no-space --key=0123456789
```
