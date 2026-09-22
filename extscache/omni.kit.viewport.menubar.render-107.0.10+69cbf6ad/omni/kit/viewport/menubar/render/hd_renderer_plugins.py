# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["HdRendererPlugins"]

from pxr import Tf, Plug


class HdRendererPlugins:
    def __init__(self, callback_fn: callable = None):
        self.__callback_fn = callback_fn
        self.__renderers = {}
        self.__listener = Tf.Notice.RegisterGlobally(
            "PlugNotice::DidRegisterPlugins", lambda notice, _: self.__add_renderers(notice.GetNewPlugins())
        )
        self.__add_renderers(Plug.Registry().GetAllPlugins())

    def __add_renderers(self, plugins):
        added = False
        for renderer in [d for d in Tf.Type("HdRendererPlugin").GetAllDerivedTypes() if d not in self.__renderers]:
            for plugin in plugins:
                declared = plugin.GetMetadataForType(renderer)
                if declared:
                    display_name = declared.get("displayName")
                    self.__renderers[renderer] = {"plugin": plugin, "displayName": display_name}
                    added = True
        if added:
            self.__callback_fn(self)

    @property
    def renderers(self):
        for k, v in self.__renderers.items():
            yield k, v

    def destroy(self):
        if self.__listener:
            self.__listener.Revoke()
            self.__listener = None

    def __del__(self):
        self.destroy()
