from functools import lru_cache
from typing import Optional

import requests

from .patches import Patches


class Item:
    """
    Manipulation of static item data
    """

    ITEM_URL = f"http://ddragon.leagueoflegends.com/cdn/{Patches.get_current_patch()}/data/en_US/item.json"
    items = requests.get(ITEM_URL).json()

    @classmethod
    @lru_cache()
    def id_for_name(cls, name: str) -> Optional[str]:
        """
        Finds the id for an item given its name
        Returns the id, None if not found

        name - full name of item
        """

        for item_id, item in cls.items["data"].items():
            if item["name"].casefold() == name.casefold():
                return item_id

    @classmethod
    @lru_cache()
    def name_for_id(cls, item_id: str) -> Optional[str]:
        """
        Finds the name for an item given its id
        Returns the name, None if not found

        item_id - id of item
        """

        if item_id in cls.items["data"]:
            return cls.items["data"][item_id]["name"]
