import typing

from .initialization import ValidationTypeError, initialize, undefined, get_initializer, is_binary_field


class Enum(type):
    def __new__(mcs, *args, **kwargs):
        cls = super().__new__(mcs, *args, **kwargs)
        cls.__new__ = mcs.ctor
        return cls

    def __iter__(self):
        return (value for key, value in self.__dict__.items() if not key.startswith("_"))

    def __contains__(self, item):
        return item in self.__iter__()

    def ctor(enum, value):
        if value not in enum:
            raise ValueError(
                f"Invalid value `{value}` for {enum.__name__}. "
                f"Available values: {', '.join(enum)}."
            )
        return value

    def __initialize__(self, value, field_name: str = None, force_validation: bool = False):
        # Validation errors for enums are ignored for forward compatibility.
        # We might need a better solution because this implementation
        # allows any value to be interpreted as an enum member.
        return value


class Record(dict):
    def __init__(self, *args, **kwargs):
        for field, initial_value in self.__initial__.items():
            kwargs.setdefault(field, initial_value)
        super().__init__(*args, **kwargs)

    def __init_subclass__(cls, **kwargs):
        cls.__fields__ = cls.collect_fields(cls.mro())
        cls.__binary_fields__ = cls.collect_binary_fields()
        cls.__initial__ = {}
        cls.__initializers__ = {}
        for field in cls.__fields__.keys():
            initial_value = getattr(cls, field, None)
            if initial_value is not None:
                cls.__initial__[field] = initial_value

            field_type = cls.__fields__[field]
            try:
                cls.__initializers__[field] = get_initializer(field_type, force_validation=True)
            except initialization.InitializerNotFound:
                pass

        cls.__traverse__ = {}
        for field, field_type in cls.__fields__.items():
            cls.__traverse__[field] = cls.should_traverse(field_type)

    @staticmethod
    def collect_fields(mro):
        fields = {}
        for cls in mro:
            annotations = cls.__dict__.get("__annotations__", {})
            fields.update(annotations)
        return fields

    @classmethod
    def collect_binary_fields(cls):
        binary_fields = set()

        for field, field_type in cls.__fields__.items():
            if is_binary_field(field_type):
                binary_fields.add(field)
            else:
                child_record = None

                generic = getattr(field_type, "__origin__", None)
                if generic and generic is typing.Union:
                    child_record = None
                    for arg in field_type.__args__:
                        if type(arg) is type and issubclass(arg, Record):
                            child_record = arg
                            break
                elif type(field_type) is type and issubclass(field_type, Record):
                    child_record = field_type

                if child_record:
                    binary_fields.update(
                        f"{field}.{child_field}"
                        for child_field in child_record.collect_binary_fields()
                    )
        return binary_fields

    @classmethod
    def should_traverse(cls, field_type):
        if hasattr(field_type, "__origin__"):
            generic_type = field_type.__origin__
            if generic_type in [typing.Union, list, typing.List, dict, typing.Dict]:
                structure_found = False
                for item_type in field_type.__args__:
                    structure_found |= cls.should_traverse(item_type)
                    if structure_found:
                        return structure_found
        elif type(field_type) is not type:
            return False  # literal type (number, string, dict (capabilities))
        elif issubclass(field_type, Record):
            return True
        # Other base types (we shouldn't traverse)
        return False

    def keys(self):
        return self.__fields__.keys()

    def copy(self):
        return self.__class__(**self)

    def __getattr__(self, key):
        if key in self.keys():
            try:
                return super().__getitem__(key)
            except KeyError:
                return None
        return super().__getattribute__(key)

    def __setattr__(self, key, value):
        if key in self.keys():
            super().__setitem__(key, value)
        return super().__setattr__(key, value)

    def __setitem__(self, key, value):
        if key not in self.keys():
            raise KeyError(key)
        super().__setattr__(key, value)
        return super().__setitem__(key, value)

    @classmethod
    def __initialize__(cls, value, field_name: str = None, force_validation: bool = False):
        if not isinstance(value, dict):
            raise ValidationTypeError(dict, value)

        prefix = f"{field_name}." if field_name else ""
        kwargs = {}
        if hasattr(cls, "__fields__"):
            for field_name, field_type in cls.__fields__.items():
                field_value = value.get(field_name, undefined)
                # As Union type isn't supported in the idl.cpp library,
                # there is no need to explicitly identify a type of a field.
                # The Optional[field_type] is used as assumption if the field has an actual value
                # or None in case field's value is undefined.
                # In case field's value is None, it translates to 'undefined' object.
                if field_value is None:
                    field_value = undefined

                initializer = cls.__initializers__.get(field_name)
                if initializer and (cls.__traverse__[field_name] or __debug__ or force_validation):
                    initialized_value = initializer.__initialize__(
                        field_value, prefix + field_name, force_validation
                    )
                else:
                    initialized_value = field_value

                if initialized_value is not undefined:
                    kwargs[field_name] = initialized_value
        return cls(**kwargs)


class Literal:
    def __init__(self, value):
        self.value = value

    def __get__(self, instance, owner):
        if instance:
            return self.value
        return self

    def __set__(self, instance, value):
        if instance:
            self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return repr(self.value)

    def __eq__(self, other):
        return self.value == getattr(other, "value", None)

    def __hash__(self):
        return id(self)

    def __initialize__(self, value, field_name: str = None, force_validation: bool = False):
        if self.value == value:
            return value
        if __debug__ or force_validation:
            raise ValidationTypeError(self.value, value, field_name)
        raise

    def __call__(self):
        return self.value
