"""Generates node implementations from AutoNode decorators inside python code."""

import logging
import os
from io import TextIOWrapper
from pathlib import Path

import toml

from ..node_generator.main import main as generate_nodes
from .compiler import AutoNodeGenerator

_logger = logging.getLogger("AutoNode")

__all__ = ["build_autonode_from_toml", "build_autonode_from_paths"]


# ==============================================================================================================
def build_autonode_from_paths(
    module_root: Path,
    module_name: str,
    import_module_paths: list[str],
    ogn_folder: Path,
    node_type_folder: Path,
):  # pragma: no cover    Unsupported code
    """Controls the pipeline of building autonode from a module root to generating all needed files.

    Args:
        module_root: Path to the root directory where the Python module can be found
        module_name: Python module from which the folder was imported
        import_module_paths: List of module import paths to search - must be relative to "module_root", or if "" then
                             the entire "module_root" directory is searched.
        ogn_folder: Location of the directory where the .ogn files should be saved
        node_type_folder: Location of the directory where the files generated from the .ogn files should be saved.

    Raises:
        ValueError: If any of the paths or the module name are not legal
    """
    _logger.info(
        "Building AutoNode at %s for module %s using paths %s targeting folders %s and %s",
        module_root,
        module_name,
        import_module_paths,
        ogn_folder,
        node_type_folder,
    )
    # Sanity check
    module_path = module_root / "/".join(module_name.split("."))
    if not module_path.is_dir():
        raise ValueError(f"{module_name} was not found at {module_path}")

    # Search the referenced imports to find all files potentially containing AutoNode definitions.
    # An undocumented feature here is to allow Python module paths as well as file paths but as that would be more
    # difficult to fully support it is not explicitly exposed. (i.e. if your Python module is omni.my.extension and
    # you put an import_path of tests.autonode then the build path pointing to that module is added to the list:
    # $BUILD/exts/omni.my.extension/omni/my/extension/tests/autonode.py)
    import_paths = []
    for import_module_path in import_module_paths:
        if import_module_path.endswith(".py"):
            # Take care not to include the .py extension as part of the module path
            import_path = module_path / "/".join(import_module_path[:-3].split("."))
            import_path = import_path.with_suffix(".py")
        else:
            import_path = module_path / "/".join(import_module_path.split("."))
        if import_path.is_dir():
            for root, dirs, files in os.walk(str(import_path)):
                dirs[:] = [d for d in dirs if d not in ["__pycache__"]]
                for python_file in files:
                    if python_file.suffix == ".py":
                        import_paths.append(Path(root) / python_file)
        # Accept either the case of a specific file (e.g. "tests/_autonode_definitions.py")
        elif import_path.is_file():
            import_paths.append(import_path)
        # Or a file-based module name (e.g. "tests._autonode_definitions")
        elif import_path.with_suffix(".py").is_file():
            import_paths.append(import_path.with_suffix(".py"))
        else:
            raise ValueError(f"Import path element {import_path} is neither a directory nor a Python file")

    # # Step 1: Generate .ogn and .py implementations from the functions found
    # TODO: This is a good candidate for multiprocessing
    _logger.info("Building AutoNode definitions in module %s", module_name)
    _logger.debug("   Importing: %s", import_paths)
    module_generator = AutoNodeGenerator(
        module_name=module_name, python_root=module_root, import_paths=import_paths, node_folder=node_type_folder
    )
    generated_files = module_generator.parse_all()
    if _logger.level < logging.INFO:
        _logger.debug("    OGN Destination: %s", ogn_folder)
        _logger.debug("    Node Type Path:  %s", node_type_folder)
        _logger.debug("    Generated Count: %d", len(generated_files))
        for class_name, ogn_file, py_file in generated_files:
            _logger.debug("      %s, %s, %s", class_name, ogn_file, py_file)

    # Step 2: Call the normal node generation pipeline
    if node_type_folder:
        for class_name, ogn, impl in generated_files:
            _logger.debug("    Generating node definition for %s at %s/%s", class_name, ogn, impl)
            arguments = [
                "--extension",
                module_name,
                "--nodeFile",
                str(ogn),
                "--module",
                str(node_type_folder),
                "--python",
                str(node_type_folder),
                "--icons",
                str(node_type_folder / "icons"),
            ]
            _logger.debug("    Command arguments = '%s'", arguments)
            generate_nodes(arguments)


# ==============================================================================================================
def build_autonode_from_toml(
    module_root: Path, toml_file: TextIOWrapper, ogn_folder: Path, node_type_folder: Path
):  # pragma: no cover    Unsupported code
    """Controls the pipeline of building autonode from a module root to generating all needed files.

    Args:
        module_root: Path to the root directory where the Python module can be found
        toml_file: File containing the AutoNode configuration in [[python.module]] and [omni.graph.autonode]
        ogn_folder: Location of the directory where the .ogn files should be saved
        node_type_folder: Location of the directory where the files generated from the .ogn files should be saved

    Raises:
        ValueError: If any of the paths or the module name are not legal
    """
    # Sanity check
    _logger.debug("Loading .toml file %s", toml_file.name)
    try:
        toml_contents = toml.load(toml_file)
    except toml.TomlDecodeError as error:
        raise ValueError(f"Could not read {toml_file.name}") from error

    try:
        python_modules = toml_contents["python"]["module"]
        python_module = python_modules[0]["name"]
        _logger.debug("Found Python module %s", python_module)
    except KeyError as error:
        raise ValueError(f"No [[python.module]] entry in {toml_file.name}") from error
    except IndexError as error:
        raise ValueError(f"[[python.module]] in {toml_file.name} is empty but requires a module name") from error

    try:
        autonode_config = toml_contents["omni"]["graph"]["autonode"]
    except KeyError as error:
        raise ValueError(f"[omni.graph.autonode] configuration not found in {toml_file.name}") from error

    if not autonode_config.get("developer_mode", False):
        _logger.info(
            "Skipping generation of AutoNode definitions because [omni.graph.autonode.developer_mode] is false in %s",
            toml_file.name,
        )
        return

    try:
        import_paths = autonode_config["import_paths"]
        if "" in import_paths:
            if len(import_paths) > 1:
                _logger.warning(
                    "Other paths are ignored when an empty string, indicating the entire Python module directory,"
                    " is in the 'import_paths' list - %s",
                    import_paths,
                )
            import_paths = [""]
        _logger.debug("Searching import paths %s", import_paths)
    except KeyError:
        # If no import paths were specified then search the entire module
        import_paths = [""]
        _logger.debug("No import paths found, default to %s", python_module)

    build_autonode_from_paths(module_root, python_module, import_paths, ogn_folder, node_type_folder)
