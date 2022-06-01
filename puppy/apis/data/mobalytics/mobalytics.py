from functools import lru_cache
from typing import Optional, Tuple

from puppy.apis.data.data_source import DataSourceAbc
from puppy.apis.data.exceptions import NoDataError
from puppy.apis.data.mobalytics.fetcher import Fetcher
from puppy.apis.ddragon import Patches, Runes, Item
from puppy.config import config
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
    MIN_ACCEPTABLE_PATCH_MATCH_RATIO,
    FLASH,
    ABILITY_NUMBERS,
    SUMMONERS_RIFT,
)


class Mobalytics(DataSourceAbc):
    def __init__(
        self, champion_id: str, current_queue: Queue, assigned_role: Optional[Role]
    ):
        self.champion_id = champion_id
        self.current_queue = current_queue
        self.assigned_role = assigned_role

        try:
            current_patch_data = Fetcher(
                champion_id,
                current_queue,
                Patches.get_current_patch(),
            )
        except NoDataError:
            print("No data on current patch, attempting to revert to previous patch")
            self.fetcher = Fetcher(
                champion_id,
                current_queue,
                Patches.get_previous_patch(),
            )
            return

        if config.revert_patch:
            try:
                previous_patch_data = Fetcher(
                    champion_id,
                    current_queue,
                    Patches.get_previous_patch(),
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
                build = current_patch_data.get_build("world", role)
                current_patch_matches += build["stats"]["matches"]
                build = previous_patch_data.get_build("world", role)
                previous_patch_matches += build["stats"]["matches"]

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
            self.fetcher = current_patch_data

    @lru_cache()
    def get_roles(self) -> RoleList:
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
        build = self.fetcher.get_build("world", role)

        primary_style = build["runes"]["primary_style"]
        secondary_style = build["runes"]["secondary_style"]
        all_runes = build["runes"]["runes"]
        shards = all_runes[-3:]

        sorted_runes = Runes.sort_runes(
            tuple(all_runes), primary_style, secondary_style
        )

        return RuneList(
            runes=sorted_runes + shards,
            rune_page_name=role.display_role_name,
            primary_style=primary_style,
            secondary_style=secondary_style,
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
        build = self.fetcher.get_build("world", role)

        starting = ItemBlock(
            items=build["starting_items"] + [int(Item.id_for_name(item_name)) for item_name in config.small_items], # type: ignore
            block_name=f"Starting/Small Items, Start: {first_abilities_string}",
        )
        early = ItemBlock(
            items=build["early_items"],
            block_name=f"Early Items,                    Max: {ability_max_order_string}",
        )
        core = ItemBlock(
            items=build["core_items"],
            block_name=f"Core Items",
        )
        situational = ItemBlock(
            items=build["situational_items"],
            block_name=f"Situational Items",
        )
        full_build = ItemBlock(
            items=build["full_build_items"],
            block_name=f"Full Build Items",
        )

        return ItemSet(
            item_blocks=[starting, early, core, situational, full_build],
            item_set_name=item_set_name,
            champion_id=int(self.champion_id),
            preferred_item_slots={
                Item.id_for_name(item_name): slot
                for item_name, slot in config.preferred_item_slots.items()
            },  # type: ignore
        )

    @lru_cache()
    def get_summoners(self, role: Role) -> Tuple[int, int]:
        build = self.fetcher.get_build("world", role)
        summoners = build["summoner_spells"]

        # flash is on wrong key
        if (config.flash_on_f and summoners[0] == FLASH) or (
            not config.flash_on_f and summoners[1] == FLASH
        ):
            summoners = reversed(summoners)
        return tuple(summoners)

    @lru_cache()
    def get_abilities(self, role: Role) -> AbilityList:
        build = self.fetcher.get_build("world", role)

        abilities = []
        for ability_number in build["abilities"]["ability_order"]:
            ability = ABILITY_NUMBERS[ability_number]
            if ability:
                abilities.append(ability)
        return AbilityList(abilities=abilities)

    @lru_cache()
    def get_max_order(self, role: Role) -> AbilityList:
        build = self.fetcher.get_build("world", role)

        abilities = []
        for ability_number in build["abilities"]["ability_max_order"]:
            ability = ABILITY_NUMBERS[ability_number]
            if ability:
                abilities.append(ability)
        return AbilityList(abilities=abilities)
