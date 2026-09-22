## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.app
import omni.kit.commands
import omni.kit.property.layer as layers_property
import omni.kit.test
import omni.kit.widget.layers as layers_widget
from omni.kit import ui_test
from omni.kit.property.layer.layer_property_models import LayerMetaModel, LayerWorldAxisModel
from omni.kit.property.layer.types import LayerMetaType
from omni.ui.tests.test_base import OmniUiTest
from pxr import Sdf, UsdGeom, UsdPhysics


class TestLayerPropertyUI(OmniUiTest):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        self._usd_context = omni.usd.get_context()
        await self._usd_context.new_stage_async()

    # After running each test
    async def tearDown(self):
        await self._usd_context.close_stage_async()
        await super().tearDown()

    async def test_layer_replacement(self):
        omni.usd.get_context().set_pending_edit(False)

        stage = self._usd_context.get_stage()
        root_layer = stage.GetRootLayer()
        sublayer = Sdf.Layer.CreateAnonymous()
        sublayer_replace = Sdf.Layer.CreateAnonymous()
        root_layer.subLayerPaths.append(sublayer.identifier)
        missing_identifier = "non_existed_sublayer_identifier.usd"
        root_layer.subLayerPaths.append(missing_identifier)
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        layers_widget.get_instance().set_current_focused_layer_item(sublayer.identifier)

        # Wait several frames to make sure it's focused
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        # Make sure it's changed
        focused_item = layers_widget.get_instance().get_current_focused_layer_item()
        self.assertTrue(focused_item)
        self.assertEqual(focused_item.identifier, sublayer.identifier)

        layer_path_widget = layers_property.get_instance()._layer_path_widget
        layer_path_widget._show_file_picker()
        await ui_test.human_delay(10)

        layer_path_widget._on_file_selected(sublayer_replace.identifier)
        await ui_test.human_delay(10)

        # Make sure it's replaced
        self.assertTrue(root_layer.subLayerPaths[0], sublayer_replace.identifier)

        omni.kit.undo.undo()
        self.assertTrue(root_layer.subLayerPaths[0], sublayer.identifier)

        # Focus and replace missing layer
        layers_widget.get_instance().set_current_focused_layer_item(missing_identifier)

        # Wait several frames to make sure it's focused
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        # Make sure it's changed
        focused_item = layers_widget.get_instance().get_current_focused_layer_item()
        self.assertTrue(focused_item and focused_item.missing)
        self.assertEqual(focused_item.identifier, missing_identifier)

        layer_path_widget = layers_property.get_instance()._layer_path_widget
        layer_path_widget._show_file_picker()
        await ui_test.human_delay(10)

        layer_path_widget._on_file_selected(sublayer_replace.identifier)
        await ui_test.human_delay(10)

        # Make sure it's replaced
        self.assertTrue(root_layer.subLayerPaths[0], sublayer_replace.identifier)

    async def test_commands(self):
        test_comment = "test comment"
        test_doc = "test document"
        test_start_time = "0.0"
        test_end_time = "96.0"
        test_timecodes_per_second = "24.0"
        test_fps_per_second = "24.0"
        test_units = "10.0"
        test_kg_per_units = "10.0"
        test_layer_offset = "1.0"
        test_layer_scale = "10.0"

        omni.usd.get_context().set_pending_edit(False)
        stage = self._usd_context.get_stage()
        root_layer = stage.GetRootLayer()
        layers_widget.get_instance().set_current_focused_layer_item(root_layer.identifier)
        await ui_test.human_delay(10)

        meta_models = layers_property.get_instance()._meta_widget._models
        modified_metadata = {}
        old_up_index = new_up_index = None
        for _, model in meta_models.items():
            if isinstance(model, LayerMetaModel):
                new_value = None
                if model._meta_type == LayerMetaType.COMMENT:
                    new_value = test_comment
                elif model._meta_type == LayerMetaType.DOC:
                    new_value = test_doc
                elif model._meta_type == LayerMetaType.START_TIME:
                    new_value = test_start_time
                elif model._meta_type == LayerMetaType.END_TIME:
                    new_value = test_end_time
                elif model._meta_type == LayerMetaType.TIMECODES_PER_SECOND:
                    new_value = test_timecodes_per_second
                elif model._meta_type == LayerMetaType.UNITS:
                    new_value = test_units
                elif model._meta_type == LayerMetaType.KG_PER_UNIT:
                    new_value = test_kg_per_units
                elif model._meta_type == LayerMetaType.FPS_PER_SECOND and root_layer.HasFramesPerSecond():
                    new_value = test_fps_per_second

                if new_value:
                    model.set_value(new_value)
                    model.end_edit()
                    modified_metadata[model._meta_type] = model

            elif isinstance(model, LayerWorldAxisModel):
                old_up_index = model._current_index.get_value_as_int()
                if old_up_index == 0:  # up_axis is UsdGeom.Tokens.y
                    new_up_index = 1
                else:  # up_axis is UsdGeom.Tokens.z
                    new_up_index = 0
                model._current_index.set_value(new_up_index)

        # Wait several frames to make sure it's focused
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        # Check if the metadata is set correctly
        for meta_type, _ in modified_metadata.items():
            if meta_type == LayerMetaType.COMMENT:
                self.assertEqual(test_comment, str(root_layer.comment))
            elif meta_type == LayerMetaType.DOC:
                self.assertEqual(test_doc, str(root_layer.documentation))
            elif meta_type == LayerMetaType.START_TIME:
                self.assertEqual(test_start_time, str(root_layer.startTimeCode))
            elif meta_type == LayerMetaType.END_TIME:
                self.assertEqual(test_end_time, str(root_layer.endTimeCode))
            elif meta_type == LayerMetaType.TIMECODES_PER_SECOND:
                self.assertEqual(test_timecodes_per_second, str(root_layer.timeCodesPerSecond))
            elif meta_type == LayerMetaType.UNITS:
                meters = UsdGeom.GetStageMetersPerUnit(stage)
                self.assertEqual(test_units, str(meters))
            elif meta_type == LayerMetaType.KG_PER_UNIT:
                kilograms = UsdPhysics.GetStageKilogramsPerUnit(stage)
                self.assertEqual(test_kg_per_units, str(kilograms))
            elif meta_type == LayerMetaType.FPS_PER_SECOND and root_layer.HasFramesPerSecond():
                self.assertEqual(test_fps_per_second, str(root_layer.framesPerSecond))

        if new_up_index is not None:
            up_axis = UsdGeom.GetStageUpAxis(stage)
            if new_up_index == 0:
                self.assertEqual(up_axis, UsdGeom.Tokens.y)
            elif new_up_index == 1:
                self.assertEqual(up_axis, UsdGeom.Tokens.z)

        # Testing metadata for sublayers
        sublayer = Sdf.Layer.CreateAnonymous()
        root_layer.subLayerPaths.append(sublayer.identifier)

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        layers_widget.get_instance().set_current_focused_layer_item(sublayer.identifier)

        # Wait several frames to make sure it's focused
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()

        # Make sure it's changed
        focused_item = layers_widget.get_instance().get_current_focused_layer_item()
        self.assertTrue(focused_item)
        self.assertEqual(focused_item.identifier, sublayer.identifier)

        meta_models = layers_property.get_instance()._meta_widget._models
        modified_metadata = {}
        for _, model in meta_models.items():
            if isinstance(model, LayerMetaModel):
                new_value = None
                if model._meta_type == LayerMetaType.LAYER_OFFSET and model._layer_item().parent:
                    new_value = test_layer_offset
                elif model._meta_type == LayerMetaType.LAYER_SCALE and model._layer_item().parent:
                    new_value = test_layer_scale

                if new_value:
                    model.set_value(new_value)
                    model.end_edit()
                    modified_metadata[model._meta_type] = model

        # Check if the metadata is set correctly
        for meta_type, model in modified_metadata.items():
            parent = model._layer_item().parent
            layer = model._layer_item().layer
            layer_index = layers_widget.LayerUtils.get_sublayer_position_in_parent(parent.identifier, layer.identifier)
            offset = parent.layer.subLayerOffsets[layer_index]
            if meta_type == LayerMetaType.LAYER_OFFSET:
                self.assertEqual(test_layer_offset, str(offset.offset))
            elif meta_type == LayerMetaType.LAYER_SCALE and model._layer_item().parent:
                self.assertEqual(test_layer_scale, str(offset.scale))

    async def test_shut_down(self):
        manager = omni.kit.app.get_app().get_extension_manager()
        ext_id = "omni.kit.property.layer"
        self.assertTrue(ext_id)
        self.assertTrue(manager.is_extension_enabled(ext_id))

        manager.set_extension_enabled(ext_id, False)
        await ui_test.human_delay(10)
        self.assertTrue(not manager.is_extension_enabled(ext_id))

        manager.set_extension_enabled(ext_id, True)
        await ui_test.human_delay(10)
        self.assertTrue(manager.is_extension_enabled(ext_id))
