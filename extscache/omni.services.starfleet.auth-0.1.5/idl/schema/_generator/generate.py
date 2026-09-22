import os

from idl.schema._parse import _parse
from idl.templates.renderer import Renderer

script_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))


def run():
    spec = _parse(os.path.join(script_path, "schema.json"))
    renderer = Renderer(template_path=script_path)
    renderer.filters["py.type_name"] = python_type_name
    renderer.filters["py.type"] = python_type_from_dict

    renderer.render(
        "template.pyi",
        os.path.join(script_path, "..", "__init__.py"),
        {
            "spec": spec["__all__"]
        }
    )


def get_type(spec, type_name):
    if type_name in builtin_types:
        return {"type": "primitive", "name": type_name}

    struct = spec["structs"].get(type_name)
    if struct:
        return struct
    enum = spec["enums"].get(type_name)
    if enum:
        return enum
    const = spec["consts"].get(type_name)
    if const:
        return const
    alias = spec["aliases"].get(type_name)
    if alias:
        return alias
    union = spec["unions"].get(type_name)
    if union:
        return union
    raise ValueError(f"Unknown type {type_name}.")


def python_type_from_dict(prop: dict) -> str:
    name = python_type_name(prop["type"])
    if prop.get("is_array"):
        name = f"List[{name}]"

    if prop.get("optional"):
        name = f"Optional[{name}]"
    return name


builtin_types = {
    "number": "int",
    "string": "str",
    "boolean": "bool",
    "object": "dict",
    "uint64": "int",
}


def python_type_name(type_name: str) -> str:
    return builtin_types.get(type_name, type_name)


if __name__ == "__main__":
    run()
