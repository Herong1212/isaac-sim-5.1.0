import collections
from abc import ABC, abstractmethod
from typing import Type, Tuple, List, Union, AsyncIterator, TypeVar, Iterable

from idl.data.serializers import Serializer

T = TypeVar("T", bound=dict)


class Marshaller(ABC):
    @classmethod
    def name(cls) -> str:
        # Binary separately
        return "bs"

    def __init_subclass__(cls, **kwargs):
        Marshaller.register(cls)

    @staticmethod
    def register(cls: Type['Marshaller']):
        name = cls.name()
        if name:
            registry[name] = cls

    @staticmethod
    def get_all() -> Iterable[Type['Marshaller']]:
        return registry.values()

    @classmethod
    def create(cls, name: str, serializer: str) -> 'Marshaller':
        marshaller_cls = registry.get(name)
        if marshaller_cls is None:
            raise ValueError(f"Marshaller {name!r} is not registered.")
        serializer = Serializer.create(serializer)
        return marshaller_cls(serializer)

    def __init__(self, serializer: Serializer):
        self.serializer = serializer

    async def marshal(self, data: T, from_type: Type[T] = None) -> Tuple[bytes, List["ByteField"]]:
        if from_type is None:
            from_type = type(data)

        data = data.copy()
        byte_fields = self.introspect(data, from_type)
        byte_values = []
        for byte_field in byte_fields:
            byte_values.append([byte_field.name, byte_field.get()])
            byte_field.delete()

        content = await self.serializer.serialize(data, from_type)

        byte_fields = []
        for field, binary in byte_values:
            byte_field = ByteField(field, data)
            byte_field.set(binary)
            byte_fields.append(byte_field)
        return content, byte_fields

    async def unmarshal(self, data: bytes) -> dict:
        return await self.serializer.deserialize(data)

    def introspect(self, data: dict, data_type: Type[T]) -> List["ByteField"]:
        binary_fields = getattr(data_type, "__binary_fields__", None)
        if binary_fields is not None:
            return [ByteField(field, data) for field in binary_fields]

        def _find(current, node=""):
            if current in (bytes, bytearray):
                yield ByteField(node, data)
            elif hasattr(current, "__origin__"):
                generic_type = current.__origin__
                if generic_type is Union:
                    for item_type in current.__args__:
                        for info in _find(item_type, node):
                            if info:
                                yield ByteField(node, data)
                                return
                elif generic_type is AsyncIterator or generic_type is collections.abc.AsyncIterator:
                    item_type = current.__args__[0]
                    if item_type in (bytes, bytearray):
                        yield ByteField(node, data)
            elif hasattr(current, "__annotations__"):
                for field, field_type in current.__annotations__.items():
                    yield from _find(field_type, _move(node, to=field))

        def _move(node, to):
            if node:
                return node + "." + to
            return to

        return list(_find(data_type))


class ByteField:
    name: str

    def __init__(self, name, owner):
        self.name = name
        self.owner = owner

    def get(self):
        def _get(obj, path):
            if not path:
                return obj
            try:
                current_path, next_path = path.split(".", maxsplit=1)
            except ValueError:
                current_path, next_path = path, None

            if isinstance(obj, dict):
                return _get(obj.get(current_path), next_path)
            elif isinstance(obj, list):
                index = int(current_path)
                return _get(obj[index], next_path)
            else:
                raise AttributeError("Can't find path.")
        return _get(self.owner, self.name)

    def set(self, value):
        def _set(obj, path):
            if not path:
                return value
            try:
                current_path, next_path = path.split(".", maxsplit=1)
            except ValueError:
                current_path, next_path = path, None

            if isinstance(obj, dict):
                obj[current_path] = _set(obj.get(current_path), next_path)
            elif isinstance(obj, list):
                index = int(current_path)
                obj[index] = _set(obj[index], next_path)
            else:
                raise AttributeError("Can't find path.")
            return obj
        return _set(self.owner, self.name)

    def delete(self):
        def _del(obj, path):
            try:
                current_path, next_path = path.split(".", maxsplit=1)
            except ValueError:
                current_path, next_path = path, None

            if not next_path:
                if path in obj:
                    del obj[path]
                return
            if isinstance(obj, dict):
                _del(obj.get(current_path), next_path)
            elif isinstance(obj, list):
                index = int(current_path)
                return _del(obj[index], next_path)
            else:
                raise AttributeError("Can't find path.")
        return _del(self.owner, self.name)


registry = {}
Marshaller.register(Marshaller)
