from gettext import gettext, GNUTranslations, translation
from pathlib import Path

_LOCALEDIR = Path(__file__).parent / 'locales'
_FALLBACK_LANG = 'en'
_translations: dict = {}


def _get_translation(lang: str) -> GNUTranslations:
    if lang not in _translations:
        try:
            _translations[lang] = translation(
                'owm', localedir=_LOCALEDIR, languages=[lang]
            )
        except FileNotFoundError:
            try:
                _translations[lang] = translation(
                    'owm', localedir=Path('/usr/share/locale'),
                    languages=[lang]
                )
            except FileNotFoundError:
                _translations[lang] = translation(
                    'owm', localedir=_LOCALEDIR, languages=[_FALLBACK_LANG]
                )
    return _translations[lang]

def msg(lang: str, key: str) -> str:
    return _get_translation(lang).gettext(key)
