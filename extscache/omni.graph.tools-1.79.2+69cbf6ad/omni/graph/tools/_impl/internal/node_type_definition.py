"""Management of the files related to a node type definition and its generated files."""

from __future__ import annotations

from asyncio import streams
from collections import abc
from contextlib import suppress
from pathlib import Path

import carb
import omni.graph.tools.ogn as ogn

from ..node_generator.utils import Settings
from .file_utils import (
    GENERATED_FILE_CONFIG_NAMES,
    GENERATED_FILE_LOCATIONS,
    GENERATORS,
    FileType,
    get_ogn_file_name,
    is_generated_file_type,
    is_user_file_type,
)
from .logging_utils import LOG
from .versions import Compatibility, GenerationVersions


# ==============================================================================================================
class NodeTypeDefinition:
    """Class that manages everything required for a node type definition
    Members:
        name: Unique name of the node type
        cached_files: Dictionary of file type to (path, mtime) for files scanned from the cache
        cached_versions: Extension version information for the set of cached files
        generated_files: Dictionary of file type to (path, mtime) for files scanned from the generated build directory
        generated_versions: Extension version information for the set of generated files
        user_files: Dictionary of file type to (path, mtime) for files scanned from the user-defined node type files
        __generated_file_types: (Cache of file types that the node definition allows to be generated, modification time
                                of the .ogn from which that information was taken)
    """

    # --------------------------------------------------------------------------------------------------------------
    class _TypedFiles:
        """A collection of typed files that have their modification time readily available.
        These are the files that are written by the user and so do not require version information. There can only be
        one of these registered for a single node type.
        """

        def __init__(self):
            self.file_info = {}

        def __len__(self) -> int:
            return len(self.file_info)

        def __str__(self) -> str:
            return ", ".join(f"{file_type}: ({path}, {mtime})" for file_type, (path, mtime) in self.file_info.items())

        def __getitem__(self, file_type: FileType) -> tuple[Path, float]:
            """Returns the file path and last modification time for a given file type, (None, 0) if no such file"""
            return self.file_info.get(file_type, (None, 0))

        def __setitem__(self, file_type: FileType, file_path: Path):
            """Add a file of a given type to the collection"""
            mtime = file_path.stat().st_mtime if file_path is not None and file_path.is_file() else 0
            self.file_info[file_type] = (file_path, mtime)

        def touch(self, file_type: FileType) -> bool:
            """For testing - touch the file of the given type, returning True iff the file existed and was touched"""
            with suppress(KeyError):
                file_to_touch, _old_time = self.file_info[file_type]
                if file_to_touch is not None and file_to_touch.is_file():
                    _ = LOG.disabled or LOG.info("--> Touch %s", file_to_touch)
                    file_to_touch.touch()
                    # Add 1 to the touch time to ensure that the value is more recent
                    self.file_info[file_type] = (file_to_touch, file_to_touch.stat().st_mtime + 1)
                    return True
            return False

        def keys(self) -> abc.KeysView[FileType]:
            """Like a dictionary, returns the list of available file type keys (mostly for testing)"""
            return self.file_info.keys()

        def values(self) -> abc.ValuesView[FileType]:
            """Like a dictionary, returns the list of available file type values (mostly for testing)"""
            return self.file_info.values()

        def items(self) -> abc.ItemsView[FileType]:
            """Like a dictionary, returns the key:value paris of the available file type values (mostly for testing)"""
            return self.file_info.items()

    # --------------------------------------------------------------------------------------------------------------
    def __init__(self, name: str, ogn_file_path: Path):
        """Sets up a node type definition, pointing to the .ogn file that defines it.
        Raises ValueError if the path was not found or not a .ogn file"""
        _ = LOG.disabled or LOG.info("Creating node type definition for %s at %s", name, ogn_file_path)
        self.name = name
        if not ogn_file_path.is_file() or not ogn_file_path.name.endswith(".ogn"):
            raise ValueError(f"Attempted to create a node type definition with non-ogn file {ogn_file_path}")
        self.cached_files = self._TypedFiles()
        self.cached_versions = GenerationVersions(Compatibility.FullyCompatible)
        self.generated_files = self._TypedFiles()
        self.generated_versions = GenerationVersions()
        self.user_files = self._TypedFiles()
        self.user_files[FileType.OGN] = ogn_file_path
        self.__generated_file_types = ([], 0)

    # --------------------------------------------------------------------------------------------------------------
    def __str__(self) -> str:
        """Return a user-friendly representation of a node type definition"""
        return f"({self.name}:\n    GENERATED: {self.generated_files}\n    USER: {self.user_files})"

    # --------------------------------------------------------------------------------------------------------------
    def db_class_name(self) -> str:
        """Returns a string containing the expected database class name for this node type's definition"""
        return f"{self.name}Database"

    # --------------------------------------------------------------------------------------------------------------
    def file_mtime(self, file_type: FileType) -> float:
        """Return the modification time of the file of the most recent file of the given type on this node type,
        0 if it does not exist"""
        try:
            if is_user_file_type(file_type):
                return self.user_files[file_type][1]
            (_gen_path, gen_mtime) = self.generated_files[file_type]
            (_cache_path, cache_mtime) = self.cached_files[file_type]
            # Since non-existent files have 0 as their time this comparison will default to the generated version
            if cache_mtime > gen_mtime:
                return cache_mtime
            return gen_mtime
        except (KeyError, IndexError):
            return 0

    # --------------------------------------------------------------------------------------------------------------
    def file_path(self, file_type: FileType) -> Path | None:
        """Return the path to the file of the given type on this node type, None if it does not exist"""
        try:
            if is_user_file_type(file_type):
                return self.user_files[file_type][0]
            (gen_path, gen_mtime) = self.generated_files[file_type]
            (cache_path, cache_mtime) = self.cached_files[file_type]
            # Since non-existent files have 0 as their time this comparison will default to the generated version
            if cache_mtime > gen_mtime:
                return cache_path
            return gen_path
        except (KeyError, IndexError):
            return None

    # --------------------------------------------------------------------------------------------------------------
    def __warn_if_not_same_size(self, file1: Path, file2: Path, file_type: FileType):
        """Issue a warning if the two files are not pointing to the same thing (e.g. symlinks).
        Use the size of the file as a good-enough quick guess that they are identical, which is the usual case
        """
        try:
            file1_size = file1.stat().st_size
        except TypeError:
            file1_size = 0
        try:
            file2_size = file2.stat().st_size
        except TypeError:
            file2_size = 0

        if file1_size != file2_size:
            carb.log_warn(
                f"Two copies of the file of type {file_type} found\n",
                f"Using {file1} (size {file1_size}), ignoring {file2} (size {file2_size})",
            )

    # --------------------------------------------------------------------------------------------------------------
    def add_files(self, files_to_add: list[tuple[Path, FileType]], versions: GenerationVersions = None):
        """Add a new set of files to the collection of files related to this node type.
        The files are unfiltered so verify that each one is a valid file
        Args:
            files_to_add: List of (Path, FileType) for all files to potentially be added
            versions: Versions used for the creation of the generated files, if any
        """
        if not files_to_add:
            return
        _ = LOG.disabled or LOG.info("Adding %d files at version %s", len(files_to_add), versions)
        if versions is not None:
            self.generated_versions = versions
        for file_path, file_type in files_to_add:
            current_path = self.generated_files[file_type][0]
            if is_user_file_type(file_type):
                _ = LOG.disabled or LOG.info("add user file(%s, %s)", file_path, file_type)
                if current_path is not None:
                    self.__warn_if_not_same_size(current_path, file_path, file_type)
                    continue

                self.user_files[file_type] = file_path
                continue

            # Anything not recognized is silently skipped
            if not is_generated_file_type(file_type):
                _ = LOG.disabled or LOG.debug("...skipping unknown file type '%s'", file_type)
                continue

            _ = LOG.disabled or LOG.info("add generated file(%s, %s)", file_path, file_type)
            if current_path is not None:
                self.__warn_if_not_same_size(current_path, file_path, file_type)
                continue
            self.generated_files[file_type] = file_path

    # --------------------------------------------------------------------------------------------------------------
    def add_cached_files(self, files_to_add: list[tuple[Path, FileType]]):
        """Add a new set of cached files to the collection of files related to this node type.
        The files are unfiltered so verify that each one is a valid file
        Args:
            files_to_add: List of (Path, FileType) for all files to potentially be added - can be empty if the cache
                          will be populated later
        """
        if not files_to_add:
            return
        _ = LOG.disabled or LOG.info("Adding %d cached files at version %s", len(files_to_add), self.cached_versions)
        for file_path, file_type in files_to_add:
            current_path = self.cached_files[file_type][0]
            # Anything not generated is silently skipped
            if not is_generated_file_type(file_type):
                _ = LOG.disabled or LOG.debug("...skipping unknown cache file '%s'", file_path)
                continue

            _ = LOG.disabled or LOG.info("...add cached file(%s, %s)", file_path, file_type)
            if current_path is not None:
                self.__warn_if_not_same_size(current_path, file_path, file_type)
                continue
            self.cached_files[file_type] = file_path

    # --------------------------------------------------------------------------------------------------------------
    def database_to_use(self) -> Path | None:
        """Returns a path to the database file that matches the required versions and is newer than the .ogn file.
        If neither the generated or cached file fit that requirement then None is returned.
        """
        current_versions = GenerationVersions(Compatibility.FullyCompatible)
        (path, ogn_mtime) = self.user_files[FileType.OGN]
        if path is None:
            _ = LOG.disabled or LOG.debug("Database cannot be out of date when no .ogn file exists")
            return False

        def __version_out_of_date(path: Path, mtime: float, versions: GenerationVersions) -> bool:
            """Check the version and timing for either a cached or generated file"""
            if path is None or versions.compatibility(current_versions) == Compatibility.Incompatible:
                return True
            return mtime < ogn_mtime

        # Check both the generated and cached version of the file type
        (path, _) = self.generated_files[FileType.PYTHON_DB]
        if path is None:
            # C++ nodes may have excluded generation of the Python DB so use their own DB as the check instead
            (path, _) = self.generated_files[FileType.CPP_DB]
        # ogn_mtime is used to skip the out of date check on package files.
        if path is None or __version_out_of_date(path, ogn_mtime, self.generated_versions):
            (path, mtime) = self.cached_files[FileType.PYTHON_DB]
            if not __version_out_of_date(path, mtime, self.cached_versions):
                return path
            (path, mtime) = self.cached_files[FileType.CPP_DB]
            if not __version_out_of_date(path, mtime, self.cached_versions):
                return path
            return None

        return path

    # --------------------------------------------------------------------------------------------------------------
    def test_to_use(self) -> Path | None:
        """Returns a path to the generated test file that matches the required versions and is newer than the .ogn file.
        If neither the generated or cached file fit that requirement then None is returned.
        """
        current_versions = GenerationVersions(Compatibility.FullyCompatible)
        (path, ogn_mtime) = self.user_files[FileType.OGN]
        if path is None:
            _ = LOG.disabled or LOG.debug("Database cannot be out of date when no .ogn file exists")
            return False

        def __version_out_of_date(path: Path, mtime: float, versions: GenerationVersions) -> bool:
            """Check the version and timing for either a cached or generated file"""
            if path is None or versions.compatibility(current_versions) == Compatibility.Incompatible:
                return True
            return mtime < ogn_mtime

        # Check both the generated and cached version of the file type

        (path, _) = self.generated_files[FileType.TEST]
        # ogn_mtime is used to skip the out of date check on package files.
        if __version_out_of_date(path, ogn_mtime, self.generated_versions):
            (path, mtime) = self.cached_files[FileType.TEST]
            if not __version_out_of_date(path, mtime, self.cached_versions):
                return path
            return None

        return path

    # --------------------------------------------------------------------------------------------------------------
    def is_out_of_date(self, versions_required: GenerationVersions) -> bool:
        """Returns True iff this node type is out of date compared to the given versions.
        That means that either the database is missing, is older than the .ogn, or was generated with a version that
        is not compatibile with the one passed in. If a cache was read then consider the contents of it as well.
        """
        (path, ogn_mtime) = self.user_files[FileType.OGN]
        if path is None:
            _ = LOG.disabled or LOG.debug("Database cannot be out of date when no .ogn file exists")
            return False

        def __version_out_of_date(path: Path, mtime: float, versions: GenerationVersions) -> bool:
            """Check the version and timing for either a cached or generated file"""
            # If the file came from the build tree the version will be the same (unless the dev forgot to rebuild,
            # in which case it's on them to fix), and the version from the cache the versions are chosen to be the
            # same so a simple equality comparison is enough to determine if it is up to date.
            if path is None or versions.compatibility(versions_required) == Compatibility.Incompatible:
                _ = LOG.disabled or LOG.info(
                    "-> Database for %s with version %s is not compatible with version %s (%s)",
                    self.name,
                    versions,
                    versions_required,
                    path,
                )
                return True
            if mtime < ogn_mtime:
                _ = LOG.disabled or LOG.info(
                    "-> Database for %s built at %f is older than .ogn at %f (%s)", self.name, mtime, ogn_mtime, path
                )
                return True
            return False

        # Check both the generated and cached version of the file type
        (path, _) = self.generated_files[FileType.PYTHON_DB]
        if path is None:
            # C++ nodes may have excluded generation of the Python DB so use their own DB as the check instead
            (path, _) = self.generated_files[FileType.CPP_DB]
        # ogn_mtime is used to skip the out of date check on package files.
        if path is None or __version_out_of_date(path, ogn_mtime, self.generated_versions):
            (path, mtime) = self.cached_files[FileType.PYTHON_DB]
            if path is None:
                (path, mtime) = self.cached_files[FileType.CPP_DB]
            return __version_out_of_date(path, mtime, self.cached_versions)

        return False

    # --------------------------------------------------------------------------------------------------------------
    def _can_generate(self) -> list[str]:
        """Returns the list of file types this node definition allows to be generated"""
        _ = LOG.disabled or LOG.info("Checking for file types that can be generated")
        (ogn_file, mtime) = self.user_files[FileType.OGN]

        # Only rebuild if there is a .ogn file and it is newer than the one last scanned
        if ogn_file is not None and mtime > self.__generated_file_types[1]:
            # A quick read can be made to determine the full set of generated files a particular node supports.
            # This is faster than a full scan, though still not the O(1) that we'd like.
            node_can_generate = ogn.NodeInterface.quick_generation_check(ogn_file)
            can_generate_types = [
                generated_file_type
                for generated_file_type, config_name in GENERATED_FILE_CONFIG_NAMES.items()
                if config_name in node_can_generate
            ]
            # Generation of the icon modifies data in the node interface so force it to happen first
            with suppress(ValueError):
                can_generate_types.remove(FileType.ICON)
                can_generate_types.insert(0, FileType.ICON)
            self.__generated_file_types = (can_generate_types, mtime)
        return self.__generated_file_types[0]

    # --------------------------------------------------------------------------------------------------------------
    def iter_valid_generated_filetypes(self) -> str:
        """Generator that iterates over the set of file types the node type is expected to generate"""
        yield from self._can_generate()

    # --------------------------------------------------------------------------------------------------------------
    def iter_all_known_files(self) -> str:
        """Generator that iterates over the set of existing files known to this definition"""
        for user_file_path, _user_mtime in self.user_files.values():
            if user_file_path.is_file():
                yield user_file_path
        for generated_file_path, _generated_mtime in self.generated_files.values():
            if generated_file_path.is_file():
                yield generated_file_path
        for cached_file_path, _cached_mtime in self.cached_files.values():
            if cached_file_path.is_file():
                yield cached_file_path

    # --------------------------------------------------------------------------------------------------------------
    def generate(
        self, generation_root: Path, ext_name: streams, module_name: str, config_dir: Path, categories: dict[str, str]
    ) -> bool:
        """Generate the node code into the appropriate directory based on caching requirements

        Arguments all come from the extension owner, passed in individually to avoid a circular reference.

        Args:
            generation_root: Directory in the cache where this node type's generated code should go
            ext_name: Name of the extension owning this node definition
            module_name: Name of the Python module in which the generated Python files will live
            config_dir: Path to the directory containing the hard-coded OGN configuration files
            categories: Dictionary of the categories contained in the config_dir
        Returns:
            True if there was at least one test file generated (for extension scanning optimization)
        """
        _ = LOG.disabled or LOG.info(
            "Regenerating node type %s into extension %s, directory %s", self.name, ext_name, generation_root
        )

        if not generation_root:
            _ = LOG.disabled or LOG.warning("-> Cannot generate without a target path")
            return False

        has_tests = False
        # By design the files will always contain the .ogn reference so it's safe to just access it
        try:
            ogn_path = self.file_path(FileType.OGN)
        except (TypeError, KeyError):
            _ = LOG.disabled or LOG.warning(
                "Missing .ogn file in node definition %s. Skipping regeneration.", self.name
            )
            return has_tests

        # Read in and parse the .ogn file
        _ = LOG.disabled or LOG.info("Parsing ogn file %s", ogn_path)
        with open(ogn_path, "r", encoding="utf-8") as ogn_fd:
            _ = LOG.disabled or LOG.info("...Processed %s", ogn_path)
            interface_wrapper = ogn.NodeInterfaceWrapper(
                ogn_fd, extension=ext_name, config_directory=str(config_dir), categories_allowed=categories
            )

        # Populate the configuration that will be shared by all generators
        _ = LOG.disabled or LOG.info("Creating generator config")
        generator_config = ogn.GeneratorConfiguration(
            node_file_path=ogn_path.as_posix(),
            node_interface=interface_wrapper.node_interface,
            extension=ext_name,
            module=module_name,
            base_name=self.name,
            destination_directory=str(generation_root),
            verbose=not LOG.disabled,
            settings=Settings.generator_settings(),
        )

        # Walk through the list of file types this node type can generate and run the appropriate generator to do so
        _ = LOG.disabled or LOG.info("Looping over file types %s", list(self.iter_valid_generated_filetypes()))
        for generated_file_type in self.iter_valid_generated_filetypes():
            _ = LOG.disabled or LOG.info("...check for generating %s", generated_file_type)

            try:
                target_relpath = GENERATED_FILE_LOCATIONS[generated_file_type]  # eg. "docs" for doc filetype
                target_dir = generation_root / target_relpath
                generator_config.destination_directory = target_dir
                target_dir.mkdir(exist_ok=True, parents=True)

                target_file_path = target_dir / get_ogn_file_name(self.name, generated_file_type)

                _ = LOG.disabled or LOG.info(
                    "-> adding generation of %s using %s", target_file_path, GENERATORS[generated_file_type]
                )
                return_value = GENERATORS[generated_file_type](generator_config)
                # The icon generator is a bit of an oddball as it sets new metadata onto the node interface
                if generated_file_type == FileType.ICON:
                    interface_wrapper.node_interface.icon_path = return_value

                self.cached_files[generated_file_type] = target_file_path

                if generated_file_type == FileType.TEST:
                    has_tests = True
            except Exception as error:  # noqa: broad-except
                LOG.error("Failed to generate %s from %s with %s", generated_file_type, target_file_path, error)

        return has_tests
