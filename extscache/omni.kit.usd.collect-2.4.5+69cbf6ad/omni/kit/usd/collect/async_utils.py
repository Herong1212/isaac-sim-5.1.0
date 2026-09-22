# Copyright (c) 2018-2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["aio_open_layer", "aio_re_find_all", "aio_replace_all", "aio_save_layer", "aio_re_sub_all"]

import re
from omni.kit.async_engine import run_coroutine

from pxr import Sdf, Usd

def _run_asyncio(sync_fn, *args, **kwargs):
    async def async_fn():
        return sync_fn(*args, **kwargs)

    return run_coroutine(async_fn())


def _run_replacement(s, old_text, new_text, exact_match=False):
    if type(s) == bytes:
        s = s.decode()

    if exact_match:
        return str(re.sub(r"\b{}\b".format(old_text), new_text, s))
    else:
        return s.replace(old_text, new_text)


def aio_open_layer(path):
    return _run_asyncio(Sdf.Layer.FindOrOpen, path)

def aio_save_layer(layer):
    return _run_asyncio(layer.Save)

def aio_re_find_all(regex, content):
    return _run_asyncio(re.findall, regex, content)

def aio_replace_all(s, old_text, new_text, exact_match=False):
    return _run_asyncio(_run_replacement, s, old_text, new_text, exact_match)

def aio_re_sub_all(s, pattern, replace):
    return _run_asyncio(re.sub, pattern, replace, s)
