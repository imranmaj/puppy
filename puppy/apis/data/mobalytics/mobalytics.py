from typing import Optional, Tuple

from puppy.apis.data.data_source import DataSourceAbc
from puppy.apis.data.exceptions import NoDataError
from puppy.apis.data.mobalytics.fetcher import Fetcher
from puppy.apis.ddragon.patches import Patches
from puppy.models import (
    Queue,
    Role,
    RoleList,
    ItemBlock,
    ItemSet,
    RuneList,
    AbilityList,
)


class Mobalytics(DataSourceAbc):
    def __init__(
        self, champion_id: str, current_queue: Queue, assigned_role: Optional[Role]
    ):
        fetcher = Fetcher(
            champion_id=champion_id,
            current_queue=current_queue,
            patch=Patches.get_current_patch(),
        )

    def get_roles(self) -> RoleList:
        return super().get_roles()

    def get_runes(self, role: Role, active: bool) -> RuneList:
        return super().get_runes(role, active)

    def get_items(
        self,
        role: Role,
        item_set_name: str,
        first_abilities_string: str,
        ability_max_order_string: str,
    ) -> ItemSet:
        return super().get_items(
            role, item_set_name, first_abilities_string, ability_max_order_string
        )

    def get_summoners(self, role: Role) -> Tuple[int, int]:
        return super().get_summoners(role)

    def get_first_abilities(self, role: Role) -> AbilityList:
        return super().get_first_abilities(role)

    def get_max_order(self, role: Role) -> AbilityList:
        return super().get_max_order(role)
