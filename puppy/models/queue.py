from typing import List, Optional

from puppy.models.role import RoleList


class Queue:
    """
    Represents a queue (e.g. SR, ARAM)
    """

    def __init__(
        self,
        lcu_queue_name: str,
        ugg_queue_name: str,
        mobalytics_queue_name: str,
        rank: str,
        roles: RoleList,
    ):
        """
        lcu_queue_name - lcu name for queue
        ugg_queue_name - ugg name for queue. Must be one of:
            ["ranked_solo_5x5", "ranked_flex_sr", "nexus_blitz", "normal_aram", "normal_blind_5x5", "normal_draft_5x5"]
        mobalytics_queue_name - mobalytics name for queue. Must be one of:
            ["RANKED_SOLO", "ARAM"]
        rank - name of rank to get data for
        roles - RoleList of roles for this queue
        """

        self.lcu_queue_name = lcu_queue_name
        self.ugg_queue_name = ugg_queue_name
        self.mobalytics_queue_name = mobalytics_queue_name
        self.rank = rank
        self.roles = roles

    def __repr__(self) -> str:
        return self.lcu_queue_name


class QueueList:
    """
    A list of queues
    """

    def __init__(self, queues: List[Queue]):
        """
        queues - list of queues to store
        """

        self.queues = queues

    def get_queue_by_lcu_queue_name(self, lcu_queue_name: str) -> Optional[Queue]:
        """
        Returns a queue in the list with the given lcu name
        Returns None if there is no queue for the given name
        """

        for queue in self:
            if queue.lcu_queue_name == lcu_queue_name:
                return queue
        print("Queue not found:", lcu_queue_name)

    def get_queue_by_ugg_queue_name(self, ugg_queue_name: str) -> Optional[Queue]:
        """
        Returns a queue in the list with the given ugg name
        Returns None if there is no queue for the given name
        """

        for queue in self:
            if queue.ugg_queue_name == ugg_queue_name:
                return queue
        print("UGG queue not found:", ugg_queue_name)

    def get_default(self) -> Queue:
        """
        Returns the default queue
        """

        return self.get_queue_by_lcu_queue_name("Summoner's Rift")  # type: ignore

    def __iter__(self):
        return iter(self.queues)
