def n(value, digits=1):
    if value % 1 == 0:
        return int(value)
    return '{:.{}f}'.format(value, digits)

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

temperature = lambda v, u: (
    f'{n(v)}°C' if u == 'metric' else f'{n(v * 9/5 + 32)}°F'
)

pressure = lambda v, u: (
    f'{n(v, 2)}hPa' if u == 'metric' else f'{n(v * 0.02953, 2)}inHg'
)

visibility = lambda v, u: (
    f'{n(v / 1000)}Km' if u == 'metric' or v == 10000
    else f'{n(v * 0.00062137, 2)}mi'
)

wind = lambda v, u: (
    f'{n(v * 3.6, 2)}Km/h' if u == 'metric' else f'{n(v * 2.23694, 2)}mph'
)
