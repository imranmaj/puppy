from typing import List, Optional


class Role:
    """
    Represents a role (on a team)
    """

    def __init__(
        self,
        display_role_name: str,
        display_short_role_name: str,
        lcu_role_name: str,
        ugg_role_name: str,
    ):
        """
        display_role_name - display name for role
        display_short_role_name - short display name for role
        lcu_role_name - lcu name for role
        ugg_role_name - ugg name for role
        """

        self.display_role_name = display_role_name
        self.display_short_role_name = display_short_role_name
        self.lcu_role_name = lcu_role_name
        self.ugg_role_name = ugg_role_name

    def __repr__(self) -> str:
        return self.display_role_name


class RoleList:
    """
    A list of roles
    """

    def __init__(self, roles: List[Role]):
        """
        List of roles to store
        """

        self.roles = roles

    def get_role_by_display_role_name(self, display_role_name: str) -> Optional[Role]:
        """
        Returns a role given its display name
        Returns None if there is no role for the display name
        """

        for role in self:
            if role.display_role_name == display_role_name:
                return role

    def get_role_by_display_short_role_name(
        self, display_short_role_name: str
    ) -> Optional[Role]:
        """
        Returns a role given its short display name
        Returns None if there is no role for the short display name
        """

        for role in self:
            if role.display_short_role_name == display_short_role_name:
                return role

    def get_role_by_lcu_role_name(self, lcu_role_name: str) -> Optional[Role]:
        """
        Returns a role given its lcu name
        Returns None if there is no role for the lcu name
        """

        for role in self:
            if role.lcu_role_name == lcu_role_name:
                return role

    def get_role_by_ugg_role_name(self, ugg_role_name: str) -> Optional[Role]:
        """
        Returns a role given its ugg role name
        Returns None if there is no role for the ugg role name
        """

        for role in self:
            if role.ugg_role_name == ugg_role_name:
                return role

    def find_role(self, role_string: str) -> Optional[Role]:
        """
        Attempts to find a role based on a string representation of it
            (case insensitive)
        """

        for role in self:
            if role.display_role_name.casefold() == role_string.casefold():
                return role
        for role in self:
            if role.display_short_role_name.casefold() == role_string.casefold():
                return role
        for role in self:
            if role.lcu_role_name.casefold() == role_string.casefold():
                return role
        for role in self:
            if role.ugg_role_name.casefold() == role_string.casefold():
                return role

    def move_to_front(self, role: Role):
        """
        If the Role is found in self, moves it to index 0
        """

        for i, found_role in enumerate(self):
            if found_role == role:
                break
        else:
            return
        self.roles.insert(0, self.roles.pop(i))

    def __iter__(self):
        return iter(self.roles)

    def __len__(self):
        return len(self.roles)
