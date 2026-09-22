# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import re, datetime
from typing import Tuple, List


def parse_version(line):
    """Try parse line as a version, assuming it will look like ' [2.3.1] - 2020-09-30 '"""
    line = line.lstrip(" #")
    m = re.match(r"\[?(?P<version>[^(\]|\s)]+)\]? - (?P<release_date>\d{4}-\d{2}-\d{2})$", line)
    if m:
        return (m.group("version"), (datetime.datetime.strptime(m.group("release_date"), "%Y-%m-%d").date()))

    # Support no date format
    m = re.match(r"\[?(?P<version>[^(\]|\s)]+)\]?$", line)
    if m:
        return (m.group("version"), None)

    m = re.match(r"\[(?P<version>Unreleased)\]$", line)
    if m:
        return (m.group("version"), None)

    return None


def parse_changelog(change: str) -> Tuple[str, datetime.date, List]:
    """Parse changelog content and yield tuples of version, date and list of strings"""
    version = None
    date = None
    content = []

    for line in change.splitlines():
        res = parse_version(line)
        if res:
            yield version, date, content

            version, date = res
            content = []
        else:
            content.append(line)

    if version:
        yield version, date, content
