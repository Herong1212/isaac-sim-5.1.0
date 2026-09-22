# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import weakref


class WeakMethod(weakref.WeakMethod):
    def __call__(self, *args, **kwargs):
        obj = weakref.ref.__call__(self)
        func = self._func_ref()
        if obj is None or func is None:
            return None
        return func(obj, *args, **kwargs)
