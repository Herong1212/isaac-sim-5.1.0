import json
from typing import Type

from . import Serializer, T


class JSONSerializer(Serializer):
    @classmethod
    def name(cls) -> str:
        return "json"

    async def serialize(self, data: T, from_type: Type[T] = None) -> bytes:
        return json.dumps(data).encode()

    async def deserialize(self, data: bytes, to_type: Type[T] = dict) -> dict:
        return json.loads(data)
