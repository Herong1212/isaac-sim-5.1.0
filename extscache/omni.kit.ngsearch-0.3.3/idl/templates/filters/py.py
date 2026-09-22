from typing import List

import idl.formatting
import idl.templates.filters
from idl.spec import PropertySchema, Spec, InterfaceSchema, StructSchema, MethodSchema, StructSchemaType, BuiltinType


def include(spec: Spec):
    return {
        "py.type": python_type,
        "py.type_name": python_type_name,
        "py.arguments": arguments,
        "py.request": python_request,
        "py.request_data": request_data,
        "py.request_record": request_record,
        "py.request_record_name": request_record_name,
    }


def python_type(prop: PropertySchema):
    name = python_type_name(prop.type)
    if prop.get("is_const"):
        name = f"Literal({name})"

    if prop.get("is_array"):
        name = f"List[{name}]"

    if prop.get("optional"):
        name = f"Optional[{name}]"
    return name


type_mapping = {
    BuiltinType.int8: "int",
    BuiltinType.uint8: "int",
    BuiltinType.int16: "int",
    BuiltinType.uint16: "int",
    BuiltinType.int32: "int",
    BuiltinType.uint32: "int",
    BuiltinType.int64: "int",
    BuiltinType.uint64: "int",
    BuiltinType.boolean: "bool",
    BuiltinType.number: "float",
    BuiltinType.float: "float",
    BuiltinType.double: "float",
    BuiltinType.string: "str",
    BuiltinType.bytes: "AsyncIterator[bytes]",
    BuiltinType.blob: "AsyncIterator[bytes]",
    BuiltinType.object: "dict",
}


def python_type_name(type_name: str):
    return type_mapping.get(type_name, type_name)


def arguments(params: List[PropertySchema], default="None", *, interface: InterfaceSchema = None):
    optional = []
    required = []

    if interface:
        params = params + interface.fields

    for param in params:
        if not param.is_const:
            if param.optional:
                optional.append(param)
            else:
                required.append(param)

    result = ""
    for param in required:
        name = idl.formatting.underscore(param.name)
        result += f"{name}: {python_type(param)}, "

    for param in optional:
        name = idl.formatting.underscore(param.name)
        result += f"{name}: {python_type(param)} = {default}, "
    return result[:-2]


def python_request(params: List[PropertySchema]):
    return idl.templates.filters.request(params, formatter=idl.formatting.underscore)


def request_data(params: List[PropertySchema], interface: InterfaceSchema, default="None", indent=8, variable="data"):
    def append(prop, prop_from, fallback=None):
        if prop.is_const:
            lines.append(f"{variable}[\"{prop.name}\"] = {prop.type}")
        else:
            param_var = idl.formatting.underscore(prop_from)
            if fallback:
                fallback_var = idl.formatting.underscore(fallback)
                lines.append(f"{param_var} = {param_var} if {param_var} is not {default} else {fallback_var}")

            if prop.optional:
                lines.append(f"if {param_var} is not {default}:")
                lines.append(f"    {variable}[\"{prop.name}\"] = {param_var}")
            else:
                lines.append(f"{variable}[\"{prop.name}\"] = {param_var}")

    lines = [f"{variable} = {'{}'}"]
    for field in interface.fields:
        append(field, prop_from=field.name, fallback=f"self.{field.name}")

    for param in params:
        append(param, prop_from=param.name)

    spaces = indent * " "
    return f"\n{spaces}".join(lines)


def request_record_name(method_name: str, interface_name: str):
    return idl.formatting.pascal(interface_name) + idl.formatting.pascal(method_name) + "Args"


def request_record(method: MethodSchema, interface: InterfaceSchema):
    struct: StructSchema = StructSchema()
    struct.name = request_record_name(method.name, interface.name)
    struct.type = StructSchemaType
    struct.fields = [param for param in method.params + interface.fields]
    struct.mapping = None
    struct.extends = None
    return struct
