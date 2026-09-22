import abc
import collections.abc
import inspect
import re
import typing

forward_ref_re = re.compile(r"_ForwardRef\(\'.*\'\)")


def get_initializer(return_type, force_validation):
    try:
        if isinstance(return_type, Initializer) or issubclass(return_type, Initializer):
            # Type can validate itself
            return return_type
    except TypeError:
        pass

    generic = get_generic_initializer(return_type, force_validation)
    if generic:
        # Type is generic, it should validate itself and its item types
        return generic

    # We shouldn't traverse through BuiltinTypeInitializer structures in case validation is disabled
    if __debug__ or force_validation:
        # Type isn't a generic type and doesn't have __initialize__ classmethod.
        # We should pick one of our builtin initializers to parse specified data type.
        initializer = initializers.get(return_type)
        if initializer:
            return initializer

        if hasattr(return_type, "__mro__"):
            for typ in return_type.__mro__:
                initializer = initializers.get(typ)
                if initializer:
                    return initializer
        else:
            # Type can be a literal type. For Python < 3.8 we use type assignment to create such aliases.
            # These type assignments interpreted as forward references.
            if forward_ref_re.match(str(return_type)):
                return BuiltinTypeInitializer(str)

            if type(return_type) in initializers.keys():
                return initializers[type(return_type)]
        raise InitializerNotFound(return_type)
    return None


T = typing.TypeVar("T")


def initialize(value: typing.Any, value_type: typing.Type[T] = None,
    value_name: str = None, force_validation: bool = False) -> T:
    if value_type is None:
        value_type = type(value)
    initializer = get_initializer(value_type, force_validation)
    return initializer.__initialize__(value, value_name, force_validation) if initializer else value


class Initializer(abc.ABC):
    @classmethod
    def __subclasshook__(cls, subclass):
        return hasattr(subclass, "__initialize__")

    @classmethod
    @abc.abstractmethod
    def __initialize__(cls, value, field_name: str = None, force_validation: bool = False):
        ...


class ValidationError(Exception):
    pass


class InitializerNotFound(Exception):
    def __init__(self, validated_type):
        self.validated_type = validated_type

    def __str__(self):
        return (
            f"Initializer for {self.validated_type} was not found. "
            f"You can implement __initialize__ classmethod in {self.validated_type} to parse client's data."
        )


class ValidationTypeError(ValidationError):
    def __init__(self, expected_type, value, field_name=None):
        self.expected_type = expected_type
        self.value_type = self.cast(value)
        self.value = value
        self.field_name = field_name

    def __str__(self):
        if self.field_name:
            return f"`{self.field_name}` must be {self.type_name(self.expected_type)}, got {self.type_name(self.value_type)}."
        return f"Expected {self.type_name(self.expected_type)}, got {self.type_name(self.value_type)}."

    @staticmethod
    def cast(value):
        if isinstance(value, list):
            try:
                item = value.pop()
                if item:
                    return typing.List[item.__class__]
                else:
                    return typing.List
            except IndexError:
                return typing.List
        else:
            return value.__class__

    @staticmethod
    def type_name(value_type):
        if hasattr(value_type, "__name__"):
            value_type_name = value_type.__name__
            value_type_args = getattr(value_type, "__args__", [])
            if value_type_args:
                value_type_name += f"[{', '.join((ValidationTypeError.type_name(arg) for arg in value_type_args))}]"
            return value_type_name
        return str(value_type)


class BuiltinTypeInitializer(Initializer):
    def __init__(self, builtin_type, strict=False):
        self.builtin_type = builtin_type
        self.strict = strict

    def __initialize__(self, value, field_name: str = None, force_validation: bool = False):
        if value is None:
            raise ValidationTypeError(expected_type=self.builtin_type, value=None, field_name=field_name)

        if self.strict:
            if isinstance(value, self.builtin_type):
                return value
            else:
                raise ValidationTypeError(expected_type=self.builtin_type, value=value, field_name=field_name)

        try:
            return self.builtin_type(value)
        except (TypeError, ValueError):
            raise ValidationTypeError(expected_type=self.builtin_type, value=value, field_name=field_name)


class NoneInitializer(Initializer):
    @classmethod
    def __initialize__(cls, value, field_name: str = None, force_validation: bool = False):
        if value is not None and value is not undefined:
            raise ValidationTypeError(expected_type=type(None), value=value, field_name=field_name)
        # As Union type isn't supported in the idl.cpp library,
        # there is no need to explicitly identify a type of a field.
        # The Optional[field_type] is used as assumption if the field has an actual value
        # or None in case field's value is undefined.
        # In case field's value is None, it translates to 'undefined' object.
        return undefined


class UnionInitializer(Initializer):
    def __init__(self, *item_types: typing.Type, force_validation):
        self.item_types = item_types
        self.item_initializers = [get_initializer(item_type, force_validation) for item_type in item_types]

    def __initialize__(self, value, field_name: str = None, force_validation: bool = False):
        # Should be validated by at least one validator
        for initializer in self.item_initializers:
            try:
                return initializer.__initialize__(value, field_name, force_validation) if initializer else value
            except ValidationError:
                pass

        expected_type = f"Union[{', '.join((str(item_type) for item_type in self.item_types))}]"
        if field_name:
            raise ValidationError(f"Unexpected type {type(value)} for `{field_name}`, must be {expected_type}.")
        raise ValidationError(f"Unexpected type {type(value)}, must be {expected_type}.")


class ListInitializer(Initializer):
    def __init__(self, item_type, force_validation):
        self.item_type = item_type
        self.item_initializer = get_initializer(item_type, force_validation)

    def __initialize__(self, value, field_name: str = None, force_validation: bool = False):
        if not isinstance(value, typing.List):
            raise ValidationTypeError(typing.List[self.item_type], value, field_name)

        if not field_name:
            field_name = ""
        return [self.item_initializer.__initialize__(item, f"{field_name}.{index}", force_validation) if self.item_initializer else item
                for index, item in enumerate(value)]


class DictInitializer(Initializer):
    def __init__(self, key_type, item_type, force_validation):
        self.key_type = key_type
        self.key_initializer = get_initializer(key_type, force_validation)
        self.item_type = item_type
        self.item_initializer = get_initializer(item_type, force_validation)

    def __initialize__(self, value, field_name: str = None, force_validation: bool = False):
        if not isinstance(value, typing.Dict):
            raise ValidationTypeError(typing.Dict[self.key_type, self.item_type], value, field_name)

        if not field_name:
            field_name = ""

        return {
            self.key_initializer.__initialize__(key, f"{field_name}.{key}.<key>", force_validation) if self.key_initializer else key:
                self.item_initializer.__initialize__(value, f"{field_name}.{key}", force_validation) if self.item_initializer else value
            for key, value in value.items()
        }


class AsyncIteratorInitializer(Initializer):
    def __init__(self, item_type, force_validation):
        self.item_type = item_type

    def __initialize__(self, value, field_name: str = None, force_validation: bool = False):
        # Validation of async iterable will consume it which can make it no longer available for the actual consumer.
        # Such iterable fields should be validated manually.
        if not inspect.isasyncgen(value) and not hasattr(value, "__aiter__"):
            raise ValidationTypeError(typing.AsyncIterator[self.item_type], value, field_name)
        return value


def get_generic_initializer(return_type, force_validation):
    generic = getattr(return_type, "__origin__", None)
    if generic:
        initializer = generic_initializers.get(generic)
        if not initializer:
            raise InitializerNotFound(generic)
        # No need to initialize AsyncIterator, traverse it only in case 'force_validation' is enabled
        if __debug__ or force_validation or not isinstance(initializer, AsyncIteratorInitializer):
            return initializer(*return_type.__args__, force_validation=force_validation)
    return None


def is_binary_field(field_type) -> bool:
    if field_type in (bytes, bytearray):
        return True
    generic = getattr(field_type, "__origin__", None)
    if generic:
        generic_args = getattr(field_type, "__args__", [])
        if generic in (collections.abc.AsyncIterator, typing.AsyncIterator) and bytes in generic_args:
            return True
        elif generic is typing.Union:
            return any(is_binary_field(arg) for arg in generic_args)
    return False


generic_initializers = {
    typing.Union: UnionInitializer,
    typing.List: ListInitializer,
    list: ListInitializer,
    typing.Dict: DictInitializer,
    dict: DictInitializer,
    typing.AsyncIterator: AsyncIteratorInitializer,
    collections.abc.AsyncIterator: AsyncIteratorInitializer,
}

initializers = {
    int: BuiltinTypeInitializer(int),
    str: BuiltinTypeInitializer(str, strict=True),
    float: BuiltinTypeInitializer(float),
    bool: BuiltinTypeInitializer(bool, strict=True),
    bytes: BuiltinTypeInitializer(bytes),
    bytearray: BuiltinTypeInitializer(bytearray),
    type(None): NoneInitializer,
    dict: BuiltinTypeInitializer(dict),
}

undefined = object()
