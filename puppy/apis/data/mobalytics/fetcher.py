from functools import lru_cache
from typing import Dict, Any, Optional
from puppy.apis.data.exceptions import NoDataError

import requests

from puppy.static import ALL_ROLES, UAS
from puppy.models import RoleList, Role, Queue
from puppy.apis.ddragon.patches import Patches
from puppy.apis.ddragon.champions import Champions

RANKS = {
    "pro": "Pro",
    "challenger": "Challenger",
    "master": "Master",
    "diamond": "Diamond",
    "platinum": "Platinum",
    "gold": "Gold",
    "silver": "Silver",
    "bronze": "Bronze",
    "overall": "All",
    "platinum_plus": "PlatinumPlus",
    "diamond_plus": "DiamondPlus",
    "iron": "Iron",
    "grandmaster": "GrandMaster",
    "master_plus": "MasterPlus",
    "diamond_2_plus": "Diamond2Plus",
}
REGIONS = {
    "na1": "NA",
    "euw1": "EUW",
    "kr": "KR",
    "eun1": "EUNE",
    "br1": "BR",
    "la1": "LAN",
    "la2": "LAS",
    "oc1": "OCE",
    "ru": "RU",
    "tr1": "TR",
    "jp1": "JP",
    "world": "ALL",
}


class Fetcher:
    def __init__(self, champion_id: str, current_queue: Queue, patch: str):
        self.champion_id = champion_id
        self.current_queue = current_queue
        self.patch = patch

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": UAS})

        self.initial_data = self.get_data(
            champion_id=champion_id,
            build_id=None,
            role=None,
            queue=current_queue,
            region="world",
            rank=current_queue.rank,
            patch=patch,
        )

    @lru_cache()
    def primary_roles(self) -> RoleList:
        for champion_roles in self.initial_data["championRoles"]["champions"]:
            if int(self.champion_id) == int(champion_roles["id"]):
                roles = []
                for mobalytics_role_name in champion_roles["roles"]:
                    role = ALL_ROLES.get_role_by_mobalytics_role_name(
                        mobalytics_role_name
                    )
                    if role is not None:
                        roles.append(role)
                return RoleList(roles)
        raise NoDataError(
            f"No roles data for champion={Champions.name_for_id(self.champion_id)}, queue={self.current_queue}, rank={self.current_queue.rank}, patch={self.patch}"
        )

    @lru_cache()
    def get_build(self, region: str, role: Role) -> Dict[str, Any]:
        data_in_role = self.get_data(
            champion_id=self.champion_id,
            build_id=None,
            role=role,
            queue=self.current_queue,
            region=region,
            rank=self.current_queue.rank,
            patch=self.patch,
        )
        for build in data_in_role["builds"]["buildsOptions"]["options"]:
            if build["type"] == "MOST_POPULAR":
                build_id = build["id"]
                break
        else:
            raise NoDataError(
                f"No data for champion={Champions.name_for_id(self.champion_id)}, queue={self.current_queue}, rank={self.current_queue.rank}, patch={self.patch}"
            )

        build = self.get_data(
            champion_id=self.champion_id,
            build_id=build_id,
            role=role,
            queue=self.current_queue,
            region=region,
            rank=self.current_queue.rank,
            patch=self.patch,
        )["selectedBuild"]["build"]
        starter_items = {}
        early_items = {}
        core_items = {}
        situational_items = {}
        full_build_items = {}
        for item_chunk in build["items"]:
            if item_chunk["type"] == "Starter":
                starter_items = item_chunk
            elif item_chunk["type"] == "Early":
                early_items = item_chunk
            elif item_chunk["type"] == "Core":
                core_items = item_chunk
            elif item_chunk["type"] == "Situational":
                situational_items = item_chunk
            elif item_chunk["type"] == "FullBuild":
                full_build_items = item_chunk
        return {
            "runes": {
                "primary_style": build["perks"]["style"],
                "secondary_style": build["perks"]["subStyle"],
                "runes": build["perks"]["IDs"],
            },
            "summoner_spells": build["spells"],
            "starting_items": starter_items["items"],
            "early_items": early_items["items"],
            "core_items": core_items["items"],
            "situational_items": situational_items["items"],
            "full_build_items": full_build_items["items"],
            "abilities": {
                "ability_order": build["skillOrder"],
                "ability_max_order": build["skillMaxOrder"],
            },
            "stats": {
                "matches": build["stats"]["matchCount"],
                "wins": build["stats"]["wins"],
            },
        }

    @lru_cache()
    def get_data(
        self,
        champion_id: str,
        build_id: Optional[str],
        role: Optional[Role],
        queue: Optional[Queue],
        region: Optional[str],
        rank: Optional[str],
        patch: str,
    ) -> Dict[str, Any]:
        alternate_name = Champions.alternate_name_for_id(champion_id)
        if alternate_name is None:
            raise ValueError(f"Unknown champion id {champion_id}")
        r = self.session.post(
            "https://app.mobalytics.gg/api/lol/graphql/v1/query",
            json={
                "operationName": "LolChampionPageQuery",
                "variables": {
                    "slug": alternate_name.lower(),  # type: ignore
                    "summonerName": None,
                    "summonerRegion": None,
                    "buildId": build_id,
                    "vsChampionRole": None,
                    "matchups": None,
                    "role": None if role is None else role.mobalytics_role_name,
                    "queue": None if queue is None else queue.mobalytics_queue_name,
                    "region": None if region is None else REGIONS[region],
                    "proPlayerType": None,
                    "rank": None if rank is None else RANKS[rank],
                    "matchResult": None,
                    "withCommon": True,  # needed for roles
                    "withRoleSpecificCommon": False,
                    "withGuidesData": False,
                    "withBuildsList": True,
                    "withRunesBuildsList": False,
                    "withAramBuildsList": True,
                    "withCountersList": False,
                    "withCountersStats": False,
                    "withFilters": True,
                    "withBuild": True,
                    "withRunesBuild": False,
                    "withAramBuild": True,
                    "withCounter": False,
                    "withProBuilds": False,
                    "withProBuildsMatches": False,
                    "sortField": "WR",
                    "order": "DESC",
                    "patch": Patches.major_minor(patch),
                },
                "extensions": {
                    "persistedQuery": {
                        "version": 1,
                        "sha256Hash": "b8bb420a9484863bceda642c365d9bbae62f6531654572620e86a7ca1532202c",
                    }
                },
            },
        )
        data = r.json()
        if "errors" in data or "selectedBuild" not in data["data"]["lol"]:
            raise NoDataError
        return data["data"]["lol"]