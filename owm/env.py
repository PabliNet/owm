from os import getenv


def get_env(key: str) -> str | None:
    value = getenv(key)
    if value:
        return value.strip()
    return None
