from typing import Dict

from idl.parser import SpecProcessor
from idl.schema import CustomSchema, CustomSchemaType, TypeName, Meta, PropertySchema, ConstSchemaType, Definition, \
    AliasSchemaType
from idl.spec import Spec

AsymmetricSchemaType = "asymmetric"


class AsymmetricSchema(CustomSchema):
    name: str
    type: CustomSchemaType
    schema: AsymmetricSchemaType
    client: TypeName
    server: TypeName
    comment: str
    meta: Meta


def processor(client: bool = True) -> SpecProcessor:
    def process(spec: Spec):
        asymmetric = {
            schema.name: schema
            for schema in spec.custom.values()
            if schema.schema == AsymmetricSchemaType
        }
        for interface in spec.interfaces.values():
            for field in interface.fields:
                specify_const(field, asymmetric, spec, client)

            for func in interface.functions:
                for param in func.params:
                    specify_const(param, asymmetric, spec, client)
        for struct in spec.structs.values():
            for field in struct.fields:
                specify_const(field, asymmetric, spec, client)
    return process


def specify_const(param: PropertySchema, asymmetric: Dict[str, AsymmetricSchema], spec: Spec, client: bool):
    asymmetric_type: AsymmetricSchema = asymmetric.get(param.type)
    if asymmetric_type:
        ref = asymmetric_type.client if client else asymmetric_type.server
        ref_type = spec.get_type(ref)
        param.is_const = check_const(ref_type, spec)


def check_const(definition: Definition, spec: Spec) -> bool:
    if not definition:
        return False

    if definition.type == AliasSchemaType:
        try:
            definition.is_const = check_const(spec.get_type(definition.value), spec)
        except ValueError:
            definition.is_const = False
        return definition.is_const

    return definition.type == ConstSchemaType

