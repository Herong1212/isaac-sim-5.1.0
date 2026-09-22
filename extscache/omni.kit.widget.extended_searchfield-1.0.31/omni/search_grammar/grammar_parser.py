# Copyright (c) 2020-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import datetime

# standard modules
import logging
import os
import re
from typing import List

from . import DEFAULT_FIELD_NAME, ERROR_FIELD_NAME, DefaultQueryConfig, GrammarPrefix


def str2bool(s):
    """Convert input string to bool"""
    if isinstance(s, str):
        return s.lower() in ("true", "1")
    else:
        return s


OMNI_SEARCH_GRAMMAR_OR_SUPPORT_ENABLED = str2bool(os.getenv("OMNI_SEARCH_GRAMMAR_OR_SUPPORT_ENABLED", "True"))

OMNI_SEARCH_GRAMMAR_EXT_WILDCARD_SUPPORT_ENABLED = str2bool(
    os.getenv("OMNI_SEARCH_GRAMMAR_EXT_WILDCARD_SUPPORT_ENABLED", "True")
)


def set_logger(logger_name: str, loglevel: str = "INFO"):
    """Create a simple logger.

    Args:
        str logger_name: name of the logger
        str loglevel: logging level (default: 'INFO')
    """
    logger = logging.getLogger(logger_name)
    log_level = eval("logging." + loglevel.upper())
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] {:} %(message)s".format("[" + "] [".join(logger_name.split(" ")) + "]")
    )
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.handlers = []
    logger.addHandler(ch)
    # log only once
    logger.propagate = False

    return logger


logger = set_logger("omni.search_grammar")


def get_max_results(query_dict: dict) -> int:
    subgroup_max_sizes: List[int] = []
    subgroup: List[str]
    for subgroup in query_dict[GrammarPrefix.MAX_RESULTS]:
        subgroup_max_sizes.append(max([int(v) for v in subgroup]))

    return min(subgroup_max_sizes)


def get_similarity_threshold(query_dict: dict) -> float:
    subgroup_max_sizes: List[float] = []
    subgroup: List[str]
    for subgroup in query_dict[GrammarPrefix.SIMILARITY_THRESHOLD]:
        subgroup_max_sizes.append(max([float(v) for v in subgroup]))

    return min(subgroup_max_sizes)


def create_boolean_filters(query_dict: dict):
    """For each key, generate a boolean filter. If the key begins with "-",
    generate the "must_not" version of the filter.
    """

    filters = {"must": [], "filter": [], "must_not": []}

    # inclusion filters
    bf: GrammarPrefix
    for bf in [
        GrammarPrefix.CREATED_BY,
        GrammarPrefix.MODIFIED_BY,
        GrammarPrefix.DELETED_BY,
    ]:
        if bf in query_dict:
            for values in query_dict[bf]:
                bool_group = []
                for val in values:
                    bool_group.append({"match_phrase": {bf.value: val}})
                filters["filter"].append({"bool": {"should": bool_group}})

    # exclusion filters
    for bf in [
        GrammarPrefix.NOT_CREATED_BY,
        GrammarPrefix.NOT_MODIFIED_BY,
        GrammarPrefix.NOT_DELETED_BY,
    ]:
        if bf in query_dict:
            for values in query_dict[bf]:
                for val in values:
                    filters["must_not"].append({"match_phrase": {bf.value[1:]: val}})

    # boolean filters
    for bf in [GrammarPrefix.IS_DELETED]:
        if bf in query_dict:
            for values in query_dict[bf]:
                bool_group = []
                for val in values:
                    # NOTE:
                    # is_deleted field is optional, so if it not set it should be considered as False
                    #  this condition allows to return items in this case
                    if not str2bool(val):
                        bool_group.append({"bool": {"must_not": [{"exists": {"field": bf}}]}})
                    bool_group.append({"term": {bf.value: str2bool(val)}})
                filters["filter"].append({"bool": {"should": bool_group}})

    return filters


def clean_date(date: str):
    # If possible, convert the date to YYYY-MM-DD format
    output_format = "%Y-%m-%d"
    input_formats = ["%Y-%m-%d"]  # In the future we might want to allow more input formats
    for separator in ["-"]:  # In the future we might want to allow more separators
        for format in input_formats:
            try:
                f = format.replace("-", separator)
                result = datetime.datetime.strptime(date, f).strftime(output_format)
                return result
            except ValueError:
                continue

    # No luck with the above formats, try whatever we were given. This may be valid.
    return date


def create_date_filters(query_dict: dict):
    filters = []

    for query, values in query_dict.items():
        if (
            query == GrammarPrefix.CREATED_BEFORE
            or query == GrammarPrefix.MODIFIED_BEFORE
            or query == GrammarPrefix.DELETED_BEFORE
        ):
            if query == GrammarPrefix.CREATED_BEFORE:
                field_name = "created_timestamp"
            elif query == GrammarPrefix.MODIFIED_BEFORE:
                field_name = "modified_timestamp"
            elif query == GrammarPrefix.DELETED_BEFORE:
                field_name = "deleted_timestamp"

            for dates in values:
                date_group = []
                for date in dates:
                    date_group.append({"range": {field_name: {"lt": clean_date(date)}}})
                filters.append({"bool": {"should": date_group}})
        if (
            query == GrammarPrefix.CREATED_AFTER
            or query == GrammarPrefix.MODIFIED_AFTER
            or query == GrammarPrefix.DELETED_AFTER
        ):
            if query == GrammarPrefix.CREATED_AFTER:
                field_name = "created_timestamp"
            elif query == GrammarPrefix.MODIFIED_AFTER:
                field_name = "modified_timestamp"
            elif query == GrammarPrefix.DELETED_AFTER:
                field_name = "deleted_timestamp"

            for dates in values:
                date_group = []
                for date in dates:
                    date_group.append({"range": {field_name: {"gt": clean_date(date)}}})
                filters.append({"bool": {"should": date_group}})

    return filters


def parse_size(input: str, default: str = "mb"):
    input = input.lower()
    try:
        sz = float(input)
        unit = default
    except ValueError:
        unit = None

    if unit is None:
        numbers = re.findall(r"[\d.]*\d+", input)
        if len(numbers) > 1:
            raise ValueError(f"Incorrect size format: {input}")
        elif len([m.start() for m in re.finditer("\\.", numbers[0])]) > 1:
            raise ValueError(f"Multiple dots in input: {input}")
        else:
            sz = float(numbers[0])
            unit = input[len(numbers[0]) :].strip()

    if unit == "b":
        return f"{sz}"
    elif unit == "kb":
        return f"{sz * 1024}"
    elif unit == "mb":
        return f"{sz * 1024 * 1024}"
    elif unit == "gb":
        return f"{sz * 1024 * 1024 * 1024}"
    elif unit == "tb":
        return f"{sz * 1024 * 1024 * 1024 * 1024}"
    else:
        raise ValueError(f"Unknown unit: {unit} ({input})")


def create_size_filters(query_dict: dict) -> list:
    subfilter = {}
    for query, values in query_dict.items():
        if len(values) > 1:
            # TODO handle this case
            log = logging.getLogger(__name__)
            log.warning(f"Warning: more than 1 value for query: {query}")

        if GrammarPrefix.LARGER_THAN in query:
            subfilter.update({"gt": max([min([parse_size(sz) for sz in sizes]) for sizes in values])})
        if GrammarPrefix.SMALLER_THAN in query:
            subfilter.update({"lt": min([max([parse_size(sz) for sz in sizes]) for sizes in values])})
    if len(subfilter) > 0:
        return [{"range": {"size": subfilter}}]
    else:
        return []


def create_path_filters(query_dict: dict, wildcard_support: bool = True) -> list:
    """Convert the query dictionary into a component of request to Elastic Search

    Args:
        query_dict (dict): input query dicitonary
        wildcard_support (bool, optional): If ``True`` - add wildcard support. Defaults to ``True``.

    Returns:
        list: list of filter for elastic search query
    """
    filters = []
    if GrammarPrefix.PATH in query_dict:
        for paths in query_dict[GrammarPrefix.PATH]:
            path_group = []
            for p in paths:
                if p.endswith("/"):
                    p = p[:-1]
                if p != "":
                    if wildcard_support:
                        path_group.append(
                            {
                                "wildcard": {
                                    "path": {
                                        "case_insensitive": True,
                                        "value": f"*{p}*",
                                    }
                                }
                            }
                        )
                    else:
                        path_group.append({"term": {"path.tree": {"value": p}}})
            filters.append({"bool": {"should": path_group}})

    return filters


def create_name_filters(
    query_dict: dict,
    boost: float = 1.0,
    # allow_regexp: bool = False,
):
    # def proc(input: str):
    #     if allow_regexp:
    #         return input
    #     else:
    #         return f'"{input}"'

    # def proc(input: list):
    #     if allow_regexp:
    #         return "(" + "|".join(input) + ")"
    #     else:
    #         return '("' + '"|"'.join(input) + '")'

    filters = []
    if GrammarPrefix.NAME in query_dict:
        for it, p in enumerate(query_dict[GrammarPrefix.NAME]):
            name_group = []
            for case_insensitive in [True, False]:
                for word in p:
                    name_group.append(
                        {
                            "wildcard": {
                                "name": {
                                    "_name": f"name_{it}_{case_insensitive}",
                                    "case_insensitive": case_insensitive,
                                    "value": f"*{word}*",
                                    "boost": boost / len(query_dict[GrammarPrefix.NAME]),
                                    "rewrite": "constant_score",
                                }
                            }
                        },
                    )
            # for case_insensitive in [True, False]:
            for word in p:
                name_group.append(
                    {
                        "wildcard": {
                            "name": {
                                "_name": f"name_{it}_True_exact",
                                "case_insensitive": True,
                                "value": word,
                                "boost": float(
                                    query_dict.get(
                                        GrammarPrefix.EXACT_NAME_WEIGHT,
                                        [[DefaultQueryConfig.exact_name_boost]],
                                    )[0][0]
                                ),
                                "rewrite": "constant_score",
                            }
                        }
                    }
                )

            name_group.extend(
                [
                    multi_match_tag_query(
                        word,
                        fields={
                            "name": str(
                                float(
                                    query_dict.get(
                                        GrammarPrefix.EXACT_NAME_WEIGHT,
                                        [[DefaultQueryConfig.exact_name_boost]],
                                    )[0][0]
                                    / len(p)
                                    / 10
                                )
                            ),
                        },
                        analyzer="keyword",
                        name=f"name_match_{it}_{jt}",
                    )
                    for jt, word in enumerate(p)
                ]
            )
            filters.append({"bool": {"should": name_group}})

    if GrammarPrefix.NOT_NAME in query_dict:
        flat_list = [name for names in query_dict[GrammarPrefix.NOT_NAME] for name in names]
        filters.append(
            {
                "bool": {
                    "must_not": [
                        {"wildcard": {"name": {"case_insensitive": True, "value": f"*{word}*"}}} for word in flat_list
                    ]
                }
            }
        )

    return filters


def clean_ext(ext: str) -> str:
    if ext.startswith("."):
        ext = ext[1:]
    return ext


def create_ext_filters(
    query_dict: dict,
    # wildcard_support: bool = OMNI_SEARCH_GRAMMAR_EXT_WILDCARD_SUPPORT_ENABLED,
):
    result = {}

    def processing_fn(ext: str) -> dict:
        # check that special symbols are present
        wildcard_support = ext.find("*") >= 0 or ext.find("?") >= 0

        if wildcard_support:
            return {"wildcard": {"ext": {"case_insensitive": True, "value": clean_ext(ext)}}}
        else:
            return {"term": {"ext": {"value": clean_ext(ext)}}}

    if GrammarPrefix.EXT in query_dict:
        result["filter"] = [
            {"bool": {"should": [processing_fn(ext) for ext in extensions]}}
            for extensions in query_dict[GrammarPrefix.EXT]
        ]
    if GrammarPrefix.NOT_EXT in query_dict:
        result["must_not"] = [
            processing_fn(ext) for extensions in query_dict[GrammarPrefix.NOT_EXT] for ext in extensions
        ]

    return result


def create_tag_filters(query_dict: dict, filter_only: bool = False):
    tag_filters = {"must": [], "filter": [], "must_not": []}

    def generate_tag_query(tag):
        tag_dict = validate_tag(tag, allow_hidden_tags=True)
        if tag_dict is None:
            return None

        query = []
        if tag_dict["key"]:
            query = [{"match": {"tags.tag": tag_dict["key"]}}]
        if tag_dict["full_namespace"]:
            query.append({"match": {"tags.namespace": tag_dict["full_namespace"]}})
        if tag_dict["value"]:
            query.append({"match": {"tags.value": tag_dict["value"]}})

        if query:
            return {
                "nested": {
                    "path": "tags",
                    "score_mode": "max",
                    "inner_hits": {"name": tag},
                    "query": {"bool": {"must": query}},
                }
            }

    # add must include tag filters
    for tags in query_dict.get(GrammarPrefix.TAG, []):
        group_tags = []
        for tag in tags:
            filter_dict = generate_tag_query(tag)
            if filter_dict:
                group_tags.append(filter_dict)
        tag_filters["filter" if filter_only else "must"].append({"bool": {"should": group_tags}})

    # add must exclude tag filters
    for tags in query_dict.get(GrammarPrefix.NOT_TAG, []):
        for tag in tags:
            filter_dict = generate_tag_query(tag)
            if filter_dict:
                tag_filters["must_not"].append(filter_dict)
    return tag_filters


def query_list_to_string(input_list: list):
    return " ".join([",".join(words) for words in input_list])


def flatten_list_of_lists(input_list: list):
    return [w for words in input_list for w in words]


def multi_match_tag_query(
    tag_query: str,
    fields: list = {
        # "name.simple": DefaultQueryConfig.name_boost,
        "tags.tag": DefaultQueryConfig.tag_boost
    },
    # multi_match_type: str = "cross_fields",
    multi_match_type: str = "most_fields",
    score_mode: str = "max",
    name: str = "tags",
    analyzer: str = "standard",  # important, otherwise text will be treated as keywords
) -> dict:
    # tag_query = " ".join(tag_list)

    return {
        "multi_match": {
            "query": tag_query,
            "type": multi_match_type,
            "fields": [f"{k}^{v}" for k, v in fields.items()],
            "analyzer": analyzer,
            "tie_breaker": 1.0,
            "_name": name,
        }
    }


def create_default_field_filters(query_dict: dict) -> list:
    # get tag filters
    if DEFAULT_FIELD_NAME in query_dict and len(query_dict[DEFAULT_FIELD_NAME]) > 0:
        flattened_list = flatten_list_of_lists(query_dict[DEFAULT_FIELD_NAME])
        n_words = len(flattened_list)

        per_word_multimatch = [
            multi_match_tag_query(
                word,
                fields={
                    "name.simple": str(
                        float(
                            query_dict.get(GrammarPrefix.NAME_WEIGHT, [[DefaultQueryConfig.name_boost]],)[
                                0
                            ][0]
                        )
                        / n_words
                    ),
                    "tags.tag": str(
                        float(
                            query_dict.get(GrammarPrefix.TAG_WEIGHT, [[DefaultQueryConfig.tag_boost]],)[
                                0
                            ][0]
                        )
                        / n_words
                    ),
                    # "name": str(
                    #     float(
                    #         query_dict.get(
                    #             GrammarPrefix.EXACT_NAME_WEIGHT,
                    #             [[DefaultQueryConfig.exact_name_boost]],
                    #         )[0][0]
                    #     )
                    # ),
                },
                analyzer="keyword",
                name=f"multi_match_{it}",
            )
            for it, word in enumerate(flattened_list)
        ]
        # per_word_multimatch.append(
        #     multi_match_tag_query(
        #         query_list_to_string(query_dict[DEFAULT_FIELD_NAME]),
        #         fields={
        #             "name": str(
        #                 float(
        #                     query_dict.get(
        #                         GrammarPrefix.EXACT_NAME_WEIGHT,
        #                         [[DefaultQueryConfig.exact_name_boost]],
        #                     )[0][0]
        #                 )
        #             ),
        #         },
        #         analyzer="keyword",
        #         name="exact_name_match",
        #     )
        # )

        # name regexp filters
        name_match = create_name_filters(
            {GrammarPrefix.NAME: [[w] for w in flattened_list]},
            boost=float(
                query_dict.get(GrammarPrefix.NAME_REGEXP_WEIGHT, [[DefaultQueryConfig.name_regexp_boost]],)[
                    0
                ][0]
            ),
            # allow_regexp=True,
        )

        for item in name_match:
            per_word_multimatch.extend(item["bool"]["should"])

        return per_word_multimatch  # + name_match
    else:
        return []


def split(query: str):
    pieces = [p for p in re.split('("[^"]*")', query)]
    pp = [""]
    pointer = 0
    while pointer < len(pieces):
        if re.match('"*?"', pieces[pointer]) is not None:
            pp[-1] += pieces[pointer]
        else:
            for it, s in enumerate(re.split(" ", pieces[pointer])):
                if it >= 1:
                    pp.append("")
                pp[-1] += s

        pointer += 1

    if pp[-1] == "":
        pp = pp[:-1]
    return pp


def get_prefix(query: str):
    # take into account cases, where colon is a part of input, not prefix separator
    if (
        # re.match("'.*\:.*'", query) is not None
        # or
        re.match('".*\\:.*"', query)
        is not None
    ):
        result = [query[1:-1]]
    else:
        result = query.split(":")

    prefix = None
    value = result[0]

    if len(result) > 1:
        if len(result) > 2:
            # Multiple colons in an expression - only use the 1st.
            prefix = result[0]
            value = ":".join(result[1:])
        else:
            prefix = result[0]
            value = result[1]

    value = [item.strip(",") for item in re.split('("[^"]*")', value)]
    res_value = []
    for v in value:
        if re.match('".*"', v) is not None:
            res_value.append(v[1:-1])
        elif v != "":
            if OMNI_SEARCH_GRAMMAR_OR_SUPPORT_ENABLED:
                res_value.extend(v.split(","))
            else:
                res_value.append(v)

    return prefix, res_value


def parse_query(query: str):
    log = logging.getLogger(__name__)
    words = split(query)
    queries = {}
    for word in words:
        prefix, rest = get_prefix(word)
        if rest in [[""], [], ""] and prefix != "":
            log.warning(f"Empty string for prefix '{prefix}' - skipping")
            continue

        # GrammarPrefix is an Enum, so we cannot say `if prefix in GrammarPrefix`
        found = False
        for legal_prefix in GrammarPrefix:
            if prefix == legal_prefix:
                found = True

        if prefix and found:
            if prefix not in queries:
                queries[prefix] = []
            queries[prefix].append(rest)
        elif prefix is None:
            # request from @Boris Ustaev:
            #  if a wildcard symbol is present in the word - convert it into a name filter
            if re.match(".*(\\*|\\?).*", "".join(rest)) is not None:
                # Default to name for quieries without prefixes
                queries[GrammarPrefix.NAME] = queries.get(GrammarPrefix.NAME, []) + [rest]
            else:
                # Default to name for quieries without prefixes
                queries[DEFAULT_FIELD_NAME] = queries.get(DEFAULT_FIELD_NAME, []) + [rest]
        else:
            queries[ERROR_FIELD_NAME] = queries.get(ERROR_FIELD_NAME, []) + [word]

    return queries


def create_filters(query_dict: dict, path: str):
    filters = []
    if GrammarPrefix.PATH in query_dict:
        filters += create_path_filters(query_dict)
    elif len(path) > 1:
        filters += create_path_filters({GrammarPrefix.PATH: [[path]]}, wildcard_support=False)
    name_filters = create_name_filters(query_dict)
    filters += create_date_filters(query_dict)
    filters += create_size_filters(query_dict)
    tag_filters = create_tag_filters(query_dict)
    ext_result = create_ext_filters(query_dict)
    bool_filters = create_boolean_filters(query_dict)

    # create default field filters
    default_filter = create_default_field_filters(query_dict)
    tag_filters["must"] = tag_filters.get("must", []) + name_filters
    tag_filters["should"] = tag_filters.get("should", []) + default_filter
    tag_filters["filter"] = (
        tag_filters.get("filter", []) + ext_result.get("filter", []) + bool_filters.get("filter", [])
    )
    tag_filters["must_not"] = (
        tag_filters.get("must_not", []) + ext_result.get("must_not", []) + bool_filters.get("must_not", [])
    )

    return filters, tag_filters


def validate_tag(tag, allow_hidden_tags=True):
    """Validate the tag, make sure there is a category, namespace, and key,
    and return the dict if valid.
    """
    is_hidden = False
    namespace = None
    hidden_label = None
    kv_split = tag.split("=")
    full_key = kv_split[0]
    val = ""
    if len(kv_split) > 2:
        return None
    if ".." in full_key:
        return None

    if len(kv_split) > 1:
        val = kv_split[1]

    dot_split = full_key.split(".")

    # the full_namespace combines the hidden/system namespace with the normal one.
    if len(dot_split) <= 1:
        key = full_key
        full_namespace = ""
    else:
        key = dot_split[-1]
        full_namespace = ".".join(dot_split[:-1])

    # remove the key
    dot_split = dot_split[:-1]

    if len(dot_split) >= 1 and dot_split[0] == "":
        # a hidden/system namespace begins with a .
        is_hidden = True
        # remove the empty string
        dot_split = dot_split[1:]

        if len(dot_split) == 0:
            return None
        elif len(dot_split) == 1:
            namespace = ""
            hidden_label = "." + dot_split[0]
        else:
            # a namespace may contain multiple .'s, but the system namespace may not
            hidden_label = "." + dot_split[-1]
            namespace = ".".join(dot_split[:-1])
    else:
        if full_namespace == "":
            namespace = ""
        else:
            namespace = ".".join(dot_split)

    if not key:
        return None

    if is_hidden and not allow_hidden_tags:
        return None

    return {
        "hidden_label": hidden_label,
        "namespace": namespace,
        "key": key,
        "value": val,
        "full_namespace": full_namespace,
    }


def parse_description(query_dict: dict):
    return query_list_to_string(query_dict[GrammarPrefix.DESCRIPTION])
