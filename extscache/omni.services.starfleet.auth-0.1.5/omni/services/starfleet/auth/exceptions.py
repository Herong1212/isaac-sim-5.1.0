class BaseTokenExchangeError(Exception):
    """ Base class to use for Token exchange errors
    """


class StarfleetTokenExchangeError(BaseTokenExchangeError):
    """ Raised when Starfleet token exchange error occurs
    """
    def __init__(self, msg='Failed to exchange Starfleet session token', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class LauncherUnavailableError(Exception):
    """ Raised when the Launcher is not running but needed for authentication
    """
