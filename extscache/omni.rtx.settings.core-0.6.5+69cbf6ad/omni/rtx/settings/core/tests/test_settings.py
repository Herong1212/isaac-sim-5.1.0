
import carb
import omni.kit.test
import omni.usd
import tempfile
import pathlib
import rtx.settings
import unittest
from omni.kit import ui_test
from omni.rtx.tests.test_common import wait_for_update
from omni.kit.test_suite.helpers import get_test_data_path, wait_stage_loading


settings = carb.settings.get_settings()

EXTENSION_FOLDER_PATH = pathlib.Path(omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__))
USD_DIR = EXTENSION_FOLDER_PATH.joinpath("data/usd")

class TestRTXCoreSettingsUI(omni.kit.test.AsyncTestCase):
    VALUE_EPSILON = 0.00001

    async def setUp(self):
        super().setUp()
        # We need to trigger Iray load to get the default render-settings values written to carb.settings
        # Viewports state is valid without any open stage, and only loads renderer when stage is opened.
        await omni.usd.get_context().new_stage_async()
        await omni.kit.app.get_app().next_update_async()

    # After running each test
    async def tearDown(self):
        pass

    def get_render_setings_window(self):
        render_settings_window = ui_test.find("Render Settings")
        render_settings_window.widget.height = 1200
        render_settings_window.widget.width = 600
        render_settings_window.widget.visible = True
        return render_settings_window

    def set_renderer(self, render_settings_window, index):
        #select the combo box item
        box = render_settings_window.find("Frame/VStack[0]/HStack[0]/ComboBox[*]")
        box.model.get_item_value_model(None, 0).set_value(index)

    def compare_floats(self, a, b, epsilon):
        self.assertEqual(len(a), len(b))
        for i in range(0, len(a)):
            self.assertLessEqual(
                abs(a[i] - b[i]), epsilon, "a[" + str(i) + "] = " + str(a[i]) + ", b[" + str(i) + "] = " + str(b[i])
            )

    def compare_float(self, a, b, epsilon):
        self.assertLessEqual(abs(a - b), epsilon)

    def open_usd(self, usdSubpath: pathlib.Path):
        path = USD_DIR.joinpath(usdSubpath)
        omni.usd.get_context().open_stage(str(path))

    @unittest.skip("This test is unhelpful... omni.ui should be tested by omni.ui tests.")
    async def test_bool_checkbox_setting(self):
        '''
        check that we can switch on/off back face culling in Common/Geometry
        '''
        render_settings_window = self.get_render_setings_window()
        setting_name = "/rtx/hydra/faceCulling/enabled"

        await wait_stage_loading()

        #Cycle through Realtime, path-tracing renders
        for index in range(0, 2):

            self.set_renderer(render_settings_window, index)

            # Set initial value
            settings.set(setting_name, False)
            await omni.kit.app.get_app().next_update_async()

            #choose the "Common" tab in each case
            button = render_settings_window.find("Frame/VStack[0]/VStack[0]/HStack[0]/RadioButton[0]")
            await button.click()

            #Get the collapsable frame for Geometry and open it
            collapsable_frame = render_settings_window.find("**/Geometry")
            collapsable_frame.widget.collapsed = False
            await omni.kit.app.get_app().next_update_async()

            #This is the back face culling hstack
            back_face_culling_setting = collapsable_frame.find("/**/HStack_Back_Face_Culling")
            self.assertTrue(isinstance(back_face_culling_setting.widget, omni.ui.HStack))
            check_box = back_face_culling_setting.find("**/CheckBox[0]")
            self.assertTrue(isinstance(check_box.widget, omni.ui.CheckBox))

            await check_box.click(human_delay_speed=10)
            face_culling_value = settings.get(setting_name)
            self.assertTrue(face_culling_value)

            await check_box.click(human_delay_speed=10)
            face_culling_value = settings.get(setting_name)
            self.assertFalse(face_culling_value)

    @unittest.skip("This test is unhelpful... omni.ui should be tested by omni.ui tests.")
    async def test_combo_box_setting(self):
        '''
        check that we can set TBNFrame mode Combo Box in Common/Geometry
        '''

        render_settings_window = self.get_render_setings_window()
        setting_name = "/rtx/hydra/TBNFrameMode"

        #Cycle through Realtime, path-tracing renders
        for index in range(0, 2):

            self.set_renderer(render_settings_window, index)

            # Set initial value
            settings.set(setting_name, 0)
            await omni.kit.app.get_app().next_update_async()

            #choose the "Common" tab in each case
            button = render_settings_window.find("Frame/VStack[0]/VStack[0]/HStack[0]/RadioButton[0]")
            await button.click()

            #Get the collapsable frame for Geometry and open it
            collapsable_frame = render_settings_window.find("**/Geometry")
            collapsable_frame.widget.collapsed = False
            await omni.kit.app.get_app().next_update_async()

            tangent_space_setting = collapsable_frame.find("/**/HStack_Normal_&_Tangent_Space_Generation_Mode")
            self.assertTrue(isinstance(tangent_space_setting.widget, omni.ui.HStack))
            combo_box = tangent_space_setting.find("ComboBox[0]")
            self.assertTrue(isinstance(combo_box.widget, omni.ui.ComboBox))

            combo_box.model.get_item_value_model(None, 0).set_value(1)

            tbn_frame_mode_setting = settings.get(setting_name)
            self.assertTrue(tbn_frame_mode_setting == 1)

    @unittest.skip("This test is unhelpful... omni.ui should be tested by omni.ui tests.")
    async def test_float_setting(self):
        '''
        check that we can set float MDL Animation Time Override in Common/Materials
        '''
        render_settings_window = self.get_render_setings_window()
        setting_name = "/rtx/animationTime"

        #Cycle through Realtime, path-tracing renders
        for index in range(0, 2):

            self.set_renderer(render_settings_window, index)

            # Set initial value
            settings.set(setting_name, -1.0)
            await omni.kit.app.get_app().next_update_async()

            #choose the "Common" tab in each case
            button = render_settings_window.find("Frame/VStack[0]/VStack[0]/HStack[0]/RadioButton[0]")
            await button.click()

            #Get the collapsable frame for Materials and expand it
            collapsable_frame = render_settings_window.find("**/Geometry")
            collapsable_frame.widget.collapsed = True
            collapsable_frame = render_settings_window.find("**/Materials")
            collapsable_frame.widget.collapsed = False
            await omni.kit.app.get_app().next_update_async()

            tangent_space_setting = collapsable_frame.find("**/HStack_Animation_Time_Override")
            self.assertTrue(isinstance(tangent_space_setting.widget, omni.ui.HStack))
            slider = tangent_space_setting.find("FloatDrag[0]")
            self.assertTrue(isinstance(slider.widget, omni.ui.FloatDrag))
            await ui_test.human_delay(50)

            await slider.input("20.0")
            tbn_frame_mode_setting = settings.get(setting_name)
            self.assertAlmostEqual(tbn_frame_mode_setting, 20.0, 2, f"was actually {tbn_frame_mode_setting}")

    async def run_render_settings_storage_helper(self, must_save=False):
        with tempfile.TemporaryDirectory() as tmpdirname:
            usd_context = omni.usd.get_context()
            await omni.kit.app.get_app().next_update_async()

            # save the file with various types of setting value types.
            # Note: if ever any of these were removed, replace them with a new setting of the same type.
            setting_fog_b = "/rtx/fog/enabled" # bool
            setting_meter_unit_f = "/rtx/scene/renderMeterPerUnit" # float
            setting_heatmap_i = "/rtx/debugView/heatMapPass" # int
            setting_max_bounce_i = "/rtx/pathtracing/maxBounces" # int, pathtracer
            setting_mat_white_s =  "/rtx/debugMaterialWhite" # string
            setting_ambinet_arr_f = "/rtx/sceneDb/ambientLightColor" # array of float3
            setting_saturation_arr_f = "/rtx/post/colorcorr/saturation" # array of double3

            # settings with special kSettingFlagTransient, treated like rtx-transient.
            setting_mthread_transient_b = "/rtx/multiThreading/enabled" # uses kSettingFlagTransient in C++
            setting_dir_light_b = "/rtx-transient/disable/directLightingSampled" # manual transient
            setting_place_col_b = "/persistent/rtx/resourcemanager/placeholderTextureColor" # persistent

            # set as transient in [[test]]
            setting_fog_dist_i = "/rtx/fog/fogEndDist" # int
            setting_fog_color_arr_f = "/rtx/fog/fogColor" # array of float

            settings.set_bool(setting_fog_b, True)
            settings.set_float(setting_meter_unit_f, 0.5)
            settings.set_int(setting_heatmap_i, 3)
            settings.set_int(setting_max_bounce_i, 33)
            settings.set_string(setting_mat_white_s, "NoActualMat") # a random non-existent material
            settings.set_float_array(setting_ambinet_arr_f, [0.4, 0.5, 0.6])
            settings.set_float_array(setting_saturation_arr_f, [0.7, 0.8, 0.9])

            # with special flags
            # Note: we can't test sync/async settings, since they are needed for the loading stage.
            settings.set_bool(setting_mthread_transient_b, False)
            settings.set_bool(setting_dir_light_b, True)
            settings.set_float_array(setting_place_col_b, [0.4, 0.4, 0.4])

            # this was set in [[test]] as transient
            settings.set(setting_fog_dist_i, 999)
            settings.set_float_array(setting_fog_color_arr_f, [0.21, 0.21, 0.21])

            # verify rtx-flags is set as transient in [[test]]
            setting_fog_dist_flags = rtx.settings.get_associated_setting_flags_path(setting_fog_dist_i);
            setting_fog_color_flags = rtx.settings.get_associated_setting_flags_path(setting_fog_color_arr_f);
            value_fog_dist_flags = settings.get(setting_fog_dist_flags)
            value_fog_color_flags = settings.get(setting_fog_color_flags)

            self.assertEqual(value_fog_dist_flags, rtx.settings.SETTING_FLAGS_TRANSIENT)
            self.assertEqual(value_fog_color_flags, rtx.settings.SETTING_FLAGS_TRANSIENT)

            tmp_usd_path = pathlib.Path(tmpdirname) / "tmp_rtx_setting.usd"
            result = usd_context.save_as_stage(str(tmp_usd_path))
            self.assertTrue(result)

            stage = usd_context.get_stage()
            # Make stage dirty so reload will work
            stage.DefinePrim("/World", "Xform")

            await omni.kit.app.get_app().next_update_async()

            # Change settings
            settings.set_bool(setting_fog_b, False)
            settings.set_float(setting_meter_unit_f, 0.3)
            settings.set_int(setting_heatmap_i, 2)
            settings.set_int(setting_max_bounce_i, 9)
            settings.set_string(setting_mat_white_s, "NoActualMat2") # a random non-existent material
            settings.set_float_array(setting_ambinet_arr_f, [0.2, 0.2, 0.2])
            settings.set_float_array(setting_saturation_arr_f, [0.3, 0.3, 0.3])

            # with special flags
            settings.set_bool(setting_mthread_transient_b, True)
            settings.set_bool(setting_dir_light_b, False)
            settings.set_float_array(setting_place_col_b, [0.6, 0.6, 0.6])

            await omni.kit.app.get_app().next_update_async()

            # Reload stage will reload all the rtx settings
            # Reload with native API stage.Reload will not reopen settings
            # but only lifecycle API in Kit.
            await usd_context.reopen_stage_async()
            await omni.kit.app.get_app().next_update_async()

            value_fog_b = settings.get(setting_fog_b)
            value_meter_unit_f = settings.get(setting_meter_unit_f)
            value_heatmap_i = settings.get(setting_heatmap_i)
            value_max_bounce_i = settings.get(setting_max_bounce_i)
            value_mat_white_s = settings.get(setting_mat_white_s)
            value_ambinet_arr_f = settings.get(setting_ambinet_arr_f)
            value_saturation_arr_f = settings.get(setting_saturation_arr_f)

            # with special flags
            value_mthread_transient_b = settings.get(setting_mthread_transient_b)
            value_dir_light_b = settings.get(setting_dir_light_b)
            value_place_col_b = settings.get(setting_place_col_b)
            # Temporarily transient via rtx-flags specified in [[test]]
            value_fog_dist_i = settings.get(setting_fog_dist_i)
            value_fog_dist_flags = settings.get(setting_fog_dist_flags)
            value_fog_color_arr_f = settings.get(setting_fog_color_arr_f)
            value_fog_color_flags = settings.get(setting_fog_color_flags)

            # New stage to release the temp usd file
            await usd_context.new_stage_async()

            if must_save:
                self.assertEqual(value_fog_b, True)
                self.compare_float(value_meter_unit_f, 0.5, self.VALUE_EPSILON)
                self.assertEqual(value_heatmap_i, 3)
                self.assertEqual(value_max_bounce_i, 33)
                self.assertEqual(value_mat_white_s, "NoActualMat")
                self.compare_floats(value_ambinet_arr_f, [0.4, 0.5, 0.6], self.VALUE_EPSILON)
                self.compare_floats(value_saturation_arr_f, [0.7, 0.8, 0.9], self.VALUE_EPSILON)
            else:
                self.assertNotEqual(value_fog_b, True)
                self.assertNotAlmostEqual(value_meter_unit_f, 0.5, delta=self.VALUE_EPSILON)
                self.assertNotEqual(value_heatmap_i, 3)
                self.assertNotEqual(value_max_bounce_i, 33)
                self.assertNotEqual(value_mat_white_s, "NoActualMat")
                # self.compare_floats(value_ambinet_arr_f, [0.4, 0.5, 0.6], self.VALUE_EPSILON)
                # self.compare_floats(value_saturation_arr_f, [0.7, 0.8, 0.9], self.VALUE_EPSILON))

            # The ones with special flags should NOT be saved or loaded from USD
            # same with persistent and rtx-transient
            self.assertEqual(value_mthread_transient_b, True)
            self.assertEqual(value_dir_light_b, False)
            self.compare_floats(value_place_col_b, [0.6, 0.6, 0.6], self.VALUE_EPSILON)
            # Temporarily transient via rtx-flags. Should not be saved to or loaded from USD
            self.assertEqual(value_fog_dist_i, 999)
            self.assertEqual(value_fog_dist_flags, rtx.settings.SETTING_FLAGS_TRANSIENT)
            self.compare_floats(value_fog_color_arr_f, [0.21, 0.21, 0.21], self.VALUE_EPSILON)
            self.assertEqual(value_fog_color_flags, rtx.settings.SETTING_FLAGS_TRANSIENT)

    async def run_render_settings_loading_helper(self, must_load=True, must_reset=True):
        usd_context = omni.usd.get_context()
        await omni.kit.app.get_app().next_update_async()

        # Custom values already stored in the USD test
        setting_tonemap_arr_f = "/rtx/post/tonemap/whitepoint"
        setting_sample_threshold_i = "/rtx/directLighting/sampledLighting/autoEnableLightCountThreshold"
        setting_max_roughness_f = "/rtx/reflections/maxRoughness"
        setting_reflections_b = "/rtx/reflections/enabled"

        # setting with kSettingFlagTransient, that should not be loaded if saved in the old USD files.
        setting_mthread_transient_b = "/rtx/multiThreading/enabled"
        setting_mat_syncload_b = "/rtx/materialDb/syncLoads"
        setting_hydra_mat_syncload_b = "/rtx/hydra/materialSyncLoads"

        # set as transient in [[test]]
        setting_fog_dist_i = "/rtx/fog/fogEndDist" # int
        setting_fog_color_arr_f = "/rtx/fog/fogColor" # array of float

        await omni.kit.app.get_app().next_update_async()

        settings.set_float_array(setting_tonemap_arr_f, [0.15, 0.16, 0.17])
        settings.set(setting_sample_threshold_i, 43)

        # change settings with kSettingFlagTransient
        settings.set_bool(setting_mthread_transient_b, True)
        settings.set_bool(setting_mat_syncload_b, True)
        settings.set_bool(setting_hydra_mat_syncload_b, False)

        # this was set in [[test]] as transient and not saved in USD.
        settings.set(setting_fog_dist_i, 999)
        settings.set_float_array(setting_fog_color_arr_f, [0.21, 0.21, 0.21])

        await omni.kit.app.get_app().next_update_async()

        self.open_usd("cubeRtxSettings.usda")
        await wait_for_update()

        value_tonemap_arr_f = settings.get(setting_tonemap_arr_f)
        value_sample_threshold_i = settings.get(setting_sample_threshold_i)
        value_max_roughness_f = settings.get(setting_max_roughness_f)
        value_reflections_b = settings.get(setting_reflections_b)

        value_mthread_transient_b = settings.get(setting_mthread_transient_b)
        value_mat_syncload_b = settings.get(setting_mat_syncload_b)
        value_hydra_mat_syncload_b = settings.get(setting_hydra_mat_syncload_b)

        # Not stored in USD file, testing the default value
        value_fog_dist_i = settings.get(setting_fog_dist_i)
        value_fog_color_arr_f = settings.get(setting_fog_color_arr_f)

        if must_load:
            # Must match to what we stored in USD
            self.compare_floats(value_tonemap_arr_f, [0.1, 0.2, 0.3], self.VALUE_EPSILON)
            self.assertEqual(value_sample_threshold_i, 77)
            self.compare_float(value_max_roughness_f, 0.53, self.VALUE_EPSILON)
            self.assertEqual(value_reflections_b, False)
        else:
            if must_reset:
                # Current default values set in C++ code.
                self.compare_floats(value_tonemap_arr_f, [1.0, 1.0, 1.0], self.VALUE_EPSILON)
                self.assertEqual(value_sample_threshold_i, 10)
            else:
                # what we set before loading the USD and not defaults.
                self.compare_floats(value_tonemap_arr_f, [0.15, 0.16, 0.17], self.VALUE_EPSILON)
                self.assertEqual(value_sample_threshold_i, 43)

            self.assertNotAlmostEqual(value_max_roughness_f, 0.53, delta=self.VALUE_EPSILON)
            self.assertNotEqual(value_reflections_b, False)


        # Must skip loading setting that use kSettingFlagTransient flag from USD
        # Such settings are not saved or loaded in USD, ut may exist in old USD files, such as cubeRtxSettings.usda.
        # if usd was re-saved, you need to manually add those transient setting for this test. Otherwise, they will be removed.
        self.assertEqual(value_mthread_transient_b, True)
        self.assertEqual(value_mat_syncload_b, True)
        self.assertEqual(value_hydra_mat_syncload_b, False)

        # Temporarily transient via rtx-flags. Should not be saved to or loaded from USD
        self.assertEqual(value_fog_dist_i, 999)
        self.compare_floats(value_fog_color_arr_f, [0.21, 0.21, 0.21], self.VALUE_EPSILON)

    async def test_render_settings_storage(self):
        await self.run_render_settings_storage_helper(must_save=True)

    async def test_render_settings_not_storing(self):
        # Test to make sure rtx settings are not stored in USD, when asked.
        storeRenderSettingsToStage = "/app/omni.usd/storeRenderSettingsToUsdStage";

        settings.set_bool(storeRenderSettingsToStage, False)
        await self.run_render_settings_storage_helper(must_save=False)
        settings.set_bool(storeRenderSettingsToStage, True)

    async def test_render_settings_loading(self):
        await self.run_render_settings_loading_helper()

    async def test_render_settings_not_loading(self):
        # Test to make sure rtx settings are not loaded from USD, when asked.
        loadRenderSettingsFromStage = "/app/omni.usd/loadRenderSettingsFromUsdStage";

        settings.set_bool(loadRenderSettingsFromStage, False)
        await self.run_render_settings_loading_helper(must_load=False)
        settings.set_bool(loadRenderSettingsFromStage, True)

    async def test_render_settings_not_loading_not_reset(self):
        # Test to make sure rtx settings are not loaded from USD, when asked.
        loadRenderSettingsFromStage = "/app/omni.usd/loadRenderSettingsFromUsdStage";
        resetRenderSettingsStage = "/app/omni.usd/resetRenderSettingsInUsdStage";

        settings.set_bool(loadRenderSettingsFromStage, False)
        settings.set_bool(resetRenderSettingsStage, False)
        await self.run_render_settings_loading_helper(must_load=False, must_reset=False)
        settings.set_bool(loadRenderSettingsFromStage, True)
        settings.set_bool(resetRenderSettingsStage, True)
