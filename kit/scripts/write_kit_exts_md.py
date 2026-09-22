"""Writes out the kit-sdk bundled extensions to kit_exts.md for kit-manual docs.
Currently it is run manually from within kit.

Example usage:
.\_build\windows-x86_64\release\kit.exe --enable "omni.kit.pipapi" --exec .\source\python\scripts\write_kit_exts_md.py
"""

import csv
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Tuple
from functools import cache

import carb.tokens
import omni.ext
import omni.kit.app

import omni.kit.pipapi
omni.kit.pipapi.install("tomlkit")

import tomlkit as toml

app = omni.kit.app.get_app()
ext_manager = app.get_extension_manager()
exts = ext_manager.fetch_all_extension_packages()
ext_summaries = ext_manager.fetch_extension_summaries()
itokens = carb.tokens.acquire_tokens_interface()

KIT_VERSION = itokens.resolve("${kit_version}")
KIT_PATH = Path(itokens.resolve("${kit}"))
APP_NAME = itokens.resolve("${app_name}")
REPO_ROOT = KIT_PATH.parent.parent.parent
REPO_TOML = REPO_ROOT / "repo.toml"
KERNEL_DOCS = REPO_ROOT / "source" / "kernel" / "docs" / "config" / "docs.toml"
print(f"REPO_TOML: {REPO_TOML}")
KIT_EXTS_MD = REPO_ROOT / "source" / "kernel" / "docs" / "guide" / "kit_exts.md"
print(f"KIT_EXTS_MD: {KIT_EXTS_MD}")

# Some special cases to add to list from repo_toml - since they have some special setup.
SPECIAL_EXTS_DOCS = [
    "omni.graph.exec",
    "omni.kit.exec.core",
    "omni.usd.libs",
    "usdrt.scenegraph",
]

EXTERNAL_EXTS_DOCS = {
    "omni.client": "https://docs.omniverse.nvidia.com/kit/docs/client_library/latest/index.html",
    "omni.usd.resolver": "https://docs.omniverse.nvidia.com/kit/docs/usd_resolver/latest/index.html",
}


@dataclass
class ExtInfo:
    full_name: str
    version: str
    support_level: str
    deprecation_msg: str = ""
    link: str = ""
    redistributable: str = ""
    description: str = ""


def version_to_str(version: Tuple[int, int, int, str, str]) -> str:
    """Generate string `0.0.0-tag+tag`"""
    delimiters = ("", ".", ".", "-", "+")
    return "".join(
        f"{d}{v}" for d, v in zip(delimiters, version) if str(v) and v is not None
    )


def validate_all_extension_docs():
    exts_path = REPO_ROOT / "source" / "extensions"
    extension_toml_paths = exts_path.rglob("extension.toml")
    for extension_toml_path in extension_toml_paths:
        if extension_toml_path.parent.name == "template":
            continue
        # Read the file content correctly
        with extension_toml_path.open("r", encoding="utf-8") as f:
            ext_toml_data = toml.load(f)

        doc_data = ext_toml_data.get("documentation")
        if doc_data:
            yield extension_toml_path.parent.parent.name


@cache
def get_repo_docs_extensions() -> list[str]:
    with open(REPO_TOML, "r") as f:
        repo_config = toml.load(f)
    repo_docs = repo_config.get("repo_docs", {})
    repo_docs_kit = repo_docs.get("kit", {})
    repo_docs_extensions = repo_docs_kit.get("extensions", [])
    repo_docs_extensions.extend(SPECIAL_EXTS_DOCS)
    return repo_docs_extensions


def ensure_documentation_deps():
    with open(KERNEL_DOCS, "r") as f:
        docs_config = toml.load(f)
    deps = docs_config.get("documentation", {}).get("deps", [])
    existing_deps = [dep for dep, path in deps]
    repo_docs_extensions = get_repo_docs_extensions()
    missing_deps = [ext for ext in repo_docs_extensions if ext not in existing_deps]
    if not missing_deps:
        return
    for missing_dep in missing_deps:
        # Find the correct position to insert the new dependency
        insert_idx = 0
        for idx, (dep, _) in enumerate(deps):
            if missing_dep < dep:
                insert_idx = idx
                break
            else:
                insert_idx = idx + 1

        deps.insert(insert_idx, [missing_dep, f"../../../../_build/docs/{missing_dep}/latest"])
    with open(KERNEL_DOCS, "w") as f:
        toml.dump(docs_config, f)


def replace_linebreaks_with_space(input_string):
    # Replace single '\n' with ' '
    output_string = input_string.replace("\n", " ")
    # Replace single '\r' with ' '
    output_string = output_string.replace("\r", " ")

    # Check for double line breaks
    if "\n\n" in input_string or "\r\r" in input_string:
        raise ValueError("Double line breaks (\\n\\n or \\r\\r) are not allowed.")

    return output_string


def get_exts_cache() -> dict[str, ExtInfo]:
    local_exts: dict[str, ExtInfo] = {}

    repo_docs_extensions = set(get_repo_docs_extensions())

    for ext_summary in ext_summaries:
        ext_name = ext_summary["fullname"].strip()
        ext_flags = ext_summary["flags"]
        ext_bundled = bool(ext_flags & omni.ext.EXTENSION_SUMMARY_FLAG_BUILTIN)
        if not ext_bundled:
            continue

        ext_latest_version = ext_summary["latest_version"]
        # strip pre-release and metadata
        ext_version = version_to_str(ext_latest_version["version"]).split("-")[0]
        ext_version = ext_version.split("+")[0]

        ext_info_local: dict = ext_manager.get_extension_dict(ext_latest_version["id"])
        if not ext_info_local:
            continue
        is_kit_file = ext_info_local["isKitFile"]
        if is_kit_file:
            continue

        package_dict = ext_info_local.get("package", {})

        ext_support_level = package_dict.get("support_level", "sample").lower()
        if ext_support_level == "example":
            ext_support_level = "sample"
        if ext_support_level == "enterprise":
            ext_support_level = "core"

        ext_description = package_dict.get("description", "").strip()
        ext_description = replace_linebreaks_with_space(ext_description)

        # get deprecation_msg
        is_deprecated = False
        deprecation_msg = ""
        deprecation_dict = ext_info_local.get("deprecation", None)
        if deprecation_dict and "warning" in deprecation_dict:
            is_deprecated = True
            deprecation_msg = deprecation_dict["warning"]
        if is_deprecated:
            ext_support_level = "deprecated"

        redistributable = "yes"
        if is_deprecated or ext_support_level == "internal":
            redistributable = "no"

        ext_link_txt = ext_name
        if ext_name in repo_docs_extensions:
            ext_link_txt = f"{{ref}}`{ext_name} <{ext_name} module>`"
        elif ext_name in EXTERNAL_EXTS_DOCS:
            ext_link_txt = f"[{ext_name}]({EXTERNAL_EXTS_DOCS.get(ext_name)})"

        ext_info = ExtInfo(
            ext_name,
            ext_version,
            ext_support_level,
            deprecation_msg=deprecation_msg,
            redistributable=redistributable,
            link=ext_link_txt,
            description=ext_description,
        )
        local_exts[ext_name] = ext_info
    return local_exts


def write_csv(bundled_exts: dict):
    output_path = Path.home() / f"{APP_NAME}-{KIT_VERSION}-cached-extensions.csv"
    fieldnames = [field.name for field in fields(ExtInfo)]
    with open(output_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows((asdict(ext) for ext in bundled_exts.values()))


def write_md(bundled_exts: dict[str, ExtInfo], output_path_md: Path):
    with open(output_path_md, "w") as md_file:
        md_file.write("# Kit SDK Extensions\n\n")
        md_file.write("These extensions are included with Kit SDK:\n\n")

        md_file.write("::::{tab-set}\n\n")

        md_file.write(":::{tab-item} Core Extensions\n\n")

        md_file.write("| Extensions | Description |\n")
        md_file.write("| :--------- | :-------------- |\n")
        for ext_name, ext_info in bundled_exts.items():
            if ext_info.support_level == "core":
                md_file.write(f"| {ext_info.link} | {ext_info.description} |\n")
        md_file.write(":::\n\n")

        md_file.write(":::{tab-item} Sample Extensions\n\n")
        md_file.write("| Extensions | Description |\n")
        md_file.write("| :--------- | :-------------- |\n")
        for ext_info in bundled_exts.values():
            if ext_info.support_level == "sample":
                md_file.write(f"| {ext_info.link} | {ext_info.description} |\n")
        md_file.write(":::\n\n")

        md_file.write(":::{tab-item} Deprecated Extensions\n\n")
        md_file.write("| Extensions | Deprecation Message |\n")
        md_file.write("| :--------- | :-------------- |\n")
        for ext_info in bundled_exts.values():
            if ext_info.support_level == "deprecated":
                md_file.write(f"| {ext_info.link} | {ext_info.deprecation_msg} |\n")
        md_file.write(":::\n\n")

        md_file.write("::::\n\n")


if __name__ == "__main__":
    bundled_exts = get_exts_cache()
    write_md(bundled_exts, KIT_EXTS_MD)
    ensure_documentation_deps()

    docs_extensions = set(get_repo_docs_extensions())
    all_exts_with_documentation = set(validate_all_extension_docs())
    print(f"The following extensions with documentation are missing from docs.toml:")
    for item in (all_exts_with_documentation - docs_extensions):
        print(f'"{item}",')