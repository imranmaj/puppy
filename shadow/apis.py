import platform
import string
from functools import lru_cache
from typing import List, Dict, Optional, Any

import urllib3
import requests
from requests.exceptions import ConnectionError
from requests.models import Response
import psutil

from shadow.exceptions import LeagueProcessNotFoundError, UnsupportedPlatformError

class Lcu:
    """
    Lcu api connector
    """

    def __init__(self):

        # don't verify ssl
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        auth = Auth()

        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json"
        })
        self.session.auth = ("riot", auth.key)
        self.session.verify = False
        self.BASE_URL = f"https://127.0.0.1:{auth.port}/"

    def get(self, endpoint: List[str]) -> Response:
        """
        GETs an endpoint
        Returns requests response object

        endpoint - iterable that is joined to form the endpoint path
        """

        url = self.make_url(endpoint)
        return self.request("get", url)

    def delete(self, endpoint: List[str]) -> Response:
        """
        DELETEs to an endpoint
        Returns requests response object

        endpoint - iterable that is joined to form the endpoint path
        """

        url = self.make_url(endpoint)
        return self.request("delete", url)
        
    def post(self, endpoint: List[str], data: Any) -> Response:
        """
        POSTs to an endpoint
        Returns requests response object

        endpoint - iterable that is joined to form the endpoint path
        data - data to POST
        """

        url = self.make_url(endpoint)
        return self.request("post", url, json=data)

    def put(self, endpoint: List[str], data: Any) -> Response:
        """
        PUTS to an endpoint
        Returns requests response object

        endpoint - iterable that is joined to form the endpoint path
        data - data to PUT
        """

        url = self.make_url(endpoint)
        return self.request("put", url, json=data)

    def patch(self, endpoint: List[str], data: Any) -> Response:
        """
        PATCHes to an endpoint
        Returns requests response object

        endpoint - iterable that is joined to form the endpoint path
        data - data to PATCH
        """

        url = self.make_url(endpoint)
        return self.request("patch", url, json=data)

    def make_url(self, endpoint: List[str]) -> str:
        """
        Constructs a url from an endpoint iterable
        Returns url string

        endpoint - iterable that is joined to form the endpoint path
        """

        return self.BASE_URL + "/".join(endpoint)

    def request(self, *args, **kwargs) -> Response:
        """
        Performs an http request

        Returns requests response object
        """

        try:
            return self.session.request(*args, **kwargs)
        except ConnectionError:
            raise LeagueProcessNotFoundError

    def get_summoner_id(self):
        """
        Returns the summoner id for the current summoner
        """

        return self.get(["lol-summoner", "v1", "current-summoner"]).json()["summonerId"]

class Patches:
    """
    Manipulation of static patch data
    """

    @classmethod
    def get_all_patches(cls) -> List[str]:
        """
        Returns list of all patches
        """
        PATCHES_URL = "http://ddragon.leagueoflegends.com/api/versions.json"
        return requests.get(PATCHES_URL).json()

    @classmethod
    def get_current_patch(cls) -> str:
        """
        Returns current patch
        """

        return cls.get_all_patches()[0]

    @classmethod
    def get_format_underscore_previous_patch(cls) -> str:
        """
        Returns the previous patch with underscores instead of periods
        Uses only the first 2 parts of the patch name
        """

        previous_patch = cls.get_all_patches()[1]
        return "_".join(previous_patch.split(".")[:2])

class Champions:
    """
    Manipulation of static champion data
    """

    CHAMPIONS_URL = f"http://ddragon.leagueoflegends.com/cdn/{Patches.get_current_patch()}/data/en_US/champion.json"
    champions = requests.get(CHAMPIONS_URL).json()["data"]

    @classmethod
    @lru_cache()
    def id_for_name(cls, name: str) -> Optional[str]:
        """
        Finds the id for a champion given its name
        Returns the id, None if not found

        name - full name of champion
        """

        try:
            return cls.champions[cls.remove_punctuation(name).capitalize()]["key"]
        except KeyError:
            return

    @classmethod
    @lru_cache()
    def name_for_id(cls, champion_id: str) -> Optional[str]:
        """
        Finds the name for a champion given its id
        Returns the name, None if not found

        champion_id - id of champion
        """

        for champion_name in cls.champions:
            if cls.champions[champion_name]["key"] == champion_id:
                return champion_name

    @staticmethod
    @lru_cache()
    def remove_punctuation(text: str) -> str:
        """
        Removes punctuation from a string

        text - str to remove punctuation from
        """

        return text.translate(str.maketrans("", "", string.punctuation))

class Runes:
    """
    Manipulation of static runes data
    """

    RUNES_URL = f"http://ddragon.leagueoflegends.com/cdn/{Patches.get_current_patch()}/data/en_US/runesReforged.json"
    runes = requests.get(RUNES_URL).json()

    @classmethod
    @lru_cache()
    def get_all_rune_trees(cls) -> Dict[int, List[int]]:
        """
        Returns dict of all rune trees:
        {
            <tree style>: [
                <list of runes>
            ]
        }
        """

        all_rune_trees = dict()
        for tree in cls.runes:
            tree_style = tree["id"]
            all_rune_trees[tree_style] = []

            slots = tree["slots"]
            for slot in slots:
                runes = slot["runes"]
                for rune in runes:
                    all_rune_trees[tree_style].append(rune["id"])

        return all_rune_trees

    @classmethod
    @lru_cache()
    def style_for_rune(cls, rune: int) -> Optional[int]:
        """
        Returns the integer id for the rune tree style of a rune
            given its id
        Returns None if it does not exist
        """

        all_rune_trees = cls.get_all_rune_trees()
        for tree_style, runes in all_rune_trees.items():
            if rune in runes:
                return tree_style

    @classmethod
    @lru_cache()
    def sort_runes(cls, runes: List[int], primary_style: int, secondary_style: int) -> List[int]:
        """
        Sorts list of runes into the correct order
        Runes are ordered by primary and secondary, then by order in their respective tree

        primary_style - style of primary runes in runes list
        secondary_style - style of secondary runes in runes lists
        """

        # find primary and secondary runes
        all_rune_trees = cls.get_all_rune_trees()
        primary_runes = [rune for rune in runes if cls.style_for_rune(rune) == primary_style]
        secondary_runes = [rune for rune in runes if cls.style_for_rune(rune) == secondary_style]

        # sort both primary and secondary runes by order in tree
        sorted_primary_runes = sorted(primary_runes, key=lambda i: all_rune_trees[primary_style].index(i))
        sorted_secondary_runes = sorted(secondary_runes, key=lambda i: all_rune_trees[secondary_style].index(i))

        return sorted_primary_runes + sorted_secondary_runes

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
