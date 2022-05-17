from typing import Dict, Any, Optional

import requests

from puppy.static import UAS
from puppy.models import RoleList, Role, Queue
from puppy.apis.ddragon.patches import Patches
from puppy.apis.ddragon.champions import Champions


RANKS = [
    "Diamond2Plus",
    "Master",
    "Gold",
    "Diamond",
    "Platinum",
    "DiamondPlus",
    "All",
    "PlatinumPlus",
    "Pro",
    "Silver",
    "Challenger",
    "MasterPlus",
    "GrandMaster",
    "Bronze",
    "Iron",
]
REGIONS = [
    "ALL",
    "BR",
    "EUNE",
    "EUW",
    "JP",
    "KR",
    "LAN",
    "LAS",
    "NA",
    "OCE",
    "RU",
    "TR",
]


class Fetcher:
    def __init__(self, champion_id: str, current_queue: Queue, patch: str):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": UAS})

        # r = self.session.post(
        #     "https://app.mobalytics.gg/api/lol/graphql/v1/query",
        #     json={
        #         "operationName": "LolChampionPageQuery",
        #         "variables": {
        #             "slug": "garen",
        #             "summonerName": None,
        #             "summonerRegion": None,
        #             "buildId": None,
        #             # "buildId": 865823222,
        #             "vsChampionRole": None,
        #             "matchups": None,
        #             "role": None,
        #             "queue": None,
        #             "region": None,
        #             "proPlayerType": None,
        #             "rank": None,
        #             "matchResult": None,
        #             "withCommon": True,  # needed for roles
        #             "withRoleSpecificCommon": False,
        #             "withGuidesData": False,
        #             "withBuildsList": True,
        #             "withRunesBuildsList": False,
        #             "withAramBuildsList": True,
        #             "withCountersList": False,
        #             "withCountersStats": False,
        #             "withFilters": True,
        #             "withBuild": True,
        #             "withRunesBuild": False,
        #             "withAramBuild": True,
        #             "withCounter": False,
        #             "withProBuilds": False,
        #             "withProBuildsMatches": False,
        #             "sortField": "WR",
        #             "order": "DESC",
        #             "patch": "12.8"
        #         },
        #         "extensions": {
        #             "persistedQuery": {
        #                 "version": 1,
        #                 "sha256Hash": "b8bb420a9484863bceda642c365d9bbae62f6531654572620e86a7ca1532202c",
        #             }
        #         },
        #     },
        # )
        # with open("data3.json", "w") as f:
        #     import json

        #     json.dump(r.json(), f)

        data = self.get_data(
            champion_id=champion_id,
            build_id=None,
            role=None,
            queue=current_queue,
            region=None,
            rank=None,
            patch=patch,
        )
        with open("data3.json", "w") as f:
            import json

            json.dump(data, f)
        raise SystemExit

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
        r = self.session.post(
            "https://app.mobalytics.gg/api/lol/graphql/v1/query",
            json={
                "operationName": "LolChampionPageQuery",
                "variables": {
                    "slug": Champions.alternate_name_for_id(champion_id).lower(),
                    "summonerName": None,
                    "summonerRegion": None,
                    "buildId": build_id,
                    "vsChampionRole": None,
                    "matchups": None,
                    "role": None if role is None else role.mobalytics_role_name,
                    "queue": None if queue is None else queue.mobalytics_queue_name,
                    "region": region,
                    "proPlayerType": None,
                    "rank": rank,
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
        return r.json()
