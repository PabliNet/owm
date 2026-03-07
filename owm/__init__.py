from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version('owm')
except PackageNotFoundError:
    __version__ = 'unknown'
