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

        for champion in cls.champions.values():
            if cls.remove_punctuation(champion["name"]).casefold().replace(
                " ", ""
            ) == cls.remove_punctuation(name).casefold().replace(" ", ""):
                return champion["key"]

    @classmethod
    @lru_cache()
    def name_for_id(cls, champion_id: str) -> Optional[str]:
        """
        Finds the name for a champion given its id
        Returns the name, None if not found

        champion_id - id of champion
        """

        for champion in cls.champions.values():
            if champion["key"] == champion_id:
                return champion["name"]

    @classmethod
    @lru_cache()
    def correct_name(cls, name: str) -> Optional[str]:
        """
        Corrects the champion name given a name missing spaces, capital letters, or punctuation
        """

        return cls.name_for_id(cls.id_for_name(name))

    @classmethod
    @lru_cache()
    def alternate_name_for_id(cls, champion_id: str) -> Optional[str]:
        """
        Finds the alternate name for a champion given its id
            (eg. Miss Fortune is "MissFortune", Kog'Maw is "KogMaw", Wukong is "MonkeyKing")
        Returns the alternate name, None if not found

        champion_id - id of champion
        """

        for champion in cls.champions.values():
            if champion["key"] == champion_id:
                return champion["id"]

    @classmethod
    @lru_cache()
    def id_for_alternate_name(cls, alternate_name: str) -> Optional[str]:
        """
        Finds the id for a champion given its alternate name
            (eg. Miss Fortune is "MissFortune", Kog'Maw is "KogMaw", Wukong is "MonkeyKing")
        Returns the id, None if not found

        alternate_name - alternate_name of champion
        """

        for champion in cls.champions.values():
            if (
                cls.remove_punctuation(champion["id"]).casefold()
                == cls.remove_punctuation(alternate_name).casefold()
            ):
                return champion["key"]

    @classmethod
    @lru_cache()
    def square_asset_url(cls, alternate_name: str) -> Optional[str]:
        """
        Returns the url for the square asset of the champion given its alternate name
        """

        return f"http://ddragon.leagueoflegends.com/cdn/{Patches.get_current_patch()}/img/champion/{alternate_name}.png"

    @staticmethod
    @lru_cache()
    def remove_punctuation(text: str) -> str:
        """
        Removes punctuation from a string

        text - str to remove punctuation from
        """

        return text.translate(str.maketrans("", "", string.punctuation))
