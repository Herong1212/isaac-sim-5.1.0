import json
import typing

from idl.types import Record
from .json import JSONSerializer
from . import T


class OmniJSONSerializer(JSONSerializer):
    @classmethod
    def name(cls) -> str:
        return "omni_json"

    def validation(self, data):
        data_type = type(data)
        if data_type in [dict, typing.Dict]:
            for item in data:
                self.validation(item)
                self.validation(data[item])
        elif data_type in [list, typing.List]:
            for item in data:
                self.validation(item)
        elif issubclass(data_type, Record):
            for field in data.__fields__.keys():
                value = getattr(data, field, None)
                self.validation(value)
        elif data_type is str:
            if '\0' in data:
                raise ValueError(f"String {data} contains terminate symbol")

    async def serialize(self, data: T, from_type: typing.Type[T] = None) -> bytes:
        self.validation(data)
        return json.dumps(data).encode()