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

from typing import Any, List, Optional, Union

import carb
import numpy as np
import omni.timeline
import omni.UsdMdl as UsdMdl
import pxr
import usdrt


def apply_schemas(prim_spec: pxr.Sdf.Spec, schemas: List[str]):
    """Applies USD schemas to a prim spec and creates their default attributes.

    Args:
        prim_spec: Prim spec to apply schemas to
        schemas: List of schema classes to apply
    """
    schema_registry = pxr.Usd.SchemaRegistry()

    for schema in schemas:
        if not isinstance(schema, str):
            raise ValueError(f"Encountered invalid schema {schema}. Schema must be defined as a string")
        # Check if this is a concrete/typed schema or an API schema
        concrete_def = schema_registry.FindConcretePrimDefinition(schema)
        # Split schema_name from schema_name:instance_name if schema is provided as a multi-apply schema
        schema_instance = schema.split(":")
        schema_name = schema_instance[0]
        instance_name = schema_instance[1] if len(schema_instance) == 2 else ""
        api_def = schema_registry.FindAppliedAPIPrimDefinition(schema_name)

        if not concrete_def and not api_def:
            raise ValueError(f"Schema {schema} not found")

        is_multiple_apply = schema_registry.IsMultipleApplyAPISchema(schema_name)

        if concrete_def:
            prim_spec.typeName = schema
        elif api_def:
            # This is an API schema
            # Get the current apiSchemas metadata. Avoid forcing an explicit list-op,
            # which can mask weaker layer opinions (e.g., physics API schemas).
            api_schemas: pxr.Sdf.TokenListOp = prim_spec.GetInfo("apiSchemas") or pxr.Sdf.TokenListOp()

            # Helper: determine if schema token is already present in this layer's list-op
            def _op_contains(op: pxr.Sdf.TokenListOp, token: str) -> bool:
                lists = []
                if getattr(op, "explicitItems", None):
                    lists.append(op.explicitItems)
                if getattr(op, "prependedItems", None):
                    lists.append(op.prependedItems)
                if getattr(op, "appendedItems", None):
                    lists.append(op.appendedItems)
                return any(token in lst for lst in lists)

            if _op_contains(api_schemas, schema):
                continue

            # Prefer updating explicit items only if explicit is already used in this layer;
            # otherwise append to appendedItems to preserve weaker opinions.
            if getattr(api_schemas, "explicitItems", None):
                new_explicit = list(api_schemas.explicitItems)
                if schema not in new_explicit:
                    new_explicit.append(schema)
                api_schemas.explicitItems = new_explicit
            else:
                new_appended = list(api_schemas.appendedItems or [])
                if schema not in new_appended:
                    new_appended.append(schema)
                api_schemas.appendedItems = new_appended

            prim_spec.SetInfo("apiSchemas", api_schemas)

            # Apply schema attributes
            for prop_name in api_def.GetPropertyNames():
                prop_spec = api_def.GetSchemaPropertySpec(prop_name)

                # Replace __INSTANCE_NAME__ with the actual instance name
                if instance_name and is_multiple_apply:
                    prop_name = prop_name.replace("__INSTANCE_NAME__", instance_name)

                # Skip if property already exists
                if prop_name in prim_spec.properties:
                    continue

                # Create the property on the prim spec
                if isinstance(prop_spec, pxr.Sdf.AttributeSpec):
                    attr_spec = pxr.Sdf.AttributeSpec(
                        prim_spec, prop_name, prop_spec.typeName, variability=prop_spec.variability
                    )

                    # Copy default value if it exists
                    if hasattr(prop_spec, "default") and prop_spec.default is not None:
                        attr_spec.default = prop_spec.default


def get_is_fsd_enabled():
    return False
    # return carb.settings.get_settings().get_as_bool("/app/useFabricSceneDelegate")


def _get_case_insensitive_attr(module: Any, attr_str: str):
    for m_attr_str in dir(module):
        if m_attr_str.lower() == attr_str.lower():
            return getattr(module, m_attr_str)


def _get_dtype(attr_str: str):
    if attr_str is None:
        return None
    if attr_str == "terminal":
        return pxr.Sdf.ValueTypeNames.Token
    return _get_case_insensitive_attr(pxr.Sdf.ValueTypeNames, attr_str)


def get_world_transform(prim: Union[pxr.Usd.Prim, usdrt.Usd.Prim]):
    """Gets the world transform matrix for the specified prim

    Args:
        prim (Union[str, pxr.Sdf.Path, usdrt.Sdf.Path, pxr.Usd.Prim, usdrt.Usd.Prim]):
            Reference to get transform from.

    Returns:
        Gf.Matrix4d: World transform matrix of the reference.

    Raises:
        ValueError: If relative_to is invalid or prim cannot be found.
    """
    if not isinstance(prim, (pxr.Usd.Prim, usdrt.Usd.Prim)):
        raise ValueError(f"Invalid prim type: {type(prim)}")

    # Get world transform of reference prim
    if get_is_fsd_enabled() and isinstance(prim, usdrt.Usd.Prim):
        stage = prim.GetStage()
        stage_id = stage.GetStageIdAsStageId()
        fabric_id = stage.GetFabricId()
        prim_path = prim.GetPrimPath()

        hier = usdrt.hierarchy.IFabricHierarchy().get_fabric_hierarchy(fabric_id, stage_id)
        return usdrt.Gf.Transform(hier.get_world_xform(prim_path))
    else:
        timeline_iface = omni.timeline.get_timeline_interface()
        xformable = pxr.UsdGeom.Xformable(prim)
        return pxr.Gf.Transform(xformable.ComputeLocalToWorldTransform(timeline_iface.get_current_time()))


def get_local_transform(prim: Union[pxr.Usd.Prim, usdrt.Usd.Prim]):
    """Gets the local transform matrix for the specified prim

    Args:
        prim (Union[str, pxr.Sdf.Path, usdrt.Sdf.Path, pxr.Usd.Prim, usdrt.Usd.Prim]):
            Reference to get transform from.

    Returns:
        Gf.Matrix4d: Local transform matrix of the reference.

    Raises:
        ValueError: If relative_to is invalid or prim cannot be found.
    """
    if not isinstance(prim, (pxr.Usd.Prim, usdrt.Usd.Prim)):
        raise ValueError(f"Invalid prim type: {type(prim)}")

    # Get world transform of reference prim
    if get_is_fsd_enabled() and isinstance(prim, usdrt.Usd.Prim):
        stage = prim.GetStage()
        stage_id = stage.GetStageIdAsStageId()
        fabric_id = stage.GetFabricId()
        prim_path = prim.GetPrimPath()

        hier = usdrt.hierarchy.IFabricHierarchy().get_fabric_hierarchy(fabric_id, stage_id)
        return usdrt.Gf.Transform(hier.get_local_xform(prim_path))
    else:
        timeline_iface = omni.timeline.get_timeline_interface()
        xformable = pxr.UsdGeom.Xformable(prim)
        return pxr.Gf.Transform(xformable.GetLocalTransformation(timeline_iface.get_current_time()))


def get_shader_from_material(prim, get_prim=False):
    if isinstance(prim, usdrt.Usd.Prim):
        # TODO: this is not correct, we need to get the shader from the material
        shader = usdrt.UsdShade.Shader(prim.GetChildren()[0])
        if get_prim:
            return shader.GetPrim()
        return shader

    material = pxr.UsdShade.Material(prim)
    shader = material.ComputeSurfaceSource("mdl")[0] if material else None

    if shader and get_prim:
        return shader.GetPrim()
    return shader


def populate_material_inputs(prim: Union[pxr.Usd.Prim, usdrt.Usd.Prim]):
    if not isinstance(prim, (pxr.Usd.Prim, usdrt.Usd.Prim)) or prim.GetTypeName() != "Material":
        raise ValueError(f"Invalid prim {prim} of type {prim.GetTypeName()}. Expected Material.")

    if isinstance(prim, usdrt.Usd.Prim):
        return

    shader = get_shader_from_material(prim, False)

    shader_node = UsdMdl.RegistryUtils.GetShaderNodeForPrim(shader.GetPrim())
    for input_name in shader_node.GetInputNames():
        if prim.HasAttribute(f"inputs:{input_name}"):
            continue
        dtype = _get_dtype(shader_node.GetInput(input_name).GetType())
        default_value = shader_node.GetInput(input_name).GetDefaultValue()
        if dtype == "string" and default_value is not None:
            dtype = pxr.Sdf.GetValueTypeNameForValue(default_value)
        shader.CreateInput(input_name, dtype)


def get_batched_value(
    value: Any,
    prims: Optional[Union[List[Union[pxr.Usd.Prim, usdrt.Usd.Prim]], usdrt.Rt.RtPrimSelection]] = None,
    count: Optional[int] = None,
):
    if value is None:
        return value

    if isinstance(value, np.ndarray):
        value = value.tolist()

    if not isinstance(value, list):
        value = [value]

    if count is None and prims is not None:
        if isinstance(prims, (pxr.Usd.Prim, usdrt.Usd.Prim)):
            count = 1
        else:
            count = 0
            for prim in prims:
                if not isinstance(prim, (pxr.Usd.Prim, usdrt.Usd.Prim)):
                    raise ValueError(f"Invalid prim type: {type(prim)}, expected `pxr.Usd.Prim` or `usdrt.Usd.Prim`")

                if prim.GetTypeName() == "PointInstancer":
                    count += len(prim.GetAttribute("protoIndices").Get())
                elif isinstance(prim, (pxr.Usd.Prim, usdrt.Usd.Prim)):
                    count += 1
                elif isinstance(prim, usdrt.Rt.RtPrimSelection):
                    count += len(prim)
                else:
                    raise ValueError(f"Unsupported prim type: {type(prim)}")
    elif count is None:
        raise ValueError("Either 'count' or 'prims' must be provided")

    if len(value) == 1 and count > 1:
        return value * count
    elif len(value) != count:
        return [value] * count
    return value
