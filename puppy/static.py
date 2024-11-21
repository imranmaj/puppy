from typing import Dict, List
from itertools import chain
from enum import Enum

from puppy.apis.ddragon import Item
from puppy.models import (
    Queue,
    QueueList,
    Role,
    RoleList,
    # Shard,
    # ShardList,
    Ability,
    AbilityList,
)


# queue types
QUEUES = QueueList(
    queues=[
        Queue(
            lcu_queue_name="Summoner's Rift",
            ugg_queue_name="ranked_solo_5x5",
            mobalytics_queue_name="RANKED_SOLO",
            rank="platinum_plus",
            roles=RoleList(
                roles=[
                    Role(
                        display_role_name="Top",
                        display_short_role_name="Top",
                        lcu_role_name="top",
                        ugg_role_name="top",
                        mobalytics_role_name="TOP",
                    ),
                    Role(
                        display_role_name="Jungle",
                        display_short_role_name="JG",
                        lcu_role_name="jungle",
                        ugg_role_name="jungle",
                        mobalytics_role_name="JUNGLE",
                    ),
                    Role(
                        display_role_name="Middle",
                        display_short_role_name="Mid",
                        lcu_role_name="middle",
                        ugg_role_name="mid",
                        mobalytics_role_name="MID",
                    ),
                    Role(
                        display_role_name="ADC",
                        display_short_role_name="ADC",
                        lcu_role_name="bottom",
                        ugg_role_name="adc",
                        mobalytics_role_name="ADC",
                    ),
                    Role(
                        display_role_name="Support",
                        display_short_role_name="Sup",
                        lcu_role_name="utility",
                        ugg_role_name="supp",
                        mobalytics_role_name="SUPPORT",
                    ),
                ]
            ),
        ),
        Queue(
            lcu_queue_name="Howling Abyss",
            ugg_queue_name="normal_aram",
            mobalytics_queue_name="ARAM",
            rank="overall",
            roles=RoleList(
                roles=[
                    Role(
                        display_role_name="ARAM",
                        display_short_role_name="ARAM",
                        lcu_role_name="",
                        ugg_role_name="none",
                        mobalytics_role_name="MID",
                    )
                ]
            ),
        ),
        Queue(
            lcu_queue_name="Bridge of Progress",
            ugg_queue_name="normal_aram",
            mobalytics_queue_name="ARAM",
            rank="overall",
            roles=RoleList(
                roles=[
                    Role(
                        display_role_name="ARAM",
                        display_short_role_name="ARAM",
                        lcu_role_name="",
                        ugg_role_name="none",
                        mobalytics_role_name="MID",
                    )
                ]
            ),
        ),
        Queue(
            lcu_queue_name="Nexus Blitz",
            ugg_queue_name="nexus_blitz",
            mobalytics_queue_name="",  # TODO: unknown
            rank="overall",
            roles=RoleList(
                roles=[
                    Role(
                        display_role_name="Nexus Blitz",
                        display_short_role_name="NB",
                        lcu_role_name="",
                        ugg_role_name="none",
                        mobalytics_role_name="",  # TODO: unknown
                    )
                ]
            ),
        ),
    ]
)

SUMMONERS_RIFT: Queue = QUEUES.get_queue_by_lcu_queue_name("Summoner's Rift")  # type: ignore
ARAM: Queue = QUEUES.get_queue_by_lcu_queue_name("Howling Abyss")  # type: ignore

# list of all roles
ALL_ROLES = chain.from_iterable([queue.roles.roles for queue in QUEUES])
ALL_ROLES = RoleList(roles=[role for role in ALL_ROLES])

# ability types
ABILITIES = AbilityList(
    abilities=[
        Ability(key="Q"),
        Ability(key="W"),
        Ability(key="E"),
        Ability(key="R"),
    ]
)
# mapping of mobalytics ability numbers to keys
ABILITY_NUMBERS = {
    1: ABILITIES.get_ability_by_key("Q"),
    2: ABILITIES.get_ability_by_key("W"),
    3: ABILITIES.get_ability_by_key("E"),
    4: ABILITIES.get_ability_by_key("R"),
}
# basic abilities
BASIC_ABILITIES = AbilityList(
    abilities=[
        ABILITIES.get_ability_by_key("Q"),
        ABILITIES.get_ability_by_key("W"),
        ABILITIES.get_ability_by_key("E"),
    ]  # type: ignore
)

# rune shards
# SHARDS = ShardList(
#     shards=[
#         Shard(ugg_shard_name="Adaptive Force", shard_id=5008),
#         Shard(ugg_shard_name="Attack Speed", shard_id=5005),
#         Shard(ugg_shard_name="Scaling Cooldown Reduction", shard_id=5007),
#         Shard(ugg_shard_name="Armor", shard_id=5002),
#         Shard(ugg_shard_name="Magic Resist", shard_id=5003),
#         Shard(ugg_shard_name="Scaling Health", shard_id=5001),
#     ]
# )


# gameflow phases
class GAMEFLOW_PHASE(Enum):
    NONE = "None"
    LOBBY = "Lobby"
    MATCHMAKING = "Matchmaking"
    READY_CHECK = "ReadyCheck"
    CHAMP_SELECT = "ChampSelect"
    IN_PROGRESS = "InProgress"
    RECONNECT = "Reconnect"
    PRE_END_OF_GAME = "PreEndOfGame"
    END_OF_GAME = "EndOfGame"
    WAITING_FOR_STATS = "WaitingForStats"


UAS = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"  # user agent string
SLEEP_TIME = 0.5  # time to sleep between polls
MIN_ACCEPTABLE_PATCH_MATCH_RATIO = 0.3  # ratio of games on current patch to previous patch required to use current patch's data
FLASH = 4  # id for flash summoner
CONFIG_FILENAME = "config.json"  # name of config file
DEFAULT_CONFIG = {  # default config file contents
    "flash_on_f": True,
    "revert_patch": True,
    "preferred_item_slots": dict(),
    "small_items": list(),
    "backend": "ugg",
}
BACKENDS = ["ugg", "mobalytics"]  # data source


def convert_preferred_item_slots(item_slots: Dict[str, int]) -> Dict[str, int]:
    converted_item_slots = {}
    for item_id, slot in item_slots.items():
        converted_item = Item.name_for_id(item_id)
        if converted_item is not None:
            converted_item_slots[converted_item] = slot
    return converted_item_slots


def convert_small_items(items: List[int]) -> List[str]:
    converted_small_items = []
    for item_id in items:
        converted_item = Item.name_for_id(str(item_id))
        if converted_item is not None:
            converted_small_items.append(converted_item)
    return converted_small_items


def validate_preferred_item_slots(item_slots: Dict[str, int]):
    for name in item_slots:
        if Item.id_for_name(name) is None:
            raise ValueError(
                f"Invalid item in config field preferred_item_slots: {name}"
            )


def validate_small_items(items: List[int]):
    for name in items:
        if Item.id_for_name(name) is None:
            raise ValueError(f"Invalid item in config field small_items: {name}")


def validate_backend(backend: str):
    if backend not in BACKENDS:
        raise ValueError(
            f"Invalid value for config field backend: {backend} "
            f"(must be one of {', '.join(BACKENDS)})"
        )


CONFIG_STRUCTURE = {
    "flash_on_f": {
        "type": bool,
        "default": True,
    },
    "revert_patch": {"type": bool, "default": True},
    "preferred_item_slots": {
        "type": dict,
        "default": {},
        "should_convert": lambda item_slots: item_slots
        and all(  # backwards compatibility converter
            item.isdigit() for item in item_slots
        ),
        "converter": convert_preferred_item_slots,
        "validator": validate_preferred_item_slots,
    },
    "small_items": {
        "type": list,
        "default": [],
        "should_convert": lambda items: items
        and all(isinstance(item, int) for item in items),
        "converter": convert_small_items,
        "validator": validate_small_items,
    },
    "backend": {
        "type": str,
        "default": "ugg",
        "validator": validate_backend,
    },
    "debug": {"type": bool, "default": False},
}
