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

import ctypes
import json

import carb
import carb.events
import numpy as np
import omni.graph.core as og
import omni.kit
import warp as wp
from omni.replicator.core import AnnotatorRegistry, WriterRegistry, WriterRegistryError, annotators, orchestrator

"""OmniGraph node to call python writer"""


class OgnWriterInternalState:
    def __init__(self):
        self._input_attributes = None


class OgnWriter:
    @staticmethod
    def internal_state():
        return OgnWriterInternalState()

    @staticmethod
    def compute(db) -> bool:
        state = db.shared_state
        writer_id = db.inputs.writerId
        writer_name = db.inputs.writerName
        data_structure = db.inputs.dataStructure
        render_products = db.inputs.renderProducts

        # Check that the writer ID is not empty first
        if writer_id == "":
            db.outputs.exec = og.ExecutionAttributeState.DISABLED
            return False

        try:
            writer = WriterRegistry._get_attached_writer(writer_id)
        except WriterRegistryError as error:
            db.log_error(error)
            db.outputs.exec = og.ExecutionAttributeState.DISABLED
            return False

        inputs = {}
        writer_payload = {
            "swhFrameNumber": 0,  # Deprecated, kept for backwards compatibility
            "reference_time": (db.inputs.referenceTimeNumerator, db.inputs.referenceTimeDenominator),
        }

        # FIXME: Because of OM-47286, can't pass a bundle for now.
        def _populate_anno_attributes(db):
            state = db.shared_state
            state._input_attributes = {}
            for attribute in db.node.get_attributes():
                param = attribute.get_name()
                if attribute.get_port_type() != og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT:
                    continue
                if attribute.get_resolved_type().get_role_name() == "execution":
                    continue
                attr_str = param.split(":")
                if len(attr_str) != 4:
                    continue
                _, render_prod, annotator_type, param_name = attr_str
                state._input_attributes.setdefault((render_prod, annotator_type), {})[param_name] = attribute

        if state._input_attributes is None:
            # Cache valid annotator inputs from attributes so they aren't parsed every time
            _populate_anno_attributes(db)
        inputs = state._input_attributes

        # Get render products data
        rp_resolutions = db.node.get_attribute("inputs:render_products:resolution").get_array(False, False, 0)
        rp_cameras = db.node.get_attribute("inputs:render_products:camera").get_array(False, False, 0)
        rp_names = db.node.get_attribute("inputs:render_products:name").get_array(False, False, 0)

        # Get distribution nodes
        # NOTE: Indexing using reduced sim time may not function with asyncRendering = True
        sim_time = orchestrator.get_reduced_ref_time(
            db.inputs.referenceTimeNumerator, db.inputs.referenceTimeDenominator
        )
        writer_payload["distribution_outputs"] = orchestrator._get_distribution_values(sim_time)
        writer_payload["trigger_outputs"] = orchestrator._get_trigger_values(sim_time)
        writer_payload["named_outputs"] = orchestrator._get_named_node_values(sim_time)

        data_structure = data_structure.lower()
        use_legacy_structure = data_structure == "legacy"
        # Add camera data
        for name, camera, resolution in zip(rp_names, rp_cameras, rp_resolutions):
            if use_legacy_structure:
                writer_payload[f"rp_{name}"] = {"camera": camera, "resolution": resolution}
            elif data_structure == "renderproduct":
                writer_payload.setdefault("renderProducts", {})
                writer_payload["renderProducts"].setdefault(name, {}).update(
                    {"camera": camera, "resolution": resolution}
                )
            elif data_structure == "annotator":
                writer_payload.setdefault("annotators", {})
                writer_payload["annotators"].setdefault("camera", {}).update({name: camera})
                writer_payload["annotators"].setdefault("resolution", {}).update({name: resolution})
            else:
                raise ValueError(
                    f"Invalid output structure specified: {data_structure}. Select from [legacy, renderProduct, annotator]"
                )
        carb.profiler.begin(124, "OgnWriter - prepare annotator")

        # Write data to payload
        for annotator_id, params in inputs.items():
            (render_prod_name, annotator_type) = annotator_id
            annotator_params = AnnotatorRegistry._annotators.get(annotator_type)
            annotator_output, do_synchronize = annotators.annotator_utils._get_annotator_data(
                params, annotator_params, None, annotator_id, use_legacy_structure=use_legacy_structure
            )

            annotator_label = annotator_type

            if use_legacy_structure:
                if not len(render_products) == 1:
                    annotator_label += "-" + render_prod_name
                writer_payload[annotator_label] = annotator_output
            elif data_structure == "renderproduct":
                writer_payload["renderProducts"][render_prod_name].update({annotator_label: annotator_output})
            elif data_structure == "annotator":
                writer_payload["annotators"].setdefault(annotator_label, {}).update(
                    {render_prod_name: annotator_output}
                )
            else:
                raise ValueError(
                    f"Invalid output structure specified: {data_structure}. Select from [legacy, renderProduct, annotator]"
                )

        if do_synchronize:
            wp.synchronize()

        carb.profiler.end(124)
        carb.profiler.begin(125, "OgnWriter - write payload")
        writer._write(writer_payload)
        carb.profiler.end(125)
        return True
