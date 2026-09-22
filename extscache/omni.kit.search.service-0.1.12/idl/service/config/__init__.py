from idl.service.config import fields
from idl.types import Record


class BaseConfig(Record):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialize all unread values from config with values from kwargs or None
        for field_name, field in self.__config_fields__.items():
            if not isinstance(field, BaseConfig):
                self[field_name] = kwargs.get(field_name)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if not hasattr(cls, "__annotations__"):
            cls.__annotations__ = {}

        cls.__config_fields__ = {}
        for attr_name, attr in cls.__dict__.items():
            if isinstance(attr, (fields.Environment, BaseConfig)):
                cls.__config_fields__[attr_name] = attr
                cls.__annotations__[attr_name] = attr.get_value_type()
                cls.__fields__[attr_name] = attr.get_value_type()

    def __getitem__(self, item):
        if item in self.keys():
            return super().__getattribute__(item)
        raise KeyError(item)

    def __set_name__(self, owner, name):
        self._field_name = name

    def read(self):
        for field_name, field in self.__config_fields__.items():
            self[field_name] = field.read()
        return self

    def get_value_type(self):
        return self
