import abc
from functools import lru_cache
from typing import Optional, Tuple

from puppy.models import (
    Queue,
    Role,
    RoleList,
    ItemSet,
    RuneList,
    AbilityList,
)
from puppy.static import BASIC_ABILITIES


class DataSourceAbc(abc.ABC):
    @abc.abstractmethod
    def __init__(
        self, champion_id: str, current_queue: Queue, assigned_role: Optional[Role]
    ):
        pass

    @abc.abstractmethod
    def get_roles(self) -> RoleList:
        pass

    @abc.abstractmethod
    def get_runes(self, role: Role, active: bool) -> RuneList:
        pass

    @abc.abstractmethod
    def get_items(
        self,
        role: Role,
        item_set_name: str,
        first_abilities_string: str,
        ability_max_order_string: str,
    ) -> ItemSet:
        pass

    @abc.abstractmethod
    def get_summoners(self, role: Role) -> Tuple[int, int]:
        pass

    @abc.abstractmethod
    def get_abilities(self, role: Role) -> AbilityList:
        pass

    @lru_cache()
    def get_first_abilities(self, role: Role) -> AbilityList:
        """
        Returns AbilityList for first abilities upgrade order of current champion

        role - role of current champion
        """

        first_abilities = []
        for ability in self.get_abilities(role):
            if all([ability in first_abilities for ability in BASIC_ABILITIES]):
                break  # stop when we've seen every basic ability at least once
            else:
                first_abilities.append(ability)

        return AbilityList(abilities=first_abilities)

    @abc.abstractmethod
    def get_max_order(self, role: Role) -> AbilityList:
        pass
