"""Script to gather various diagnostic on extensions (and fix issues)."""

import argparse
import glob, re, os
import pprint
from pathlib import Path
import omni.kit.app, carb
from dataclasses import dataclass
from typing import Set, List, Dict

modules = {}

manager = omni.kit.app.get_app().get_extension_manager()


class ExtInfo:
    def __init__(self, name):
        self.name = name
        self.config = ""
        self.modules = []
        self.imports = set()

    def __repr__(self):
        return pprint.pformat(vars(self))


def gather_all_exts_info():
    exts = {}
    for ext in manager.get_extensions():
        ext_id = ext["id"]
        info = manager.get_extension_dict(ext_id)
        if info:
            path = info["path"]
            ext_name, *_ = ext_id.split("-")
            ext_info = ExtInfo(ext_name)
            ext_info.config = info["configPath"]
            for script in glob.glob(path + "/**/*.py", recursive=True):
                with open(script, "r", encoding="utf8") as f:
                    all_imports = r"\s*(?:from|import)\s+([\w.]+(?:\s*,\s*[\w.]+)*)"
                    for m in re.findall(all_imports, f.read()):
                        ext_info.imports.add(m)
            ext_info.deps = info.get("dependencies", {})
            for module in info.get("python", {}).get("module", []):
                ext_info.modules.append(module["name"])

            exts[ext_id] = ext_info

    return exts


cwd = Path(os.getcwd())
EXCLUDES = ["omni.kit.test", "omni.ui", "omni.kit.editor", "omni.kit.pipapi", "omni.kit.mainwindow"]


def find_missing_deps(exts, try_fix=False):
    # Build map where each module comes from
    modules = {}
    for _, ext in exts.items():
        for m in ext.modules:
            modules[m] = ext.name

    for _, ext in exts.items():
        to_add = set()
        for imp in ext.imports:
            if imp in modules and modules[imp] not in ext.deps:
                ext_name = ext.name
                missing_dep = modules[imp]
                if ext_name == missing_dep:
                    continue
                if missing_dep in EXCLUDES:
                    continue
                print(f"extension: '{ext_name}' imports '{imp}' but doesn't depend on '{missing_dep}'")
                to_add.add(missing_dep)

        if len(to_add) > 0 and try_fix:
            config_path = Path(ext.config).resolve()
            if cwd in config_path.parents:
                print(f"fixing: {config_path}")

                with open(config_path, "r") as f:
                    buf = f.readlines()

                with open(config_path, "w") as f:
                    for line in buf:
                        if "[dependencies]" in line:
                            for dep in to_add:
                                line = line + f'"{dep}" = {{}}\n'
                        f.write(line)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--deps", action="store_true", help="Look for missing deps.")
    parser.add_argument("-f", "--fix", action="store_true", help="Try to fix.")

    try:
        options = parser.parse_args()
    except Exception as e:
        carb.log_error(str(e))
        return

    exts = gather_all_exts_info()

    if options.deps:
        find_missing_deps(exts, options.fix)
        return


main()
