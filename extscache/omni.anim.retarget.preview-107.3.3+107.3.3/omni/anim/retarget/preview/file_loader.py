# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#


import omni.usd
from typing import Callable
from functools import partial


class FileLoader:
    def __init__(self, context_name_prefix: str = None):
        prefix = context_name_prefix
        if prefix is None:
            prefix = ''

        load_context_name = prefix + "_loading"
        self.__load_context = omni.usd.get_context(load_context_name)
        if not self.__load_context:
            self.__load_context = omni.usd.create_context(load_context_name)

    def is_supported_file(self, path: str) -> bool:
        extensions = ['usd', 'usda', 'usdc', 'usdz']  # TODO: fbx, etc?
        split = path.split('.')
        if split and split[-1] in extensions:
            return True
        return False

    def load_file_async(self, path: str, callback: Callable[[str, bool, str], None]):
        """ Load a file asynchronously.
        Args:
            path: url to file
            callback: callback function that is called after loading was complete
        """
        # TODO: check if stage was already loaded, or close it somewhere once used
        if not self.__load_context.can_open_stage():
            # TODO: warning.
            return
        self.__load_context.open_stage_with_callback(path, partial(callback, path))

    def get_stage(self):
        if self.__load_context is None:
            return None
        return self.__load_context.get_stage()

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.__load_context:
            if self.__load_context.can_close_stage():
                self.__load_context.close_stage()
            self.__load_context = None
