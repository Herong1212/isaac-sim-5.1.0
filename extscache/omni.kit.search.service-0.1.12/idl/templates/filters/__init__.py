from typing import List

import idl.formatting
from idl.spec import Spec, PropertySchema, InterfaceSchema


def include(spec: Spec):
    """
    Returns all default filters to be included to renderer.
    :param spec: Parsed IDL JSON.
    """
    return {
        "camelcase": idl.formatting.camel,
        "underscore": idl.formatting.underscore,
        "pascal": idl.formatting.pascal,
        "format_doc": format_doc,
        "find_interface_method": find_interface_method,
    }


def request(params: List[PropertySchema], formatter):
    req = ""
    for param in params:
        if param.is_const:
            value = param.type
        else:
            value = formatter(param.name)
        req += f"\"{param.name}\": {value}, "
    return req[:-2]


def format_doc(comment: str, indent: int):
    doc = "\n".join(
        idl.formatting.format_doc(comment, line_limit=80, indent=indent)
    )

    import jinja2
    return jinja2.filters.do_indent(doc, width=indent)


def find_interface_method(interface: InterfaceSchema, func_name: str):
    for function in interface.functions:
        if function.name == func_name:
            return function
    return None
