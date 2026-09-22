# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ['AudioFileDropDelegate']

import re
from pxr import Gf
from .scene_drop_delegate import SceneDropDelegate


class AudioFileDropDelegate(SceneDropDelegate):
    # Method to allow subclassers to test url and keep all other default behavior
    def accept_url(self, url: str) -> str:
        # Early out for protocols not understood
        if super().is_ignored_protocol(url):
            return False

        if super().is_ignored_extension(url):
            return False

        # Validate it's a known Audio file
        is_audio = re.compile(r"^.*\.(wav|wave|ogg|oga|flac|fla|mp3|m4a|spx|opus)(\?.*)?$", re.IGNORECASE).match(url)
        return url if bool(is_audio) else False

    def accepted(self, drop_data: dict) -> bool:
        # Reset state (base-class implemented)
        self.reset_state()

        # Validate there is a UsdContext and Usd.Stage
        usd_context, _ = self.get_context_and_stage(drop_data)
        if not usd_context:
            return False

        # Test if this url should be accepted
        url = self.get_url(drop_data)
        url = self.accept_url(url)
        if (url is None) or (not url):
            return False

        return True

    def dropped(self, drop_data: dict):
        self.remove_drop_marker(drop_data)

        # Validate there is still a UsdContext and Usd.Stage
        usd_context, stage = self.get_context_and_stage(drop_data)
        if stage is None:
            return

        url_path = self.accept_url(drop_data.get('mime_data'))
        if (url_path is None) or (not url_path):
            return

        import omni.usd
        import omni.kit.commands

        url_path = self.make_relative_to_layer(stage, url_path)
        prim_path = self.make_prim_path(stage, url_path)

        try:
            omni.kit.undo.begin_group()
            omni.kit.commands.execute('CreateAudioPrimFromAssetPath',
                                      path_to=prim_path, asset_path=url_path, usd_context=usd_context)

            world_space_pos = self._get_world_position(drop_data)
            if world_space_pos:
                omni.kit.commands.execute('TransformPrimCommand',
                                          path=prim_path,
                                          new_transform_matrix=Gf.Matrix4d().SetTranslate(world_space_pos),
                                          usd_context_name=drop_data.get('usd_context_name', ''))
        finally:
            omni.kit.undo.end_group()
