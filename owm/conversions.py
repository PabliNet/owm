def n(value, digits=1, unit='°C', lang='en'):
    '''Formatea un número con unidad, separadores según idioma.'''
    if value % 1 == 0:
        num = int(value)
        if lang != 'en':
            formatted = f'{num:,}'.replace(',', '.')
        else:
            formatted = f'{num:,}'
    else:
        if lang != 'en':
            formatted = '{:.{}f}'.format(value, digits).replace('.', ',')
        else:
            formatted = '{:.{}f}'.format(value, digits)
    return f'{formatted}{unit}'


def convert(value, key, unit='metric'):
    '''Convierte un valor numérico sin formato.'''
    if key in ('temp', 'feels-like'):
        if unit == 'metric':
            return value
        return value * 9 / 5 + 32
    elif key == 'pressure':
        if unit == 'metric':
            return value
        return value * 0.02953
    elif key == 'visibility':
        if unit == 'metric':
            return value / 1000
        return value * 0.00062137
    elif key == 'wind_speed':
        if unit == 'metric':
            return value * 3.6
        return value * 2.23694


def icons(code, is_emoji=False):
    if is_emoji:
        _icons = {
            '01d': '☀️',  '01n': '🌙',
            '02d': '🌤️', '02n': '🌙',
            '03d': '⛅',  '03n': '☁️',
            '04d': '☁️',  '04n': '☁️',
            '09d': '🌧️', '09n': '🌧️',
            '10d': '🌦️', '10n': '🌧️',
            '11d': '⛈️', '11n': '⛈️',
            '13d': '❄️',  '13n': '❄️',
            '50d': '🌫️', '50n': '🌫️',
        }
    else:
        _icons = {
            '01d': '☀',  '01n': '☾',
            '02d': '☀☁', '02n': '☁☾',
            '03d': '☁',  '03n': '☁',
            '04d': '☁☁', '04n': '☁☁',
            '09d': '☂',  '09n': '☂',
            '10d': '☀☂', '10n': '☾☂',
            '11d': '⚡',  '11n': '⚡',
            '13d': '❄',  '13n': '❄',
            '50d': '≋',  '50n': '≋',
        }
    return _icons.get(code, '?')


def temperature(v, u, lang='en'):
    if u == 'metric':
        return n(v, 1, '°C', lang)
    return n(v * 9 / 5 + 32, 1, '°F', lang)


def pressure(v, u, lang='en'):
    if u == 'metric':
        return n(v, 2, 'hPa', lang)
    return n(v * 0.02953, 2, 'inHg', lang)


def visibility(v, u, lang='en'):
    if u == 'metric':
        return n(v / 1000, 1, 'Km', lang)
    return n(v * 0.00062137, 2, 'mi', lang)


def wind(v, u, lang='en'):
    if u == 'metric':
        return n(v * 3.6, 2, 'Km/h', lang)
    return n(v * 2.23694, 2, 'mph', lang)
