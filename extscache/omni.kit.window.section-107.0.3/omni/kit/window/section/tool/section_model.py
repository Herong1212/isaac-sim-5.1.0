# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["SectionModel"]

import carb.settings
import omni.kit.app
import omni.usd
from omni.ui import scene as sc
from pxr import Gf, Tf, Usd

from ..common import SECTION_DIRECTION_TOP, SETTING_SECTION_DIRECTION, SETTING_SECTION_PLANE, SectionManager

SETTING_SECTION_TOOL_ROOT = "/exts/omni.kit.window.section/"
SETTING_SECTION_USE_SESSION_LAYER = SETTING_SECTION_TOOL_ROOT + "useSessionLayer"


class SectionModel(sc.AbstractManipulatorModel):
    """
    User part. The model tracks the section object.
    """

    class TransformItem(sc.AbstractManipulatorItem):
        """
        The Model Item represents the transform
        """

        def __init__(self):
            super().__init__()
            self.value = Gf.Matrix4d()

    def __init__(self):
        # this should re-create when open stage
        super().__init__()

        self._settings = carb.settings.get_settings()
        self._transform = SectionModel.TransformItem()
        section_transform_attr = SectionManager().get_transform_attr()
        if section_transform_attr:  # pragma: no cover
            self.set_floats(self._transform, section_transform_attr.Get())

        stage = omni.usd.get_context().get_stage()
        self._usd_listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._on_usd_changed, stage)

    def __del__(self):  # pragma: no cover
        self.destroy()

    def destroy(self):  # pragma: no cover
        self._settings = None
        self._section_manager = None
        self._usd_listener = None
        self._transform = None

    def refresh(self):
        self._usd_listener = None
        stage = omni.usd.get_context().get_stage()
        self._usd_listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._on_usd_changed, stage)

    def get_item(self, identifier):
        return self._transform

    def get_as_floats(self, item):
        return self._transform.value

    def _get_section_edit_context(self):
        stage = omni.usd.get_context().get_stage()
        sect_layer = self._get_section_layer()
        return Usd.EditContext(stage, sect_layer)

    def _get_section_layer(self):
        settings = carb.settings.get_settings()
        use_session_layer = settings.get(SETTING_SECTION_USE_SESSION_LAYER)
        stage = omni.usd.get_context().get_stage()
        if bool(use_session_layer):
            return stage.GetSessionLayer()
        else:  # pragma: no cover
            return stage.GetRootLayer()

    def set_floats(self, item, value):
        with self._get_section_edit_context():
            if not value:  # pragma: no cover
                return
            # Set directly to the item
            self._transform.value = value
            self.update_section_plane()
            # This makes the manipulator updated
            self._item_changed(self._transform)

    def _on_usd_changed(self, notice, stage):
        with self._get_section_edit_context():
            section_transform_attr = SectionManager().get_transform_attr()
            if section_transform_attr:
                attr_path = section_transform_attr.GetPath()
                if attr_path in notice.GetChangedInfoOnlyPaths():
                    self.set_floats(self._transform, section_transform_attr.Get())

    def update_section_plane(self):
        with self._get_section_edit_context():
            # update the render section settings
            if self._settings.get_as_int(SETTING_SECTION_DIRECTION) == SECTION_DIRECTION_TOP:
                direction = Gf.Vec3d(0, 0, -1)
            else:
                direction = Gf.Vec3d(0, 0, 1)

            point = self._transform.value.ExtractTranslation()
            normal = self._transform.value.TransformDir(direction)
            d = point * normal
            sectionPlane = [normal[0], normal[1], normal[2], -d]
            self._settings.set_float_array(SETTING_SECTION_PLANE, sectionPlane)
