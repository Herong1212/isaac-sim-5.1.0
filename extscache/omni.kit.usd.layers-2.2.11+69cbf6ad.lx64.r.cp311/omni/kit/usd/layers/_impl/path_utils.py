# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["PathUtils"]

import traceback
import carb
import omni.client
from pxr import Sdf


class PathUtils:  # pragma: no cover
    @staticmethod
    def is_omni_objects_enabled_path(path: str):
        return omni.client.is_omni_objects_enabled(path)

    @staticmethod
    def compute_absolute_path(base_path, path):
        """Computes absolute path.

        Args:
            base_path (str): Absolute path that path will be based on.
            path (str): Path to be combined.
        """

        if Sdf.Layer.IsAnonymousLayerIdentifier(path) or Sdf.Layer.IsAnonymousLayerIdentifier(base_path):
            return omni.client.normalize_url(path)

        # If it's old path without server, it needs to strip omni prefix
        if not path.startswith("omni://") and path.startswith("omni:/"):
            path = path[5:]

        return omni.client.combine_urls(base_path, path)

    @staticmethod
    def compute_relative_path(base_path, file_path):
        """Computes relative path given base path.

        Args:
            base_path (str): Absolute path that file path will be relative to.
            file_path (str): Absolute path.

        Return:
            Relative path of file_path that is relative to base_path. If base_path
            and file_path are not in the same domain or server, it will return file_path
            directly.
        """
        if Sdf.Layer.IsAnonymousLayerIdentifier(file_path) or Sdf.Layer.IsAnonymousLayerIdentifier(base_path):
            return omni.client.normalize_url(file_path)

        return omni.client.make_relative_url(base_path, file_path)

    @staticmethod
    async def exists_async(path):
        try:
            result, _ = await omni.client.stat_async(path)
            return result == omni.client.Result.OK
        except Exception as e:
            traceback.print_exc()
            carb.log_error(str(e))
            return False

    @staticmethod
    def exists_sync(path):
        try:
            result, _ = omni.client.stat(path)
            return result == omni.client.Result.OK
        except Exception as e:
            traceback.print_exc()
            carb.log_error(str(e))
            return False
