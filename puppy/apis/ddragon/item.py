from functools import lru_cache
from typing import Optional
import string

import requests

from .patches import Patches


def transform_name(name: str) -> str:
    """
    Transforms a string to lowercase and removes punctuation and whitespace
    """

    return name.casefold().translate(
        str.maketrans("", "", string.punctuation + string.whitespace)
    )


class Item:
    """
    Manipulation of static item data
    """

    ITEM_URL = f"http://ddragon.leagueoflegends.com/cdn/{Patches.get_current_patch()}/data/en_US/item.json"
    items = requests.get(ITEM_URL).json()
    id_name = {
        item_id: item_data["name"] for item_id, item_data in items["data"].items()
    }
    name_id = {
        transform_name(item_name): item_id for item_id, item_name in id_name.items()
    }

    @classmethod
    @lru_cache()
    def id_for_name(cls, name: str) -> Optional[str]:
        """
        Finds the id for an item given its name
        Returns the id, None if not found

        name - full name of item
        """

        return cls.name_id.get(transform_name(name))

    @classmethod
    @lru_cache()
    def name_for_id(cls, item_id: str) -> Optional[str]:
        """
        Finds the name for an item given its id
        Returns the name, None if not found

        item_id - id of item
        """

        return cls.id_name.get(item_id)
