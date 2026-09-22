# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module provides core search functionality including a singleton decorator, abstract search item and model classes, and search lifetime management to support search operations in Omni UI."""


__all__ = [
    "AbstractSearchItem",
    "AbstractSearchModel",
    "SearchLifetimeObject",
    "SearchEngineRegistry",
]

from .abstract_search_model import AbstractSearchItem
from .abstract_search_model import AbstractSearchModel
from .abstract_search_model import SearchLifetimeObject
from .search_engine_registry import SearchEngineRegistry
