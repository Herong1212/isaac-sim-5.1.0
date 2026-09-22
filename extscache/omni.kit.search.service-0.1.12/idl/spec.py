from typing import Dict, Optional

try:
    from idl.schema import (
        Definition, InterfaceSchema, InterfaceSchemaType, StructSchema, StructSchemaType, EnumSchema, EnumSchemaType,
        EnumMemberSchema, ConstSchema, ConstSchemaType, AliasSchema, AliasSchemaType, UnionSchema, UnionSchemaType,
        MethodSchema, MethodReturnSchema, PropertySchema, BuiltinType, Record, CustomSchema
    )
except ImportError:
    # Schema was not generated.
    # This allows low-level parser to ignore annotations and be imported for schema class generation.
    Definition = None
    InterfaceSchema = None
    InterfaceSchemaType = "interface"
    StructSchema = None
    StructSchemaType = "struct"
    EnumSchema = None
    EnumSchemaType = "enum"
    EnumMemberSchema = None
    ConstSchema = None
    ConstSchemaType = "const"
    AliasSchema = None
    AliasSchemaType = "alias"
    UnionSchema = None
    UnionSchemaType = "union"
    MethodSchema = None
    MethodReturnSchema = None
    PropertySchema = None
    BuiltinType = None
    Record = object
    CustomSchema = None


class Spec(Record):
    origin: str
    interfaces: Dict[str, InterfaceSchema]
    structs: Dict[str, StructSchema]
    enums: Dict[str, EnumSchema]
    consts: Dict[str, ConstSchema]
    aliases: Dict[str, AliasSchema]
    unions: Dict[str, UnionSchema]
    custom: Dict[str, CustomSchema]

    def __init__(self, origin: str = None, interfaces: Dict[str, InterfaceSchema] = None,
                 structs: Dict[str, StructSchema] = None, enums: Dict[str, EnumSchema] = None,
                 consts: Dict[str, ConstSchema] = None, aliases: Dict[str, AliasSchema] = None,
                 unions: Dict[str, UnionSchema] = None, custom: Dict[str, CustomSchema] = None, *, types=None):
        super().__init__()
        self.origin = origin or ""
        self._types = types or []
        self.interfaces = interfaces if interfaces is not None else {}
        self.structs = structs if structs is not None else {}
        self.enums = enums if enums is not None else {}
        self.consts = consts if consts is not None else {}
        self.aliases = aliases if aliases is not None else {}
        self.unions = unions if unions is not None else {}
        self.custom = custom if custom is not None else {}

    @property
    def types(self):
        return self._types

    def get_type(self, type_name: str):
        struct = self.structs.get(type_name)
        if struct:
            return struct
        enum = self.enums.get(type_name)
        if enum:
            return enum
        const = self.consts.get(type_name)
        if const:
            return const
        alias = self.aliases.get(type_name)
        if alias:
            return alias
        union = self.unions.get(type_name)
        if union:
            return union
        interface = self.interfaces.get(type_name)
        if interface:
            return interface
        custom = self.custom.get(type_name)
        if custom:
            return custom
        if type_name in BuiltinType:
            raise ValueError(f"Type {type_name} is builtin.")
        raise ValueError(f"Unknown type {type_name}.")

    def resolve_name(self, type_name: str):
        current = self.get_type(type_name)
        if current.type == AliasSchemaType:
            return self.resolve_name(current.value)
        return type_name
