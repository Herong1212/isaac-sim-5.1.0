## Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##

import time
import asyncio
import carb
from omni.kit.test.async_unittest import AsyncTestCase
from ..utils import get_user_folders_dict
from functools import wraps

# change this flag to true will print every test's cost time
PRINT_TEST_TIME = False
def time_logger(cls):
    original_init = cls.__init__

    @wraps(cls.__init__)
    def new_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self._wrap_methods()

    def _wrap_methods(self):
        if hasattr(self, 'setUp') and asyncio.iscoroutinefunction(getattr(self, 'setUp')):
            original_setup = self.setUp
            @wraps(original_setup)
            async def setup_wrapper(*args, **kwargs):
                self._start_time = time.monotonic()
                return await original_setup(*args, **kwargs)
            self.setUp = setup_wrapper

        if hasattr(self, 'tearDown') and asyncio.iscoroutinefunction(getattr(self, 'tearDown')):
            original_teardown = self.tearDown
            @wraps(original_teardown)
            async def teardown_wrapper(*args, **kwargs):
                end_time = time.monotonic()
                elapsed_time = end_time - self._start_time
                if elapsed_time > 2:
                    print("=====================Long test time==========================")
                print(f"Test time: {elapsed_time:.4f} seconds")
                return await original_teardown(*args, **kwargs)
            self.tearDown = teardown_wrapper
    if PRINT_TEST_TIME:
        cls.__init__ = new_init
        cls._wrap_methods = _wrap_methods
    return cls


class TestUtils(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        pass

    # After running each test
    async def tearDown(self):
        pass

    """Testing the get user folders functions"""
    async def test_get_user_folders(self):
        import os
        if os.name == 'nt':
            user_folders_dict = get_user_folders_dict()
            import winreg
            sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
            downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                try:
                    downloads = winreg.QueryValueEx(key, downloads_guid)[0]
                except:
                    downloads = None
                if downloads:
                    # TODO: seems only could get custom download from winreg
                    # how to get other custom user folder for test?
                    self.assertEqual(str(downloads).replace("\\", "/"), user_folders_dict["Downloads"])
