# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Tuple

import carb.events
import carb.settings
import numpy as np
import omni.graph.core as og
import omni.kit
from pxr import Sdf

from . import utils

ORCHESTRATOR_EVENT = "omni.replicator.core.orchestrator:orchestratorEvent"

active_generators = {}


def release(node_path):
    if node_path in active_generators:
        gen = active_generators.pop(node_path)
        gen.release()


def set_global_seed(seed: int):
    """Set a global seed.

    Args:
        seed: Seed to use as initialization for the pseudo-random number generator. Seed is expected to be a
            non-negative integer.
    """
    if seed < 0:
        raise ValueError(f"Seed must be a non-negative integer, got {seed}")

    if seed == carb.settings.get_settings().get_as_int("/omni/replicator/globalSeed"):
        return

    carb.settings.get_settings().set_int("/omni/replicator/globalSeed", seed)

    graph = utils.get_graph()
    if graph is None:
        raise ValueError("Unable to retrieve replicator graph")
    context = graph.get_default_graph_context()
    if not graph.find_variable("globalSeed"):
        graph.create_variable("globalSeed", og.Type(og.BaseDataType.INT64))
    variable = graph.find_variable("globalSeed")
    variable.set(context, seed)


def get_global_seed():
    """
    Return global seed value

    :return: (int)seed value
    """
    seed = carb.settings.get_settings().get("/omni/replicator/globalSeed")
    if seed is None:
        seed = np.random.randint(
            int(0x7FFFFFFF)
        )  # choose within max of int32 values, otherwise causes error on Windows
        set_global_seed(seed)
    return seed


class ReplicatorRNG:
    """Replicator Random Number Generator
    Wraps the numpy RNG to respond to certain events.
    """

    def __init__(self, seed: int = None, node: og.Node = None):
        if node is not None:
            self._node_path = node.get_prim_path()
        else:
            self._node_path = None
        self._sub_orchestrator = None
        self._sub_settings = None
        self._generator = None

        self._subscribe()

        self._seed = seed
        self._node_id = 0

        self.initialize(seed, node=node)

    def _on_global_seed_change(self, value, *args):
        self.reset()

    def _set_node_entropy(self, entropy):
        # Create dynamic entropy attribute if it doesn't exist and set to entropy value
        graph = utils.get_graph()
        if graph is None:
            return
        node = graph.get_node(self._node_path)
        if not node:
            return

        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(node.get_prim_path())

        if not node.get_attribute_exists("inputs:entropy"):
            # Create Fabric attribute
            node.create_attribute("inputs:entropy", og.Type(og.BaseDataType.INT, 2))
            # Create USD attribute - necessary only for standalone mode (OMPE-25552)
            prim.CreateAttribute("inputs:entropy", Sdf.ValueTypeNames.Int2)

        node.get_attribute("inputs:entropy").set_metadata("hidden", "true")
        og.AttributeValueHelper(node.get_attribute("inputs:entropy")).set(entropy, update_usd=True)

    def _on_orchestrator(self, event):
        if event is None:
            return
        if not event.has_key("command"):
            return
        if event.get("command") == "initialize":
            self.reset()

    def _subscribe(self):
        """Checked call to set up carb subscription"""
        if self._sub_orchestrator is None:
            # Add a subscription for the given event name. This is a pop subscription, so we expect a 1-frame
            # lag between send and receive
            self._sub_orchestrator = carb.eventdispatcher.get_eventdispatcher().observe_event(
                observer_name="RNG", event_name=ORCHESTRATOR_EVENT, on_event=self._on_orchestrator
            )

        if self._sub_settings is None:
            self._mode_sub = omni.kit.app.SettingChangeSubscription(
                "/omni/replicator/globalSeed", self._on_global_seed_change
            )

    def reset(self):
        global_seed = get_global_seed()
        graph = utils.get_graph()
        if self._seed is None or self._seed < 0:
            # If using global seed, add a unique node ID to the seed sequence. This will ensure that two identical
            # samplers nevertheless produce different outputs in a repeatable manner.
            seed = global_seed
        else:
            seed = self._seed

        node = None
        if self._node_path and graph:
            node = utils.get_graph().get_node(self._node_path)
            if self._seed is None or self._seed < 0:
                # If using global seed, add a unique node ID to the seed sequence. This will ensure that two identical
                # samplers nevertheless produce different outputs in a repeatable manner.
                seed = (global_seed, self._node_id)
            else:
                seed = (self._seed, 0)

        # The seed includes the main seed component and a unique seed to ensure each component produces unique samples
        seed_sequence = np.random.SeedSequence(seed)
        if node:
            self._set_node_entropy(seed_sequence.entropy)
            active_generators[self._node_path] = self
        self._generator = np.random.default_rng(seed=seed_sequence)

    def release(self):
        if self._sub_orchestrator is not None:
            self._sub_orchestrator.reset()
        if self._sub_settings is not None:
            self._sub_settings.unsubscribe()

    @property
    def seed(self):
        return self._seed

    @seed.setter
    def seed(self, value):
        self._seed = value
        self.reset()

    @property
    def generator(self):
        return self._generator

    def initialize(self, seed: int, node: og.Node = None, node_id: int = None):
        self._seed = seed
        if node is not None:
            self._node_path = node.get_prim_path()
            self._graph = node.get_graph()
        if node_id is not None:
            release((self._seed, self._node_id))
            self._node_id = node_id
        self.reset()
