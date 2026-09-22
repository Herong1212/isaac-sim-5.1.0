# Copyright (c) 2018-2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["MDLImportItem", "MDLParser", "MdlUrlDecoder"]

import os
import time

import carb
import omni.mdl.neuraylib as neuraylib

from .async_utils import aio_re_find_all
from .omni_client_wrapper import OmniClientWrapper
from .utils import Utils



class MdlUrlDecoder:
    """MDL URL decoder utility"""
    _neuray = None
    @classmethod
    def decode(cls, text: str) -> str:
        """
        Convert MDL encoded text to plain text

        Args:
            text: Encoded text

        Returns:
            str: Decoded text
        """
        try:
            if cls._neuray is None:
                cls._neuray = neuraylib.get_neuraylib()
            return cls._neuray._unmangleUri(text, "::")
        except Exception as e:
            carb.log_warn(f"Failed to decode MDL path: {e}")
            return text


class MDLImportItem:
    def __init__(self):
        self.import_clause = ""  # The import clause like `import xx`
        self.import_package = ""  # The package name without import directive
        self.package_path = ""  # The package path converted from import package
        self.module_preset = False  # If it's preset.

    def __repr__(self):
        s = f"<'import_clause': {self.import_clause},"
        s += f"'import_package': {self.import_package},"
        s += f"'packag_path': {self.package_path}>"

        return s


class MDLParser:
    """A parser of mdl file, for get the relative texture files.

    Args:
        mdl_file_path (str): Human readable string describing the exception.
        mdl_content(bytes): MDL content in bytes array.
    """

    def __init__(self, mdl_file_path, mdl_content, path_cache: dict = None):
        self._parsed = False
        self._mdl_file_path = mdl_file_path
        self._mdl_content = mdl_content
        if type(self._mdl_content) == bytes:
            self._mdl_content = self._mdl_content.decode()
        self._raw_to_absolute_texture_paths = {}
        self._mdl_imports = {}
        self._path_cache = path_cache

    @property
    def content(self):
        return self._mdl_content

    async def parse(self):
        if not self._parsed:
            start_time = time.monotonic()
            carb.log_info(f"Starting to parse MDL file {self._mdl_file_path}...")

            self._parsed = True
            texture_paths, self._mdl_imports = await self._parse_internal()

            absolute_mdl_basepath = os.path.dirname(self._mdl_file_path)
            if absolute_mdl_basepath != "/":
                absolute_mdl_basepath += "/"

            for raw_texture_path in texture_paths:
                if not raw_texture_path.strip():
                    continue

                if raw_texture_path[0] == "/":
                    texture_path = "." + raw_texture_path
                else:
                    texture_path = raw_texture_path

                absolute_texture_path = Utils.compute_absolute_path(absolute_mdl_basepath, texture_path)
                self._raw_to_absolute_texture_paths[raw_texture_path] = absolute_texture_path

            valid_imports = []
            for mdl_import in self._mdl_imports:
                mdl_import.package_path = Utils.compute_absolute_path(absolute_mdl_basepath, mdl_import.package_path)

                # If package does not exist, skip it.
                exists = self._path_cache.get(mdl_import.package_path, None)
                if exists is None:
                    exists = await OmniClientWrapper.exists(mdl_import.package_path)
                    self._path_cache[mdl_import.package_path] = exists

                if not exists:
                    continue

                valid_imports.append(mdl_import)

            self._mdl_imports = valid_imports

            end_time = time.monotonic()
            carb.log_info(f"Finished to parse MDL file {self._mdl_file_path}, time cost: {end_time - start_time}s")

        return self._raw_to_absolute_texture_paths, self._mdl_imports

    async def _parse_internal(self):
        if not self._mdl_content:
            return [], []

        external_paths = await aio_re_find_all(r'texture_(?:2d|3d|cube|ptex)[ \t]*\([ \t]*"(.*?)"', self._mdl_content)

        external_paths.extend(
            await aio_re_find_all('<input name="file" type="filename" value="(.*?)"', self._mdl_content)
        )

        external_paths.extend(await aio_re_find_all(r'bsdf_measurement[ \t]*\([ \t]*"(.*?)"', self._mdl_content))

        mdl_packages = []
        mdl_imports = []
        packages = await aio_re_find_all("(import[ \t]+(.*)::.*;)", self._mdl_content)
        packages += await aio_re_find_all("(using[ \t]+(.*)[ \t]+import.*;)", self._mdl_content)
        packages += await aio_re_find_all("(=[ \t]+(.*)::.*)", self._mdl_content)
        for imp, package in packages:
            mdl_packages.append(package)
            mdl_imports.append(imp)

        mdl_paths = self._convert_packages(mdl_packages)

        import_items = []
        for clause, package, path in zip(mdl_imports, mdl_packages, mdl_paths):
            item = MDLImportItem()
            item.import_clause = clause
            item.import_package = package
            item.package_path = path
            if clause.startswith("="):
                item.module_preset = True
            import_items.append(item)

        return external_paths, import_items

    def _convert_packages(self, packages):
        paths = []
        for mdl_package in packages:
            # OMPE-41571: should remove ZD6_3 in path
            if mdl_package.find("_") != -1:
                path = MdlUrlDecoder.decode(mdl_package)
            else:
                path = mdl_package.replace("::", "/")
            path += ".mdl"
            paths.append(path)

        return paths
