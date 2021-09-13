from typing import List

import requests


class Patches:
    """
    Manipulation of static patch data
    """

    @classmethod
    def get_all_patches(cls) -> List[str]:
        """
        Returns list of all patches
        """
        PATCHES_URL = "http://ddragon.leagueoflegends.com/api/versions.json"
        return requests.get(PATCHES_URL).json()

    @classmethod
    def get_current_patch(cls) -> str:
        """
        Returns current patch
        """

        return cls.get_all_patches()[0]

    @classmethod
    def get_format_underscore_current_patch(cls) -> str:
        """
        Returns the current patch with underscores instead of periods
        Uses only the first 2 parts of the patch name
        """

        current_patch = cls.get_current_patch()
        return "_".join(current_patch.split(".")[:2])

    @classmethod
    def get_format_underscore_previous_patch(cls) -> str:
        """
        Returns the previous patch with underscores instead of periods
        Uses only the first 2 parts of the patch name
        """

        previous_patch = cls.get_all_patches()[1]
        return "_".join(previous_patch.split(".")[:2])
