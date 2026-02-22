#!/usr/bin/env python3
from time import time
from os import getenv, makedirs
from os.path import exists, getmtime
from pathlib import Path
from locale import getlocale
from sys import argv, exit
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from json import dump, load
from re import fullmatch, match

has_arg = lambda x: len([_ for _ in argv[1:] if _.startswith(x)]) == 1

LANG = (
    (getlocale()[0] or 'en').split('_')[0] if not has_arg('--lang=') else
    get_arg('--lang=')
)

WINDOW = (
    get_arg('--window=') if has_arg('--window=') else
    getenv('WINDOW_TERMINAL', '')
)

SECONDS_ENV = (
    get_arg('--time=') if has_arg('--time=') else
    int(getenv('OWM_SECONDS', 300))
)

SECONDS = 300 if SECONDS_ENV < 300 else SECONDS_ENV

UNITS = (
    get_arg('--units=') if has_arg('--units=') else
    getenv('OWM_UNITS', 'metric')
)

def city_name_to_list(city):
    params = {
        'q': city,
        'limit': 5,
        'appid': API_KEY,
    }

    BASE_URL = 'https://api.openweathermap.org/geo/1.0/direct?'

    return BASE_URL + urlencode(params)

def info_in_dict(url):
    try:
        with urlopen(url, timeout=10) as response:
            data = load(response)
            return data

    except HTTPError as e:
        print(f'Error HTTP: {e.code}')

    except URLError as e:
        print(f'Error de conexión: {e.reason}')

def point_url(lat, lon):
    params = {
        'lat': lat,
        'lon': lon,
        'units': UNITS,
        'lang': LANG,
        'appid': API_KEY,
    }

    BASE_URL = 'https://api.openweathermap.org/data/2.5/weather?'

    return BASE_URL + urlencode(params)

def is_cache_valid(path, max_age=SECONDS):
    if not exists(path):
        return False

    file_time = getmtime(path)
    age = time() - file_time

    return age < max_age

def deg_to_dir(e):
    if e < 23 or e >= 338:
        return 'N'
    elif e < 68:
        return 'NE'
    elif e < 113:
        return 'E'
    elif e < 158:
        return 'SE'
    elif e < 203:
        return 'S'
    elif e < 248:
        return 'SO' if LANG == 'es' else 'SW'
    elif e < 293:
        return 'O' if LANG == 'es' else 'S'
    else:
        return 'NO' if LANG == 'es' else 'NW'

def icons(code):
    icons = {
        '01d': '☀',
        '01n': '☾',
        '02d': '☀☁',
        '02n': '☁☾',
        '03d': '☁',
        '03n': '☁',
        '04d': '☁☁',
        '04n': '☁☁',
        '09d': '☂',
        '09n': '☂',
        '10d': '☀☂',
        '10n': '☾☂',
        '11d': '⚡',
        '11n': '⚡',
        '13d': '❄',
        '13n': '❄',
        '50d': '≋',
        '50n': '≋',
    }

    return icons.get(code, '?')

def dict_info(opt, data):
    temp = data.get('main', {}).get('temp')
    fl = data.get('main', {}).get('feels_like')
    pressure = data.get('main', {}).get('pressure')
    humidity = data.get('main', {}).get('humidity')
    visib_raw = data.get('visibility')
    wind_speed = data.get('wind', {}).get('speed')
    wind_deg =   data.get('wind', {}).get('deg')

    DEG_UNIT = 'C' if UNITS == 'metric' else 'F'
    if visib_raw is None:
        visibility = ''
    else:
        visib = (
            visib_raw / 1000 if UNITS == 'metric' else visib_raw / 1609.344
        )
        visibility = str(int(visib)) if visib.is_integer() else f'{visib:.1f}'
    visib_unit = 'Km' if UNITS == 'metric' else 'mi'

    if wind_speed is None or wind_deg is None:
        wind = ''
    else:
        wind = round(wind_speed * 3.6) if UNITS == 'metric' else wind_speed
    VEL_UNIT = 'Km/h' if UNITS == 'metric' else 'mph'

    values = {
        'n': data.get('name'),
        'i': icons(data.get('weather', [{}])[0].get('icon')),
        'd': data.get('weather', [{}])[0].get('description'),
        't': '--' if temp is None else f'{round(temp)}°{DEG_UNIT}',
        'l': '--' if fl is None else f'{round(fl)}°{DEG_UNIT}',
        'p': '--' if pressure is None else f'{round(pressure)}hPa',
        'h': '--' if humidity is None else f'{round(humidity)}%',
        'v': '--' if not visibility else f'{visibility}{visib_unit}',
        'w': '--' if not wind else f'{wind}{VEL_UNIT} {deg_to_dir(wind_deg)}'
    }
    return values.get(opt, '--')

def get_arg(prefix):
    for item in argv[1:]:
        if item.startswith(prefix):
            return item.split('=', 1)[1]
    return None

def help (lang):
    show = {
        'es': """

Uso:
  owm --city="CIUDAD"
  owm --geo=LAT,LON
  owm --lat=LAT --lon=LON

  owm [UBICACIÓN] [OPCIONES DE DATOS] [OPCIONES GENERALES]

Descripción:
  Obtiene información meteorológica actual desde OpenWeatherMap.

Requisito:
  Es obligatorio proporcionar una API key válida de OpenWeatherMap.

Opciones de autenticación:
  --key=API_KEY        Clave personal de OpenWeatherMap.

                       También puede definirse mediante variable de entorno:
                         export OWM_API_KEY="tu_clave"

Opciones de ubicación (una obligatoria):
  --city="CIUDAD"      Especifica el nombre de la ciudad.
  --geo=LAT,LON        Especifica coordenadas geográficas.
  --lat=LAT            Latitud en grados decimales.
  --lon=LON            Longitud en grados decimales.

  Las coordenadas deben expresarse en formato decimal.
  Utilice valores negativos para los hemisferios Sur y Oeste.

Opciones de datos meteorológicos:
  -n                   Nombre de la ciudad
  -i                   Ícono del clima
  -d                   Descripción del clima
  -t                   Temperatura actual
  -l                   Sensación térmica
  -p                   Presión atmosférica
  -v                   Visibilidad
  -w                   Velocidad del viento

  Las opciones cortas deben agruparse en un único argumento.
  Ejemplo válido:
    -tl
  Ejemplo inválido:
    -t -l

Modos especiales:
  --temp-feelslike     Alterna entre temperatura y sensación térmica
                       cada 5 segundos.

                       Esta opción funciona como modo independiente.
                       No puede combinarse con otras opciones meteorológicas.

                       No es válida junto con:
                         -n -i -d -t -l -p -v -w
                         --help
                         --version

                       Formato de salida:
                         Español:
                           T24°C   (temperatura)
                           S24°C   (sensación térmica)

                         Inglés:
                           T24°C   (temperature)
                           L24°C   (feels like)

Opciones de salida:
  --space=SEP          Define el separador entre los valores mostrados.
                        Por defecto un espacio en blanco (" ")
                       --space=""
                       --space=","
                       --space=" | "

Opciones generales:
  --units=UNIDAD       Define el sistema de unidades.
                       metric     (°C, m/s)
                       imperial   (°F, mph)
                       standard   (K, m/s)

  --lang=IDIOMA        Define el idioma de la respuesta (ej: es, en, fr).

  --time=SEGUNDOS      Intervalo de actualización en segundos.
                       Valor mínimo: 300 segundos (5 minutos).
                       Valores menores a 300 se tomarán como 300.
                       Útil para paneles o barras de estado.

  --window=conky       Indica ejecución dentro de Conky.
                       También puede configurarse mediante variable de entorno:
                         export WINDOW_TERMINAL=$(ps -o comm= -p $PPID)

  --help               Muestra esta ayuda y finaliza.
  --version            Muestra la versión y finaliza.

Notas:
  • Es obligatorio especificar una opción de ubicación.
  • Es obligatorio proporcionar una API key.
  • Las opciones de datos pueden combinarse (ej: -tld).

Ejemplos:
  owm --city="Puerto Iguazú" --key=0123456789
  owm --geo=-25.6346782,-54.58287530604622 -tl --key=0123456789
  owm --lat=-25.6346782 --lon=-54.58287530604622 -t --units=metric
  owm --geo=-25.6346782,-54.58287530604622 -tl --no-space --key=0123456789""",

        'en': """Usage:
  owm --city="CITY"
  owm --geo=LAT,LON
  owm --lat=LAT --lon=LON

  owm [LOCATION] [WEATHER OPTIONS] [GENERAL OPTIONS]

Description:
  Retrieves current weather information from OpenWeatherMap.

Requirement:
  A valid OpenWeatherMap API key is required.

Authentication options:
  --key=API_KEY        Personal OpenWeatherMap API key.

                       Can also be set via environment variable:
                         export OWM_API_KEY="your_key"

Location options (one required):
  --city="CITY"        Specify city name.
  --geo=LAT,LON        Specify geographic coordinates.
  --lat=LAT            Latitude in decimal degrees.
  --lon=LON            Longitude in decimal degrees.

  Coordinates must be expressed in decimal format.
  Use negative values for South and West hemispheres.

Weather data options:
  -n                   City name
  -i                   Weather icon
  -d                   Weather description
  -t                   Current temperature
  -l                   Feels like temperature
  -p                   Atmospheric pressure
  -v                   Visibility
  -w                   Wind speed

  Short options must be combined into a single argument.
  Example:
    -tl
  Not valid:
    -t -l

Special modes:
  --temp-feelslike     Alternates between temperature and feels-like
                       every 5 seconds.

                       This option works as a standalone mode.
                       It cannot be combined with other weather options.

                       Not valid with:
                         -n -i -d -t -l -p -v -w
                         --help
                         --version

                       Output format:
                         English:
                           T24°C   (temperature)
                           L24°C   (feels like)

                         Spanish:
                           T24°C   (temperatura)
                           S24°C   (sensación térmica)

Output options:
  --space=SEP          Set output separator string.
                       Default: single space (" ").
                       Example:
                         --space=""
                         --space=","
                         --space=" | "

General options:
  --units=UNIT         Set unit system.
                       metric     (°C, m/s)
                       imperial   (°F, mph)
                       standard   (K, m/s)

  --lang=LANG          Set response language (e.g. en, es, fr).

  --time=SECONDS       Refresh interval in seconds.
                       Minimum value: 300 seconds (5 minutes).
                       Values lower than 300 will be treated as 300.
                       Useful for panels or status bars.

  --window=conky       Indicates execution inside Conky.
                       Can also be set via environment variable:
                         export WINDOW_TERMINAL=$(ps -o comm= -p $PPID)

  --help               Display this help and exit.
  --version            Output version information and exit.

Notes:
  • One location option is required.
  • A valid API key must be provided.
  • Weather data options can be combined (e.g. -tld).

Examples:
  owm --city="Puerto Iguazú" --key=0123456789
  owm --geo=-25.6346782,-54.58287530604622 -tl --key=0123456789
  owm --lat=-25.6346782 --lon=-54.58287530604622 -t --units=metric
  owm --geo=-25.6346782,-54.58287530604622 -tl --no-space --key=0123456789"""
}
    print (show.get(lang, show['en']))

def err_msg(cod, lang=LANG):
    messages = {
        1: {
            'es': 'Faltan argumentos.',
            'en': 'Missing arguments.'
        },
        2: {
            'es': 'Argumento inválido.',
            'en': 'Invalid argument.'
        }
    }

    return messages.get(cod, {}).get(lang, 'en')

version = '0.1'
DIR = '/tmp/owm'
API_KEY = (
    get_arg('--key=') if has_arg('--key=') else getenv('OWM_API_KEY', 'err')
)

ARGVs = len(argv) - 1
PATTERN_GEO = r'^-?\d{1,3}(\.\d+)?,-?\d{1,3}(\.\d+)?$'
PATTERN_POINT = r'^-?\d{1,3}(\.\d+)?$'
OPTIONS = 'dhilnptvw'
PATTERN_OPTION = r'^-['+ OPTIONS + ']+$'
PATTERN_ARG = (
    r'^(--(city|geo|key|lat|lon|space|time)=.+'
    r'|--(help|temp-feelslike|version)'
    r'|(-[' + OPTIONS + ']+))$'
)

if __name__ == '__main__':
    if ARGVs == 0:
        if WINDOW.lower() == 'conky':
            print ('--')
            exit(0)
        else:
            raise IndexError(err_msg(1))
    elif not all(fullmatch(PATTERN_ARG, arg) for arg in argv[1:]):
        if WINDOW.lower() == 'conky':
            print ('--')
            exit(0)
        else:
            raise TypeError(err_msg(2))
    elif len(argv) == 2 and argv[1] in ('--help', '--version'):
        if argv[1] == '--help':
            help(LANG)
        else:
            print (f'{Path(argv[0]).stem} {version}')
    elif has_arg('--city='):
        city_name = get_arg('--city=')
        citys_url = city_name_to_list(city_name)
        data = info_in_dict(citys_url)
        citys = []
        g_map = f'https://maps.google.com/?q='
        old_owm = 'https://old.openweathermap.org/city/'
        for d in data:
            data_city = info_in_dict(point_url(d.get('lat'), d.get('lon')))
            id_city = data_city.get('id', 'error')
            name_lang = d.get("local_names", {}).get(LANG)
            name = name_lang or d.get("name", "--")
            state = '' if d.get('state') is None else ', ' + d.get('state')
            country = d.get('country')
            citys.append( [f'''{name}{state}, {country}
\033[1m{Path(argv[0]).stem} --geo={d.get('lat')},{d.get('lon')} -t\033[0m
\033[1m{Path(argv[0]).stem} --lat={d.get('lat')} --lon={d.get('lon')} -t\
\033[0m
\033[4mOpen Weather Map\033[0m: {point_url(d.get('lat'),d.get('lon'))}
\033[4mGoogle Map\033[0m: {g_map}{d.get('lat')},{d.get('lon')}
\033[4mWidget Widget Plus\033[0m: {old_owm}{id_city}
\033[4mID\033[0m: {id_city}'''])
        for i, _ in enumerate(citys):
            if i > 0:
                print ('···')
            for x in _:
                print (x)
    elif (
        (has_arg('--geo=') and match(PATTERN_GEO, get_arg('--geo='))
         and not has_arg('--lat=') and not has_arg('--lon='))
    or
        (has_arg('--lat=') and match(PATTERN_POINT, get_arg('--lat=')) and
         has_arg('--lon=') and match(PATTERN_POINT, get_arg('--lon=')) and
         not has_arg('--geo='))
    ):
        space = get_arg('--space') if has_arg('--space=') else ' '
        if has_arg('--geo='):
            lat, lon = get_arg('--geo=').split(',')
        else:
            lat, lon = get_arg('--lat='), get_arg('--lon=')
        lat, lon = float(lat), float(lon)
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError('')

        makedirs(DIR, exist_ok=True)
        file = f'{DIR}/{lat},{lon}.json'
        file = file.replace('.', '_', file.count('.') - 1)

        city_url = point_url(lat, lon)

        if (
            any(fullmatch(PATTERN_OPTION, arg) for arg in argv[1:]) or
            '--temp-feelslike' in argv[1:]
        ):
            for e in argv[1:]:
                if (
                    fullmatch(PATTERN_OPTION, e) or
                    '--temp-feelslike' in argv[1:]
                ):
                    option = e
                    if is_cache_valid(file):
                        with open(file, "r") as f:
                            data = load(f)
                    else:
                        data = info_in_dict(city_url)
                    with open(file, 'w', encoding='utf-8') as f:
                        dump(data, f, indent=4, ensure_ascii=False)
                    break
            options = []
            if (
                '--temp-feelslike' in argv[1:] and
                not any(fullmatch(PATTERN_OPTION, arg) for arg in argv[1:])
            ):
                time_now = int(time()) % 10
                temp, feels_like = dict_info('t', data), dict_info('l', data)
                AT = 'S' if LANG == 'es' else 'L'
                if temp != feels_like and time_now >= 5:
                    print(f'{AT}{feels_like}')
                else:
                    print(f'T{temp}')
                exit(0)
            for e in option[1:]:
                if len(option) != len(set(option)):
                    if WINDOW.lower() == 'conky':
                        print ('--')
                        exit(0)
                    else:
                        raise IndexError(err_msg(2))
                options.append(dict_info(e, data))
            print(space.join(options))
        else:
            if WINDOW.lower() == 'conky':
                print ('--')
                exit(0)
            else:
                raise IndexError(err_msg(2))
                exit(0)
