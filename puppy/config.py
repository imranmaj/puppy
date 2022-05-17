import json
from pathlib import Path
from typing import Any

from puppy.static import CONFIG_FILENAME, DEFAULT_CONFIG


class Config:
    def __init__(self):
        if not Path(CONFIG_FILENAME).exists():
            self.is_new = True
            with open(CONFIG_FILENAME, "w") as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
        else:
            self.is_new = False

        with open(CONFIG_FILENAME, "r") as f:
            self.config = json.load(f)

        for k, v in DEFAULT_CONFIG.items():
            if k not in self.config:
                # config is outdated
                self.config[k] = v
                with open(CONFIG_FILENAME, "w") as f:
                    json.dump(self.config, f, indent=4)

    def __getattr__(self, attr: str) -> Any:
        return self.config[attr]
