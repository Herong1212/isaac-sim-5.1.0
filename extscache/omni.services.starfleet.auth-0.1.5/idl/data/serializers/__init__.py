from abc import abstractmethod, ABC
from typing import TypeVar, Type, Iterable

T = TypeVar("T", bound=dict)


class Serializer(ABC):
    @classmethod
    @abstractmethod
    def name(cls) -> str:
        ...

    def __init_subclass__(cls, **kwargs):
        Serializer.register(cls)

    @staticmethod
    def register(cls: Type['Serializer']):
        name = cls.name()
        if name:
            registry[name] = cls

    @staticmethod
    def get_all() -> Iterable[Type['Serializer']]:
        return registry.values()

    @classmethod
    def create(cls, name: str) -> 'Serializer':
        serializer_cls = registry.get(name)
        if serializer_cls is None:
            raise ValueError(f"Serializer {name!r} is not registered.")
        return serializer_cls()

    @abstractmethod
    async def serialize(self, data: T, from_type: Type[T] = dict) -> bytes:
        ...

    @abstractmethod
    async def deserialize(self, data: bytes, to_type: Type[T] = dict) -> T:
        ...


registry = {}
