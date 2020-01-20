from time import sleep
from typing import Dict, Tuple, Optional, Any

from shadow.apis import Lcu
from shadow.static import QUEUES, GAMEFLOW_PHASE, ALL_ROLES
from shadow.models import Queue, Role


class LcuInterface:
    """
    High level interface to lcu api
    """

    def __init__(self):
        self.lcu = Lcu()

    def get_gameflow_phase(self) -> GAMEFLOW_PHASE:
        """
        Gets the current gameflow phase
        Returns a GAMEFLOW_PHASE enum
        """

        return GAMEFLOW_PHASE(self.lcu.get(["lol-gameflow", "v1", "gameflow-phase"]).text.strip("\""))

    def get_current_queue(self) -> Queue:
        """
        Returns the current queue (from QUEUES QueueList)
        """

        return QUEUES.get_queue_by_lcu_queue_name(self.lcu.get(["lol-gameflow", "v1", "session"]).json()["map"]["name"])

    def wait_for_champ_select(self, sleep_time):
        """
        Blocks until champ select

        sleep_time - time to sleep between polls (seconds)
        """

        while True:
            if self.get_gameflow_phase() == GAMEFLOW_PHASE.CHAMP_SELECT:
                break
            else:
                sleep(sleep_time)

    def wait_for_champion_lock(self, sleep_time):
        """
        Blocks until champion lock in

        sleep_time - time to sleep between polls (seconds)
        """

        while True:
            r = self.lcu.get(["lol-champ-select", "v1", "current-champion"])
            if r.status_code != "404" and r.text != "0":
                return
            else:
                sleep(sleep_time)

    def get_current_champion(self) -> str:
        """
        Gets the id of the currently selected champion
        Returns the champion id as str
        """

        return self.lcu.get(["lol-champ-select", "v1", "current-champion"]).text

    def get_assigned_role(self) -> Optional[Role]:
        """
        Returns assigned role of type Role
        Returns None if there is no assigned role
        """

        my_team = self.lcu.get(["lol-champ-select", "v1", "session"]).json()["myTeam"]
        for team_member in my_team:
            if team_member["summonerId"] == self.lcu.get_summoner_id():
                lcu_role_name = team_member["assignedPosition"]
                # can just search through sr roles because only sr has assigned roles
                return QUEUES.get_queue_by_lcu_queue_name("Summoner's Rift").roles.get_role_by_lcu_role_name(lcu_role_name)

    def get_current_rune_page(self) -> Dict[str, Any]:
        """
        Returns dict of current rune page
        """

        return self.lcu.get(["lol-perks", "v1", "currentpage"]).json()

    def set_current_rune_page(self, rune_page_id: str):
        """
        Sets the current/active rune page

        rune_page_id - id of rune page to set as active
        """

        r = self.lcu.put(["lol-perks", "v1", "currentpage"], data=rune_page_id)

    def get_rune_pages(self) -> Dict[str, Any]:
        """
        Returns dict of all rune pages
        """

        return self.lcu.get(["lol-perks", "v1", "pages"]).json()

    def delete_rune_page(self, rune_page_id: str):
        """
        Deletes a rune page given its id

        rune_page_id - id of rune page to delete
        """

        r = self.lcu.delete(["lol-perks", "v1", "pages", rune_page_id])

    def post_rune_page(self, rune_page: dict):
        """
        Posts a rune_page

        rune_page - built rune page
        """

        r = self.lcu.post(["lol-perks", "v1", "pages"], data=rune_page)

    # def get_owned_rune_page_count(self) -> int:
    #     """
    #     Gets the count of owned rune pages
    #     """

    #     return self.lcu.get(["lol-perks", "v1", "inventory"]).json()["ownedPageCount"]

    def edit_summoners(self, summoners: Tuple[int, int]):
        """
        Patches new summoners

        summoners - tuple of summoners ids
        """

        r = self.lcu.patch(["lol-champ-select", "v1", "session", "my-selection"], data={
            "spell1Id": summoners[0],
            "spell2Id": summoners[1]
        })

    def get_item_sets_data(self) -> Dict[str, Any]:
        """
        Returns all item set data
        """

        return self.lcu.get(["lol-item-sets", "v1", "item-sets", str(self.lcu.get_summoner_id()), "sets"]).json()

    def put_item_sets_data(self, item_sets_data: dict):
        """
        Puts and overwrites all item set data

        item_sets_data - item sets data to put
        """

        r = self.lcu.put(["lol-item-sets", "v1", "item-sets", str(self.lcu.get_summoner_id()), "sets"], data=item_sets_data)