from typing import List, Any

import urllib3
import requests
from requests.models import Response
from requests.exceptions import ConnectionError

from shadow.apis.auth import Auth
from shadow.exceptions import LeagueProcessNotFoundError


class Lcu:
    """
    Lcu api connector
    """

    def __init__(self):

        # don't verify ssl
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        auth = Auth()

        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json"
        })
        self.session.auth = ("riot", auth.key)
        self.session.verify = False
        self.BASE_URL = f"https://127.0.0.1:{auth.port}/"

    def get(self, endpoint: List[str]) -> Response:
        """
        GETs an endpoint
        Returns requests response object

        endpoint - iterable that is joined to form the endpoint path
        """

        url = self.make_url(endpoint)
        return self.request("get", url)

    def delete(self, endpoint: List[str]) -> Response:
        """
        DELETEs to an endpoint
        Returns requests response object

        endpoint - iterable that is joined to form the endpoint path
        """

        url = self.make_url(endpoint)
        return self.request("delete", url)
        
    def post(self, endpoint: List[str], data: Any) -> Response:
        """
        POSTs to an endpoint
        Returns requests response object

        endpoint - iterable that is joined to form the endpoint path
        data - data to POST
        """

        url = self.make_url(endpoint)
        return self.request("post", url, json=data)

    def put(self, endpoint: List[str], data: Any) -> Response:
        """
        PUTS to an endpoint
        Returns requests response object

        endpoint - iterable that is joined to form the endpoint path
        data - data to PUT
        """

        url = self.make_url(endpoint)
        return self.request("put", url, json=data)

    def patch(self, endpoint: List[str], data: Any) -> Response:
        """
        PATCHes to an endpoint
        Returns requests response object

        endpoint - iterable that is joined to form the endpoint path
        data - data to PATCH
        """

        url = self.make_url(endpoint)
        return self.request("patch", url, json=data)

    def make_url(self, endpoint: List[str]) -> str:
        """
        Constructs a url from an endpoint iterable
        Returns url string

        endpoint - iterable that is joined to form the endpoint path
        """

        return self.BASE_URL + "/".join(endpoint)

    def request(self, *args, **kwargs) -> Response:
        """
        Performs an http request

        Returns requests response object
        """

        try:
            return self.session.request(*args, **kwargs)
        except ConnectionError:
            raise LeagueProcessNotFoundError

    def get_summoner_id(self):
        """
        Returns the summoner id for the current summoner
        """

        return self.get(["lol-summoner", "v1", "current-summoner"]).json()["summonerId"]