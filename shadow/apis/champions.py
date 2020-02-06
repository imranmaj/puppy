import string
from functools import lru_cache
from typing import Optional

import requests

from .patches import Patches


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