from typing import List, Optional


class Ability:
    """
    Represents one ability
    """

    def __init__(self, key: str):
        """
        key - key used to press ability
        """

        self.key = key

    def __str__(self):
        return self.key


class AbilityList:
    """
    A list of abilities
    """

    def __init__(self, abilities: List[Ability]):
        """
        List of abilities
        """

        self.abilities = abilities

    def get_ability_by_key(self, key: str) -> Optional[Ability]:
        """
        Returns an ability given the key used to press it
        Returns None if there is no ability for the key
        """

        for ability in self:
            if ability.key == key:
                return ability

    def to_str_list(self) -> List[str]:
        """
        Returns a list of keys for abilities
        """

        return [str(ability) for ability in self]

    def __iter__(self):
        return iter(self.abilities)
