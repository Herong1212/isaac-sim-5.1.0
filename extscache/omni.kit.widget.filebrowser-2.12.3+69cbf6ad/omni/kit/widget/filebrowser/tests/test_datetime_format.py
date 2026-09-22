## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
import omni.kit.app
import carb.settings

from functools import partial
from ..date_format_menu import DatetimeFormatMenu, DATETIME_FORMAT_SETTING, get_datetime_format


class TestDatetimeFormat(omni.kit.test.AsyncTestCase):
    """Testing DatetimeFormatMenu"""
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def _after_redraw_async(self):
        for _ in range(2):
            await omni.kit.app.get_app().next_update_async()

    async def test_datetime_format_change(self):
        """ Test datetime format setting changes"""
        self._datetime_format = "MM/DD/YYYY"
        self._format_changed = False
        def format_change_callback(owner):
            owner._format_changed = True

        datetime_menu = DatetimeFormatMenu(partial(format_change_callback, self))
        datetime_menu.visible = True

        # test datetime format value
        carb.settings.get_settings().set(DATETIME_FORMAT_SETTING, self._datetime_format)
        await self._after_redraw_async()
        self.assertEqual(get_datetime_format(), "%m/%d/%Y")

        carb.settings.get_settings().set(DATETIME_FORMAT_SETTING, "DD-MM-YYYY")
        await self._after_redraw_async()
        self.assertEqual(get_datetime_format(), "%d-%m-%Y")

        # test datetime format setting change callback is work as expected
        carb.settings.get_settings().set(DATETIME_FORMAT_SETTING, "DD/MM/YYYY")
        await self._after_redraw_async()
        self.assertEqual(get_datetime_format(), "%x")
        self.assertTrue(self._format_changed)
