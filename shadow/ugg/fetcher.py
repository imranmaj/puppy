from typing import Dict, Any, Optional
from json import JSONDecodeError

import requests

from shadow.static import UAS, ALL_ROLES
from shadow.models import RoleList, Role, Queue
from shadow.exceptions import NoDataError


REGIONS = {
    "na1": "1",
    "euw1": "2",
    "kr": "3",
    "eun1": "4",
    "br1": "5",
    "la1": "6",
    "la2": "7",
    "oc1": "8",
    "ru": "9",
    "tr1": "10",
    "jp1": "11",
    "world": "12",
}
RANKS = {
    "challenger": "1",
    "master": "2",
    "diamond": "3",
    "platinum": "4",
    "gold": "5",
    "silver": "6",
    "bronze": "7",
    "overall": "8",
    "platinum_plus": "10",
    "diamond_plus": "11",
    "iron": "12",
    "grandmaster": "13",
    "master_plus": "14",
    "diamond_2_plus": "15",
}
ROLES = {"top": "4", "jungle": "1", "mid": "5", "adc": "3", "supp": "2", "none": "6"}
REVERSED_ROLES = {v : k for k, v in ROLES.items()}


class Fetcher:
    UGG_PRIMARY_ROLES = (
        "https://stats2.u.gg/lol/1.1/primary_roles/{underscored_patch}/1.4.0.json"
    )
    UGG_OVERVIEW = "https://stats2.u.gg/lol/1.1/overview/{underscored_patch}/{ugg_queue_name}/{champion_id}/1.4.0.json"
    UGG_RANKINGS = "https://stats2.u.gg/lol/1.1/rankings/{underscored_patch}/{ugg_queue_name}/{champion_id}/1.4.0.json"

    def __init__(self, champion_id: str, current_queue: Queue, underscored_patch: str):
        session = requests.Session()
        session.headers.update({"User-Agent": UAS})

        try:
            self.primary_roles = session.get(
                self.UGG_PRIMARY_ROLES.format(underscored_patch=underscored_patch)
            ).json()[champion_id]
            self.overview = session.get(
                self.UGG_OVERVIEW.format(
                    underscored_patch=underscored_patch,
                    ugg_queue_name=current_queue.ugg_queue_name,
                    champion_id=champion_id,
                )
            ).json()
            self.rankings = session.get(
                self.UGG_RANKINGS.format(
                    underscored_patch=underscored_patch,
                    ugg_queue_name=current_queue.ugg_queue_name,
                    champion_id=champion_id,
                )
            ).json()
        except JSONDecodeError:
            raise NoDataError

    def primary_roles_data(self) -> RoleList:
        return RoleList(
            [
                ALL_ROLES.get_role_by_ugg_role_name(REVERSED_ROLES[str(ugg_role_number)])
                for ugg_role_number in self.primary_roles
            ]
        )

    def overview_data(self, region: str, rank: str, role: Role) -> Optional[Dict[str, Any]]:
        data = self.overview[REGIONS[region]][RANKS[rank]].get(ROLES[str(role.ugg_role_name)], None)
        if data is None:
            return
        data = data[0]
        item_4_options = list()
        for option in data[5][0]:
            item_4_options.append(
                {"item": option[0], "wins": option[1], "matches": option[2]}
            )
        item_5_options = list()
        for option in data[5][1]:
            item_5_options.append(
                {"item": option[0], "wins": option[1], "matches": option[2]}
            )
        item_6_options = list()
        for option in data[5][2]:
            item_6_options.append(
                {"item": option[0], "wins": option[1], "matches": option[2]}
            )
        return {
            "runes": {
                "matches": data[0][0],
                "wins": data[0][1],
                "primary_style": data[0][2],
                "secondary_style": data[0][3],
                "runes": data[0][4],
            },
            "summoner_spells": {
                "matches": data[1][0],
                "wins": data[1][1],
                "summoner_spells": data[1][2],
            },
            "starting_items": {
                "matches": data[2][0],
                "wins": data[2][1],
                "starting_items": data[2][2],
            },
            "core_items": {
                "matches": data[3][0],
                "wins": data[3][1],
                "core_items": data[3][2],
            },
            "abilities": {
                "matches": data[4][0],
                "wins": data[4][1],
                "ability_order": data[4][2],
                "ability_max_order": list(data[4][3]),
            },
            "item_4_options": item_4_options,
            "item_5_options": item_5_options,
            "item_6_options": item_6_options,
            "wins": data[6][0],
            "matches": data[6][1],
            "low_sample_size_warning": data[7],
            "shards": {"matches": data[8][0], "wins": data[8][1], "shards": data[8][2]},
        }

    def rankings_data(self, region: str, rank: str, role: Role) -> Optional[Dict[str, Any]]:
        data = self.rankings[REGIONS[region]][RANKS[rank]].get(
            ROLES[str(role.ugg_role_name)], None
        )
        if data is None:
            return
        matchups = list()
        for matchup in data[12]:
            matchups.append(
                {
                    "champion_id": matchup[0],  # id of matchup champion
                    "wins": data[1],  # number of wins against matchup champion
                    "matches": data[
                        2
                    ],  # number of games played against matchup champion
                }
            )
        return {
            "wins": data[0],  # number of matches played with champion that were won
            "matches": data[1],  # number of matches played with champion, won or lost
            "rank": data[2],  # winrate rank out of all champions in this role
            "total_rank": data[3],  # number of champions in this role
            "total_damage": data[4],  # total damage across all games played
            "total_gold": data[5],  # total gold across all games played
            "total_kills": data[6],  # total kills across all games played
            "total_assists": data[7],  # total assists across all games played
            "total_deaths": data[8],  # total deaths across all games played
            "total_cs": data[9],  # total cs across all games played
            "matches_banned": data[10],  # number of matches where champion was banned
            "matches_not_banned": data[
                11
            ],  # number of matches where champion was not banned
            "matchups": matchups,  # matchups list
            "matches_played_and_not_played": data[
                13
            ],  # total number of matches played in this region and rank, with or without the champion
        }
