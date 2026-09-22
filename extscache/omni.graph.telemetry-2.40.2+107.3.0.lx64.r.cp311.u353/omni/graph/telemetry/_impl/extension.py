# Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import threading
from datetime import datetime, timedelta

import carb.settings
import omni.ext
import omni.graph.core as og
import omni.kit.commands

from .._telemetry import send_graph_info

USAGE_KEY = "/privacy/usage"


class Extension(omni.ext.IExt):
    def __init__(self):
        super().__init__()
        self.__command_callback_ids = []
        self.__last_updated = {}
        self.__last_updated_lock = threading.Lock()

    def on_startup(self):
        settings = carb.settings.get_settings_interface()
        usage_consent = settings.get_as_bool(USAGE_KEY)
        if not usage_consent:
            return

        # List of Kit commands to watch for triggering graphInfo events
        commands = [
            "ConnectAttrsCommand",
            "DisconnectAttrsCommand",
        ]

        self.__command_callback_ids = [
            omni.kit.commands.register_callback(command, omni.kit.commands.POST_DO_CALLBACK, self.__do_send_graph_info)
            for command in commands
        ]

    def on_shutdown(self):
        for callback_id in self.__command_callback_ids:
            omni.kit.commands.unregister_callback(callback_id)
        self.__command_callback_ids = None
        self.__last_updated = None

    def __do_send_graph_info(self, command_args):
        graph = None
        src_attr = command_args.get("src_attr", None)
        if isinstance(src_attr, og.Attribute):
            graph = src_attr.get_node().get_graph()
        if not isinstance(graph, og.Graph):
            return

        # FIXME: There should be a helper function that gets the root graph
        while graph.get_owning_compound_node():
            graph = graph.get_owning_compound_node().get_graph()
        path_to_root_graph = graph.get_path_to_graph()

        # Skip if an event was sent for the graph less than a minute ago
        if not self.__last_updated_lock.acquire(blocking=False):  # noqa: PLR1732
            return  # pragma: no cover
        try:
            if path_to_root_graph in self.__last_updated and (
                datetime.now() - self.__last_updated[path_to_root_graph]
            ) < timedelta(minutes=1):
                return
            self.__last_updated[path_to_root_graph] = datetime.now()
        finally:
            self.__last_updated_lock.release()

        send_graph_info(path_to_root_graph)
