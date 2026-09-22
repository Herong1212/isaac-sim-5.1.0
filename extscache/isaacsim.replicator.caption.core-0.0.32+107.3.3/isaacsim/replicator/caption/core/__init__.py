# Copyright (c) 2018-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#


__all__ = []
import omni.kit.commands

# hack for unit tests
from omni.kit.commands.builtin.settings_commands import ChangeDraggableSettingCommand, ChangeSettingCommand

# PIP/Install pip package

# omni.kit.pipapi extension is required
import omni.kit.pipapi

# It wraps `pip install` calls and reroutes package installation into user specified environment folder.
# That folder is added to sys.path.
# Note: This call is blocking and slow. It is meant to be used for debugging, development. For final product packages
# should be installed at build-time and packaged inside extensions.
omni.kit.pipapi.install(
    package="openai",
    ignore_import_check=False,
    ignore_cache=False,
    use_online_index=True,
    surpress_output=False,
    extra_args=[],
)


from .extension import IRCInfoCollectorExtension
from .object_caption.generate_object_caption import GenObjectCap
from .sft_autolabeling.scene_graph_sft import GenSceneCap
from .writers.scene_graph_writer import SceneGraphWriter
from .writers.iro_scene_graph_writer import IROSceneGraphWriter
from .writers.combined_iro_scene_graph_writer import CombinedIROSceneGraphWriter
from .writers.iro_object_caption_writer import IRObjectCaptionWriter

omni.kit.commands.command.register(ChangeDraggableSettingCommand)
omni.kit.commands.command.register(ChangeSettingCommand)
