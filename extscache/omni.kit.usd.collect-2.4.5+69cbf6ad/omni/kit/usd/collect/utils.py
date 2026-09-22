# Copyright (c) 2018-2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["Utils"]

import re
import omni.usd
import omni.client
from urllib.parse import unquote

from pxr import Sdf


class Utils:
    MDL_RE = re.compile("^.*\\.(mdl|mtlx)?$", re.IGNORECASE)
    # References https://gitlab-master.nvidia.com/omniverse/rtxdev/kit/blob/d37f0906c58cb1a5d8591f9e47125b4154b19b88/rendering/source/plugins/common/UDIM.h#L22
    # for regex details to detect udim textures.
    UDIM_MARKER_RE = re.compile("^.*(<UDIM>|<UVTILE0>|<UVTILE1>).*")
    UDIM_GROUP_RE = re.compile("^(.*)(<UDIM>|<UVTILE0>|<UVTILE1>)(.*)")

    @staticmethod
    def normalize_path(path) -> str:
        return unquote(omni.client.normalize_url(path))

    @staticmethod
    def compute_absolute_path(base_path, path) -> str:
        return unquote(omni.client.make_absolute_url_if_possible(base_path, path))

    @staticmethod
    def is_material(path) -> bool:
        if not path:
            return False

        url = omni.client.break_url(path)
        if Utils.MDL_RE.match(url.path):
            return True

        return False

    @staticmethod
    def is_omniverse_path(path) -> bool:
        return not omni.client.is_local_url(path) and omni.client.is_valid_url(path)

    @staticmethod
    def is_udim_texture(path) -> bool:
        if not path:
            return False

        url = omni.client.break_url(path)
        if url and Utils.UDIM_MARKER_RE.match(url.path):
            return True

        return False

    @staticmethod
    def is_udim_wildcard_texture(path, udim_texture_path) -> bool:
        if not path or not udim_texture_path:
            return False

        url = omni.client.break_url(udim_texture_path)
        groups = Utils.UDIM_GROUP_RE.match(url.path)
        if not groups:
            return False

        base_path = groups[1]
        suffix_path = groups[3]
        wildcard_re = re.compile(re.escape(base_path) + "((\\d\\d\\d\\d)|(_u\\d*_v\\d*))" + suffix_path)
        url = omni.client.break_url(path)
        if wildcard_re.match(url.path):
            return True

        return False

    @staticmethod
    def make_relative_path(relative_to, path) -> str:
        return unquote(omni.client.make_relative_url_if_possible(relative_to, path))

    def is_usd_writable_filetype(path) -> bool:
        return Sdf.Layer.IsAnonymousLayerIdentifier(path) or omni.usd.is_usd_writable_filetype(path)
