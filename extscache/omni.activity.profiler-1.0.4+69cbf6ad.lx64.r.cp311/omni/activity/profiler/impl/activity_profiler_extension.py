## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.ext
from .._activity_profiler_bindings import *

_activity_profiler = None

# Public API.
def get_activity_profiler() -> IActivityProfiler:
    return _activity_profiler


class ActivityProfilerExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        global _activity_profiler
        _activity_profiler = acquire_activity_profiler()

    def on_shutdown(self):
        global _activity_profiler
        release_activity_profiler(_activity_profiler)
        _activity_profiler = None
