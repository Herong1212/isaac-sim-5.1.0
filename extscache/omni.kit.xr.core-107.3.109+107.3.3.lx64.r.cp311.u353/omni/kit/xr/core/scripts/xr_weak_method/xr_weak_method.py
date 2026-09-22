# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

# =================================== NOTE ====================================
# The APIs in this file are unfinished and may change in future releases
# Using these is at your own risk, and forward-compatability is not supported

import weakref
from typing import Any, Callable, Union


def XRWeakMethod(
    fn: Union[Callable[..., Any], Callable[..., None]], def_return: Any = None
) -> Union[Callable[..., Any], Callable[..., None]]:
    """
    Wrap function through a weak link so object can get deleted and
    is not forever bound inside a callable. This breaks circular links
    and helps cleanup xr.
    """

    weak = weakref.WeakMethod(fn)

    def _fn(*args, **kwargs):
        strong = weak()
        if strong is not None:
            return strong(*args, **kwargs)
        return def_return

    return _fn
