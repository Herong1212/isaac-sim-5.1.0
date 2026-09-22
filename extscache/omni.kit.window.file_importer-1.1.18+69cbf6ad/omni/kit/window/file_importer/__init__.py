# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""A standardized dialog for importing files"""
__all__ = ['FileImporterExtension', 'ImportOptionsDelegate', 'get_file_importer']

from carb import log_warn
from omni.kit.window.filepicker import DetailFrameController as ImportOptionsDelegate
from .extension import FileImporterExtension, get_instance


def get_file_importer() -> FileImporterExtension:
    """Returns the singleton file_importer extension instance"""
    instance = get_instance()
    if instance is None:
        log_warn("File importer extension is no longer alive.")
    return instance