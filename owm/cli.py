from time import time
from argparse import ArgumentParser, ArgumentTypeError, HelpFormatter
from datetime import datetime
from pathlib import Path
from re import fullmatch, split as re_split, sub as re_sub
from shutil import get_terminal_size, rmtree
from sys import argv, exit
from json import dumps, loads, JSONDecodeError

from owm import __version__
from owm.i18n import msg, _LOCALEDIR
from owm.weather import get_weather
from owm.api import get_api_key
from owm.cache import build_cache_path, get_cache_dir, read_cache
from owm.geocode import city_name_to_list
from owm.exceptions import OWMError
from owm.env import get_env
from owm.models import Weather
from owm.validators import Validator
from owm.conversions import (
    convert, icons, pressure, temperature, visibility, wind
)


def parse_geo(value: str) -> str:
    '''Acepta LAT,LON o un alias de ciudad a resolver más tarde.'''
    if ',' in value:
        parts = value.split(',')
        lang = detect_lang()
        if len(parts) != 2:
            raise ArgumentTypeError(msg(lang, 'geo_format_error'))
        try:
            float(parts[0])
            float(parts[1])
        except ValueError:
            raise ArgumentTypeError(msg(lang, 'geo_format_error'))
    return value


def detect_lang() -> str:
    for arg in argv:
        if arg.startswith('--lang='):
            return arg.split('=', 1)[1]
    lang = (get_env('LANG') or 'en')[:2]
    mo = _LOCALEDIR / lang / 'LC_MESSAGES' / 'owm.mo'
    if not mo.exists():
        return 'en'
    return lang


class AlignedHelpFormatter(HelpFormatter):
    def _format_action_invocation(self, action):
        if (action.option_strings and
                len(action.option_strings) == 1 and
                action.option_strings[0].startswith('--')):
            return '    ' + action.option_strings[0]
        return super()._format_action_invocation(action)


def build_parser(lang: str) -> ArgumentParser:
    m = lambda key: msg(lang, key)
    parser = ArgumentParser(prog='owm', formatter_class=AlignedHelpFormatter)
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

    # Gestión de localidades
    cities = parser.add_argument_group(m('group_cities'))
    cities.add_argument('--add-city', default=None,
                        dest='add_city', help=m('help_add_city'))
    cities.add_argument('--alias', default=None, help=m('help_alias'))
    cities.add_argument('--list', action='store_true',
                        dest='list_cities', help=m('help_list'))
    cities.add_argument('--list-alias', action='store_true',
                        dest='list_alias', help=m('help_list_alias'))
    cities.add_argument('--order', default=None, help=m('help_order'))
    cities.add_argument('--remove-city', default=None,
                        dest='remove_city', help=m('help_remove_city'))

    # Configuración
    config = parser.add_argument_group(m('group_config'))
    config.add_argument('--clear-cache', action='store_true',
                        dest='clear_cache', help=m('help_clear_cache'))
    config.add_argument('--lang', default=None, help=m('help_lang'))
    config.add_argument('--offline', action='store_true',
                        help=m('help_offline'))
    config.add_argument('--raw', action='store_true',
                        dest='raw', help=m('help_raw'))
    config.add_argument('--terminal', default=None, help=m('help_terminal'))
    config.add_argument('--time', type=int, default=None,
                        dest='cache_seconds', metavar='SECONDS',
                        help=m('help_time'))
    config.add_argument('--units', choices=['metric', 'imperial'],
                        default=None, metavar='UNITS', help=m('help_units'))

    # Flags de salida (modo clima) — orden alfabético
    output = parser.add_argument_group(m('group_output'))
    output.add_argument('-b', '--visibility', action='store_true',
                        help=m('help_visibility'))
    output.add_argument('-d', '--description', action='store_true',
                        help=m('help_description'))
    output.add_argument('-D', '--desc-cap', action='store_true',
                        help=m('help_description_capitalize'))
    output.add_argument('-i', '--icon', action='store_true',
                        help=m('help_icon'))
    output.add_argument('--icon-next', action='store_true',
                        dest='icon_next', help=m('help_icon_next'))
    output.add_argument('--icon-prev', action='store_true',
                        dest='icon_prev', help=m('help_icon_prev'))
    output.add_argument('-I', '--icon-emoji', action='store_true',
                        dest='icon_emoji', help=m('help_icon_emoji'))
    output.add_argument('--id', action='store_true', help=m('help_id'))
    output.add_argument('-l', '--feels-like', action='store_true',
                        dest='feels_like', help=m('help_feels_like'))
    output.add_argument('--last-update', action='store_true',
                        dest='last_update', help=m('help_last_update'))
    output.add_argument('-n', '--name', action='store_true',
                        help=m('help_name'))
    output.add_argument('-p', '--pressure', action='store_true',
                        help=m('help_pressure'))
    output.add_argument('--space', default=' ', help=m('help_space'))
    output.add_argument('-r', '--sunrise', action='store_true',
                        help=m('help_sunrise'))
    output.add_argument('-s', '--sunset', action='store_true',
                        help=m('help_sunset'))
    output.add_argument('-t', '--temp', action='store_true',
                        help=m('help_temp'))
    output.add_argument('--text-next', action='store_true',
                        dest='text_next', help=m('help_text_next'))
    output.add_argument('--text-prev', action='store_true',
                        dest='text_prev', help=m('help_text_prev'))
    output.add_argument('-T', '--toggle', action='store_true',
                        dest='toggle', help=m('help_toggle'))
    output.add_argument('-u', '--humidity', action='store_true',
                        help=m('help_humidity'))
    output.add_argument('-w', '--wind', action='store_true',
                        help=m('help_wind'))
    output.add_argument('--wind-deg', action='store_true',
                        dest='wind_deg_flag', help=m('help_wind_deg'))
    output.add_argument('--wind-speed', action='store_true',
                        dest='wind_speed_flag', help=m('help_wind_speed'))

    return parser


def _is_latlon(value: str) -> bool:
    '''Devuelve True si el valor es un string LAT,LON válido.'''
    parts = value.split(',')
    if len(parts) != 2:
        return False
    try:
        float(parts[0])
        float(parts[1])
        return True
    except ValueError:
        return False


def resolve_geo_alias(args, lang: str) -> None:
    '''Si --geo no es LAT,LON, busca el alias en ~/.owm/cities.json.'''
    if args.geo is None or _is_latlon(args.geo):
        return
    alias = args.geo
    cities_file = Path.home() / '.owm' / 'cities.json'
    if not cities_file.exists():
        raise OWMError(
            msg(lang, 'geo_alias_no_file').format(alias=alias)
        )
    try:
        cities = loads(cities_file.read_text())
    except (JSONDecodeError, OSError) as exc:
        raise OWMError(
            msg(lang, 'geo_alias_read_error').format(error=exc)
        ) from exc

    entry = cities.get(alias)
    if entry is None:
        raise OWMError(
            msg(lang, 'geo_alias_not_found').format(alias=alias)
        )

    if 'geo' in entry:
        args.geo = entry['geo']
    elif 'lat' in entry and 'lon' in entry:
        args.lat = str(entry['lat'])
        args.lon = str(entry['lon'])
        args.geo = None
    else:
        raise OWMError(
            msg(lang, 'geo_alias_bad_entry').format(alias=alias)
        )


def _ansi_len(s: str) -> int:
    '''Longitud visible de un string ignorando escapes ANSI.'''
    return len(re_sub(r'\x1b\[[0-9;]*m', '', s))


def _print_with_url(prefix: str, name: str, url: str) -> None:
    '''Imprime prefix+name+(url) en una o dos líneas según el ancho.'''
    cols = get_terminal_size().columns
    # Indentación de la segunda línea: posición de la primera letra del nombre
    indent = ' ' * _ansi_len(prefix)
    one_line = f'{prefix}{name} ({url})'
    if _ansi_len(one_line) <= cols:
        print(one_line)
    else:
        print(f'{prefix}{name}')
        print(f'{indent}{url}')



def normalize_alias(alias: str, lang: str) -> str:
    '''Normaliza el alias: strip, espacios → _, minúsculas, valida charset.'''
    alias = alias.strip().replace(' ', '_').lower()
    if not fullmatch(r'[a-z0-9_]+', alias):
        raise OWMError(msg(lang, 'alias_invalid'))
    return alias


def add_city_cmd(city_name: str, alias: str | None,
                 api_key: str, lang: str) -> None:
    '''Busca una ciudad y la guarda en ~/.owm/cities.json.'''
    try:
        print(msg(lang, 'dl-city'))
        cities = city_name_to_list(city_name, api_key=api_key, lang=lang)
    except KeyboardInterrupt:
        print()
        return

    # Mostrar resultados numerados desde 1 con URL de Google Maps
    total = len(cities)
    num_width = len(str(total))
    for i, city in enumerate(cities):
        parts = [city.name]
        if city.state:
            parts.append(city.state)
        parts.append(city.country)
        num = f'\x1b[1m{i + 1}.\x1b[22m'
        # Indentación: ancho del número más largo + punto + espacio
        padding = ' ' * (num_width + 2)
        prefix = f'{num}{" " * (num_width - len(str(i + 1)) + 1)}'
        url = f'https://maps.google.com/?q={city.lat},{city.lon}'
        _print_with_url(prefix, ', '.join(parts), url)

    # Pedir al usuario que elija — acepta número o C para cancelar
    while True:
        try:
            raw = input(msg(lang, 'add_city_choose')).strip()
        except KeyboardInterrupt:
            print()
            return
        if fullmatch(r'[Cc]', raw):
            return
        if fullmatch(r'\d+', raw):
            choice = int(raw)
            if 1 <= choice <= len(cities):
                break
        print(msg(lang, 'add_city_invalid_choice').format(max=len(cities)))

    # El usuario ve 1..N, la lista es 0..N-1
    city = cities[choice - 1]

    # Pedir alias si no se proporcionó
    if alias is None:
        try:
            alias = input(msg(lang, 'add_city_alias_prompt')).strip()
        except KeyboardInterrupt:
            print()
            return
        if not alias:
            raise OWMError(msg(lang, 'add_city_alias_empty'))

    alias = normalize_alias(alias, lang)

    # Nombre legible: ciudad (estado, país)
    extra = ', '.join(filter(None, [city.state, city.country]))
    display_name = f'{city.name} ({extra})' if extra else city.name

    # Leer o crear el archivo cities.json
    cities_file = Path.home() / '.owm' / 'cities.json'
    cities_file.parent.mkdir(parents=True, exist_ok=True)
    if cities_file.exists():
        try:
            data = loads(cities_file.read_text())
        except (JSONDecodeError, OSError):
            data = {}
    else:
        data = {}

    # Si el alias ya existe, pedir otro hasta que sea único o se cancele
    while alias in data:
        print(msg(lang, 'add_city_alias_exists').format(alias=alias))
        try:
            alias = input(msg(lang, 'add_city_alias_prompt')).strip()
        except KeyboardInterrupt:
            print()
            return
        if fullmatch(r'[Cc]', alias):
            return
        if not alias:
            raise OWMError(msg(lang, 'add_city_alias_empty'))
        alias = normalize_alias(alias, lang)

    data[alias] = {
        'geo': f'{city.lat},{city.lon}',
        'name': display_name,
    }

    cities_file.write_text(dumps(data, ensure_ascii=False, indent=4))
    print(msg(lang, 'add_city_saved').format(alias=alias, name=display_name))


def list_cities_cmd(lang: str) -> None:
    '''Lista las ciudades guardadas en ~/.owm/cities.json.'''
    prog = 'owm'
    cities_file = Path.home() / '.owm' / 'cities.json'
    if not cities_file.exists():
        raise OWMError(
            msg(lang, 'cities_no_data').format(prog=prog)
        )
    try:
        data = loads(cities_file.read_text())
    except (JSONDecodeError, OSError) as exc:
        raise OWMError(
            msg(lang, 'geo_alias_read_error').format(error=exc)
        ) from exc
    if not data:
        raise OWMError(
            msg(lang, 'cities_no_data').format(prog=prog)
        )
    for alias, entry in data.items():
        name = entry.get('name', alias)
        geo = entry.get('geo', '')
        prefix = f'\x1b[1m{alias}\x1b[22m: '
        url = f'https://maps.google.com/?q={geo}'
        _print_with_url(prefix, name, url)


def list_alias_cmd(lang: str) -> None:
    '''Imprime solo los alias guardados en ~/.owm/cities.json.'''
    cities_file = Path.home() / '.owm' / 'cities.json'
    if not cities_file.exists():
        raise OWMError(msg(lang, 'cities_no_data').format(prog='owm'))
    try:
        data = loads(cities_file.read_text())
    except (JSONDecodeError, OSError) as exc:
        raise OWMError(
            msg(lang, 'geo_alias_read_error').format(error=exc)
        ) from exc
    if not data:
        raise OWMError(msg(lang, 'cities_no_data').format(prog='owm'))
    for alias in data:
        print(alias)


def remove_city_cmd(alias: str, lang: str) -> None:
    '''Elimina una ciudad de ~/.owm/cities.json por alias.'''
    alias = normalize_alias(alias, lang)
    cities_file = Path.home() / '.owm' / 'cities.json'
    if not cities_file.exists():
        raise OWMError(msg(lang, 'cities_no_data').format(prog='owm'))
    try:
        data = loads(cities_file.read_text())
    except (JSONDecodeError, OSError) as exc:
        raise OWMError(
            msg(lang, 'geo_alias_read_error').format(error=exc)
        ) from exc
    if alias not in data:
        raise OWMError(
            msg(lang, 'geo_alias_not_found').format(alias=alias)
        )
    name = data[alias].get('name', alias)
    del data[alias]

    if data:
        # Aún quedan ciudades — reescribir el archivo
        cities_file.write_text(dumps(data, ensure_ascii=False, indent=4))
    else:
        # cities.json queda vacío — eliminarlo
        cities_file.unlink()
        owm_dir = cities_file.parent
        # Eliminar ~/.owm si quedó sin archivos
        if not any(owm_dir.iterdir()):
            owm_dir.rmdir()

    print(msg(lang, 'remove_city_saved').format(name=name))


def order_cities_cmd(order: str, lang: str) -> None:
    '''Reordena las ciudades en ~/.owm/cities.json según el orden indicado.'''
    cities_file = Path.home() / '.owm' / 'cities.json'
    if not cities_file.exists():
        raise OWMError(msg(lang, 'cities_no_data').format(prog='owm'))
    try:
        data = loads(cities_file.read_text())
    except (JSONDecodeError, OSError) as exc:
        raise OWMError(
            msg(lang, 'geo_alias_read_error').format(error=exc)
        ) from exc

    # Separar aliases por coma con o sin espacios
    aliases = [a.strip() for a in re_split(r',\s*', order) if a.strip()]

    # Validar que todos los aliases existan y que no falte ninguno
    existing = set(data.keys())
    requested = set(aliases)

    missing = requested - existing
    if missing:
        raise OWMError(
            msg(lang, 'order_alias_not_found').format(
                aliases=', '.join(sorted(missing)))
        )

    extra = existing - requested
    if extra:
        raise OWMError(
            msg(lang, 'order_missing_aliases').format(
                aliases=', '.join(sorted(extra)))
        )

    # Reordenar
    reordered = {alias: data[alias] for alias in aliases}
    cities_file.write_text(dumps(reordered, ensure_ascii=False, indent=4))
    print(msg(lang, 'order_saved'))


def clear_cache_cmd(lang: str) -> None:
    '''Elimina el directorio de caché /tmp/.owm_{user}/.'''
    cache_dir = get_cache_dir()
    if cache_dir.exists():
        rmtree(cache_dir)
        print(msg(lang, 'cache_cleared'))
    else:
        print(msg(lang, 'cache_empty'))


def _fmt_last_update(cache_path: Path, units: str) -> str:
    '''Formatea la hora de última actualización del caché.
    Si es del mismo día: HH:MM:SS
    Si es de otro día: DD/MM/YYYY HH:MM:SS o MM/DD/YYYY HH:MM:SS según units.
    '''
    dt = datetime.fromtimestamp(cache_path.stat().st_mtime)
    if dt.date() == datetime.now().date():
        return dt.strftime('%H:%M:%S')
    if units == 'metric':
        return dt.strftime('%d/%m/%Y %H:%M:%S')
    return dt.strftime('%m/%d/%Y %H:%M:%S')


def fetch_weather(
    lat: float,
    lon: float,
    api_key: str,
    lang: str,
    units: str,
    cache_seconds: int,
    terminal: str | None,
    online: bool = True,
) -> 'Weather':
    '''Obtiene el clima online o directo del caché según online.'''
    if online:
        return get_weather(
            lat=lat, lon=lon, api_key=api_key, lang=lang,
            units=units, cache_seconds=cache_seconds, terminal=terminal,
        )
    # Modo offline: leer directo del JSON
    cache_path = build_cache_path(lat, lon, lang)
    if not cache_path.exists():
        raise OWMError(msg(lang, 'cache_no_data'))
    data = loads(cache_path.read_text())
    return Weather.from_api(data, lang)


def apply_env_defaults(args) -> None:
    '''Completa los args faltantes desde variables de entorno.'''
    if args.key is None:
        args.key = get_env('OWM_API_KEY')

    if (
        args.city is None and args.geo is None and args.lat is None and
        args.lon is None
    ):
        env_geo = get_env('OWM_GEO')
        if env_geo:
            args.geo = env_geo

    if args.lang is None:
        args.lang = detect_lang()

    resolve_geo_alias(args, args.lang)

    if args.units is None:
        env_units = get_env('OWM_UNITS')
        if env_units in ('metric', 'imperial'):
            args.units = env_units
        else:
            args.units = 'metric'  # por defecto

    if args.cache_seconds is None:
        env_time = get_env('OWM_SECONDS')
        if env_time is not None:
            try:
                args.cache_seconds = int(env_time)
            except ValueError:
                pass
        if args.cache_seconds is None:
            args.cache_seconds = 300  # 5 min por defecto

    if args.terminal is None:
        args.terminal = get_env('WINDOW_TERMINAL')


def default_report(weather, lang: str, units: str) -> None:
    '''Reporte completo cuando no se pasan flags de salida.'''
    m = lambda key: msg(lang, key)
    keys = [
        'label_name', 'label_description', 'label_temp',
        'label_humidity', 'label_pressure', 'label_visibility',
        'label_wind', 'label_sunrise', 'label_sunset',
    ]
    width = max(len(m(k)) for k in keys)
    _u = lambda label: (
        f'\x1b[1;4m{label}\x1b[24m:\x1b[0m' + ' ' * (width - len(label))
    )
    fl_short = msg(lang, 'feels_like_short')
    vis = (
        str(visibility(weather.visibility, units))
        if weather.visibility is not None else 'N/A'
    )
    temp = temperature(weather.temperature, units)
    feels = temperature(weather.feels_like, units)
    desc = f"{icons(weather.icon)} {weather.description.capitalize()}"
    list_print = [
        f"{_u(m('label_name'))} {weather.city_name}",
        f"{_u(m('label_description'))} {desc}",
        f"{_u(m('label_temp'))} {temp} ({fl_short} {feels})",
        f"{_u(m('label_humidity'))} {weather.humidity}%",
        f"{_u(m('label_pressure'))} {pressure(weather.pressure, units)}",
        f"{_u(m('label_visibility'))} {vis}",
        f"{_u(m('label_wind'))} "
        f"{wind(weather.wind_speed, units)} {weather.wind_direction(lang)}",
        f"{_u(m('label_sunrise'))} {weather.sunrise_str}",
        f"{_u(m('label_sunset'))} {weather.sunset_str}",
    ]
    print('\n'.join(list_print))


def main() -> None:
    parser = build_parser(detect_lang())
    args, _ = parser.parse_known_args()

    apply_env_defaults(args)

    lang = args.lang

    # ── Modo limpiar caché — no requiere API key ────────────────────────────
    if args.clear_cache:
        try:
            clear_cache_cmd(lang)
        except OWMError as exc:
            print(exc)
            exit(1)
        return

    try:
        # Modos que no necesitan API key
        if args.list_cities:
            list_cities_cmd(lang)
            return

        if args.list_alias:
            list_alias_cmd(lang)
            return

        if args.remove_city:
            remove_city_cmd(args.remove_city, lang)
            return

        if args.order:
            order_cities_cmd(args.order, lang)
            return

        _api_flags = {
            'description', 'feels_like', 'humidity', 'icon', 'pressure',
            'temp', 'toggle', 'visibility', 'wind', 'sunrise', 'sunset', 'id',
        }
        _needs_api = (
            args.add_city
            or args.city
            or (not args.offline
                and any(getattr(args, f, False) for f in _api_flags))
        )
        api_key = get_api_key(args.key, lang) if _needs_api else args.key

        # ── Modo agregar ciudad ─────────────────────────────────────────────
        if args.add_city:
            add_city_cmd(
                city_name=args.add_city,
                alias=args.alias,
                api_key=api_key,
                lang=lang,
            )
            return

    except OWMError as exc:
        print(exc)
        exit(1)
    except KeyboardInterrupt:
        print()
        exit(0)

    try:
        validator = Validator(lang)
        validator.validate_args(args)
    except ValueError as exc:
        parser.error(str(exc))

    try:
        _api_flags2 = {
            'description', 'feels_like', 'humidity', 'icon', 'pressure',
            'temp', 'toggle', 'visibility', 'wind', 'sunrise', 'sunset', 'id',
        }
        _needs_api2 = (
            args.city
            or (not args.offline
                and any(getattr(args, f, False) for f in _api_flags2))
        )
        api_key = get_api_key(args.key, lang) if _needs_api2 else args.key

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
                    units='metric',
                    cache_seconds=args.cache_seconds,
                    terminal=args.terminal,
                )
                lat, lon = city.lat, city.lon
                city_id = weather.city_id

                header_parts = [city.name]
                if city.state:
                    header_parts.append(city.state)
                header_parts.append(city.country)
                lines = [', '.join(header_parts)]

                lines.append(f'owm --geo={lat},{lon} -t')
                lines.append(f'owm --lat={lat} --lon={lon} -t')

                owm_url = (
                    f'https://api.openweathermap.org/data/2.5/weather'
                    f'?lat={lat}&lon={lon}&units=metric&lang={lang}'
                    f'&appid={api_key}'
                )
                lines.append(f'\x1b[4mOpen Weather Map\x1b[24m: {owm_url}')
                lines.append(
                    f'\x1b[4mGoogle Map\x1b[24m: '
                    f'https://maps.google.com/?q={lat},{lon}'
                )

                if city_id:
                    lines.append(
                        f'\x1b[4mWidget Widget Plus\x1b[24m: '
                        f'https://old.openweathermap.org/city/{city_id}'
                    )
                    lines.append(f'\x1b[4mID\x1b[24m: {city_id}')

                blocks.append('\n'.join(lines))

            print('\n···\n'.join(blocks))
            return

        # ── Modo clima ──────────────────────────────────────────────────────
        UNITS = args.units

        # Flags que solo leen del caché — no necesitan descargar
        api_flags = {
            'description', 'feels_like', 'humidity', 'icon', 'pressure',
            'temp', 'toggle', 'visibility', 'wind', 'sunrise', 'sunset', 'id',
        }
        needs_download = any(getattr(args, f, False) for f in api_flags)
        online = not args.offline

        if needs_download or (not args.name and not args.last_update):
            weather = fetch_weather(
                lat=args.lat,
                lon=args.lon,
                api_key=api_key,
                lang=lang,
                units='metric',
                cache_seconds=args.cache_seconds,
                terminal=args.terminal,
                online=online,
            )
        else:
            # Solo -n y/o --last-update: leer del caché
            cache_path = build_cache_path(args.lat, args.lon, lang)
            if not cache_path.exists():
                raise OWMError(msg(lang, 'cache_no_data'))
            cached = read_cache(cache_path)
            if cached is None:
                raise OWMError(msg(lang, 'cache_no_data'))
            weather = Weather.from_api(cached, lang)

        def toggle_output():
            second_unit = int(time()) % 10
            temp, fl = round(weather.temperature), round(weather.feels_like)
            if second_unit >= 5 and temp != fl:
                return f'⇄{temperature(weather.feels_like, UNITS)}'
            else:
                return f'T{temperature(weather.temperature, UNITS)}'

        output_map = {
            '--temp':        lambda: temperature(
                             weather.temperature, UNITS, lang),
            '-t':            lambda: temperature(
                             weather.temperature, UNITS, lang),
            '--toggle':      toggle_output,
            '-T':            toggle_output,
            '--feels-like':  lambda: temperature(
                             weather.feels_like, UNITS, lang),
            '-l':            lambda: temperature(
                             weather.feels_like, UNITS, lang),
            '--desc-cap':    lambda: weather.description.capitalize(),
            '-D':            lambda: weather.description.capitalize(),
            '--description': lambda: weather.description,
            '-d':            lambda: weather.description,
            '--humidity':    lambda: f'{weather.humidity}%',
            '-u':            lambda: f'{weather.humidity}%',
            '--pressure':    lambda: pressure(weather.pressure, UNITS, lang),
            '-p':            lambda: pressure(weather.pressure, UNITS, lang),
            '--wind':        lambda: (
                             f'{wind(weather.wind_speed, UNITS, lang)}'
                             f' {weather.wind_direction(lang)}'),
            '-w':            lambda: (
                             f'{wind(weather.wind_speed, UNITS, lang)}'
                             f' {weather.wind_direction(lang)}'),
            '--visibility':  lambda: (
                             str(visibility(weather.visibility, UNITS, lang))
                             if weather.visibility is not None else 'N/A'),
            '-b':            lambda: (
                             str(visibility(weather.visibility, UNITS, lang))
                             if weather.visibility is not None else 'N/A'),
            '--icon':        lambda: icons(weather.icon),
            '-i':            lambda: icons(weather.icon),
            '--icon-emoji':  lambda: icons(weather.icon, is_emoji=True),
            '-I':            lambda: icons(weather.icon, is_emoji=True),
            '--name':        lambda: weather.city_name,
            '-n':            lambda: weather.city_name,
            '--id':          lambda: (
                             str(weather.city_id)
                             if weather.city_id is not None else 'N/A'),
            '--sunrise':     lambda: weather.sunrise_str,
            '-r':            lambda: weather.sunrise_str,
            '--sunset':      lambda: weather.sunset_str,
            '-s':            lambda: weather.sunset_str,
            '--last-update': lambda: (
                             _fmt_last_update(
                                 build_cache_path(args.lat, args.lon, lang),
                                 UNITS
                             )
                             if build_cache_path(
                                 args.lat, args.lon, lang
                             ).exists()
                             else msg(lang, 'cache_no_data')),
            '--wind-speed':  lambda: str(convert(
                             weather.wind_speed, 'wind_speed', UNITS)),
            '--wind-deg':    lambda: str(weather.wind_deg)
                             if weather.wind_deg is not None else 'N/A',
        }

        # Variantes sin formato para --raw
        if args.raw:
            output_map.update({
                '--temp':        lambda: str(convert(
                                     weather.temperature, 'temp', UNITS)),
                '-t':            lambda: str(convert(
                                     weather.temperature, 'temp', UNITS)),
                '--feels-like':  lambda: str(convert(
                                     weather.feels_like, 'feels-like', UNITS)),
                '-l':            lambda: str(convert(
                                     weather.feels_like, 'feels-like', UNITS)),
                '--humidity':    lambda: str(weather.humidity),
                '-u':            lambda: str(weather.humidity),
                '--pressure':    lambda: str(convert(
                                     weather.pressure, 'pressure', UNITS)),
                '-p':            lambda: str(convert(
                                     weather.pressure, 'pressure', UNITS)),
                '--visibility':  lambda: str(convert(
                                     weather.visibility, 'visibility', UNITS))
                                 if weather.visibility is not None else 'N/A',
                '-b':            lambda: str(convert(
                                     weather.visibility, 'visibility', UNITS))
                                 if weather.visibility is not None else 'N/A',
            })

        # Aliases para evitar duplicados
        aliases = {
            '-t':            '--temp',
            '--temp':        '-t',
            '-T':            '--toggle',
            '--toggle':      '-T',
            '-l':            '--feels-like',
            '--feels-like':  '-l',
            '-D':            '--desc-cap',
            '--desc-cap':    '-D',
            '-d':            '--description',
            '--description': '-d',
            '-u':            '--humidity',
            '--humidity':    '-u',
            '-p':            '--pressure',
            '--pressure':    '-p',
            '-w':            '--wind',
            '--wind':        '-w',
            '-b':            '--visibility',
            '--visibility':  '-b',
            '-i':            '--icon',
            '--icon':        '-i',
            '-I':            '--icon-emoji',
            '--icon-emoji':  '-I',
            '-n':            '--name',
            '--name':        '-n',
            '-r':            '--sunrise',
            '--sunrise':     '-r',
            '-s':            '--sunset',
            '--sunset':      '-s',
        }

        seen = set()
        outputs = []
        icon_is_emoji = False

        # Flags que se excluyen mutuamente
        exclusions = {
            '-T':            {'-t', '--temp', '-l', '--feels-like'},
            '--toggle':      {'-t', '--temp', '-l', '--feels-like'},
            '-t':            {'-T', '--toggle'},
            '--temp':        {'-T', '--toggle'},
            '-l':            {'-T', '--toggle'},
            '--feels-like':  {'-T', '--toggle'},
            '-D':            {'-d', '--description'},
            '--desc-cap':    {'-d', '--description'},
            '-d':            {'-D', '--desc-cap'},
            '--description': {'-D', '--desc-cap'},
            '-i':            {'-I', '--icon-emoji'},
            '--icon':        {'-I', '--icon-emoji'},
            '-I':            {'-i', '--icon'},
            '--icon-emoji':  {'-i', '--icon'},
        }

        for arg in argv[1:]:
            if not arg.startswith('-'):
                outputs.append(('literal', arg))
                continue

            # Expandir flags combinados tipo -tuw → -t -u -w
            if not arg.startswith('--') and len(arg) > 2:
                expanded = [f'-{c}' for c in arg[1:]]
            else:
                expanded = [arg]

            for key in expanded:
                key = key.split('=')[0]
                if key in output_map and key not in seen:
                    seen.add(key)
                    seen.add(aliases.get(key, key))
                    seen.update(exclusions.get(key, set()))
                    if key in ('-I', '--icon-emoji'):
                        icon_is_emoji = True
                    outputs.append(('value', output_map[key]()))

        if outputs:
            # Resolver text-prev y text-next
            if args.text_prev or args.text_next:
                merged = []
                for j, item in enumerate(outputs):
                    kind, val = item
                    if kind == 'literal':
                        # text-prev: literal se pega al value siguiente
                        if args.text_prev and j + 1 < len(outputs):
                            nxt_kind, nxt_val = outputs[j + 1]
                            if nxt_kind == 'value':
                                outputs[j + 1] = ('value', f'{val}{nxt_val}')
                                continue
                        # text-next: literal se pega al value anterior
                        if args.text_next and j > 0:
                            prev_kind, prev_val = merged[-1]
                            if prev_kind == 'value':
                                merged[-1] = ('value', f'{prev_val}{val}')
                                continue
                    merged.append(item)
                outputs = merged

            # Extraer solo los valores
            flat = [val for _, val in outputs]

            # Aplicar --icon-prev / --icon-next si hay ícono
            icon_keys = {'--icon', '-i', '--icon-emoji', '-I'}
            icon_in_outputs = any(k in seen for k in icon_keys)
            if icon_in_outputs and (args.icon_prev or args.icon_next):
                icon_val = icons(weather.icon, is_emoji=icon_is_emoji)
                try:
                    icon_idx = flat.index(icon_val)
                except ValueError:
                    icon_idx = None

                if icon_idx is not None:
                    flat.pop(icon_idx)
                    if args.icon_prev and args.icon_next:
                        if icon_idx > 0 and icon_idx <= len(flat):
                            prev = flat[icon_idx - 1]
                            nxt = (flat[icon_idx]
                                   if icon_idx < len(flat) else None)
                            if nxt is not None:
                                flat.pop(icon_idx - 1)
                                flat.insert(icon_idx - 1,
                                            f'{prev} {icon_val} {nxt}')
                    elif args.icon_prev:
                        if icon_idx < len(flat):
                            flat[icon_idx] = f'{icon_val} {flat[icon_idx]}'
                        else:
                            flat.append(icon_val)
                    elif args.icon_next:
                        if icon_idx > 0:
                            flat[icon_idx - 1] = (
                                f'{flat[icon_idx - 1]} {icon_val}'
                            )
                        else:
                            flat.insert(0, icon_val)

            print(args.space.join(flat))
        else:
            default_report(weather, lang, UNITS)

    except OWMError as exc:
        print(exc)
        exit(1)
    except KeyboardInterrupt:
        print()
        exit(0)
