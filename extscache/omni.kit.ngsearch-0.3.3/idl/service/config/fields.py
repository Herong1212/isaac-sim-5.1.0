import os
from typing import Any, Optional

import typing


class Environment:
    def __init__(self, name: str = "", default=None, required: bool = False, choices: list = None):
        self.name = name
        self.field_name = None
        self.default = default
        self.required = required
        self.choices = choices or []
        assert default is None or not required, "`default` option shouldn't be used with `required`."

    def __set_name__(self, owner, name):
        if not self.name:
            self.name = name
        self.field_name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self

        value = instance.__dict__.get(self.field_name)
        if value is None or isinstance(value, Environment):
            instance.__dict__[self.field_name] = value = self.read()
        return value

    def __set__(self, instance, value):
        if instance is not None:
            instance.__dict__[self.field_name] = value

    def get_value_type(self) -> type:
        raise NotImplementedError()

    def read(self):
        value = os.getenv(self.name)
        if value is None:
            if self.required:
                raise EnvironmentError(self.name)
            else:
                value = self.default
        return self.parse(value)

    def parse(self, value: Optional[str]) -> Optional[Any]:
        if self.choices:
            if value not in self.choices:
                raise ValueError(f"{value!r} should be one of these values: {self.choices}.")
        return value


class String(Environment):
    def get_value_type(self) -> type:
        return str

    def parse(self, value: Optional[str]) -> Optional[str]:
        value = super().parse(value)
        if value is None:
            return value
        return str(value)


class Int(Environment):
    def get_value_type(self) -> type:
        return int

    def parse(self, value: Optional[str]) -> Optional[int]:
        value = super().parse(value)
        if value is None:
            return value
        return int(value)


class Float(Environment):
    def get_value_type(self) -> type:
        return float

    def parse(self, value: Optional[str]) -> Optional[float]:
        value = super().parse(value)
        if value is None:
            return value
        return float(value)


class Boolean(Environment):
    TRUE = ("True", "true", "1", "+", True)

    def get_value_type(self) -> type:
        return bool

    def parse(self, value: Optional[str]) -> bool:
        return value in self.TRUE


class File(Environment):
    def get_value_type(self) -> type:
        return str

    def parse(self, value: Optional[str]) -> Optional[str]:
        if not value:
            return None

        with open(value) as file:
            return file.read()


class List(Environment):
    def __init__(self, child: Environment, name: str = "", default=None, required: bool = False, separator=","):
        super().__init__(name, default, required)
        self.child = child
        self.separator = separator

    def get_value_type(self) -> type:
        return typing.List[self.child.get_value_type()]

    def parse(self, value: Optional[str]):
        if value is None:
            return value

        return [
            self.child.parse(item)
            for item in value.split(self.separator)
        ]
