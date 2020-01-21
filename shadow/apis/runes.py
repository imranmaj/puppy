from functools import lru_cache
from typing import Dict, List, Optional

import requests

from shadow.apis.patches import Patches


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