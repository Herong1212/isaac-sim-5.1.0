## Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
from unittest.mock import Mock

class AsyncMock(Mock):
    """Async equivalent of Mock class"""
    def __call__(self, *args, **kwargs):
        sup = super(AsyncMock, self)
        async def coro():
            return sup.__call__(*args, **kwargs)
        return coro()

    def __await__(self):
        return self().__await__()


from .test_widget import *
from .test_populate import *
from .test_thumbnails import *
from .test_auto_refresh import *
from .test_grid_view import *
from .test_zoom_bar import *
from .test_datetime_format import *
from .test_drop import *
