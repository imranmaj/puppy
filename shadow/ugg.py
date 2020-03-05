import json
from typing import Optional, Tuple, Dict
import re
from functools import lru_cache

import requests

from shadow.environment import config
from shadow.apis import Patches, Runes
from shadow.models import Queue, Role, RoleList, ItemBlock, ItemSet, RuneList, AbilityList
from shadow.static import UAS, SMALL_ITEMS, ABILITIES, BASIC_ABILITIES, MIN_ACCEPTABLE_NORMED_MATCH_COUNT, MIN_ACCEPTABLE_PATCH_MATCH_RATIO, FLASH


class UGG:
    def __init__(self, champion_name: str, current_queue: Queue, assigned_role: Optional[Role]):
        """
        champion_name - full name of champion to get data for
        current_queue - Queue to get data for
        """

        self.current_queue = current_queue
        self.assigned_role = assigned_role

        url = current_queue.ugg_url.format(champion_name=champion_name)
        current_patch_data = self.get_and_parse_data(self.current_queue, url)
        if config.revert_patch:
            previous_patch_data = self.get_and_parse_data(self.current_queue, url, underscored_patch=Patches.get_format_underscore_previous_patch())
            if previous_patch_data is None:
                print("No data from previous patch")
                self.data = current_patch_data
                return

            current_patch_match_counts = self.get_match_counts(current_queue=self.current_queue, data=current_patch_data)
            previous_patch_match_counts = self.get_match_counts(current_queue=self.current_queue, data=previous_patch_data)
            # use current patch only if max match count of any role in current patch is at least 10% of
            # the max match count in any role on the previous patch
            if max(current_patch_match_counts.values()) / max(previous_patch_match_counts.values()) > MIN_ACCEPTABLE_PATCH_MATCH_RATIO:
                print(f"Using current patch's data ({max(current_patch_match_counts.values())}/{max(previous_patch_match_counts.values())})")
                self.data = current_patch_data
            else:
                print(f"Reverting to previous patch data ({max(current_patch_match_counts.values())}/{max(previous_patch_match_counts.values())})")
                self.data = previous_patch_data
        else:
            # no reversion, use current patch
            self.data = current_patch_data

    @staticmethod
    @lru_cache()
    def get_and_parse_data(current_queue, url, underscored_patch: str=None) -> Optional[Dict[Role, Dict]]:
        if underscored_patch:
            r = requests.get(
                url,
                headers={
                    "User-Agent": UAS
                },
                params={
                    "patch": underscored_patch
                }
            )
        else:
            r = requests.get(
                url,
                headers={
                    "User-Agent": UAS
                }
            )

        data_text = re.search(r"(?<=(window.__REACTN_PRELOADED_STATE__ = )).*}", r.text).group(0)
        all_data = json.loads(data_text)
        for key, val in all_data.items():
            if "overview" in key:
                found_data = val["fetchedJSON"]
                break
        else:
            # no data
            return

        # parse data by role
        data = dict()
        for role in current_queue.roles:
            if role.ugg_data_name in found_data:
                data[role] = found_data[role.ugg_data_name]

        return data

    @staticmethod
    def get_match_counts(current_queue, data) -> Dict[Role, int]:
        match_counts = dict()
        for role in current_queue.roles:
            if role in data:
                match_counts[role] = data[role]["matches"]
            else: # if u.gg for some reason does not have the role at all
                match_counts[role] = 0

        return match_counts

    @lru_cache()
    def get_roles(self) -> RoleList:
        """
        Returns RoleList of commonly played roles + assigned role for current champion
        """

        # only 1 role for map (eg ARAM)
        if len(self.current_queue.roles) == 1:
            return self.current_queue.roles

        match_counts = self.get_match_counts(current_queue=self.current_queue, data=self.data)
        # check if normalized value is high enough
        champion_roles = []
        for role, count in match_counts.items():
            normed_count = ((count - min(match_counts.values())) / (max(match_counts.values()) - min(match_counts.values())))
            # check if role is played often
            if normed_count >= MIN_ACCEPTABLE_NORMED_MATCH_COUNT:
                champion_roles.append(role)

        # force assigned role
        if self.assigned_role and self.assigned_role not in champion_roles:
            champion_roles.append(self.assigned_role)

        return RoleList(roles=champion_roles)

    @lru_cache()
    def get_runes(self, role: Role, active: bool) -> Dict:
        """
        Returns built rune page for current champion

        role - role of current champion
        active - whether the returned rune page should be active
        """

        all_runes = self.data[role]["rec_runes"]["active_perks"]
        shards = [int(item) for item in self.data[role]["stat_shards"]["activeShards"]]
        primary_style = self.data[role]["rec_runes"]["primary_style"]
        secondary_style = self.data[role]["rec_runes"]["sub_style"]
        
        # lists are not hashable (for lru_cache), use tuple
        sorted_runes = Runes.sort_runes(tuple(all_runes), primary_style=primary_style, secondary_style=secondary_style)

        return RuneList(
            rune_page_name=role.display_role_name,
            primary_style=primary_style,
            secondary_style=secondary_style,
            runes=sorted_runes + shards,
            active=active
        ).build()
    
    @lru_cache()
    def get_items(self, role: Role, champion_id: int, item_set_name: str, first_abilities: str) -> Dict:
        """
        Returns built item set for current champion

        role - role of current champion
        champion_id - id of current champion
        item_set_name - name of item set
        first_abilities - first abilities upgrade order
        """

        starting = ItemBlock(
            items=self.data[role]["rec_starting_items"]["items"] + SMALL_ITEMS, 
            block_name=f"Starting/Small Items"
        )
        core = ItemBlock(items=self.data[role]["rec_core_items"]["items"], block_name="Core Items")
        item_4_options = ItemBlock(items=[item["item_id"] for item in self.data[role]["item_options_1"]], block_name="Item 4 Options")
        item_5_options = ItemBlock(items=[item["item_id"] for item in self.data[role]["item_options_2"]], block_name="Item 5 Options")
        item_6_options = ItemBlock(items=[item["item_id"] for item in self.data[role]["item_options_3"]], block_name="Item 6 Options")

        return ItemSet(item_blocks=[
            starting,
            core,
            item_4_options,
            item_5_options,
            item_6_options
        ], item_set_name=item_set_name, champion_id=champion_id, preferred_item_slots=config.preferred_item_slots).build()

    @lru_cache()
    def get_summoners(self, role: Role) -> Tuple[int, int]:
        """
        Returns length 2 tuple of summoners for current champion

        role - role of current champion
        """

        summoners = self.data[role]["rec_summoner_spells"]["items"]
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
            abilities=[ABILITIES.get_ability_by_key(key) for key in self.data[role]["rec_skill_path"]["items"]]
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
            abilities=[ABILITIES.get_ability_by_key(key) for key in self.data[role]["rec_skills"]["items"]]
        )
