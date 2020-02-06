class LeagueProcessNotFoundError(Exception):
    def __init__(self, *args, **kwargs):
        DEFAULT = "Ensure a League client process exists"

        if args or kwargs:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(DEFAULT)

class UnsupportedPlatformError(Exception):
    def __init__(self, *args, **kwargs):
        DEFAULT = "Only macOS and Windows are supported"

        if args or kwargs:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(DEFAULT)