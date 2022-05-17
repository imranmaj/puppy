from typing import Type

from .ugg import UGG
from .mobalytics import Mobalytics
from .data_source import DataSourceAbc
from puppy.environment import config

if config.backend == "ugg":
    DataSource: Type[DataSourceAbc] = UGG
elif config.backend == "mobalytics":
    DataSource: Type[DataSourceAbc] = Mobalytics
else:
    raise ValueError(f"Invalid config value for backend: {config.backend}")
