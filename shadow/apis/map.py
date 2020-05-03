from functools import lru_cache
from typing import Optional

import requests

from .patches import Patches


class Map:
    """
    Manipulation of static map data
    """

    MAP_URL = f"http://ddragon.leagueoflegends.com/cdn/{Patches.get_current_patch()}/data/en_US/map.json"
    maps = requests.get(MAP_URL).json()

    @classmethod
    @lru_cache()
    def id_for_name(cls, name: str) -> Optional[str]:
        """
        Finds the id for a map given its name
        Returns the id, None if not found

        name - full name of map
        """

        # name map is reserved
        for league_map in cls.maps["data"].values():
            if league_map["MapName"].casefold() == name.casefold():
                return league_map["MapId"]

    @classmethod
    @lru_cache()
    def name_for_id(cls, map_id: str) -> Optional[str]:
        """
        Finds the name for a map given its id
        Returns the name, None if not found

        map_id - id of map
        """

        # name map is reserved
        for league_map in cls.maps["data"].values():
            if league_map["MapId"] == map_id:
                return league_map["MapName"]