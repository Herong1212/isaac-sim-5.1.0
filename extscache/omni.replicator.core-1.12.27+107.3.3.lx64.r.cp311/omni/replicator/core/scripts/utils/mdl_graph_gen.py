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


from pathlib import Path
from typing import Any

import omni
import omni.kit.window.material_graph as material_graph
from pxr import Sdf, UsdGeom, UsdShade

try:
    # Kit 106.4+
    import omni.UsdMdl as UsdMdl
except ImportError:
    try:
        # Kit 106.[2|3]
        import UsdMdl
    except ImportError:
        # Kit 106.1
        import usd.mdl as UsdMdl


REPLICATOR_SCOPE = "/Replicator"
LOOKS_PATH = "/Replicator/Looks"
DEFAULT_MAT_NAME = "RepMaterial"
DEFAULT_SOURCE_MDL = "nvidia/core_definitions.mdl"


def _get_case_insensitive_attr(module: Any, attr_str: str):
    for m_attr_str in dir(module):
        if m_attr_str.lower() == attr_str.lower():
            return getattr(module, m_attr_str)


def _get_dtype(attr_str: str):
    if attr_str is None:
        return None
    if attr_str == "terminal":
        return Sdf.ValueTypeNames.Token
    return _get_case_insensitive_attr(Sdf.ValueTypeNames, attr_str)


def import_compound(parent_path, identifier, source_asset):
    stage = omni.usd.get_context().get_stage()
    source_layer = Sdf.Layer.FindOrOpen(source_asset)
    target_layer = stage.GetEditTarget().GetLayer()
    source_path = identifier

    if not source_path.startswith("/"):
        source_path = Sdf.Path.absoluteRootPath.AppendChild(identifier)

    target_path = omni.usd.get_stage_next_free_path(
        stage, parent_path.AppendChild(Sdf.Path(source_path).name).pathString, False
    )
    target_path = Sdf.Path(target_path)

    # Copy
    Sdf.CopySpec(source_layer, source_path, target_layer, target_path)
    target_prim = stage.GetPrimAtPath(target_path)

    # remove xformOpOrder. It probably shouldn't be exported.
    if target_prim.HasProperty(UsdGeom.Tokens.xformOpOrder):
        target_prim.RemoveProperty(UsdGeom.Tokens.xformOpOrder)


class MaterialGraphGeneratorError(Exception):
    """Base exception for errors raised by the material graph generator"""

    def __init__(self, msg=None):
        if msg is None:
            msg = "A material graph generation error was encountered."
        super().__init__(msg)


class MaterialGraphGenerator:
    def __init__(self, material_definition) -> None:
        if not isinstance(material_definition, dict):
            raise MaterialGraphGeneratorError(
                f"Invalid material definition of type {type(material_definition)}, expected a dictionary."
            )

        manager = omni.kit.app.get_app().get_extension_manager()
        ext_path = manager.get_extension_path_by_module("omni.replicator.core")
        self.replicator_mdl_folder = Path(ext_path).joinpath("mdl").as_posix()

        self._mat_ext = material_graph.GraphExtension()
        self._mat_ext.refresh_compounds()

        self.compounds = {}
        for node in material_graph.compound_registry.nodes():
            self.compounds[node.subIdentifier.replace("/", "")] = node

        self.m_def = material_definition
        self.material_path = ""

        self._set_material_path()

    def _set_material_path(self):
        stage = omni.usd.get_context().get_stage()

        if not stage.GetPrimAtPath(REPLICATOR_SCOPE):
            stage.DefinePrim(REPLICATOR_SCOPE, "Scope")

        if not stage.GetPrimAtPath(LOOKS_PATH):
            stage.DefinePrim(LOOKS_PATH, "Scope")

        if "name" in self.m_def.keys():
            self.material_path = f'{LOOKS_PATH}/{self.m_def["name"]}'
        else:
            self.material_path = f"{LOOKS_PATH}/{DEFAULT_MAT_NAME}"
        self.material_path = Sdf.Path(omni.usd.get_stage_next_free_path(stage, self.material_path, False))

        UsdShade.Material.Define(stage, self.material_path)

    def _create_compound_node(self, compound_node_id):
        stage = omni.usd.get_context().get_stage()
        compound_node = self.compounds.get(compound_node_id, None)
        node_path = None
        if compound_node:
            import_compound(
                parent_path=self.material_path, identifier=compound_node_id, source_asset=compound_node.sourceAsset
            )
            node_path = Sdf.Path(self.material_path.AppendElementString(compound_node_id))
        return UsdShade.NodeGraph(stage.GetPrimAtPath(node_path))

    def _set_values(self, node_key, values):
        node = self.m_def["nodes"][node_key]["prim"]
        sdr_node = UsdMdl.RegistryUtils.GetShaderNodeForPrim(node.GetPrim())
        for input_name, value in values.items():
            pin_in = self.m_def["nodes"][node_key]["prim"].GetInput(input_name)
            if not pin_in.GetAttr().IsValid():
                if input_name not in sdr_node.GetInputNames():
                    raise MaterialGraphGeneratorError(
                        f"Node `{sdr_node.GetName()}` has no input named `{input_name}` from available inputs: {sdr_node.GetInputNames()}"
                    )

                dtype = _get_dtype(sdr_node.GetInput(input_name).GetType())
                pin_in = node.CreateInput(input_name, dtype)

            python_class = pin_in.GetAttr().GetTypeName().type.pythonClass  # Might be a better way to do this?
            if python_class:
                value = python_class(value)
            pin_in.GetAttr().Set(value)

    def _create_connection(self, connection):
        # Get the input and output nodes and types
        upstream_node = self.m_def["nodes"][connection["output"]["node"]]["prim"]
        downstream_node_type = self.m_def["nodes"][connection["input"]["node"]]["type"]
        downstream_node = self.m_def["nodes"][connection["input"]["node"]]["prim"]
        sdr_upstream_node = UsdMdl.RegistryUtils.GetShaderNodeForPrim(upstream_node.GetPrim())
        sdr_downstream_node = UsdMdl.RegistryUtils.GetShaderNodeForPrim(downstream_node.GetPrim())

        # Check that the output pin already exists
        output_pin_name = connection["output"]["pin"]
        output_pins = [p.GetBaseName() for p in upstream_node.GetOutputs()]
        if output_pin_name in output_pins:
            pin_out = upstream_node.GetOutput(output_pin_name)
        elif output_pin_name in sdr_upstream_node.GetOutputNames():
            output_dtype = _get_dtype(self.m_def["nodes"][connection["output"]["node"]].get("out_type"))
            if output_dtype is None:
                output_dtype = _get_dtype(sdr_upstream_node.GetInput(output_pin_name).GetType())
            pin_out = upstream_node.CreateOutput(output_pin_name, output_dtype)
        else:
            raise MaterialGraphGeneratorError(
                f"Node `{sdr_upstream_node.GetName()}` has no input named `{output_pin_name}` from available inputs: {sdr_upstream_node.GetInputNames()}"
            )

        if downstream_node_type.lower() == "material":
            if connection["input"]["pin"].lower() == "surface":
                downstream_node.CreateSurfaceOutput("mdl").ConnectToSource(pin_out)
            elif connection["input"]["pin"].lower() == "displacement":
                downstream_node.CreateDisplacementOutput("mdl").ConnectToSource(pin_out)
            elif connection["input"]["pin"].lower() == "volume":
                downstream_node.CreateVolumeOutput("mdl").ConnectToSource(pin_out)
        else:
            input_name = connection["input"]["pin"]
            downstream_inputs = [p.GetBaseName() for p in downstream_node.GetInputs()]
            if input_name in downstream_inputs:
                pin_in = downstream_node.GetInput(input_name)
            elif input_name in sdr_downstream_node.GetInputNames():
                dtype = _get_dtype(sdr_downstream_node.GetInput(input_name).GetType())
                pin_in = downstream_node.CreateInput(input_name, dtype)
            else:
                raise MaterialGraphGeneratorError(
                    f"Node `{sdr_downstream_node.GetName()}` has no input named `{input_name}` from available inputs: {sdr_downstream_node.GetInputNames()}"
                )
            pin_in.ConnectToSource(pin_out)

    def _check_mdl_source(self, mdl_file):
        check_path = Path(self.replicator_mdl_folder).joinpath(mdl_file)
        if check_path.exists():
            return str(check_path.as_posix())
        elif Path(mdl_file).suffix == ".mdl" and Path(mdl_file).exists():
            return str(Path(mdl_file).as_posix())

    def _create_node(self, node_type, node_name=None, alt_source=None):
        stage = omni.usd.get_context().get_stage()

        if not node_name:
            node_name = node_type

        if node_type == "material":
            node = stage.GetPrimAtPath(self.material_path)
            node = UsdShade.Material(node)
        else:
            if node_type in self.compounds.keys():
                node = self._create_compound_node(node_type)
            else:
                node_path = Sdf.Path(
                    omni.usd.get_stage_next_free_path(stage, self.material_path.AppendElementString(node_name), False)
                )
                node = UsdShade.Shader.Define(stage, node_path)
                if alt_source:
                    alt_source = self._check_mdl_source(alt_source)
                    node.SetSourceAsset(alt_source, "mdl")
                else:
                    node.SetSourceAsset(DEFAULT_SOURCE_MDL, "mdl")
                node.SetSourceAssetSubIdentifier(node_type, "mdl")
        return node

    def create_graph(self):
        self._create_graph()
        return self.material_path

    def _create_graph(self):
        # Create all the nodes and assign values first
        for node in self.m_def["nodes"]:
            working_node = self.m_def["nodes"][node]
            if "type" not in working_node.keys():
                raise MaterialGraphGeneratorError("Node needs to have a type!")
            else:
                node_name = self.m_def["nodes"][node]["name"] if "name" in self.m_def["nodes"][node].keys() else None
                alt_src = self.m_def["nodes"][node]["source"] if "source" in self.m_def["nodes"][node].keys() else None
                n = self._create_node(self.m_def["nodes"][node]["type"], node_name, alt_src)
                working_node["prim"] = n

        # Connect all the created nodes
        for edge in self.m_def["edges"]:
            working_edge = self.m_def["edges"][edge]
            if "output" in working_edge.keys() and "input" in working_edge.keys():
                self._create_connection(working_edge)
            elif "output" not in working_edge.keys() and "input" in working_edge.keys():
                self._set_values(working_edge["input"]["node"], working_edge["input"]["values"])
