## Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import os
import threading
import asyncio
import time
import tempfile
import random
import omni.kit.app
import omni.kit.test

from omni.kit import ui_test
from ..dialog import FilePickerDialog
from .test_utils import time_logger


class CreateDummyFileThread(threading.Thread):
    def __init__(self, dir: str, max_size: int = 1000, max_duration: int = 5, thread: int = 0):
        super().__init__()
        self._name = "Dummy"
        self._dir = dir
        self._max_size = max_size
        self._max_duration = max_duration
        self._thread = thread

    @property
    def name(self):
        return self._name

    def run(self):
        time.sleep(random.randrange(self._max_duration))
        with tempfile.NamedTemporaryFile(dir=self._dir, delete=False) as fp:
            fp.write(os.urandom(random.randint(1, self._max_size)))
            self._name = fp.name
        # print(f"THREAD-{self._thread} Created: ", self._name)


class DeleteDummyFileThread(threading.Thread):
    def __init__(self, name: str, max_duration: int = 5, thread: int = 0):
        super().__init__()
        self._name = name
        self._max_duration = max_duration
        self._thread = thread

    def run(self):
        time.sleep(random.randrange(self._max_duration))
        try:
            os.remove(self._name)
        except FileNotFoundError as e:
            pass
        # print(f"THREAD-{self._thread} Deleted: ", self._name)


@time_logger
class TestAutoRefresh(omni.kit.test.AsyncTestCase):
    """Testing ui.TreeView"""
    __async_lock = asyncio.Lock()

    async def setUp(self):
        self.num_files =  5
        self.max_file_size = 100
        self.max_stagger = 3

    async def _test_auto_refresh_common_async(self, title: str, show_grid_view: bool = True):
        """Testing that updates to the filesystem updates the list view"""
        # Create test dir in temp area
        temp_path = os.path.join(omni.kit.test.get_test_output_path(), f"tmp{random.randint(0, int('0xffff', 16))}")
        temp_path = temp_path.replace("\\", "/")
        if os.path.exists(temp_path):
            os.rmdir(temp_path)
        os.mkdir(temp_path)

        # Navigate to test dir, need to wait a few frames before and after for proper redraw
        under_test = FilePickerDialog(
            title,
            current_directory=temp_path,
            show_grid_view=show_grid_view,
            show_only_collections=["my-computer"])
        await ui_test.human_delay(10)

        # Create files in concurrent threads to check that the UI keeps up with the updates
        threads = []
        for i in range(self.num_files):
            thread = CreateDummyFileThread(temp_path, self.max_file_size, max_duration=self.max_stagger, thread=i)
            thread.start()
            threads.append(thread)

        done = False
        while not done:
            # Loop until all threads are done
            await ui_test.human_delay(1)
            done = not any([thread.is_alive() for thread in threads])

        # Confirm the temp folder in the filesystem model has been populated
        await ui_test.human_delay(10)
        temp_dir = await under_test._widget._model.find_item_async(temp_path)
        self.assertTrue(bool(temp_dir))
        self.assertEqual(len(temp_dir.children), self.num_files)

        # Delete files in concurrent threads to check that the UI keeps up with the updates
        filenames = [thread.name for thread in threads]
        for i, filename in enumerate(filenames):
            thread = DeleteDummyFileThread(filename, max_duration=self.max_stagger, thread=i)
            thread.start()
            threads.append(thread)

        done = False
        while not done:
            # Loop until all threads are done
            await ui_test.human_delay(1)
            done = not any([thread.is_alive() for thread in threads])

        # Confirm the temp folder in the filesystem model has been emptied
        await ui_test.human_delay(10)
        self.assertEqual(len(temp_dir.children), 0)

        # Cleanup
        os.rmdir(temp_path)
        under_test.destroy()

    async def test_auto_refresh_grid_view(self):
        """Testing that updates to the filesystem updates the grid view"""
        async with self.__async_lock:
            await self._test_auto_refresh_common_async("test_auto_refresh_grid_view", show_grid_view=True)

    async def test_auto_refresh_list_view(self):
        """Testing that updates to the filesystem updates the tree view"""
        async with self.__async_lock:
            await self._test_auto_refresh_common_async("test_auto_refresh_list_view", show_grid_view=False)
