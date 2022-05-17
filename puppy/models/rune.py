from typing import List, Dict, Any, Optional


class RuneList:
    """
    A list of runes (list of rune integer ids)
    """

    def __init__(
        self,
        runes: List[int],
        rune_page_name: str,
        primary_style: int,
        secondary_style: int,
        active: bool,
    ):
        """
        runes - list of integer runes ids to store
        rune_page_name - name of the rune page
        primary_style - style of primary rune tree
        secondary_style - style of secondary rune tree
        active - whether the rune page should be the current active rune page
        """

        self.runes = runes
        self.rune_page_name = rune_page_name
        self.primary_style = primary_style
        self.secondary_style = secondary_style
        self.active = active

    def __iter__(self):
        return iter(self.runes)

    def build(self) -> Dict[str, Any]:
        """
        Builds an item set using given item blocks 
            that can be passed to the league client
        """

        return {
            "autoModifiedSelections": [],
            "id": 0,
            "isDeletable": True,
            "isEditable": True,
            "isValid": True,
            "lastModified": 0,
            "order": 0,
            # edit the ones below
            "name": self.rune_page_name,
            "current": self.active,
            "isActive": self.active,
            "primaryStyleId": self.primary_style,
            "subStyleId": self.secondary_style,
            "selectedPerkIds": self.runes,
        }


# class Shard:
#     """
#     Represents a rune shard
#     """

#     def __init__(self, ugg_shard_name: str, shard_id: int):
#         """
#         ugg_shard_name - u.gg name for the shard
#         shard_id - int id of shard
#         """

#         self.ugg_shard_name = ugg_shard_name
#         self.shard_id = shard_id


# class ShardList:
#     """
#     A list of shards
#     """

#     def __init__(self, shards: List[Shard]):
#         """
#         shards - a list of shards
#         """

#         self.shards = shards

#     def get_shard_by_ugg_name(self, ugg_shard_name: str) -> Optional[Shard]:
#         """
#         Returns the shard with the given name
#         Returns None if the shard with the given name does not exist
#         """

#         for shard in self:
#             if shard.ugg_shard_name == ugg_shard_name:
#                 return shard

#     def __iter__(self):
#         return iter(self.shards)
