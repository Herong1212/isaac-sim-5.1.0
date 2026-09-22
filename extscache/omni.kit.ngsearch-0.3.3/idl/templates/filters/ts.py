from typing import List

import idl.formatting
import idl.templates.filters
from idl.spec import PropertySchema, BuiltinType, Spec
from idl.schema import MethodReturnSchema
from idl.templates.filters.js import request_data


def include(spec: Spec):
    """
    Returns all filters for TypeScript to be included to renderer.
    :param spec: Parsed IDL JSON.
    """
    return {
        "ts.request": request,
        "ts.request_data": request_data,
        "ts.arguments": arguments,
        "ts.return_type": return_type,
        "ts.type": ts_type,
    }


def arguments(params: List[PropertySchema]):
    result = ""
    for param in params:
        if param.is_const:
            continue
        result += idl.formatting.camel(param.name)
        if param.optional:
            result += "?"
        result += ": " + ts_type(param.type)
        if param.is_array:
            result += "[]"
        result += ", "
    return result[:-2]


def request(params: List[PropertySchema]):
    return idl.templates.filters.request(params=params, formatter=idl.formatting.camel)


def return_type(returns: MethodReturnSchema):
    if returns.is_many:
        return f"Stream<{ts_type(returns.type)}>"
    return f"Promise<{ts_type(returns.type)}>"


type_mapping = {
    BuiltinType.int8: "number",
    BuiltinType.uint8: "number",
    BuiltinType.int16: "number",
    BuiltinType.uint16: "number",
    BuiltinType.int32: "number",
    BuiltinType.uint32: "number",
    BuiltinType.int64: "number",
    BuiltinType.uint64: "number",
    BuiltinType.bytes: "Blob",
    BuiltinType.boolean: "boolean",
    BuiltinType.number: "number",
    BuiltinType.float: "number",
    BuiltinType.double: "number",
    BuiltinType.string: "string",
    BuiltinType.blob: "Blob",
    BuiltinType.object: "object",
}


def ts_type(type_name: str):
    is_array = type_name.endswith("[]")
    if type_name.endswith("[]"):
        type_name = type_name[:-2]
    type_name = type_mapping.get(type_name, type_name)
    if is_array:
        return type_name + "[]"
    return type_name
