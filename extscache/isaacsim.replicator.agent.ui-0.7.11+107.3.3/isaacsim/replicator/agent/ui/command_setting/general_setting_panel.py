# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import os

import __main__
import carb
import carb.events
from omni import ui
from isaacsim.replicator.agent.ui.ui_util import *
from isaacsim.replicator.agent.core.settings import CommandSetting

LABEL_WIDTH = 240
FLOAT_FIELD_WIDTH = 120
STRING_FIELD_WIDTH = 360


class GeneralCommandSettingPanel:
    def __init__(self):
        self._frame = None

    def shutdown(self):
        self._frame = None

    def build_ui_frame(self):
        self._frame = ui.CollapsableFrame(
            title="General Command Settings",
            collapsed=False,
            style=get_collapsable_frame_style(),
            name="subFrame",
            horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
            vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
        )
        with self._frame:
            with ui.VStack(spacing=5):
                ui.Label("Character Commands")
                with ui.HStack(height=30):
                    ui.Label("\tGoTo Min Distance", width=LABEL_WIDTH)
                    model = ui.FloatField(width=FLOAT_FIELD_WIDTH, height=30).model
                    model.set_value(CommandSetting.get_character_goto_min_distance())
                    model.add_end_edit_fn(lambda m: CommandSetting.set_character_goto_min_distance(m.as_float))
                with ui.HStack(height=30):
                    ui.Label("\tGoTo Max Distance", width=LABEL_WIDTH)
                    model = ui.FloatField(width=FLOAT_FIELD_WIDTH, height=30).model
                    model.set_value(CommandSetting.get_character_goto_max_distance())
                    model.add_end_edit_fn(lambda m: CommandSetting.set_character_goto_max_distance(m.as_float))
                with ui.HStack(height=30):
                    ui.Label("\tInteractable Object Root Path", width=LABEL_WIDTH)
                    model = ui.StringField(width=STRING_FIELD_WIDTH, height=30).model
                    model.set_value(CommandSetting.get_character_interact_object_root_path())
                    model.add_end_edit_fn(lambda m: CommandSetting.set_character_interact_object_root_path(m.as_string))
                ui.Label("Robot Commands")
                with ui.HStack(height=30):
                    ui.Label("\tGoTo Min Distance", width=LABEL_WIDTH)
                    model = ui.FloatField(width=FLOAT_FIELD_WIDTH, height=30).model
                    model.set_value(CommandSetting.get_robot_goto_min_distance())
                    model.add_end_edit_fn(lambda m: CommandSetting.set_robot_goto_min_distance(m.as_float))
                with ui.HStack(height=30):
                    ui.Label("\tGoTo Max Distance", width=LABEL_WIDTH)
                    model = ui.FloatField(width=FLOAT_FIELD_WIDTH, height=30).model
                    model.set_value(CommandSetting.get_robot_goto_max_distance())
                    model.add_end_edit_fn(lambda m: CommandSetting.set_robot_goto_max_distance(m.as_float))
