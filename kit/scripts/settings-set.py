import ast
import sys
import carb
import carb.settings


def main():
    if len(sys.argv) < 3:
        print("Usage: set path/to/value value")
        return

    isregistry = carb.settings.get_settings()

    value_lower = sys.argv[2].lower()
    if value_lower == "true":
        print("set bool true")
        isregistry.set_bool(sys.argv[1], True)
        return
    elif value_lower == "false":
        print("set bool false")
        isregistry.set_bool(sys.argv[1], False)
        return

    try:
        value = ast.literal_eval(sys.argv[2])
    except:
        value = sys.argv[2]

    if isinstance(value, int):
        print("set int")
        isregistry.set_int(sys.argv[1], value)
    elif isinstance(value, float):
        print("set float")
        isregistry.set_float(sys.argv[1], value)
    else:
        print("set string")
        isregistry.set_string(sys.argv[1], value)


main()
