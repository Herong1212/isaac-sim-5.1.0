"""This tool wraps repo_docs to avoid repeating configuration for each extension doc unit (project).

It adds `kit` namespace to `repo_docs`. There you can specify a list of extensiosn to generate docs for:

```toml
[repo_docs.kit]
extensions = [
    "omni.ui.scene",
    "omni.ui"
]
```

That automatically produces `projects` entry for each of them using default (template) config: EXT_DOC_PROJECT_TEMPLATE.
You can override template:

```toml
[repo_docs.kit]
project_template.sphinx_conf_py_extra = "xyz = 123"
```

You can override  specific project too:

```toml
[repo_docs.projects."omni.ui"]
sphinx_conf_py_extra = "xyz = 456"
```

If you have extensions in directories other than "source/extensions" you can override the locations that are searched
for those extensions

```toml
[repo_docs.kit]
extension_roots = [
    "source/extensions",
    "source/more_extensions",
]
```

It also:
    * automatically extracts extension version from `extension.toml`

"""
from dataclasses import dataclass
import logging
import hashlib
import json
import shutil
import os
import glob
import sys
import re
import tempfile
import fnmatch
from copy import copy
from typing import Dict, List
from string import Template
from pathlib import Path
from datetime import datetime

import packmanapi
import omni.repo.man
import omni.repo.man.configuration
import omni.repo.docs

logger = logging.getLogger(__name__)

html_templates_path = (Path(__file__).parent.parent / "html-templates").as_posix()

DEFAULT_DOCS_ROOT_DIRNAME = "docs/"

# Base template for extension docs project
EXT_DOC_PROJECT_TEMPLATE = {
    "sphinx_exclude_patterns": [],
    "sphinx_dont_exclude_patterns": [],
    "deps": [],
    "logo": "../../../../_repo/deps/repo_docs/media/main_ov_logo_square.png",

    "sphinx_conf_py_extra": """
myst_substitutions = {}
# --TERMS--
import os
html_theme_options["navigation_depth"] = 8
html_theme_options["collapse_navigation"] = False

if html_theme != "nvidia_sphinx_theme":
    html_theme_options["titles_only"] = True
    pygments_style = 'monokai'

autodoc_member_order = 'groupwise'
extensions += ["autodocsumm"] # enables :autosummary: flag in automodule directives
myst_heading_anchors = 5
myst_enable_extensions = [
    "colon_fence", # allows code-fencing for usage of admonitions etc
    "substitution", # allows substitution of predefined patterns
]
myst_substitutions.update({
  "extension_name": "EXT_NAME",
  "extension_version": "EXT_ID",
})

# toggle this to init to help debug the source of docstring issues
# toggle to class when warnings are debugged
# (when automethod picks up the warning, it tells you where it came from more accurately)
autoclass_content = "class"

# Monkeypatch Class Documenter to drop lines of bases we want to ignore
ignore_bases = ["pybind11_builtins.pybind11_object"]
from sphinx.ext.autodoc import ClassDocumenter, _
add_line = ClassDocumenter.add_line
def add_line_no_base(self, text, *args, **kwargs):
    if 'Bases:' in text.strip():
        for base in ignore_bases:
            if f"`{base}`" in text.strip():
                return
    add_line(self, text, *args, **kwargs)

add_directive_header = ClassDocumenter.add_directive_header

def add_directive_header_ignore_base(self, *args, **kwargs):
    self.add_line = add_line_no_base.__get__(self)
    result = add_directive_header(self, *args, **kwargs)
    del self.add_line
    return result

ClassDocumenter.add_directive_header = add_directive_header_ignore_base
def autodoc_process_docstring(app, what, name, obj, options, lines):
    import textwrap, re
    for i, line in enumerate(lines):
        line = line.replace("*args", "\\*args")
        line = line.replace("**kwargs", "\\*\\*kwargs")
        if not name.startswith("pxr."):  # USD docs have had special care taken and don't need this hack
            line = re.sub(r'(?<![:])`(.+?)`', r"\\`\\1\\`", line)  # Backslash any backticks _not_ part of a reference
        # line = line.replace("`", "\\`") # Old workaround present for reference until all exts migrated
        lines[i] = line # lines must be modified in-place apparently

sphinx_event_handlers += [
    ("autodoc-process-docstring", autodoc_process_docstring)
]

if os.name == 'nt':
    os.environ['PXR_USD_WINDOWS_DLL_PATH'] = ' ' # prevent usd from running add_dll_directory twice
    for path in os.getenv('PATH', '').split(os.pathsep):
        if os.path.exists(path) and path != '.':
            os.add_dll_directory(path)

""" + f"""
templates_path = ["{html_templates_path}"]
""",
}


class KitRepoDocsError(omni.repo.man.RepoToolError):
    """Exception for kit repo docs errors."""


def load_extension_config(ext_root: str, config_path: str = None) -> dict:
    # Either use explicit config path or search for known locations
    possible_paths = [config_path] if config_path else [f"{ext_root}/config/extension.toml", f"{ext_root}/extension.toml"]
    for p in possible_paths:
        if os.path.exists(p):
            return omni.repo.man.get_toml_module().load(p), p
    raise KitRepoDocsError(f"no extension configuration found at the following path(s): {possible_paths!r}")


def check_anything_changed(input_files: List[str], output_path: str):
    """Compare modification time of all input files against all files in output_path"""
    oldest_ts = sys.maxsize
    for file in glob.glob(output_path + "/**", recursive=True):
        if not os.path.isfile(file):
            continue
        oldest_ts = min(oldest_ts, os.path.getmtime(file))

    if oldest_ts == sys.maxsize:
        return True

    changed_files = []
    for file in input_files:
        if os.path.getmtime(file) > oldest_ts:
            changed_files.append(file)

    if changed_files:
        print(f"Changes detected in: {changed_files}")
        return True

    print(f"No new changes detected, skipping generation for: {output_path} ")

    return False


class PushEnv:
    """OS environment variables context manager."""

    def __init__(self):
        pass

    def __enter__(self):
        self._environ = dict(os.environ)
        return self

    def __exit__(self, type, value, tb):
        os.environ.clear()
        os.environ.update(self._environ)


class PushLongPythonPath:
    """A way to set PYTHONPATH which bypasses too long env var limitation.

    Python will look for sitecustomize.py in the directory specified by PYTHONPATH and run it before doing anything.
    Create a temporary directory and write a sitecustomize.py file to set all paths manually, then set PYTHONPATH to
    that directory. Cleanup after.
    """

    def __init__(self, paths: List[str]):
        self.paths = [str(p) for p in paths]

    def __enter__(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        with open(f"{self.temp_dir.name}/sitecustomize.py", "w") as f:
            f.write(f"""import sys
paths = {self.paths}
for p in paths:
    sys.path.append(p)
""")
        self.prev_env = os.environ.get("PYTHONPATH", None)
        os.environ["PYTHONPATH"] = self.temp_dir.name

    def __exit__(self, type, value, tb):
        os.environ["PYTHONPATH"] = self.prev_env
        self.temp_dir.cleanup()


class FileHashChecker:
    def __init__(self, input_files, output_path):
        self.output_path = output_path
        self.hash_file_path = f"{output_path}/hashes.json"

        # build hashes
        self.current_hashes = {}
        for file in input_files:
            self.current_hashes[os.path.basename(file)] = self.sha1_file(file)

        # load hashes
        self.saved_hashes = {}
        if os.path.exists(self.hash_file_path):
            with open(self.hash_file_path) as f:
                self.saved_hashes = json.load(f)

    def check_anything_changed(self):
        diff = set(self.current_hashes.items()) ^ set(self.saved_hashes.items())
        if diff:
            print(f"Changes detected: {diff}. Regenerating: {self.output_path}")
            return True

        print(f"No new hash changes detected, skipping generation for: {self.output_path}")
        return False

    def save(self):
        with open(self.hash_file_path, "w") as f:
            json.dump(self.current_hashes, f, indent=4)

        print(f"{self.hash_file_path} was updated, commit the changes.")

    def sha1_file(self, path):
        with open(path, "rb") as f:
            file_hash = hashlib.sha1()
            # Replace CRLF -> LF to match sha1 on both platforms
            content = f.read().replace(b'\r\n', b'\n')
            file_hash.update(content)
            return file_hash.hexdigest()


def _find_longest_doxygen_strip_path(doxygen_paths):
    """Heuristic: find longest common path like "../../../../include" or just "../../.." to be removed from doxygen paths"""
    if not doxygen_paths:
        return None
    p = doxygen_paths[0]
    paths = set()
    for suffix in ["/include/", "/../"]:
        index = p.rfind(suffix)
        if index > 0:
            paths.add(p[: index + len(suffix)])
    if paths:
        return sorted(list(paths))[-1]


def _args_to_cmd(args: List[str]):
    return " ".join(a if " " not in a else f'"{a}"' for a in args)


@dataclass
class RunContext:
    repo_root: str
    repo_version: str


@dataclass
class ExtensionDocDesc:
    ext_name: str
    ext_root: str
    config_path: str = None


class ExtensionDocProject:
    def __init__(self, context: RunContext, desc: ExtensionDocDesc, project_config: dict, kit_docs_config: dict, repo_docs_is_v1: bool):
        self.build_run = {}
        self.repo_root = context.repo_root
        self.kit_docs_config = kit_docs_config
        self.ext_root = desc.ext_root
        self.ext_config, self.ext_config_path = load_extension_config(self.ext_root, desc.config_path)
        self.docs_config = self.ext_config.get("documentation", dict())
        ext_config_package = self.ext_config["package"]
        self.ext_version = ext_config_package.get("version", context.repo_version)
        self.ext_name = desc.ext_name
        self.ext_id = f"{self.ext_name}-{self.ext_version}"
        self.description = ext_config_package.get("description", self.ext_name)
        self.keywords = ext_config_package.get("keywords", list()) + re.split(r'[\._-]', self.ext_name) + [self.ext_name]

        if not repo_docs_is_v1:
            self.use_fast_doxygen_conversion = project_config.get("use_fast_doxygen_conversion", False)

        self.api_output_directory = project_config.get("api_output_directory", None)

        # Ext version = doc version
        project_config["version"] = self.ext_version

        # Docs staging area. There is where we copy all the docs src, generate files and what becomes the root for repo_docs.
        docs_stage_path = f"_build/docs/{self.ext_name}/stage"
        self.docs_stage_path = self.repo_root + "/" + docs_stage_path
        os.makedirs(self.docs_stage_path, exist_ok=True)
        project_config["docs_root"] = docs_stage_path

        # Doc name: [ext]: [title] (prefer [documentation] section title, fallback to extension title)
        ext_title = self.docs_config.get("title", ext_config_package.get("title", ""))
        self.doc_title = f"{self.ext_name}: {ext_title}" if ext_title else f"{self.ext_name} extension documentation"

        # Index of all doc files/pages
        self.index = []

        # omni.kit.documentation.builder section (integration)
        self.pages = []
        self.toc_index = []
        pages = self.docs_config.get("pages", [])
        if not pages:
            raise KitRepoDocsError("No documentation pages specified in '[documentation.pages]' of 'extension.toml'")
        if pages:
            for p in pages:
                if isinstance(pages, dict):
                    tocname = p
                    p = pages.get(p)
                    self.toc_index.append((tocname, p.split(DEFAULT_DOCS_ROOT_DIRNAME)[1]))
                if p.lower() == "index.rst":
                    raise KitRepoDocsError("No pages named index.rst allowed - The system creates the index from [documentation.pages]")
                self.pages.append(Path(self.ext_root, p).as_posix())
                self.index.append(p.split(DEFAULT_DOCS_ROOT_DIRNAME)[1])  # temp hack, maybe we require a docs_root config?

        # Identify projects that contain indicators of having "internal/public" filters, to auto-generate an internal build for that extension only
        # This won't find examples where the api might contain an internal docstring
        internal_build = "internal" in self.docs_config.get("builds", [])
        if not internal_build:
            internal_indicators = [
                ".. only:: internal",
                "```{only} internal",
                "{only}`internal",
                ".. only:: not public",
                "```{only} not public",
                "{only}`not public"
            ]
            internal_regexes = [re.compile(re.escape(indic)) for indic in internal_indicators]
            for page in self.pages:
                with open(page, "rt", encoding="UTF-8") as page_file:
                    page_content = page_file.readlines()
                for i_r in internal_regexes:
                    for line in page_content:
                        if i_r.search(line):
                            internal_build = True
                            break
        if internal_build:  # repo_docs_env.settings['project']['builds']['internal']['enabled'] = True
            project_config["builds"] = {"internal": {"enabled": True}}
        # docs dependencies (usage of objects.inv / intersphinx_mapping)
        self.deps = self.docs_config.get("deps", [])
        project_config["deps"] = self.deps

        # doxygen
        project_config.setdefault("doxygen_input", [])
        headers = self.docs_config.get("cpp_api", [])
        self.has_cpp_api = bool(headers)
        if self.has_cpp_api:
            for p in headers:
                p = os.path.join(self.ext_root, p).replace("\\", "/")
                project_config["doxygen_input"].append(p)

            doxygen_strip_from_path = _find_longest_doxygen_strip_path(project_config["doxygen_input"])
            project_config["doxygen_strip_from_path"] = [Path(self.repo_root).parent.as_posix()]
            if doxygen_strip_from_path:
                project_config["doxygen_strip_from_path"] += [Path(doxygen_strip_from_path).resolve().as_posix()]

        project_config.setdefault("doxygen_output_exclude_regexes", [])
        project_config["doxygen_output_exclude_regexes"].extend(self.docs_config.get("cpp_api_exclude_warnings", []))

        # data to be stored on website
        self.web_meta_data = {}
        self.web_meta_data["name"] = self.doc_title
        self.web_meta_data["ext"] = self.ext_name
        self.web_meta_data["title"] = ext_title
        self.web_meta_data["description"] = ext_config_package.get("description", "")
        self.web_meta_data["keywords"] = ext_config_package.get("keywords", [])
        self.web_meta_data["build_date"] = datetime.utcnow().replace(microsecond=0).isoformat()

    def on_before_sphinx(self, repo_docs_env):
        # repo_docs currently fails when docs_dst and doc_root both in build. It fails when trying to create `_build`
        # link, when building a relative path. This is WAR to fix it:
        repo_docs_env.relative_docs_dst /= Path("../../_build/docs")

        # It can be called on "exhale" phase and again later. Run only once asap.
        if self.build_run.get(repo_docs_env.build_name, False):
            return self.docs_stage_path
        self.build_run[repo_docs_env.build_name] = True

        original_docs_stage_path = self.docs_stage_path
        if repo_docs_env.build_name != "public":
            self.docs_stage_path = self.docs_stage_path + f"-{repo_docs_env.build_name}"

        if not check_anything_changed(self.pages + [self.ext_config_path], self.docs_stage_path):
            self.docs_stage_path = original_docs_stage_path
            return self.docs_stage_path

        # clean output
        omni.repo.man.clean_folders([os.path.normpath(self.docs_stage_path)])

        # run kit docs pipeline
        config = repo_docs_env.cmdline.config
        self._build_docs(config)

        # auto-add actions API
        self._auto_add_actions_api()

        # build API(s)
        if not self.docs_config.get("python_api_hidden", False) or repo_docs_env.build_name == "internal":
            self._build_python_api_root(repo_docs_env)
        if not self.docs_config.get("cpp_api_hidden", False) or repo_docs_env.build_name == "internal":
            self._build_cpp_api()

        # build index
        self._build_index()

        # build json with meta data to store in web (not to be consumed by repo_docs)
        self._dump_web_meta_data(repo_docs_env)

        self.docs_stage_path = original_docs_stage_path
        return self.docs_stage_path

    def _is_kit_documentation_builder_required(self):
        # We can make a flag to control it, but for now simple heuristic is enough:
        # detect special code blocks executed by omni.kit.documentation.builder:
        for p in self.pages:
            if p.endswith(".md"):
                with open(p, encoding="utf8") as f:
                    contents = f.read()
                    if "\n```execute" in contents: # will not trigger on nested
                        return True
        return False

    def _build_docs(self, config: str):
        if self._is_kit_documentation_builder_required():
            self._build_docs_using_kit(config)
        else:
            self._build_docs_using_simple_copy()

    def _build_docs_using_simple_copy(self):
        # Allow excluding some files, otherwise sphinx errors that some .md is not in toctree
        exclude_files = self.docs_config.get("files", {}).get("exclude", [])
        def ignore(directory, files):
            reldir = os.path.relpath(directory, self.ext_root).replace("\\", "/")
            return {f for f in files if any(fnmatch.fnmatch(f"{reldir}/{f}", pattern) for pattern in exclude_files)}
        ignore_fn = ignore if exclude_files else None

        # just copy all `docs` content:
        shutil.copytree(self.ext_root + "/docs", self.docs_stage_path, ignore=ignore_fn)

    def _auto_add_actions_api(self):
        actions_api_path = f"{self.ext_root}/config/actions_api.md"
        if os.path.exists(actions_api_path):
            shutil.copy(actions_api_path, self.docs_stage_path)
            self.pages.append(Path(actions_api_path).as_posix())
            self.index.append("Actions <actions_api.md>")


    def _get_python_modules(self):
        python_dict = self.ext_config.get("python", {})
        python_modules = python_dict.get("module", []) + python_dict.get("modules", [])
        for m in python_modules:
            module = m.get("name")
            if module:
                yield module

    def _autosummary_section(self, lines: List[str], toctree=False, template=None):
        if toctree:
            toctree = "        :toctree:\n"
        if template:
            template = f"        :template: {template}\n"
        directive = [f"""\n    .. autosummary::\n{template or ""}{toctree or ""}"""]
        directive.extend(lines)
        return directive

    def _automodule_section(self, module):
        return f"""
.. automodule:: {module}
    :autosummary:
    :platform: Windows-x86_64, Linux-x86_64
    :members:
    :undoc-members:
    :imported-members:
    :show-inheritance:
    :exclude-members: partial
    """

    def _rst_reference_line(self, indent: int, subfolder: str, module: str, use_module_prefix: bool, name: str, extension="rst", split_module=False):
        if extension:
            rst_filename = f"{name}.{extension}"
        else:
            rst_filename = f"{name}"
        if split_module and module:
            name = name.replace(f"{module}.", "")
        if use_module_prefix:
            rst_filename = f"{module}." + rst_filename
        if subfolder:
            rst_filename = f"{module}/" + rst_filename

        return " " * indent * 4 + f"{name} <{rst_filename}>"

    def _rst_toctree_header(self, header_name: str):
        return f"{header_name}" + "\n" + "=" * len(header_name) + "\n"

    def _rst_rubric(self, name):
        return f"""\n.. rubric:: {name}:"""

    def _rst_literal_block(self, content):
        lines = "\n".join(["  " + line for line in content])
        return f"""\n::\n{lines}\n\n"""

    def _rst_code_block(self, content):
        lines = "\n".join(["    " + line for line in content])
        return f"""\n.. code-block:: python\n    :force:\n\n{lines}\n\n"""

    def _rst_verbatim(self, content):
        lines = "\n".join(content)
        return f"""\n{lines}\n\n"""

    def _rst_table_rows(self, indent: int, columns: List[str]):
        rows = []
        indent = " " * 4 * indent
        for i, first in enumerate(columns[0]):
            rows.append(f"{indent}* - {first}")
            for remaining_column in columns[1:]:
                rows.append(f"{indent}  - " + remaining_column[i])
        rows.append("")
        return rows

    def _rst_table_header(self, align: str, widths: List[int], header_rows: int):
        if align:
            align = f"    :align: {align}\n"
        if widths:
            widths = "    :widths: " + " ".join(widths) + "\n"
        else:
            widths = "    :widths: auto\n"
        if header_rows:
            header_rows = f"    :header-rows: {header_rows}\n"
        else:
            header_rows = "    :header-rows: 0\n"

        return f"""\n.. list-table::\n{align or ""}{widths or ""}{header_rows or ""}"""

    def _pymodule_of(self, module: str):
        directive = [f"""\n.. py:module:: {module}\n\n"""]
        return directive

    def _toctree_of(self, name: str, toctree_header: str, lines: List[str], hidden: bool, maxdepth: int):
        if name:
            caption = f"    :caption: {name}\n"
            name = f"    :name: {name}\n"
        else:
            caption = name
        if toctree_header:
            toctree_header = self._rst_toctree_header(toctree_header)
        if maxdepth:
            maxdepth = f"    :maxdepth: {maxdepth}\n"
        if hidden:
            hidden = "    :hidden:\n"

        directive = [f"""{toctree_header or ""}\n.. toctree::\n{hidden or ""}{caption or ""}{name or ""}{maxdepth or ""}"""]
        directive.extend(lines)
        return directive

    def _module_section_table(self, module: str, section: str, sectionables):
        table_lines = []

        table_lines.append(self._rst_rubric(f"`{section} <./{module}.{section}.html>`_ Summary"))
        table_lines.append(self._rst_table_header("left", None, 0))

        if section != "Submodules":
            sectionable_column = [f":doc:`{s} <{module}/{module}.{s}>`" for s in sectionables]
            docs = [sectionables[s]["doc"] for s in sectionables]
        else:
            sectionable_column = [f":doc:`{s} <{s}>`" for s in sectionables]
            docs = [(sectionables[s]["doc"] or "No submodule docstring provided") for s in sectionables]

        doc_column = [
            (doc or "").split("\n")[0].strip().replace("*", "\\*").replace("`", "\\`").replace("_", r"\_")
            for doc in docs
        ]

        table_lines.extend(self._rst_table_rows(1, [sectionable_column, doc_column]))

        return table_lines

    def _strip_submodule_files_from_folder(self, root, modulename):
        module_path = Path(root) / modulename
        rst_files = [name for name in os.listdir(module_path) if name.endswith(".rst")]
        target_import_level = len(modulename.split(".")) + 2  # 1 for extension, 1 for the module separator
        for rst_file in rst_files:
            current_import_level = len(rst_file.split("."))
            rst_file_path = module_path / rst_file
            if target_import_level != current_import_level:
                os.remove(rst_file_path)
                continue
            automodule = False
            with open(rst_file_path) as rst:
                rst_lines = rst.readlines()
                for line in rst_lines:
                    if ".. automodule" in line:
                        automodule = True
            if automodule:
                os.remove(rst_file_path)

    def _strip_module_prefix_from_rst_files(self, root, modulename):

        module_path = Path(root) / modulename
        names = os.listdir(module_path)
        rst_files = [module_path / name for name in names if name.endswith(".rst")]
        for rst_file in rst_files:
            with open(rst_file, "r") as rst:
                rst_lines = rst.readlines()

            shortname = rst_lines[0].split('.')[-1]
            rst_lines[0] = shortname
            rst_lines[1] = "=" * (len(rst_lines[0]) - 1)

            with open(rst_file, "w") as rst:
                rst.writelines(rst_lines)

    def _inspect_python_module(self, repo_docs_env, modules: List[str]) -> Dict[str, List[str]]:
        script_dir = os.path.dirname(os.path.realpath(__file__))
        inspect_modules_script_path = os.path.join(script_dir, "kit_repo_docs_inspect_module.py")

        module_inspect_json = str(Path(self.docs_stage_path + "/module_inspection.json").absolute())
        args = modules + [module_inspect_json]
        self._run_docs_python(repo_docs_env, script_path=inspect_modules_script_path, script_args=args)

        try:
            with open(module_inspect_json, "r") as f:
                return json.load(f)
        except Exception:
            print("There is no module_inspection.json; probably nothing was importable")
            return {}

    def _build_python_api_module_section(self, module: str, section: str, sectionables, rst_lines):
        header = f"{module} {section}"

        section_toctree_lines = self._toctree_of(None, header, rst_lines, True, None)
        table_lines = (self._module_section_table(module, section, sectionables))

        with open(self.docs_stage_path + f"/{module}.{section}.rst", "w") as f:
            f.write("\n".join(section_toctree_lines + table_lines))

        section_lines = []
        section_lines.extend(self._toctree_of(None, None, [f"    {section} <{module}.{section}.rst>\n"], True, None))

        return section_lines

    def _build_python_api_module(self, repo_docs_env, m: str, module_inspection: Dict):
        title = f"{m}"
        lines = [title]
        lines.append("=" * (len(title) + 1))
        lines.append(" ")

        pregen_lines = copy(lines)
        postgen_lines = copy(lines)

        m_submodules = module_inspection["submodules"]
        m_classes = module_inspection["classes"]
        m_pre_functions = module_inspection["functions"]
        m_pre_builtins = module_inspection["builtins"]
        m_functions = {}
        if m_pre_functions:
            m_functions.update(m_pre_functions)
        if m_pre_builtins:
            m_functions.update(m_pre_builtins)

        for subm in m_submodules:
            self._build_python_api_module(repo_docs_env, subm, module_inspection["submodules"][subm])

        toctree_lines = []
        autosummary_section = []
        module_table_lines = []

        if m_submodules:
            m_s_lines = [" " * 8 + f"{m_s}" for m_s in m_submodules]
            submodule_autosummary_lines = self._autosummary_section(m_s_lines, toctree=True, template="repo-docs-recursive-module-template.rst")
            autosummary_section.extend(submodule_autosummary_lines)
            ref_m_s_lines = [self._rst_reference_line(1, None, m, False, m_s, None, True) for m_s in m_submodules]
            toctree_lines.extend(self._build_python_api_module_section(m, "Submodules", m_submodules, ref_m_s_lines))
            module_table_lines.extend(self._module_section_table(m, "Submodules", m_submodules))
        if m_classes:
            m_c_lines = [" " * 8 + f"{m}.{m_c}" for m_c in m_classes]
            class_autosummary_lines = self._autosummary_section(m_c_lines, toctree=True, template="repo-docs-recursive-class-template.rst")
            autosummary_section.extend(class_autosummary_lines)
            ref_m_c_lines = []
            for m_c in m_classes:
                # m_c_methods = m_classes[m_c]["methods"]
                ref_m_c_lines.extend([self._rst_reference_line(1, m, m, True, m_c, None)])
                # ref_m_c_lines.extend([self._rst_html_line(1, m, m, True, f"{m_c}", f"{m_m}", "html") for m_m in m_c_methods])
            toctree_lines.extend(self._build_python_api_module_section(m, "Classes", m_classes, ref_m_c_lines))
            module_table_lines.extend(self._module_section_table(m, "Classes", m_classes))
        if m_functions:
            m_f_lines = [" " * 8 + f"{m}.{m_f}" for m_f in m_functions]
            function_autosummary_lines = self._autosummary_section(m_f_lines, toctree=True)
            autosummary_section.extend(function_autosummary_lines)
            ref_m_f_lines = [self._rst_reference_line(1, m, m, True, m_f, None) for m_f in m_functions]
            toctree_lines.extend(self._build_python_api_module_section(m, "Functions", m_functions, ref_m_f_lines))
            module_table_lines.extend(self._module_section_table(m, "Functions", m_functions))

        automodule_section = self._automodule_section(m)

        pregen_lines.extend(autosummary_section)
        pregen_lines.extend(automodule_section)

        postgen_lines.extend(self._pymodule_of(m))
        postgen_lines.extend(toctree_lines)
        postgen_lines.extend(module_table_lines)

        with open(self.docs_stage_path + f"/{m}.rst", "w") as f:
            f.write("\n".join(pregen_lines))

        # generate autosummary-style stubs manually so we can rewrite the {m}.rst for more control
        self._run_sphinx_autogen(repo_docs_env, self.docs_stage_path, m, f"{m}.rst")

        self._strip_submodule_files_from_folder(self.docs_stage_path, m)
        self._strip_module_prefix_from_rst_files(self.docs_stage_path, m)

        with open(self.docs_stage_path + f"/{m}.rst", "w") as f:
            f.write("\n".join(postgen_lines))

        return m_submodules

    def _build_python_api_root(self, repo_docs_env):

        modules = list(self._get_python_modules())
        if "omni.ui_scene" in modules:  # this ext is a uniquely designed PITA and we're isolating to just one module
            modules.remove("omni.ui_scene")
        if not modules:
            return

        module_inspection = self._inspect_python_module(repo_docs_env, modules)

        modules_copy = copy(modules)
        for m in modules_copy:
            if m not in list(module_inspection.keys()) and m in modules:
                modules.remove(m)
                for _m in modules_copy:
                    if _m.startswith(m) and _m in modules:
                        modules.remove(_m)

        if not modules:
            return

        title = "API (python)"
        lines = [title]
        lines.append("=" * len(title))
        lines.append(" ")

        pregen_lines = copy(lines)
        postgen_lines = copy(lines)

        modules_docs = {}
        modules_listing = {}
        flat_modules_listing = []
        for m in modules:
            modules_listing[m] = []
            flat_modules_listing.append(m)
            modules_docs[m] = {"doc": module_inspection[m]["doc"]}
            submodules = self._build_python_api_module(repo_docs_env, m, module_inspection[m])
            for subm, contents in submodules.items():
                modules_listing[m].append(subm)
                flat_modules_listing.append(subm)
                modules_docs[subm] = {"doc": contents["doc"]}

        # add submodules to the modules list after modules recursively build them
        # but only add them here so that they end up in the top-level toctree/summaries
        # because nesting recursively hits up against toctree depth limits

        module_lines = [" " * 8 + m for m in flat_modules_listing]
        module_lines_rst = [" " * 8 + m + f" <{m}.rst>" for m in modules_listing]

        autosummary_section = self._autosummary_section(module_lines, toctree=False)

        toctree_lines = self._toctree_of(None, None, ["        Modules <Modules.rst>"], True, None)
        modules_toctree_lines = self._toctree_of(None, "Modules", module_lines_rst, True, None)

        table_lines = []
        table_lines.append(self._rst_rubric("Module Summary"))
        table_lines.append(self._rst_table_header("left", None, 0))

        module_column = [f"`{m} <./{m}.html>`_" for m in modules_listing]
        docs = [modules_docs[m]["doc"] for m in modules_listing]
        doc_column = [(doc or " ").split("\n")[0] for doc in docs]

        table_lines.extend(self._rst_table_rows(1, [module_column, doc_column]))

        headered_module_summary = []
        headered_module_summary.append(self._rst_rubric("Module Details:"))
        for m in modules_listing:
            doc_detailed = modules_docs[m]["doc"].split("\n") if modules_docs[m]["doc"] else ["No module docstring provided"]
            headered_module_summary.append(self._rst_rubric(f"`{m} <./{m}.html>`_"))
            headered_module_summary.append(self._rst_verbatim(doc_detailed))

        pregen_lines.extend(autosummary_section)

        postgen_lines.extend(toctree_lines)
        postgen_lines.extend(table_lines)
        postgen_lines.extend(headered_module_summary)  # introduces a useless toctree entry

        modules_rst_lines = modules_toctree_lines + table_lines

        with open(self.docs_stage_path + "/API.rst", "w") as f:
            f.write("\n".join(pregen_lines))

        self._run_sphinx_autogen(repo_docs_env, self.docs_stage_path, None, "API.rst")
        for m in modules_listing:
            self._strip_submodule_files_from_folder(self.docs_stage_path, m)

        with open(self.docs_stage_path + "/API.rst", "w") as f:
            f.write("\n".join(postgen_lines))
        with open(self.docs_stage_path + "/Modules.rst", "w") as f:
            f.write("\n".join(modules_rst_lines))

        self.index.append("API.rst")
        if self.toc_index:
            self.toc_index.append(("API (python)", "API.rst"))

    def _build_cpp_api(self):
        if not self.has_cpp_api:
            return

        if getattr(self, "use_fast_doxygen_conversion", True):
            self.index.append(f"API (C++) <{self.api_output_directory}/{self.ext_name}_api.rst>")
        else:
            self.index.append(f"API (C++) <_build/docs/{self.ext_name}/latest/{self.ext_name}_api.rst>")

    def _build_index(self):

        lines = []
        lines.append(f".. _{self.ext_name} module:")
        lines.append(" ")
        lines.append(".. meta::")
        if self.description:
            lines.append(f"    :description: {self.description}")
        keywords = ["omniverse", "omniverse kit", "kit", "docs", "index", "code", "dev", "developer", "api", "sdk"]
        if self.keywords:
            keywords = keywords + [keyword for keyword in self.keywords if keyword not in keywords]
        keyword_text = ", ".join(keywords)
        lines.append(f"    :keywords: {keyword_text}")
        lines.append(" ")

        lines.append(self.doc_title)
        lines.append("=" * (len(self.doc_title) + 1))
        lines.append(" ")

        # First page is "main"
        main_page = self.pages[0].split(f"/{DEFAULT_DOCS_ROOT_DIRNAME}")[1] if not self.toc_index else self.toc_index[0][1]
        main_page_target, ext = os.path.splitext(main_page)
        if ext not in [".md", ".rst"]:
            raise KitRepoDocsError("Documentation pages can only accept rst/md filetypes")
        else:
            lines.append(".. raw:: html")
            lines.append(" ")
            lines.append(f"    <meta http-equiv=\"Refresh\" content=\"0; url=./{main_page_target}.html\" />")
            lines.append(" ")

        # Auto-move changelog to the end
        toc_index = self.index if not self.toc_index else self.toc_index
        for i, p in enumerate(toc_index):
            if isinstance(p, tuple):
                p = p[1]
            if p.lower() == "changelog.md":
                self.index.append(self.index.pop(i))
                break

        lines.append(".. toctree::")
        lines.append(f"    :caption: {self.ext_name}")

        lines.append(" ")
        # Sometimes the index gets duplicate entries so keep track and filter them out.
        # (Did not use list(set(toc_index)) because that could change the ordering.)
        done = set()
        for e in toc_index:
            if e in done:
                continue
            done.add(e)
            if isinstance(e, tuple):
                lines.append(f"    {e[0]} <{e[1]}>")
            else:
                lines.append(f"    {e}")

        lines.append("")

        with open(self.docs_stage_path + "/index.rst", "w") as f:
            f.write("\n".join(lines))

    def _dump_web_meta_data(self, repo_docs_env):
        builds = ['public']
        if 'builds' in repo_docs_env.settings['project']:
            builds += list(repo_docs_env.settings['project']['builds'].keys())
        for build in builds:
            self.web_meta_data["build"] = build
            latest = str(repo_docs_env.project_latest_dst)
            if build != "public" and not latest.endswith(f"-{build}"):
                latest += f"-{build}"
            output_dir = Path(latest)
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / "kit_repo_docs.json"
            with open(output_path, "w") as f:
                f.write(json.dumps(self.web_meta_data))

    def _build_docs_using_kit(self, config: str):
        gen_path = f"{self.ext_root}/docs-gen"
        os.makedirs(gen_path, exist_ok=True)

        hash_checker = FileHashChecker(self.pages, gen_path)
        if hash_checker.check_anything_changed():
            # Something changed, but was not committed (detected on TC):
            if omni.repo.man.is_running_on_ci():
                raise KitRepoDocsError(f"Running kit to build docs is disabled on CI as it requries GPU. Run docs build locally and git commit changes in: `{gen_path}`")

            self._run_kit_documentation_builder(config, gen_path)

            # Sanity check we have the same output count of pages as input
            gen_page_count = len(glob.glob(gen_path + "/*.md"))
            input_page_count = len(self.pages)
            if input_page_count != gen_page_count:
                raise KitRepoDocsError(f"Failed to generate doc using kit. Input page count ({input_page_count}) != Generated page count ({gen_page_count})")

            hash_checker.save()

        shutil.copytree(gen_path, self.docs_stage_path)

    def _run_kit_documentation_builder(self, config: str, gen_path: str):
        """Run "kit.exe --enable omni.kit.documentation.builder..." pipeline to convert runtime docs to sphinx input."""
        platform = omni.repo.man.get_host_platform()

        def sub_extra_tokens(s):
            return Template(s).substitute({"config": config, "platform": platform})

        def process_path(p):
            return os.path.normpath(sub_extra_tokens(p))

        tool_config = self.kit_docs_config
        kit_path = process_path(tool_config.get("kit_path"))

        args = [kit_path, "--allow-root"]
        args += ["--no-window"]  # Is it ok?
        exts = ["omni.kit.documentation.builder", self.ext_name]
        for ext in exts:
            args += ["--enable", ext]

        for ext_folder in tool_config.get("ext_folders", []):
            args += ["--ext-folder", process_path(ext_folder)]

        script_args = [self.ext_id, gen_path]
        args += ["--exec", "generate_docs_for_sphinx.py " + " ".join(script_args)]
        args += ["--/log/flushStandardStreamOutput=1"]

        kit_extra_args = [sub_extra_tokens(arg) for arg in tool_config.get("kit_extra_args", [])]
        kit_extra_args += [sub_extra_tokens(arg) for arg in self.docs_config.get("args", [])]
        args += kit_extra_args

        print("running kit for docs generation, cmd: {}".format(_args_to_cmd(args)))
        rcode = omni.repo.man.run_process(args)
        if rcode != 0:
            # Should be an exception, but kit keeps crashing
            logger.error("Failed running kit for docs generation.")

    def _run_docs_python(self, repo_docs_env, script_path: str, script_args: List[str]):
        """Run python similar to how sphinx is run to perform module inspections"""

        args = [sys.executable, script_path] + script_args

        with PushEnv(), PushLongPythonPath(repo_docs_env.python_paths):
            path_env = "PATH" if os.name == "nt" else "LD_LIBRARY_PATH"
            for p in repo_docs_env.library_paths:
                os.environ[path_env] = os.environ.get(path_env, "") + f"{os.pathsep}{str(Path(p))}"

            logger.debug(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")
            logger.debug(f"path_env: {os.environ.get(path_env)}")

            print("running python for module inspection, cmd: {}".format(_args_to_cmd(args)))
            rcode = omni.repo.man.run_process(args)
            if rcode != 0:
                # Should be an exception, but kit keeps crashing
                logger.error("Failed running python for module inspection")

    def _run_sphinx_autogen(self, repo_docs_env, workdir: str, module: str, sourcefile: str):
        """Run sphinx-autogen to generate stub files similar to autosummary"""

        # templates_root = Path(repo_docs_env.tool_root) / "autosummary_templates" # maybe we'll get templates merged
        templates_root = Path(__file__).parent.parent / "rst-templates"
        # sphinx_autogen_exe = "sphinx-autogen" if os.name == "nt" else "sphinx-autogen"
        script_dir = os.path.dirname(os.path.realpath(__file__))
        autosummary_script_path = os.path.join(script_dir, "kit_repo_docs_autosummary.py")

        args = [
            sys.executable,
            autosummary_script_path,
            "-o", f"{workdir}/{module}" if module else f"{workdir}",
            "--templates", f"{templates_root}",
            "--imported-members",
            "--respect-module-all",  # Make configurable?
            f"{workdir}/{sourcefile}",
        ]
        if module:
            os.makedirs(f"{workdir}/{module}", exist_ok=True)

        if getattr(getattr(repo_docs_env, "package_paths", {}), "sphinx", None):
            sphinx_path = repo_docs_env.package_paths.sphinx
        else:  # pre repo_docs requirements-files
            sphinx_path = Path(packmanapi.install("sphinx", repo_docs_env.sphinx_version)["sphinx"])
        logger.info(f"sphinx path: {sphinx_path}")

        with PushEnv(), PushLongPythonPath([sphinx_path] + repo_docs_env.python_paths):
            # need sphinx path to use sphinx-autogen / sphinx.ext.autosummary.generate
            path_env = "PATH" if os.name == "nt" else "LD_LIBRARY_PATH"
            for p in repo_docs_env.library_paths:
                os.environ[path_env] = os.environ.get(path_env, "") + f"{os.pathsep}{str(Path(p))}"

            logger.info(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")
            logger.info(f"path_env: {os.environ.get(path_env)}")

            print("running sphinx-autogen for stub generation, cmd: {}".format(_args_to_cmd(args)))
            rcode = omni.repo.man.run_process(args)
            if rcode != 0:
                # Should be an exception, but kit keeps crashing
                logger.error("Failed running sphinx-autogen for stub generation")


def get_all_projects(repo_root, kit_docs_config: dict, extra_tokens: dict):
    # extensions
    extension_roots = kit_docs_config.get("extension_roots", ["source/extensions"])
    for ext in kit_docs_config.get("extensions", []):
        for extension_root in extension_roots:
            ext_path = repo_root + f"/{extension_root}/{ext}"
            if os.path.exists(ext_path):
                break
        config_path = None  # will be found automatically
        yield ExtensionDocDesc(ext, ext_path, config_path)

    # pseudo extensions / explicit projects
    for project in kit_docs_config.get("custom_project", []):
        omni.repo.man.configuration.resolve_tokens(project, extra_tokens=extra_tokens)
        yield ExtensionDocDesc(project["name"], project["root"], project.get("config_path", None))


def get_repo_version(repo_folders: dict) -> str:
    version_file_path = repo_folders["version_file"]
    with open(version_file_path) as in_file:
        return in_file.readline().replace("\n", "").replace("\r", "")


# reads extension.toml
def _read_extension_config(project_config):
    key = 'extension_config_path'
    if key in project_config:
        filename = project_config[key]
        return omni.repo.man.get_toml_module().load(filename)
    else:
        return None


# reads the extension's repo_docs.toml
def _read_repo_docs_config(project_config):
    key = 'repo_docs_config_path'
    if key in project_config:
        print("read repo_docs config!")
        filename = project_config[key]
        repo_docs_config = omni.repo.man.get_toml_module().load(filename)
        omni.repo.man.configuration.resolve_config_tokens(repo_docs_config)
        return repo_docs_config
    else:
        return None


# maps a setting in extension.toml to a setting in repo_docs
def _add_setting_as(project_config, project_key, extension_config, extension_key):
    # the key may describe a nested table.  get access to the leaf table
    src_key_path = extension_key.split('.')
    src_config = extension_config
    for src_key in src_key_path[:-1]:
        if src_key in src_config:
            src_config = src_config[src_key]

    # the last key in the path points to the value
    src_key = src_key_path[-1]
    if src_key in src_config:
        project_config[project_key] = src_config[src_key]


def _merge_ext_repo_docs_config(projects, options):
    if options.list:
        return # --list given on command-line, don't spend time resolving the config

    for project_name in projects:
        if options.projects and project_name not in options.projects:
            continue # project won't be built, skip resolving the config (for speed)

        project_config = projects[project_name]
        extension_config = _read_extension_config(project_config)
        if extension_config:
            _add_setting_as(project_config, "version", extension_config, "package.version")
            _add_setting_as(project_config, "name", extension_config, "package.title")

        repo_docs_config = _read_repo_docs_config(project_config)
        if repo_docs_config:
            project_config = omni.repo.man.mergedicts(project_config, repo_docs_config)

        projects[project_name] = project_config


def setup_repo_tool(parser, config):
    omni.repo.docs.setup_repo_tool(parser, config)

    def run_repo_tool(options, config):
        repo_folders = config["repo"]["folders"]
        repo_root = repo_folders["root"]

        context = RunContext(repo_root, get_repo_version(repo_folders))

        tool_config = config["repo_docs"]
        kit_docs_config = tool_config.get("kit", {})

        tool_config.setdefault("projects", {})

        projects = {}

        warn_as_error = options.warn_as_error

        repo_docs_is_v1 = omni.repo.man.version.repotool_min_version_check("repo_docs", "1.0.0")

        # For each extension build repo_docs project
        for desc in get_all_projects(repo_root, kit_docs_config, extra_tokens={"config": options.config}):
            # Start with template
            project_config = EXT_DOC_PROJECT_TEMPLATE.copy()

            if repo_docs_is_v1:
                project_config.pop("logo")

            # Allow overriding template
            project_template = kit_docs_config.get("project_template", {})
            project_config = omni.repo.man.mergedicts(project_config, project_template)

            tool_prefs = ["use_fast_doxygen_conversion", "api_output_directory"]
            for tool_pref in tool_prefs:
                if tool_pref not in project_config and tool_pref in tool_config:
                    project_config[tool_pref] = tool_config[tool_pref]

            def _perform_link_substitutions(link: str, ext_name: str) -> str:
                """Return the temporary source link with pattern substitutions made.
                TODO: repo_docs will be adding support for embedding ${platform} and ${config} in the temporary_link
                      setting. Until that time we'll rely on this function doing the right thing
                """
                variant = "release"
                if options.config is not None:
                    variant = options.config
                platform = omni.repo.man.get_host_platform()
                return link.replace("PLATFORM", platform).replace("CONFIG", variant).replace("EXT_NAME", ext_name)

            # Per extension config setup
            try:
                ext_project = ExtensionDocProject(context, desc, project_config, kit_docs_config, repo_docs_is_v1)

                # Replace the extension name substitution pattern with the actual extension ID, including version number
                project_config["sphinx_conf_py_extra"] = project_config["sphinx_conf_py_extra"].replace("EXT_NAME", ext_project.ext_name)
                project_config["sphinx_conf_py_extra"] = project_config["sphinx_conf_py_extra"].replace("EXT_ID", ext_project.ext_id)
                # If there was an ogn docs directory then it has to be linked to provide access for repo_docs.
                # Otherwise it will be filtered out since there is no mechanism to indicate "include this directory for
                # toctree searches but don't parse what's in it"
                path_pattern = _perform_link_substitutions("PLATFORM/CONFIG/exts/EXT_NAME/ogn/docs", ext_project.ext_name)
                generated_path = Path(repo_root) / "_build" / path_pattern
                if generated_path.is_dir():
                    project_config["temporary_links"] = [{
                        "source": f"../../../{path_pattern}",
                        "link_path": "GeneratedNodeDocumentation"
                    }]

                # If there is a terminology substitution file then add it to the sphinx extras with myst equivalents.
                # This avoids duplication of terms for both formatting styles.
                terms_files = ext_project.docs_config.get("terms", [])
                terms = []
                for terms_file in terms_files:
                    terms_file = Path(ext_project.ext_root, terms_file)
                    if not terms_file.is_file():
                        raise KitRepoDocsError(f"Terms file {terms_file} specified in the 'terms' configuration does not exist")
                    with open(terms_file, "r") as terms_fd:
                        terms += terms_fd.readlines()

                if terms:
                    terms = "".join(terms)
                    terms = f"""
import re
RST_TERMS = re.compile(r"\.\. \|([^\|]+)\| replace:: (.*)")

rst_epilog = '''{terms}'''
# Process the epilog to add the Myst equivalent substitutions so that they work both in a .rst file as |TERM| and
# in a .md file as {{{{ TERM }}}}
for line in rst_epilog.splitlines():
    term_match = RST_TERMS.match(line)
    if term_match is None:
        continue
    term, replacement = (term_match.group(1), term_match.group(2))
    replacement = replacement.replace(":ref:", "{{ref}}")
    myst_substitutions[term] = replacement
"""
                else:
                    terms = ""

                project_config["sphinx_conf_py_extra"] = project_config["sphinx_conf_py_extra"].replace("# --TERMS--", terms)

            except Exception as e:
                raise KitRepoDocsError(f"Failed to configure repo_docs project: {desc.ext_name}. Error: {e}")

            # Allow overriding each project separately too:
            project_config = omni.repo.man.mergedicts(project_config, tool_config["projects"].get(desc.ext_name, {}))

            # Inject final configuration in tool config:
            tool_config["projects"][desc.ext_name] = project_config

            # Keep all the data around
            projects[desc.ext_name] = ext_project

            if options.list:
                config["repo_docs"]["projects"] = tool_config["projects"]

        # for each project, check if the project specifies a .toml file containing raw repo_docs settings
        _merge_ext_repo_docs_config(tool_config["projects"], options)

        # Intercept (monkey patch) _sphinx() fn in repo_docs to do pre processing before running sphinx
        _sphinx_orig_fn = omni.repo.docs.main._sphinx

        def _sphinx_custom_fn(env, roots, *args, **kwargs):
            if env.project_name in projects:
                docs_stage_path = projects[env.project_name].on_before_sphinx(env)
                if env.build_name != "public":
                    docs_stage_path += f"-{env.build_name}"
                tool_config["projects"][desc.ext_name] = docs_stage_path
                env.docs_root = Path(docs_stage_path)
                if env.project_name == "kit-manual":
                    # In order for kit-manual to have previewable visibility to the carb docs objects and links,
                    # we symlink content from inside the packman-linked package, into the docs tree,
                    # and subsequently exclude it from being packaged/published.
                    # We need both a "latest" (for dep target) and the `VERSION` labeled folder for the local link.
                    carb_mock_doc_path = os.path.join(repo_root, "_build/docs/carbonite")
                    os.makedirs(carb_mock_doc_path, exist_ok=True)
                    link_path = os.path.join(carb_mock_doc_path, "latest")
                    target_path = os.path.join(repo_root, "_build/target-deps/carb_docs/_build/docs/carbonite/latest")
                    packmanapi.link(link_path=link_path, target_path=target_path)
                    carb_version_file = os.path.join(link_path, "VERSION")
                    carb_version = Path(carb_version_file).read_text().strip()
                    link_path = os.path.join(carb_mock_doc_path, carb_version)
                    packmanapi.link(link_path=link_path, target_path=target_path)
                if env.project_name == "pxr-usd-api": # as much as we don't want one-offs, we don't want configurable allowances for warnings
                    env.cmdline.warn_as_error = False
                else:
                    env.cmdline.warn_as_error = warn_as_error
            return _sphinx_orig_fn(env, roots, *args, **kwargs)

        try:
            omni.repo.docs.main._sphinx = _sphinx_custom_fn
            omni.repo.docs.run_repo_tool(options, config)
        finally:
            omni.repo.docs.main._sphinx = _sphinx_orig_fn

    return run_repo_tool
