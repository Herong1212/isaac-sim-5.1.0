from typing import Dict, List

import carb
import carb.settings
import carb.tokens
import omni.client

SETTING_SNIPPET_FOLDERS = "/exts/omni.kit.window.script_editor/snippetFolders"


def load_snippets() -> Dict[str, List[Dict]]:
    snippets: Dict[str, List[Dict]] = {}

    settings = carb.settings.get_settings()
    tokens = carb.tokens.get_tokens_interface()
    folders = settings.get(SETTING_SNIPPET_FOLDERS)
    for folder in folders:
        resolved_folder = tokens.resolve(folder)
        result, _ = omni.client.stat(resolved_folder)
        if result != omni.client.Result.OK:
            carb.log_warn(f"Snippet folder doesn't exist: '{resolved_folder}'")
            continue

        result, entries = omni.client.list(resolved_folder)
        if result == omni.client.Result.OK and entries:
            for entry in entries:
                if entry.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN:
                    continue
                else:
                    url = resolved_folder + "/" + entry.relative_path
                    url = url.replace("\\", "/")
                    snippet_name = entry.relative_path
                    result, _, content = omni.client.read_file(url)
                    if result != omni.client.Result.OK:
                        carb.log_error(
                            f"[omni.kit.window.script_editor] Can't read snippet file {url}, error code: {result}"
                        )
                        continue

                    data = memoryview(content).tobytes().decode("utf-8")
                    if data:
                        lines = data.split("\n")
                        first_line = lines[0]
                        if first_line.startswith("#"):
                            snippet_name = first_line[1:]
                            data = "\n".join(lines[1:])

                        fields = snippet_name.split("/")
                        if len(fields) == 2:
                            category = fields[0]
                            name = fields[1]
                        else:
                            category = "Other"
                            name = snippet_name
                        if category not in snippets:
                            snippets[category] = []
                        snippets[category].append({"category": category, "name": name, "content": data})

    return snippets
