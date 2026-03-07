from time import time
from argparse import ArgumentParser, ArgumentTypeError
from sys import argv, exit

from owm import __version__
from owm.i18n import msg
from owm.weather import get_weather
from owm.api import get_api_key
from owm.geocode import city_name_to_list
from owm.exceptions import OWMError
from owm.env import get_env
from owm.validators import Validator
from owm.conversions import icons, pressure,temperature, visibility, wind


def parse_geo(value: str) -> str:
    '''Validate format only; returns raw string for later normalization.'''
    parts = value.split(',')
    if len(parts) != 2:
        raise ArgumentTypeError(
            '--geo debe tener formato LAT,LON (ej: -34.61,-58.38)'
        )
    try:
        float(parts[0])
        float(parts[1])
    except ValueError:
        raise ArgumentTypeError(
            '--geo debe tener formato LAT,LON (ej: -34.61,-58.38)'
        )
    return value

def detect_lang() -> str:
    for arg in argv:
        if arg.startswith('--lang='):
            return arg.split('=', 1)[1]
    return (get_env('LANG') or 'en')[:2]

def build_parser(lang: str) -> ArgumentParser:
    m = lambda key: msg(lang, key)

    parser = ArgumentParser(prog='owm')
    parser.add_argument('-v', '--version', default=None, action='version',
                        version=f'%(prog)s {__version__}',
                        help=m('help_version'))

    # Autenticación
    auth = parser.add_argument_group(m('group_auth'))
    auth.add_argument('--key', default=None, help=m('help_key'))

    # Ubicación
    local = parser.add_argument_group(m('group_local'))
    local.add_argument('--city', default=None, help=m('help_city'))
    local.add_argument('--geo', type=parse_geo, default=None,
                        help=m('help_geo'))
    local.add_argument('--lat', type=str, default=None, help=m('help_lat'))
    local.add_argument('--lon', type=str, default=None, help=m('help_lon'))

    # Configuración
    config = parser.add_argument_group(m('group_config'))
    config.add_argument('--lang', default='es', help=m('help_lang'))
    config.add_argument('--time', type=int, default=None,
                        dest='cache_seconds', metavar='SECONDS',
                        help=m('help_time'))
    config.add_argument('--units', choices=['metric', 'imperial'],
                        default=None, metavar='UNITS', help=m('help_units'))

    # Flags de salida (modo clima)
    output = parser.add_argument_group(m('group_output'))
    output.add_argument('-d', '--description', action='store_true',
                        help=m('help_description'))

    output.add_argument('--feels-like', action='store_true',
                        dest='feels_like', help=m('help_feels_like'))

    output.add_argument('--humidity', action='store_true',
                        help=m('help_humidity'))

    output.add_argument('--icon', action='store_true', help=m('help_icon'))

    output.add_argument('--id', action='store_true', help=m('help_id'))

    output.add_argument('--name', action='store_true',
                        help=m('help_name'))

    output.add_argument('--pressure', action='store_true',
                        help=m('help_pressure'))

    output.add_argument('--space', default=' ', help=m('help_space'))

    output.add_argument('--sunrise', action='store_true',
                        help=m('help_sunrise'))

    output.add_argument('--sunset', action='store_true',
                        help=m('help_sunset'))

    output.add_argument('-t', '--temp', action='store_true',
                        help=m('help_temp'))

    output.add_argument('--temp-feels-like', action='store_true',
                        dest='temp_feels_like',
                        help=m('help_temp_feels_like'))

    output.add_argument('--visibility', action='store_true',
                        help=m('help_visibility'))

    output.add_argument('--wind', action='store_true',
                        help=m('help_wind'))

    return parser


def apply_env_defaults(args) -> None:
    '''Fill in missing args from environment variables.'''
    if args.key is None:
        args.key = get_env('OWM_API_KEY')

    if (
        args.city is None and args.geo is None and args.lat is None and
        args.lon is None
    ):
        env_geo = get_env('OWM_GEO')
        if env_geo:
            args.geo = env_geo

    if args.units is None:
        env_units = get_env('OWM_UNITS')
        if env_units in ('metric', 'imperial'):
            args.units = env_units
        else:
            args.units = 'metric'  # default

    if args.cache_seconds is None:
        env_time = get_env('OWM_SECONDS')
        if env_time is not None:
            try:
                args.cache_seconds = int(env_time)
            except ValueError:
                pass
        if args.cache_seconds is None:
            args.cache_seconds = 600  # default 10 min


def main() -> None:
    parser = build_parser(detect_lang())
    args = parser.parse_args()

    apply_env_defaults(args)

    lang = args.lang

    try:
        validator = Validator(lang)
        validator.validate_args(args)
    except ValueError as exc:
        parser.error(str(exc))

    try:
        api_key = get_api_key(args.key, lang)

        # ── Modo geolocalización ────────────────────────────────────────────
        if args.city:
            print(msg(lang, 'dl-city'))
            cities = city_name_to_list(args.city, api_key=api_key, lang=lang)
            blocks = []
            for city in cities:
                weather = get_weather(
                    lat=city.lat,
                    lon=city.lon,
                    api_key=api_key,
                    lang=lang,
                    units=args.units,
                    cache_seconds=args.cache_seconds,
                )
                lat, lon = city.lat, city.lon
                city_id = weather.city_id

                # Línea 1: nombre, estado (si aplica), país
                header_parts = [city.name]
                if city.state:
                    header_parts.append(city.state)
                header_parts.append(city.country)
                lines = [', '.join(header_parts)]

                # Línea 2-3: comandos owm equivalentes
                lines.append(f'owm --geo={lat},{lon} -t')
                lines.append(f'owm --lat={lat} --lon={lon} -t')

                # Línea 4: URL API OWM
                owm_url = (
                    f'https://api.openweathermap.org/data/2.5/weather'
                    f'?lat={lat}&lon={lon}&units=metric&lang={lang}'
                    f'&appid={api_key}'
                )
                lines.append(f'\x1b[4mOpen Weather Map\x1b[24m: {owm_url}')

                # Línea 5: Google Maps
                lines.append(f'\x1b[4mGoogle Map\x1b[24m: '
                             'https://maps.google.com/?q={lat},{lon}')

                # Línea 6: Widget OWM (solo si hay id)
                if city_id:
                    lines.append(
                        f'\x1b[4mWidget Widget Plus\x1b[24m: '
                        f'https://old.openweathermap.org/city/{city_id}'
                    )

                # Línea 7: ID
                if city_id:
                    lines.append(f'\x1b[4mID\x1b[24m: {city_id}')

                blocks.append('\n'.join(lines))

            print('\n···\n'.join(blocks))
            return

        # ── Modo clima ──────────────────────────────────────────────────────
        UNITS = args.units

        weather = get_weather(
            lat=args.lat,
            lon=args.lon,
            api_key=api_key,
            lang=lang,
            units=args.units,
            cache_seconds=args.cache_seconds,
        )

        def temp_feels_like_output():
            second_unit = int(time()) % 10
            if second_unit >= 5 and weather.temperature != weather.feels_like:
                prefix = msg(lang, 'feels_like_prefix')
                return f'⇄{temperature(weather.feels_like, UNITS)}'
            else:
                prefix = msg(lang, 'temp_prefix')
                return f'T{temperature(weather.temperature, UNITS)}'

        output_map = {
            '--description': lambda: weather.description.capitalize(),
            '-d': lambda: weather.description.capitalize(),
            '--feels-like': lambda: temperature(weather.feels_like, UNITS),
            '--humidity': lambda: f'{weather.humidity}%',
            '--icon': lambda: icons(weather.icon),
            '--id': lambda: (str(weather.city_id)
                             if weather.city_id is not None else 'N/A'),
            '--name': lambda: weather.city_name,
            '--pressure': lambda: pressure(weather.pressure, UNITS),
            '--sunrise': lambda: weather.sunrise_str,
            '--sunset': lambda: weather.sunset_str,
            '--temp': lambda: temperature(weather.temperature, UNITS),
            '-t': lambda: temperature(weather.temperature, UNITS),
            '--temp-feels-like': temp_feels_like_output,
            '--visibility': lambda: str(
                visibility(weather.visibility, UNITS)
                if weather.visibility is not None
                else 'N/A'),
            '--wind': lambda: f'{wind(weather.wind_speed, UNITS)} '
                                     f'{weather.wind_direction}',
        }

        # Aliases that refer to the same output, to avoid duplicates
        aliases = {'-t': '--temp', '--temp': '-t', '-d': '--description',
                   '--description': '-d',
                   '--temp-feels-like': '--temp-feels-like'}

        seen = set()
        outputs = []
        for arg in argv[1:]:
            key = arg.split('=')[0]
            if key in output_map and key not in seen:
                seen.add(key)
                seen.add(aliases.get(key, key))
                outputs.append(output_map[key]())

        print(args.space.join(outputs))

    except OWMError as exc:
        print(exc)
        exit(1)


if __name__ == '__main__':
    main()
