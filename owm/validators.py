from owm.i18n import msg


class Validator:
    def __init__(self, lang: str):
        self.lang = lang

    # =========================
    # Public API
    # =========================

    def validate_args(self, args):
        self._validate_api_key(args)
        self._validate_location(args)
        self._normalize_location(args)
        self._validate_output_flags(args)
        return args

    # =========================
    # Validation
    # =========================

    def _validate_api_key(self, args):
        if not args.key:
            raise ValueError(msg(self.lang, 'api_key_required'))

    def _validate_location(self, args):
        if args.city:
            if args.geo or args.lat or args.lon:
                raise ValueError(msg(self.lang, 'city_conflict'))
            return

        if args.geo:
            if args.lat or args.lon:
                raise ValueError(msg(self.lang, 'geo_conflict'))
            return

        if args.lat or args.lon:
            if not (args.lat and args.lon):
                raise ValueError(msg(self.lang, 'lat_lon_together'))
            return

        raise ValueError(msg(self.lang, 'location_required'))

    def _validate_output_flags(self, args):
        output_flags = [
            args.description,
            args.feels_like,
            args.humidity,
            args.icon,
            args.pressure,
            args.temp,
            args.temp_feels_like,
            args.visibility,
            args.wind,
            args.sunrise,
            args.sunset,
            args.name,
            args.id,
        ]

        if args.city:
            if any(output_flags):
                raise ValueError(msg(self.lang, 'city_no_output'))
            return

        if not any(output_flags):
            raise ValueError(msg(self.lang, 'output_required'))

    # =========================
    # Normalization
    # =========================

    def _normalize_location(self, args):
        """
        Converts geo or lat/lon strings into normalized float lat/lon.
        After this call:
            args.lat and args.lon are floats
            args.geo is None
        """
        if args.geo:
            lat, lon = self._parse_geo(args.geo)
            args.lat = lat
            args.lon = lon
            args.geo = None
            return

        if args.lat and args.lon:
            args.lat = self._validate_lat(args.lat)
            args.lon = self._validate_lon(args.lon)

    # =========================
    # Coordinate helpers
    # =========================

    def _to_float(self, value):
        try:
            return float(value)
        except ValueError:
            raise ValueError(msg(self.lang, 'invalid_format'))

    def _validate_lat(self, lat):
        _lat = self._to_float(lat)
        if not -90 <= _lat <= 90:
            raise ValueError(msg(self.lang, 'lat_range'))
        return _lat

    def _validate_lon(self, lon):
        _lon = self._to_float(lon)
        if not -180 <= _lon <= 180:
            raise ValueError(msg(self.lang, 'lon_range'))
        return _lon

    def _parse_geo(self, geo):
        try:
            lat_str, lon_str = geo.split(',')
        except ValueError:
            raise ValueError(msg(self.lang, 'geo_format'))

        lat = self._validate_lat(lat_str)
        lon = self._validate_lon(lon_str)
        return lat, lon
