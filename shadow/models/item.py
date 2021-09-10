from typing import List, Dict, Any


class ItemBlock:
    """
    Represents an item block
    """

    def __init__(self, items: List[int], block_name: str):
        """
        items - list of item ids
        block_name - name of item block
        """

        self.items = items
        self.block_name = block_name


class ItemSet:
    """
    Represents a full item set with multiple item blocks
    """

    def __init__(
        self,
        item_blocks: List[ItemBlock],
        item_set_name: str,
        champion_id: int,
        preferred_item_slots: Dict[str, int],
    ):
        """
        item_blocks - list of item blocks
        item_set_name - name of item set
        champion_id - integer id of champion
        """

        self.item_blocks = item_blocks
        self.item_set_name = item_set_name
        self.champion_id = champion_id
        self.preferred_item_slots = preferred_item_slots

    def build(self) -> Dict[str, Any]:
        """
        Builds an item set using given item blocks 
            that can be passed to the league client
        """

        parsed_blocks = []
        for item_block in self.item_blocks:
            parsed_items = []
            for item in item_block.items:
                parsed_items.append({"count": 1, "id": str(item)})

            parsed_blocks.append(
                {
                    "hideIfSummonerSpell": "",
                    "items": parsed_items,
                    "showIfSummonerSpell": "",
                    "type": item_block.block_name,
                }
            )

        parsed_preferred_item_slots = list()
        for item, slot in self.preferred_item_slots.items():
            parsed_preferred_item_slots.append(
                {"id": str(item), "preferredItemSlot": int(slot)}
            )

        return {
            "associatedChampions": [self.champion_id],
            "associatedMaps": [],  # all maps
            "blocks": parsed_blocks,
            "map": "any",
            "mode": "any",
            "preferredItemSlots": parsed_preferred_item_slots,
            "sortrank": 0,
            "startedFrom": "blank",
            "title": self.item_set_name,
            "type": "custom",
        }
