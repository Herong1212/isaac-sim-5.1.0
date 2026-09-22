import json


def _parse(filename):
    with open(filename, "rb") as file:
        parsed = json.load(file)

    result = {
        **group_types(parsed["types"]),
        "__all__": parsed["types"],
        "origin": parsed.get("origin", "")
    }
    return result


def group_types(types):
    spec = {
        "interfaces": {},
        "structs": {},
        "enums": {},
        "consts": {},
        "unions": {},
        "aliases": {},
        "custom": {}
    }

    for item in types:
        if item["type"] == "custom":
            key = "custom"
        else:
            key = get_plural_type_name(item)
        spec[key][item["name"]] = item
    return spec


def get_plural_type_name(item):
    return item["type"] + "es" if item["type"].endswith("s") else item["type"] + "s"
