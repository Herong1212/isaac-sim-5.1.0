# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.kit.test
import os
import stat
import tempfile

import carb.settings
import carb.tokens
import omni.kit.app
import omni.kit.commands
import omni.kit.window.title
import omni.usd


class TestTitleBar(omni.kit.test.AsyncTestCase):
    async def test_title(self):
        import omni.kit.stage_template.core
        title_bar = omni.kit.window.title.get_main_window_title()
        settings = carb.settings.get_settings()
        app = omni.kit.app.get_app()
        usd_context = omni.usd.get_context()

        ## Test new stage title
        await omni.kit.stage_template.core.new_stage_async()

        # make sure new stage event is handled by title extension
        await app.next_update_async()

        # Ideally we should get title from OS Window, but GLFW does not have getter for window title.
        title = title_bar.get_full_title()
        app_name = settings.get("/app/window/title")
        app_version = carb.tokens.get_tokens_interface().resolve("${app_version}")

        new_stage_title = f"{app_name} {app_version} - New Stage"
        self.assertTrue(title == new_stage_title)

        ## Test set app name and version
        test_app_name = "title extension test"
        test_version = "1.0"
        title_bar.set_app_name(test_app_name)
        title_bar.set_app_version(test_version)

        title = title_bar.get_full_title()
        self.assertTrue(title == f"{test_app_name} {test_version} - New Stage")

        ## Restore app name and version
        title_bar.set_app_name(app_name)
        title_bar.set_app_version(app_version)

        ## Test open USD file
        with tempfile.TemporaryDirectory() as dir_name:
            tmp_file_path = os.path.join(dir_name, "tmp.usda")
            await usd_context.save_as_stage_async(tmp_file_path)

            # make sure new stage event is handled by title extension
            await app.next_update_async()

            title = title_bar.get_full_title()
            title = os.path.normpath(title)
            tmp_file_path = os.path.normpath(tmp_file_path)
            # Save As should not result in dirty mark (*) on the title
            self.assertEqual(title, f"{app_name} {app_version} - {tmp_file_path}")

            ## Make an edit
            stage = usd_context.get_stage()
            stage.DefinePrim("/test")

            # make sure new stage event is handled by title extension
            await app.next_update_async()
            await app.next_update_async()

            # check the dirty mark (*)
            title = title_bar.get_full_title()
            title = os.path.normpath(title)
            self.assertEqual(title, f"{app_name} {app_version} - {tmp_file_path}*")

            ## Save the stage
            await usd_context.save_stage_async()
            await app.next_update_async()

            # check the dirty mark (*) is removed
            title = title_bar.get_full_title()
            title = os.path.normpath(title)
            self.assertEqual(title, f"{app_name} {app_version} - {tmp_file_path}")

            ## Make read-only
            await usd_context.close_stage_async()

            mode = os.stat(tmp_file_path).st_mode
            os.chmod(tmp_file_path, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
            await usd_context.open_stage_async(tmp_file_path)
            await app.next_update_async()
            await app.next_update_async()

            title = title_bar.get_full_title()
            title = os.path.normpath(title)
            self.assertEqual(title, f"{app_name} {app_version} - {tmp_file_path} (read-only)")

            await usd_context.close_stage_async()
            # restore file permission so it can be cleaned up
            os.chmod(tmp_file_path, mode)
