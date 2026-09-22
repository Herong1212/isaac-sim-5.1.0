from typing import List

import idl.formatting
import idl.templates.filters
from idl.schema import InterfaceSchema
from idl.spec import Spec, PropertySchema


def include(spec: Spec):
    """
    Returns all filters for JavaScript to be included to renderer.
    :param spec: Parsed IDL JSON.
    """
    return {
        "js.request": request,
        "js.request_data": request_data,
        "js.arguments": arguments,
    }


def arguments(params: List[PropertySchema], default: str = "undefined"):
    result = ""
    for param in params:
        if param.is_const:
            continue
        result += idl.formatting.camel(param.name)
        if param.optional:
            result += f" = {default}"
        result += ", "
    return result[:-2]


def request(params: List[PropertySchema]):
    return idl.templates.filters.request(params=params, formatter=idl.formatting.camel)


def request_data(params, interface: InterfaceSchema, default="undefined", indent=4, variable="data"):
    def append(prop, prop_from, fallback=None):
        if prop.is_const:
            lines.append(f"{variable}[\"{prop.name}\"] = {prop.type};")
        else:
            param_var = idl.formatting.camel(prop_from)
            if fallback:
                fallback_var = idl.formatting.camel(fallback)
                lines.append(f"{param_var} = {param_var} === {default} ? {fallback_var} : {param_var};")

            if prop.optional:
                lines.append(f"if ({param_var} !== {default}) {variable}[\"{prop.name}\"] = {param_var};")
            else:
                lines.append(f"{variable}[\"{param.name}\"] = {param_var};")

    lines = [f"const {variable} = {'{}'};"]
    for field in interface.fields:
        append(field, prop_from=field.name, fallback=f"this.{field.name}")

    for param in params:
        append(param, prop_from=param.name)

    spaces = indent * " "
    return f"\n{spaces}".join(lines)
