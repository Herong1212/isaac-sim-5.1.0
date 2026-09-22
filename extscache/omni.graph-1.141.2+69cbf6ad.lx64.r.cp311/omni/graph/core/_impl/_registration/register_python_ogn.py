"""Register the generated Python database objects and any node types defined by them in an extension.

Registering an extension's Python node types involves these broad steps:
1. Find all of the node types in the extension
2. Check if the database files are up to date and rebuild them in the cache if not
3. Import the up-to-date database object into the omni.my.extension.ogn package, creating it if necessary
4. Call the database's register() function to make the node type known to OmniGraph. (This step will be omitted if the
   node type is implemented in a language other than Python.)

These are the various configurations that will be handled by the registration process:

1. Node types are all prebuilt and up to date
   a. The prebuilt nodes predate the build support for embedding the version number in the module information
   b. The prebuilt nodes are in a module that itself contains version number information
2. Node types do not have any generated files, just the .py and .ogn
3. Node types are prebuilt but have an older version number
4. Node types are prebuilt or cached but a hot reload is in progress where a .ogn file has been modified
"""

from __future__ import annotations

import time
from pathlib import Path

import carb
import carb.profiler
import omni.graph.tools._internal as ogi

from .extension_management import extension_management_factory


# ==============================================================================================================
@carb.profiler.profile
def register_python_ogn(ext_name: str, module_name: str, ext_path_name: str) -> dict[str, callable]:
    """Register and potentially regenerate all Python node types defined at the module path for the extension
    This is the overall process used by the node registration:

    .. code:: text

        If AutoNode is enabled:
            For all of the AutoNode definition modules
                Find potential .ogn/.py files generated from AutoNode definitions, both locally and in the cache
                If any of the module files are newer than the .ogn or .py node type definition files
                    Run autonode_generator on the module files and overwrite the type definition files if they differ
        For all of the .ogn files in the module file tree
            Find potential generated files for the .ogn files
            Find the versions used in their generation (through the database file)
        If any of the generated files are out of date w.r.t. the current versions
            Find potential generated files in the cache directory for the current Kit OmniGraph versions
            For any files whose cached information was not found or was out of date w.r.t. the matching .ogn file
                Regenerate the out of date files
        For all of the located .ogn files
            If there is no corresponding generated database file
                issue a warning
            else
                Import the generated database file
                Call the registration function in the generated database file and save the deregistration function
        If there are any tests
            Generate the main __init__.py for the tests module for automatic test registration
            Import the test module for the extension

    Args:
        ext_name: Name of the extension owning the node types
        module_name: Name of the module containing the node types, usually the same as ext_name
        ext_path_name: Path to the root of the extension containing the module
    Returns:
        Dictionary of NodeTypeName:DeregistrationMethod Python node types that were registered here
    Raises:
        ogi.OmniGraphExtensionError if there was nothing to register
    """
    if not ogi.LOG.disabled:
        ogi.LOG.info("Registering Python Node Types from %s at %s in %s", module_name, ext_path_name, ext_name)
        ogi.LOG.info("=" * 120)
    start_time = time.perf_counter()
    deregistration_functions = {}

    ext_contents = extension_management_factory(ext_name, module_name, Path(ext_path_name))
    if ext_contents is None:
        _ = ogi.LOG.disabled or ogi.LOG.info("...None found, no registration to do")
        return {}
    _ = ogi.LOG.disabled or ogi.LOG.info("Using cache directory %s", ext_contents.cache_path)

    # Scan the extension's import modules to find any .ogn, .py, and Database.py files
    try:
        carb.profiler.begin(2, f"OGN Scan {ext_name}")
        ext_contents.scan_for_nodes()
        scan_time = time.perf_counter()
        _ = ogi.LOG.disabled or ogi.LOG.info(
            "%s: Time to scan the extension for node types = %f", ext_name, scan_time - start_time
        )
    except Exception as error:  # pylint: disable=broad-except
        carb.log_warn(f"Node scanning in {ext_name} failed - {error}. Aborting Python node registration")
        return {}
    finally:
        carb.profiler.end(2)

    # For cache files that are needed but out of date, rebuild the generated code
    try:
        carb.profiler.begin(2, f"OGN Fill Cache {ext_name}")
        ext_contents.ensure_files_up_to_date()
        update_time = time.perf_counter()
        _ = ogi.LOG.disabled or ogi.LOG.info(
            "%s: Time to update the out-of-date generated code = %f", ext_name, update_time - scan_time
        )
    except Exception as error:  # pylint: disable=broad-except
        carb.log_warn(f"Python node cache update in {ext_name} failed - {error}. Aborting Python node registration")
        return {}
    finally:
        carb.profiler.end(2)

    # Import all of the generated Python code into the EXTENSION.ogn module.
    try:
        carb.profiler.begin(2, f"OGN Import {ext_name}")
        ext_contents.do_python_imports()
        import_time = time.perf_counter()
        _ = ogi.LOG.disabled or ogi.LOG.info(
            "%s: Time to import the generated objects = %f", ext_name, import_time - update_time
        )
    except Exception as error:  # pylint: disable=broad-except
        carb.log_warn(f"Python import process in {ext_name} failed - {error}. Aborting Python node registration")
        return {}
    finally:
        carb.profiler.end(2)

    # Walk all of the import node type definitions and run their register() methods, returning the combined return
    # values which comprise their deregister() methods.
    try:
        carb.profiler.begin(2, f"OGN Register {ext_name}")
        deregistration_functions = ext_contents.do_registration()
        registration_time = time.perf_counter()
        _ = ogi.LOG.disabled or ogi.LOG.info(
            "%s: Time to register the generated objects = %f", ext_name, registration_time - import_time
        )
    except Exception as error:  # pylint: disable=broad-except
        carb.log_warn(f"Node registration process in {ext_name} failed - {error}. Aborting Python node registration")
        return {}
    finally:
        carb.profiler.end(2)

    return deregistration_functions
