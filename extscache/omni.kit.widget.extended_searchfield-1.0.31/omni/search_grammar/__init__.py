# Copyright (c) 2020-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

# standard modules
import os
from dataclasses import dataclass
from enum import Enum

DEFAULT_FIELD_NAME = "default"
ERROR_FIELD_NAME = "error"


class GrammarPrefix(str, Enum):
    NAME = "name"
    NOT_NAME = "-name"
    EXT = "ext"
    NOT_EXT = "-ext"
    MAX_RESULTS = "max"
    PATH = "path"
    TAG = "tag"
    NOT_TAG = "-tag"
    LARGER_THAN = "larger_than"
    SMALLER_THAN = "smaller_than"
    DESCRIPTION = "description"
    NOT_DESCRIPTION = "-description"
    IMAGE = "image"
    CREATED_BY = "created_by"
    NOT_CREATED_BY = "-created_by"
    MODIFIED_BY = "modified_by"
    NOT_MODIFIED_BY = "-modified_by"
    CREATED_BEFORE = "created_before"
    CREATED_AFTER = "created_after"
    MODIFIED_BEFORE = "modified_before"
    MODIFIED_AFTER = "modified_after"
    SEARCH_METHOD = "search_method"
    NAME_WEIGHT = "name_weight"
    EXACT_NAME_WEIGHT = "exact_name_weight"
    NAME_REGEXP_WEIGHT = "name_regexp_weight"
    TAG_WEIGHT = "tag_weight"
    SIMILARITY_THRESHOLD = "similarity_threshold"
    DELETED_BEFORE = "deleted_before"
    DELETED_AFTER = "deleted_after"
    DELETED_BY = "deleted_by"
    NOT_DELETED_BY = "-deleted_by"
    IS_DELETED = "is_deleted"


@dataclass
class DefaultQueryConfig:
    tag_boost: float = float(os.getenv("DEFAULT_QUERY_CONFIG_TAG_BOOST", "0.004"))
    name_boost: float = float(os.getenv("DEFAULT_QUERY_CONFIG_NAME_BOOST", "0.001"))
    exact_name_boost: float = float(os.getenv("DEFAULT_QUERY_CONFIG_EXACT_NAME_BOOST", "1.0"))
    name_regexp_boost: float = float(os.getenv("DEFAULT_QUERY_CONFIG_NAME_REGEXP_BOOST", "0.003"))
    embedding_boost: float = float(os.getenv("DEFAULT_QUERY_CONFIG_EMBEDDING_BOOST", "1.0"))


from .grammar_parser import (
    create_filters,
    flatten_list_of_lists,
    get_max_results,
    get_similarity_threshold,
    parse_description,
    parse_query,
)

__all__ = [
    "create_filters",
    "flatten_list_of_lists",
    "parse_description",
    "parse_query",
    "get_max_results",
    "get_similarity_threshold",
]
