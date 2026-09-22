import importlib
from typing import Iterable, List, Callable

from idl.schema import CustomSchema, CustomSchemaType
from idl.schema._parse import _parse, group_types
from idl.spec import (
    InterfaceSchema, InterfaceSchemaType, StructSchema, StructSchemaType,
    ConstSchema, AliasSchema, UnionSchema, EnumSchema, Spec, BuiltinType,
    EnumMemberSchema,
    EnumSchemaType, UnionSchemaType, ConstSchemaType, Definition, AliasSchemaType
)

__all__ = ["group_types", "parse"]

from idl.types.initialization import initialize


# Functions that process spec after the parsing
SpecProcessor = Callable[[Spec], None]


def parse(filename: str, processors: List[SpecProcessor] = None) -> Spec:
    definition_json = _parse(filename)

    for index, definition in enumerate(definition_json["__all__"]):
        schema = None
        kind = None

        if definition["type"] == "interface":
            schema, kind = InterfaceSchema, "interfaces"
        elif definition["type"] == "struct":
            schema, kind = StructSchema, "structs"
        elif definition["type"] == "enum":
            schema, kind = EnumSchema, "enums"
        elif definition["type"] == "const":
            schema, kind = ConstSchema, "consts"
        elif definition["type"] == "alias":
            schema, kind = AliasSchema, "aliases"
        elif definition["type"] == "union":
            schema, kind = UnionSchema, "unions"
        elif definition["type"] == "custom":
            kind = "custom"
            schema_name = definition["schema"]
            module = importlib.import_module(f"idl.schema.{schema_name}")
            try:
                schema = getattr(module, f"{schema_name.title()}Schema")
            except AttributeError:
                raise RuntimeError(f"Schema '{schema_name}' is not supported.")

        if schema is None or kind is None:
            raise ValueError(f"Unknown definition {definition}.")

        definition_json["__all__"][index] = definition_json[kind][definition["name"]] = initialize(definition, schema)

    spec = Spec(types=definition_json["__all__"])
    spec.origin = definition_json.get("origin", "")
    spec.interfaces = definition_json["interfaces"]
    spec.structs = definition_json["structs"]
    spec.enums = definition_json["enums"]
    spec.consts = definition_json["consts"]
    spec.aliases = definition_json["aliases"]
    spec.unions = definition_json["unions"]
    spec.custom = definition_json["custom"]

    if processors:
        for processor in processors:
            processor(spec)
    return spec


class DependencyList(list):
    def __init__(self, spec: Spec):
        super().__init__()
        self.spec = spec
        self.item_indexes = {}

    def __delitem__(self, key):
        item: Definition = self[key]
        self._del_item_index(item)
        return super().__delitem__(key)

    def __setitem__(self, key, value: Definition):
        super().__setitem__(key, value)
        self.item_indexes[value.name] = key

    def append(self, type_name: str) -> None:
        if type_name.endswith("[]"):
            type_name = type_name[:-2]

        if type_name in BuiltinType:
            return

        index = self.item_indexes.get(type_name)
        if index is not None:
            self.pop(index)

        self.item_indexes[type_name] = len(self)
        definition = self.spec.get_type(type_name)
        super().append(definition)

    def extend(self, iterable: Iterable[Definition]) -> None:
        for item in iterable:
            self.append(item.name)

    def pop(self, index=None):
        item: Definition = super().pop(index)
        self._del_item_index(item)
        return item

    def _del_item_index(self, item: Definition):
        item_index = self.item_indexes[item.name]
        for it, ind in self.item_indexes.items():
            if ind > item_index:
                self.item_indexes[it] = ind - 1
        del self.item_indexes[item.name]


def get_dependencies(spec: Spec):
    dependencies = DependencyList(spec)
    for interface in spec.interfaces.values():
        dependencies.append(interface.name)
        dependencies.extend(
            interface_dependencies(interface, spec)
        )

    for struct in spec.structs.values():
        dependencies.append(struct.name)
        dependencies.extend(
            struct_dependencies(struct, spec)
        )

    for enum in spec.enums.values():
        dependencies.append(enum.name)
        dependencies.extend(
            enum_dependencies(enum, spec)
        )
    return dependencies


def definition_dependencies(definition: Definition, spec: Spec, deep=False):
    resolver = dependency_resolvers.get(definition.type)
    if resolver:
        return resolver(definition, spec, deep)
    raise ValueError(f"Unknown definition type {definition.type}.")


def follow_dependencies(dependencies: DependencyList, spec: Spec):
    for dependency in [*dependencies]:
        dependencies.extend(definition_dependencies(dependency, spec, deep=True))
    return dependencies


def interface_dependencies(interface: InterfaceSchema, spec: Spec, deep=False):
    dependencies = DependencyList(spec)
    for field in interface.fields:
        dependencies.append(field.type)

    for function in interface.functions:
        for param in function.params:
            dependencies.append(param.type)
        dependencies.append(function.returns.type)
    if deep:
        follow_dependencies(dependencies, spec)
    return dependencies


def struct_dependencies(struct: StructSchema, spec: Spec, deep=False) -> DependencyList:
    dependencies = DependencyList(spec)
    if struct.extends:
        dependencies.append(struct.extends)
    if struct.mapping:
        dependencies.append(struct.mapping.key)
        dependencies.append(struct.mapping.value.type)
    for field in struct.fields:
        dependencies.append(field.type)
    if deep:
        follow_dependencies(dependencies, spec)
    return dependencies


def enum_dependencies(enum: EnumSchema, spec: Spec, deep=False):
    dependencies = DependencyList(spec)
    for member in enum.members:
        referenced_type, value = enum_reference(member)
        if referenced_type:
            dependencies.append(referenced_type)
    if deep:
        follow_dependencies(dependencies, spec)
    return dependencies


def enum_reference(member: EnumMemberSchema):
    if isinstance(member.value, int):
        # Enum consists of integers.
        return None, None

    if member.value.startswith("\""):
        # Member value is a regular string.
        return None, None

    try:
        type_name, type_member = member.value.split(".")
        return type_name, type_member
    except ValueError:
        return None, None


def union_dependencies(union: UnionSchema, spec: Spec, deep=False):
    dependencies = DependencyList(spec)
    for member in union.members:
        dependencies.append(member)
    if deep:
        follow_dependencies(dependencies, spec)
    return dependencies


def alias_dependencies(alias: AliasSchema, spec: Spec, deep=False):
    dependencies = DependencyList(spec)
    dependencies.append(alias.value)
    if deep:
        follow_dependencies(dependencies, spec)
    return dependencies


def const_dependencies(const: ConstSchema, spec: Spec, deep=False):
    # Constants don't have dependencies, they reflect primitive values of builtin types
    dependencies = DependencyList(spec)
    return dependencies


def custom_dependencies(schema: CustomSchema, spec: Spec, deep=False):
    # Dependencies for custom type are unknown
    return DependencyList(spec)


dependency_resolvers = {
    InterfaceSchemaType: interface_dependencies,
    StructSchemaType: struct_dependencies,
    EnumSchemaType: enum_dependencies,
    UnionSchemaType: union_dependencies,
    AliasSchemaType: alias_dependencies,
    ConstSchemaType: const_dependencies,
    CustomSchemaType: custom_dependencies,
}
