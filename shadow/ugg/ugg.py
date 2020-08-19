from typing import Optional, Tuple
from functools import lru_cache

from shadow.exceptions import NoDataError
from shadow.ugg.fetcher import Fetcher
from shadow.environment import config
from shadow.apis import Patches, Runes
from shadow.models import Queue, Role, RoleList, ItemBlock, ItemSet, RuneList, AbilityList
from shadow.static import ALL_ROLES, ABILITIES, BASIC_ABILITIES, MIN_ACCEPTABLE_PATCH_MATCH_RATIO, FLASH


class UGG:
    def __init__(self, champion_id: str, current_queue: Queue, assigned_role: Optional[Role]):
        """
        champion_id - id of champion to get data for
        current_queue - Queue to get data for
        assigned_role - role to get data for
        """

        self.champion_id = champion_id
        self.current_queue = current_queue
        self.assigned_role = assigned_role

        current_patch_data = Fetcher(champion_id, current_queue, Patches.get_format_underscore_current_patch())
        if config.revert_patch:
            try:
                previous_patch_data = Fetcher(champion_id, current_queue, Patches.get_format_underscore_previous_patch())
            except NoDataError:
                print("No data from previous patch")
                self.data = current_patch_data
                return

            current_patch_matches = 0
            previous_patch_matches = 0
            for role in ALL_ROLES:
                if (data := current_patch_data.rankings_data("world", self.current_queue.rank, role)) is not None:
                    current_patch_matches += data["matches"]
                if (data := previous_patch_data.rankings_data("world", self.current_queue.rank, role)) is not None:
                    previous_patch_matches += data["matches"]

            # use current patch only if max match count of any role in current patch is at least n% of
            # the max match count in any role on the previous patch
            if current_patch_matches / previous_patch_matches > MIN_ACCEPTABLE_PATCH_MATCH_RATIO:
                print(f"Using current patch's data ({current_patch_matches}/{previous_patch_matches})")
                self.data = current_patch_data
            else:
                print(f"Reverting to previous patch data ({current_patch_matches}/{previous_patch_matches})")
                self.data = previous_patch_data
        else:
            # no reversion, use current patch
            self.data = current_patch_data

    @lru_cache()
    def get_roles(self) -> RoleList:
        """
        Returns RoleList of commonly played roles + assigned role for current champion
        """

        # only 1 role for map (eg ARAM)
        if len(self.current_queue.roles) == 1:
            return self.current_queue.roles

        if self.assigned_role is not None:
            roles = self.data.primary_roles_data()
            roles.move_to_front(self.assigned_role)
            return roles
        else:
            return self.data.primary_roles_data()

    @lru_cache()
    def get_runes(self, role: Role, active: bool) -> RuneList:
        """
        Returns built rune page for current champion

        role - role of current champion
        active - whether the returned rune page should be active
        """

        all_runes = self.data.overview_data("world", self.current_queue.rank, role)["runes"]["runes"]
        shards = [int(item) for item in self.data.overview_data("world", self.current_queue.rank, role)["shards"]["shards"]]
        primary_style = self.data.overview_data("world", self.current_queue.rank, role)["runes"]["primary_style"]
        secondary_style = self.data.overview_data("world", self.current_queue.rank, role)["runes"]["secondary_style"]
        
        # lists are not hashable (for lru_cache), use tuple
        sorted_runes = Runes.sort_runes(tuple(all_runes), primary_style=primary_style, secondary_style=secondary_style)

        return RuneList(
            rune_page_name=role.display_role_name,
            primary_style=primary_style,
            secondary_style=secondary_style,
            runes=sorted_runes + shards,
            active=active
        )
    
    @lru_cache()
    def get_items(self, role: Role, item_set_name: str, first_abilities_string: str, ability_max_order_string: str) -> ItemSet:
        """
        Returns built item set for current champion

        role - role of current champion
        item_set_name - name of item set
        """

        starting = ItemBlock(
            items=self.data.overview_data("world", self.current_queue.rank, role)["starting_items"]["starting_items"] + config.small_items, 
            block_name=f"Starting/Small Items, Start: {first_abilities_string}"
        )
        core = ItemBlock(items=self.data.overview_data("world", self.current_queue.rank, role)["core_items"]["core_items"], block_name=f"Core Items,             Max:  {ability_max_order_string}")
        item_4_options = ItemBlock(items=[item["item"] for item in self.data.overview_data("world", self.current_queue.rank, role)["item_4_options"]], block_name="Item 4 Options")
        item_5_options = ItemBlock(items=[item["item"] for item in self.data.overview_data("world", self.current_queue.rank, role)["item_5_options"]], block_name="Item 5 Options")
        item_6_options = ItemBlock(items=[item["item"] for item in self.data.overview_data("world", self.current_queue.rank, role)["item_6_options"]], block_name="Item 6 Options")

        return ItemSet(item_blocks=[
            starting,
            core,
            item_4_options,
            item_5_options,
            item_6_options
        ], item_set_name=item_set_name, champion_id=int(self.champion_id), preferred_item_slots=config.preferred_item_slots)

    @lru_cache()
    def get_summoners(self, role: Role) -> Tuple[int, int]:
        """
        Returns length 2 tuple of summoners for current champion

        role - role of current champion
        """

        summoners = self.data.overview_data("world", self.current_queue.rank, role)["summoner_spells"]["summoner_spells"]
        # flash is on wrong key
        if (config.flash_on_f and summoners[0] == FLASH) or (not config.flash_on_f and summoners[1] == FLASH):
            summoners = reversed(summoners)
        return tuple(summoners)

    @lru_cache()
    def get_abilities(self, role: Role) -> AbilityList:
        """
        Returns AbilityList for ability upgrade order of current champion

        role - role of current champion
        """

        return AbilityList(
            abilities=[ABILITIES.get_ability_by_key(key) for key in self.data.overview_data("world", self.current_queue.rank, role)["abilities"]["ability_order"]]
        )

    @lru_cache()
    def get_first_abilities(self, role: Role) -> AbilityList:
        """
        Returns AbilityList for first abilities upgrade order of current champion

        role - role of current champion
        """

        first_abilities = []
        for ability in self.get_abilities(role):
            if all([ability in first_abilities for ability in BASIC_ABILITIES]):
                break # stop when we've seen every basic ability at least once
            else:
                first_abilities.append(ability)

        return AbilityList(abilities=first_abilities)

    @lru_cache()
    def get_max_order(self, role: Role) -> AbilityList:
        """
        Returns AbilityList for ability max order of current champion

        role - role of current champion
        """

        return AbilityList(
            abilities=[ABILITIES.get_ability_by_key(key) for key in self.data.overview_data("world", self.current_queue.rank, role)["abilities"]["ability_max_order"]]
        )
