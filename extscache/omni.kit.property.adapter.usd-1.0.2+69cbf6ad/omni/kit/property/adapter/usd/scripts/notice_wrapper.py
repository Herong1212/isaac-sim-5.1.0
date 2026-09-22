# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from typing import Callable

from pxr import Sdf, Tf, Usd


class TfNoticeWrapper:
    # NOTE: attr_names and prim_paths are unused. Added to keep the interface the same as RtChangeTrackerWrapper
    def __init__(
        self,
        attr_names: list[str],
        prim_paths: list[Sdf.Path],
        callback: Callable[[Usd.Notice.ObjectsChanged, Usd.Stage], None],
        stage: Usd.Stage,
    ):

        # Setup Tf Notice listener
        self._listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, callback, stage)

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self._listener:
            self._listener.Revoke()
            self._listener = None
