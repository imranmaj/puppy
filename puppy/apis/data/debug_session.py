import traceback

import requests
from requests import Session, Response

from puppy.config import config

DEBUG_FILENAME = "puppy.log"


class DebugSession:
    def __init__(self, session: Session):
        self.session = session

    def get(self, *args, **kwargs) -> Response:
        return self._request("GET", *args, **kwargs)

    def post(self, *args, **kwargs) -> Response:
        return self._request("POST", *args, **kwargs)

    def _request(self, method, *args, **kwargs) -> Response:
        if config.debug:
            with open(DEBUG_FILENAME, "w", encoding="utf-8") as f:
                f.write("\n".join([method, str(args), str(kwargs), "\n"]))

        try:
            r = self.session.request(method, *args, **kwargs)
        except Exception as e:
            if config.debug:
                with open(DEBUG_FILENAME, "a", encoding="utf-8") as f:
                    traceback.print_exc(file=f)
            raise

        if config.debug:
            with open(DEBUG_FILENAME, "a", encoding="utf-8") as f:
                f.write(
                    "\n".join(
                        [
                            "status",
                            str(r.status_code),
                            "headers",
                            str(r.headers),
                            "body",
                            r.text,
                        ]
                    )
                )

        return r
