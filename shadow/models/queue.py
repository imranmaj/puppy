from typing import List, Optional

from shadow.models.role import RoleList


class Queue:
    """
    Represents a queue (e.g. SR, ARAM)
    """

    def __init__(self, lcu_queue_name: str, roles: RoleList, ugg_url: str):
        """
        lcu_queue_name - lcu name for queue
        roles - RoleList of roles for this queue
        ugg_url - u.gg url to request data for this queue
            Must be formatted with {champion_name}
        """

        self.lcu_queue_name = lcu_queue_name
        self.roles = roles
        self.ugg_url = ugg_url

class QueueList:
    """
    A list of queues
    """

    def __init__(self, queues: List[Queue]):
        """
        queues - list of queues to store
        """

        self.queues = queues
    
    def get_queue_by_lcu_queue_name(self, queue_lcu_queue_name: str) -> Optional[Queue]:
        """
        Returns a queue in the list with the given name
        Returns None if there is no queue for the given name
        """

        for queue in self:
            if queue.lcu_queue_name == queue_lcu_queue_name:
                return queue

    def get_default(self) -> Queue:
        """
        Returns the default queue
        """

        return self.get_queue_by_lcu_queue_name("Summoner's Rift")

    def __iter__(self):
        return iter(self.queues)