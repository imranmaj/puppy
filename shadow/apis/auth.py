import platform
from functools import lru_cache
from typing import Dict

import psutil

from shadow.exceptions import UnsupportedPlatformError, LeagueProcessNotFoundError


class Auth:
    """
    Lcu api authorization
    """

    def __init__(self):
        plat = platform.system()
        if plat == "Windows":
            process_name = "LeagueClientUx.exe"
        elif plat == "Darwin":
            process_name = "LeagueClientUx"
        else:
            raise UnsupportedPlatformError

        for process in psutil.process_iter(attrs=["name"]):
            if process.info["name"] == process_name:
                args = self.parse_commandline_args(tuple(process.cmdline()))
                self.port = args["app-port"]
                self.key = args["remoting-auth-token"]
                break
        else:
            raise LeagueProcessNotFoundError

    @staticmethod
    @lru_cache()
    def parse_commandline_args(commandline_args: tuple) -> Dict[str, str]:
        """
        Parses key-value command line arguments
        """

        parsed_commandline_args = {}
        for arg in commandline_args:
            if "=" in arg:
                key, val = arg.lstrip("-").split("=")
                parsed_commandline_args[key] = val
        return parsed_commandline_args