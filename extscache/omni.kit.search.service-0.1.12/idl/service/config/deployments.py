from typing import List, Optional, Dict

from idl.service.config.fields import File, String
from idl.types import Record, initialize

import yaml


class DeploymentTransport(Record):
    type: str
    params: dict
    meta: Optional[dict]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.meta is None:
            self.meta = {}


class Deployment(Record):
    name: str
    transport: DeploymentTransport
    meta: Optional[Dict[str, str]]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.meta:
            self.meta = {}


class DeploymentConfig(Record):
    reg: List[Deployment]


class DeploymentFile(File):
    def get_value_type(self) -> type:
        return DeploymentConfig

    def parse(self, value: Optional[str]) -> Optional[DeploymentConfig]:
        if not value:
            return None

        with open(value) as file:
            raw = file.read()
            data = yaml.safe_load(raw)
            config = DeploymentConfig(**data)
            return initialize(config, force_validation=True)


class DeploymentString(String):
    def get_value_type(self) -> type:
        return DeploymentConfig

    def parse(self, value: Optional[str]) -> Optional[str]:
        if not value:
            return None

        data = yaml.safe_load(value)
        config = DeploymentConfig(**data)
        return initialize(config, force_validation=True)
