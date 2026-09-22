import sys
import carb
import carb.settings
import carb.dictionary


def clamp_string(in_str):
    if len(in_str) > 150:
        return in_str[:150] + ".."
    else:
        return in_str


def print_with_indent(d, indent=0):
    for key, value in d.items():
        print("  " * indent + str(key), end="")
        if isinstance(value, dict):
            print("")
            print_with_indent(value, indent + 1)
        else:
            str_value = clamp_string(str(value))
            print(" = " + str_value)


def print_with_fullpath(d, parent_path="/"):
    for key, value in d.items():
        print_parent_path = parent_path if parent_path is not "/" else ""
        if isinstance(value, dict):
            fullpath = print_parent_path + "/" + key
            print_with_fullpath(value, fullpath)
        else:
            str_value = clamp_string(str(value))
            print(print_parent_path + "/" + str(key) + " = " + str_value)


def main():
    fullpath_mode = True
    if "--indent" in sys.argv:
        fullpath_mode = False
        sys.argv.remove("--indent")

    path = "/"
    if len(sys.argv) > 1 and len(sys.argv[1]) > 1:
        path = sys.argv[1]

    isregistry = carb.settings.get_settings()
    idictionary = carb.dictionary.get_dictionary()

    settings_copy = isregistry.create_dictionary_from_settings(path)

    pydict = idictionary.get_dict_copy(settings_copy, "")

    if not pydict:
        print("Empty")
        return

    if fullpath_mode:
        print_with_fullpath(pydict, path)
    else:
        print_with_indent(pydict)

    idictionary.destroy_item(settings_copy)


main()
