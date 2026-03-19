from time import time
from argparse import ArgumentParser, ArgumentTypeError, HelpFormatter
from datetime import datetime
from pathlib import Path
from re import fullmatch, split as re_split, sub as re_sub
from shutil import get_terminal_size, rmtree
from sys import argv, exit
from json import dumps, loads, JSONDecodeError

from owm import __version__
from owm.i18n import msg
from owm.weather import get_weather
from owm.api import get_api_key
from owm.cache import build_cache_path, get_cache_dir
from owm.geocode import city_name_to_list
from owm.exceptions import OWMError
from owm.env import get_env
from owm.validators import Validator
from owm.conversions import icons, pressure, temperature, visibility, wind


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
    return (get_env('LANG') or 'en')[:2]


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
    local.add_argument('--add-city', default=None,
                       dest='add_city', help=m('help_add_city'))
    local.add_argument('--alias', default=None, help=m('help_alias'))
    local.add_argument('--city', default=None, help=m('help_city'))
    local.add_argument('--geo', type=parse_geo, default=None,
                       help=m('help_geo'))
    local.add_argument('--lat', type=str, default=None, help=m('help_lat'))
    local.add_argument('--list', action='store_true',
                       dest='list_cities', help=m('help_list'))
    local.add_argument('--list-alias', action='store_true',
                       dest='list_alias', help=m('help_list_alias'))
    local.add_argument('--lon', type=str, default=None, help=m('help_lon'))
    local.add_argument('--order', default=None, help=m('help_order'))
    local.add_argument('--remove-city', default=None,
                       dest='remove_city', help=m('help_remove_city'))

    # Configuración
    config = parser.add_argument_group(m('group_config'))
    config.add_argument('--clear-cache', action='store_true',
                        dest='clear_cache', help=m('help_clear_cache'))
    config.add_argument('--lang', default=None, help=m('help_lang'))
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
    output.add_argument('-T', '--toggle', action='store_true',
                        dest='toggle', help=m('help_toggle'))
    output.add_argument('-u', '--humidity', action='store_true',
                        help=m('help_humidity'))
    output.add_argument('-w', '--wind', action='store_true',
                        help=m('help_wind'))

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
        api_key = get_api_key(args.key, lang)

        # ── Modo agregar ciudad ─────────────────────────────────────────────
        if args.add_city:
            add_city_cmd(
                city_name=args.add_city,
                alias=args.alias,
                api_key=api_key,
                lang=lang,
            )
            return

        # ── Modo listar ciudades ────────────────────────────────────────────
        if args.list_cities:
            list_cities_cmd(lang)
            return

        # ── Modo listar aliases ─────────────────────────────────────────────
        if args.list_alias:
            list_alias_cmd(lang)
            return

        # ── Modo eliminar ciudad ────────────────────────────────────────────
        if args.remove_city:
            remove_city_cmd(args.remove_city, lang)
            return

        # ── Modo reordenar ciudades ─────────────────────────────────────────
        if args.order:
            order_cities_cmd(args.order, lang)
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

        weather = get_weather(
            lat=args.lat,
            lon=args.lon,
            api_key=api_key,
            lang=lang,
            units='metric',
            cache_seconds=args.cache_seconds,
            terminal=args.terminal,
        )

        def toggle_output():
            second_unit = int(time()) % 10
            temp, fl = round(weather.temperature), round(weather.feels_like)
            if second_unit >= 5 and temp != fl:
                return f'⇄{temperature(weather.feels_like, UNITS)}'
            else:
                return f'T{temperature(weather.temperature, UNITS)}'

        output_map = {
            '--temp':        lambda: temperature(weather.temperature, UNITS),
            '-t':            lambda: temperature(weather.temperature, UNITS),
            '--toggle':      toggle_output,
            '-T':            toggle_output,
            '--feels-like':  lambda: temperature(weather.feels_like, UNITS),
            '-l':            lambda: temperature(weather.feels_like, UNITS),
            '--desc-cap':    lambda: weather.description.capitalize(),
            '-D':            lambda: weather.description.capitalize(),
            '--description': lambda: weather.description,
            '-d':            lambda: weather.description,
            '--humidity':    lambda: f'{weather.humidity}%',
            '-u':            lambda: f'{weather.humidity}%',
            '--pressure':    lambda: pressure(weather.pressure, UNITS),
            '-p':            lambda: pressure(weather.pressure, UNITS),
            '--wind':        lambda: (
                             f'{wind(weather.wind_speed, UNITS)}'
                             f' {weather.wind_direction(lang)}'),
            '-w':            lambda: (
                             f'{wind(weather.wind_speed, UNITS)}'
                             f' {weather.wind_direction(lang)}'),
            '--visibility':  lambda: (
                             str(visibility(weather.visibility, UNITS)
                             if weather.visibility is not None else 'N/A')),
            '-b':            lambda: (
                             str(visibility(weather.visibility, UNITS)
                             if weather.visibility is not None else 'N/A')),
            '--icon':        lambda: icons(weather.icon),
            '-i':            lambda: icons(weather.icon),
            '--name':        lambda: weather.city_name,
            '-n':            lambda: weather.city_name,
            '--id':          lambda: (
                             str(weather.city_id)
                             if weather.city_id is not None else 'N/A'),
            '--sunrise':     lambda: weather.sunrise_str,
            '-r':            lambda: weather.sunrise_str,
            '--sunset':      lambda: weather.sunset_str,
            '-s':            lambda: weather.sunset_str,
            '--last-update': lambda: datetime.fromtimestamp(
                             build_cache_path(
                                 args.lat, args.lon, lang
                             ).stat().st_mtime
                             ).strftime('%Y-%m-%d %H:%M:%S')
                             if build_cache_path(
                                 args.lat, args.lon, lang
                             ).exists()
                             else msg(lang, 'cache_no_data'),
        }

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
            '-n':            '--name',
            '--name':        '-n',
            '-r':            '--sunrise',
            '--sunrise':     '-r',
            '-s':            '--sunset',
            '--sunset':      '-s',
        }

        seen = set()
        outputs = []

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
        }

        for arg in argv[1:]:
            if not arg.startswith('-'):
                outputs.append(arg)
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
                    outputs.append(output_map[key]())

        if outputs:
            # Aplicar --icon-prev / --icon-next si hay ícono
            icon_keys = {'--icon', '-i'}
            icon_in_outputs = any(
                k in seen for k in icon_keys
            )
            if icon_in_outputs and (args.icon_prev or args.icon_next):
                # Encontrar posición del ícono en outputs
                # El ícono es el valor del weather.icon ya evaluado
                icon_val = icons(weather.icon)
                try:
                    icon_idx = outputs.index(icon_val)
                except ValueError:
                    icon_idx = None

                if icon_idx is not None:
                    outputs.pop(icon_idx)
                    # Ajustar índice si icon_prev e icon_next
                    # ambos activos: pegar entre anterior y siguiente
                    if args.icon_prev and args.icon_next:
                        # pegar al anterior y al siguiente
                        if icon_idx > 0 and icon_idx <= len(outputs):
                            prev = outputs[icon_idx - 1]
                            nxt = (outputs[icon_idx]
                                   if icon_idx < len(outputs) else None)
                            outputs[icon_idx - 1] = f'{prev} {icon_val}'
                            if nxt is not None:
                                outputs[icon_idx] = f'{icon_val} {nxt}'
                                outputs.pop(icon_idx - 1)
                                outputs[icon_idx - 1] = (
                                    f'{prev} {icon_val} {nxt}'
                                )
                    elif args.icon_prev:
                        # pegar al siguiente
                        if icon_idx < len(outputs):
                            outputs[icon_idx] = (
                                f'{icon_val} {outputs[icon_idx]}'
                            )
                        else:
                            outputs.append(icon_val)
                    elif args.icon_next:
                        # pegar al anterior
                        if icon_idx > 0:
                            outputs[icon_idx - 1] = (
                                f'{outputs[icon_idx - 1]} {icon_val}'
                            )
                        else:
                            outputs.insert(0, icon_val)

            print(args.space.join(outputs))
        else:
            default_report(weather, lang, UNITS)

    except OWMError as exc:
        print(exc)
        exit(1)
    except KeyboardInterrupt:
        print()
        exit(0)
