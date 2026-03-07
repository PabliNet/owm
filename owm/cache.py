from os import fsync
from getpass import getuser
from pathlib import Path
from tempfile import gettempdir
from time import time
from json import dump, JSONDecodeError, load

_cache_dir = None


def get_cache_dir() -> Path:
    global _cache_dir
    if _cache_dir is None:
        _cache_dir = Path(gettempdir()) / f'.owm_{getuser()}'
        _cache_dir.mkdir(mode=0o700, exist_ok=True)
    return _cache_dir


def build_filename(lat, lon, units, lang) -> str:
    lat = f'{float(lat):.4f}'
    lon = f'{float(lon):.4f}'
    return f'{lat}_{lon}_{units}_{lang}.json'


def build_cache_path(lat, lon, lang) -> Path:
    return get_cache_dir() / build_filename(lat, lon, lang)


def is_cache_valid(path: Path, max_age: int) -> bool:
    if not path.exists():
        return False
    if max_age == 0:
        return False
    age = time() - path.stat().st_mtime
    return age < max_age


def read_cache(path: Path):
    try:
        with path.open() as f:
            return load(f)
    except (JSONDecodeError, OSError):
        path.unlink(missing_ok=True)
        return None


def write_cache(path: Path, data: dict) -> None:
    tmp = path.with_suffix('.tmp')
    with tmp.open('w') as f:
        dump(data, f)
        f.flush()
        fsync(f.fileno())
    tmp.replace(path)
