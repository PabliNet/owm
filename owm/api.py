from owm.i18n import msg
from owm.env import get_env


def get_api_key(cli_key: str | None, lang: str) -> str:
    if cli_key:
        return cli_key

    env_key = get_env('OWM_API_KEY')
    if env_key:
        return env_key

    raise ValueError(msg(lang, 'api_key_required'))
