from typing import Optional, Tuple, Dict, Any
from functools import lru_cache

from puppy.apis.data.data_source import DataSourceAbc
from puppy.apis.data.exceptions import NoDataError
from puppy.apis.data.ugg.fetcher import Fetcher
from puppy.config import config
from puppy.apis import Patches, Runes, Item
from puppy.models import (
    Queue,
    Role,
    RoleList,
    ItemBlock,
    ItemSet,
    RuneList,
    AbilityList,
)
from puppy.static import (
    ABILITIES,
    MIN_ACCEPTABLE_PATCH_MATCH_RATIO,
    FLASH,
    SUMMONERS_RIFT,
)


class UGG(DataSourceAbc):
    def __init__(
        self, champion_id: str, current_queue: Queue, assigned_role: Optional[Role]
    ):
        """
        champion_id - id of champion to get data for
        current_queue - Queue to get data for
        assigned_role - role to get data for
        """

        self.champion_id = champion_id
        self.current_queue = current_queue
        self.assigned_role = assigned_role

        try:
            current_patch_data = Fetcher(
                champion_id,
                current_queue,
                Patches.get_format_underscore_current_patch(),
            )
        except NoDataError:
            print("No data on current patch, attempting to revert to previous patch")
            self.fetcher = Fetcher(
                champion_id,
                current_queue,
                Patches.get_format_underscore_previous_patch(),
            )
            return

        if config.revert_patch:
            try:
                previous_patch_data = Fetcher(
                    champion_id,
                    current_queue,
                    Patches.get_format_underscore_previous_patch(),
                )
            except NoDataError:
                print("No data from previous patch")
                self.fetcher = current_patch_data
                return

            current_patch_matches = 0
            previous_patch_matches = 0
            for role in set(previous_patch_data.current_queue_available_roles()) & set(
                current_patch_data.current_queue_available_roles()
            ):
                data = current_patch_data.rankings_data("world", role)
                current_patch_matches += data["matches"]
                data = previous_patch_data.rankings_data("world", role)
                previous_patch_matches += data["matches"]

            # use current patch only if max match count of any role in current patch is at least n% of
            # the max match count in any role on the previous patch
            if (
                current_patch_matches / previous_patch_matches
                > MIN_ACCEPTABLE_PATCH_MATCH_RATIO
            ):
                print(
                    f"Using current patch's data ({current_patch_matches}/{previous_patch_matches} = {current_patch_matches / previous_patch_matches:.2f})"
                )
                self.fetcher = current_patch_data
            else:
                print(
                    f"Reverting to previous patch data ({current_patch_matches}/{previous_patch_matches} = {current_patch_matches / previous_patch_matches:.2f})"
                )
                self.fetcher = previous_patch_data
        else:
            # no reversion, use current patch
            self.fetcher = current_patch_data

    @lru_cache()
    def get_roles(self) -> RoleList:
        """
        Returns RoleList of commonly played roles + assigned role for current champion
        """

        if self.current_queue != SUMMONERS_RIFT:
            return self.current_queue.roles

        if self.assigned_role is not None:
            roles = self.fetcher.current_queue_available_roles()
            roles.move_to_front(self.assigned_role)
            return roles
        else:
            return self.fetcher.current_queue_available_roles()

    @lru_cache()
    def get_runes(self, role: Role, active: bool) -> RuneList:
        """
        Returns built rune page for current champion

        role - role of current champion
        active - whether the returned rune page should be active
        """

        overview_data = self.fetcher.overview_data("world", role)

        all_runes = overview_data["runes"]["runes"]
        shards = [int(item) for item in overview_data["shards"]["shards"]]
        primary_style = overview_data["runes"]["primary_style"]
        secondary_style = overview_data["runes"]["secondary_style"]

        # lists are not hashable (for lru_cache), use tuple
        sorted_runes = Runes.sort_runes(
            tuple(all_runes),
            primary_style=primary_style,
            secondary_style=secondary_style,
        )

        return RuneList(
            rune_page_name=role.display_role_name,
            primary_style=primary_style,
            secondary_style=secondary_style,
            runes=sorted_runes + shards,
            active=active,
        )

    @lru_cache()
    def get_items(
        self,
        role: Role,
        item_set_name: str,
        first_abilities_string: str,
        ability_max_order_string: str,
    ) -> ItemSet:
        """
        Returns built item set for current champion

        role - role of current champion
        item_set_name - name of item set
        """

        overview_data = self.fetcher.overview_data("world", role)

        starting = ItemBlock(
            items=overview_data["starting_items"]["starting_items"]
            + [int(Item.id_for_name(item_name)) for item_name in config.small_items],  # type: ignore
            block_name=f"Starting/Small Items, Start: {first_abilities_string}",
        )
        core = ItemBlock(
            items=overview_data["core_items"]["core_items"],
            block_name=f"Core Items,                    Max: {ability_max_order_string}",
        )
        item_4_options = ItemBlock(
            items=[item["item"] for item in overview_data["item_4_options"]],
            block_name="Item 4 Options",
        )
        item_5_options = ItemBlock(
            items=[item["item"] for item in overview_data["item_5_options"]],
            block_name="Item 5 Options",
        )
        item_6_options = ItemBlock(
            items=[item["item"] for item in overview_data["item_6_options"]],
            block_name="Item 6 Options",
        )

        return ItemSet(
            item_blocks=[
                starting,
                core,
                item_4_options,
                item_5_options,
                item_6_options,
            ],
            item_set_name=item_set_name,
            champion_id=int(self.champion_id),
            preferred_item_slots={
                Item.id_for_name(item_name): slot
                for item_name, slot in config.preferred_item_slots.items()
            },  # type: ignore
        )

    @lru_cache()
    def get_summoners(self, role: Role) -> Tuple[int, int]:
        """
        Returns length 2 tuple of summoners for current champion

        role - role of current champion
        """

        overview_data = self.fetcher.overview_data("world", role)

        summoners = overview_data["summoner_spells"]["summoner_spells"]
        # flash is on wrong key
        if (config.flash_on_f and summoners[0] == FLASH) or (
            not config.flash_on_f and summoners[1] == FLASH
        ):
            summoners = reversed(summoners)
        return tuple(summoners)

    @lru_cache()
    def get_abilities(self, role: Role) -> AbilityList:
        """
        Returns AbilityList for ability upgrade order of current champion

        role - role of current champion
        """

        overview_data = self.fetcher.overview_data("world", role)

        abilities = []
        for key in overview_data["abilities"]["ability_order"]:
            ability = ABILITIES.get_ability_by_key(key)
            if ability:
                abilities.append(ability)
        return AbilityList(abilities=abilities)

    @lru_cache()
    def get_max_order(self, role: Role) -> AbilityList:
        """
        Returns AbilityList for ability max order of current champion

        role - role of current champion
        """

        overview_data = self.fetcher.overview_data("world", role)

        abilities = []
        for key in overview_data["abilities"]["ability_max_order"]:
            ability = ABILITIES.get_ability_by_key(key)
            if ability:
                abilities.append(ability)
        return AbilityList(abilities=abilities)
