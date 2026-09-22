import sys
import carb
import carb.settings

# recursive subroutine for searching the settings dictionary
# d:                    [input] settings dictionary
# search_string:        [input] string to find in keys
# found_settings_list:  [output] list of all of the settings that contain search_string
# path_string:          [ignore] holds the root-to-setting path as the dict-of-dicts is traversed (caller may ignore)
def _search_settings(d, search_string="", found_settings_list=[], path_string=""):
    for k, v in d.items():
        key_string = path_string + "/" + str(k)
        if isinstance(v, dict):
            _search_settings(
                v,
                path_string=path_string + "/" + k,
                found_settings_list=found_settings_list,
                search_string=search_string,
            )
        elif key_string.lower().find(search_string) >= 0:
            found_settings_list.append(key_string)


def main():
    if len(sys.argv) < 2:
        print("Usage: get path/to/value")
        return

    path = sys.argv[1]
    isregistry = carb.settings.get_settings()
    value = isregistry.get(path)
    if value:
        print(value)
    else:
        settings_dict = isregistry.get_settings_dictionary("")
        matching_settings = []
        _search_settings(settings_dict.get_dict(), search_string=path.lower(), found_settings_list=matching_settings)
        if len(matching_settings) > 0:
            print("\nPossible matches:")
            for match in sorted(matching_settings):
                print(match + " : " + str(isregistry.get(match)))
        else:
            print("No setting found: " + path)


main()
