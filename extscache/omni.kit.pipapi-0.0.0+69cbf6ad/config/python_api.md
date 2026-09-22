# Public API for module omni.kit.pipapi:

## Functions

- def install(package: str, module: str = None, ignore_import_check: bool = False, ignore_cache: bool = False, version: str = None, use_online_index: bool = True, surpress_output: bool = False, extra_args: typing.List[str] = None) -> bool
- def call_pip(args: typing.List[str], surpress_output: bool = False) -> int
- def remove_archive_directory(path: str)
- def add_archive_directory(path: str, root: str = None)
