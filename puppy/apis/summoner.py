from functools import lru_cache
from typing import Optional

import requests

from .patches import Patches


class Summoner:
    """
    Manipulation of static summoner spell data
    """

    SUMMONER_URL = f"http://ddragon.leagueoflegends.com/cdn/{Patches.get_current_patch()}/data/en_US/summoner.json"
    summoners = requests.get(SUMMONER_URL).json()

    @classmethod
    @lru_cache()
    def id_for_name(cls, name: str) -> Optional[str]:
        """
        Finds the id for a summoner spell given its name
        Returns the id, None if not found

        name - full name of summoner spell
        """

        for summoner in cls.summoners["data"].values():
            if summoner["name"].casefold() == name.casefold():
                return summoner["key"]

    @classmethod
    @lru_cache()
    def name_for_id(cls, summoner_id: str) -> Optional[str]:
        """
        Finds the name for a summoner spell given its id
        Returns the name, None if not found

        summoner_id - id of summoner spell
        """

        for summoner in cls.summoners["data"].values():
            if summoner["key"] == summoner_id:
                return summoner["name"]

    @classmethod
    @lru_cache()
    def alternate_name_for_id(cls, summoner_id: str) -> Optional[str]:
        """
        Finds the alternate name for a summoner spell given its id
        Returns the alternate name, None if not found

        summoner_id - id of summoner spell
        """

        for summoner in cls.summoners["data"].values():
            if summoner["key"] == summoner_id:
                return summoner["id"]

    @classmethod
    @lru_cache()
    def id_for_alternate_name(cls, alternate_name: str) -> Optional[str]:
        """
        Finds the id for a summoner spell given its alternate name
        Returns the id, None if not found

        alternate_name - alternate_name of summoner spell
        """

        for summoner in cls.summoners["data"].values():
            if summoner["id"] == alternate_name:
                return summoner["key"]

    @classmethod
    @lru_cache()
    def asset_url(cls, alternate_name: str) -> str:
        """
        Returns the url for the asset of the summoner given its alternate name
        """

        return f"http://ddragon.leagueoflegends.com/cdn/{Patches.get_current_patch()}/img/spell/{alternate_name}.png"
