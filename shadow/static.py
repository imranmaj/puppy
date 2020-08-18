from itertools import chain
from enum import Enum

from shadow.models import Queue, QueueList, Role, RoleList, Shard, ShardList, Ability, AbilityList

# queue types
QUEUES = QueueList(queues=[
    Queue(
        lcu_queue_name="Summoner's Rift",
        roles=RoleList(roles=[
            Role(display_role_name="Top", display_short_role_name="Top", lcu_role_name="top", ugg_data_name="world_platinum_plus_top"),
            Role(display_role_name="Jungle", display_short_role_name="JG", lcu_role_name="jungle", ugg_data_name="world_platinum_plus_jungle"),
            Role(display_role_name="Middle", display_short_role_name="Mid", lcu_role_name="middle", ugg_data_name="world_platinum_plus_mid"),
            Role(display_role_name="ADC", display_short_role_name="ADC", lcu_role_name="bottom", ugg_data_name="world_platinum_plus_adc"),
            Role(display_role_name="Support", display_short_role_name="Sup", lcu_role_name="utility", ugg_data_name="world_platinum_plus_supp")
        ]),
        # even though the url says "mid", the page contains data for all roles
        ugg_url="https://u.gg/lol/champions/builds/mid-{champion_name}-build"
    ),
    Queue(
        lcu_queue_name="Howling Abyss",
        roles=RoleList(roles=[
            Role(display_role_name="ARAM", display_short_role_name="ARAM", lcu_role_name="", ugg_data_name="world_overall_none")
        ]),
        ugg_url="https://u.gg/lol/champions/builds/mid-{champion_name}-build?queueType=normal_aram"
    ),
    Queue(
        lcu_queue_name="Nexus Blitz",
        roles=RoleList(roles=[
            Role(display_role_name="Nexus Blitz", display_short_role_name="NB", lcu_role_name="", ugg_data_name="world_overall_none")
        ]),
        ugg_url="https://u.gg/lol/champions/builds/mid-{champion_name}-build?queueType=nexus_blitz"
    )
])

# list of all roles
ALL_ROLES = chain.from_iterable([queue.roles.roles for queue in QUEUES])
ALL_ROLES = RoleList(roles=[role for role in ALL_ROLES])

# ability types
ABILITIES = AbilityList(abilities=[
    Ability(key="Q"),
    Ability(key="W"),
    Ability(key="E"),
    Ability(key="R"),
])
BASIC_ABILITIES = AbilityList(abilities=[
    ABILITIES.get_ability_by_key("Q"),
    ABILITIES.get_ability_by_key("W"),
    ABILITIES.get_ability_by_key("E"),
])

# rune shards
SHARDS = ShardList(shards=[
    Shard(ugg_shard_name="Adaptive Force", shard_id=5008),
    Shard(ugg_shard_name="Attack Speed", shard_id=5005),
    Shard(ugg_shard_name="Scaling Cooldown Reduction", shard_id=5007),
    Shard(ugg_shard_name="Armor", shard_id=5002),
    Shard(ugg_shard_name="Magic Resist", shard_id=5003),
    Shard(ugg_shard_name="Scaling Health", shard_id=5001)
])

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

UAS = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36" # user agent string
SLEEP_TIME = 0.5 # time to sleep between polls
MIN_ACCEPTABLE_NORMED_MATCH_COUNT = 0.1 # minimum normalized value for match count to be considered for a rune page
MIN_ACCEPTABLE_PATCH_MATCH_RATIO = 0.15 # ratio of games on current patch to previous patch required to use current patch's data
FLASH = 4 # id for flash summoner
CONFIG_FILENAME = "config.json" # name of config file
DEFAULT_CONFIG = { # default config file contents
    "flash_on_f": True,
    "revert_patch": True,
    "preferred_item_slots": dict(),
    "small_items": list()
}