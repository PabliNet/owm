class OWMError(Exception):
    """Base exception for the application."""
    pass


class CityNotFoundError(OWMError):
    """Raised when city geocoding returns no results."""
    pass
