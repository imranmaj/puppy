import json
from pathlib import Path
from typing import Any

from puppy.static import CONFIG_FILENAME, CONFIG_STRUCTURE


class Config:
    def __init__(self):
        default = {
            name: field_structure["default"]
            for name, field_structure in CONFIG_STRUCTURE.items()
        }
        if not Path(CONFIG_FILENAME).exists():
            with open(CONFIG_FILENAME, "w") as f:
                json.dump(default, f, indent=4)
            print(f"Config file not found, created a config file {CONFIG_FILENAME}")

        with open(CONFIG_FILENAME, "r") as f:
            self.config = json.load(f)

        # add missing entries to outdated config
        for k, v in default.items():
            if k not in self.config:
                print(f"Adding missing config field {k}")
                self.config[k] = v

        # convert fields in outdated config
        for k, v in self.config.items():
            if "should_convert" in CONFIG_STRUCTURE[k] and CONFIG_STRUCTURE[k][
                "should_convert"
            ](v):
                print(f"Converting config field {k}")
                self.config[k] = CONFIG_STRUCTURE[k]["converter"](v)

        with open(CONFIG_FILENAME, "w") as f:
            json.dump(self.config, f, indent=4)

        # validate
        for k, v in self.config.items():
            expected_type = CONFIG_STRUCTURE[k]["type"]
            if not isinstance(v, expected_type):
                raise ValueError(
                    f"Invalid type for config field {k}, expected {expected_type.__name__} but found {type(v).__name__}"
                )

            if "validator" in CONFIG_STRUCTURE[k]:
                CONFIG_STRUCTURE[k]["validator"](v)

    def __getattr__(self, attr: str) -> Any:
        return self.config[attr]

config = Config()
