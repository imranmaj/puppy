from functools import lru_cache
from typing import Dict, List, Optional

import requests

from .patches import Patches


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
    def style_name_for_style_id(cls, style_id: int) -> Optional[str]:
        """
        Returns the name of the rune tree style given its id
        Returns None if it does not exist

        style_id - id of the rune tree style
        """

        for tree in cls.runes:
            if tree["id"] == style_id:
                return tree["name"]

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

    @classmethod
    @lru_cache()
    def id_for_name(cls, name: str) -> Optional[int]:
        """
        Finds the id for a rune given its name
        Returns the id, None if not found

        name - name of rune
        """

        for tree in cls.runes:
            for slot in tree["slots"]:
                for rune in slot["runes"]:
                    if rune["key"].casefold() == name.casefold():
                        return rune["id"]

    @classmethod
    @lru_cache()
    def name_for_id(cls, rune_id: int) -> Optional[str]:
        """
        Finds the name for a rune given its id
        Returns the name, None if not found

        rune_id - id of rune
        """

        for tree in cls.runes:
            for slot in tree["slots"]:
                for rune in slot["runes"]:
                    if rune["id"] == rune_id:
                        return rune["key"]

    @classmethod
    @lru_cache()
    def row_position_for_id(cls, rune_id: int) -> Optional[int]:
        """
        Finds the row position for a rune given its id
        Returns the row position, None if not found
        Row position is indexed starting at 1

        rune_id - id of rune
        """

        for tree in cls.runes:
            for slot in tree["slots"]:
                for i, rune in enumerate(slot["runes"]):
                    if rune["id"] == rune_id:
                        return i + 1

    @classmethod
    @lru_cache()
    def row_for_id(cls, rune_id: int) -> Optional[int]:
        """
        Finds the row for a rune in the tree given its id
        Returns the row, None if not found
        Row is indexed starting at 0

        rune_id - id of rune
        """

        for tree in cls.runes:
            for i, slot in enumerate(tree["slots"]):
                for rune in slot["runes"]:
                    if rune["id"] == rune_id:
                        return i