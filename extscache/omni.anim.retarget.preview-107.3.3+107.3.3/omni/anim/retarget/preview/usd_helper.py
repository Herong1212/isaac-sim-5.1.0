# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#


from pxr import Sdf, Usd, UsdSkel, UsdShade
from typing import Callable, List, Optional


def copy_prim_to_stage(
    source_stage: Usd.Stage,
    source_prim_path: Sdf.Path,
    target_stage: Usd.Stage,
    target_prim_path: Sdf.Path
):

    if not source_prim_path or not source_stage or not target_stage or not target_prim_path:
        return

    flatten_layer = source_stage.Flatten()
    target_layer = target_stage.GetRootLayer()

    target_stage.DefinePrim(target_prim_path)
    Sdf.CopySpec(flatten_layer, source_prim_path, target_layer, target_prim_path)


def traverse_prim(
    stage,
    path: Sdf.Path,
    condition_callback: Optional[Callable[[Usd.Prim, Sdf.Path], bool]] = None
) -> List[Sdf.Path]:
    return_paths = []
    prim = stage.GetPrimAtPath(Sdf.Path(path))
    for child in prim.GetChildren():
        return_paths += traverse_prim(stage, child.GetPrimPath(), condition_callback)
    if condition_callback is None or condition_callback(prim, path):
        return_paths.append(path)
    return return_paths


# DeletePrims command is tied to the default context so we write our deletion.
def delete_prims(stage, paths: List[Sdf.Path]):
    with Sdf.ChangeBlock():
        layer_stack = stage.GetLayerStack()
        for layer in layer_stack:
            temp_layer = Sdf.Layer.CreateAnonymous()
            edit = Sdf.BatchNamespaceEdit()
            for path in paths:
                prim_spec = layer.GetPrimAtPath(path)
                if prim_spec is None:
                    continue
                Sdf.CreatePrimInLayer(temp_layer, path)
                Sdf.CopySpec(layer, path, temp_layer, path)
                edit.Add(path, Sdf.Path.emptyPath)
            layer.Apply(edit)

# get the frist prim which check() is True,  return None if no prim find
def get_first_in_stage(stage, check: Callable):
    traver = Usd.TraverseInstanceProxies(Usd.PrimAllPrimsPredicate)
    primRange = iter(Usd.PrimRange(stage.GetPseudoRoot(), traver))
    for child in primRange:
        if check(child):
            return child
    return None

def is_skeleton(prim):
    return prim and prim.IsA(UsdSkel.Skeleton)


# get all binding material paths in a prim and children
def get_material_bindings(prim: Usd.Prim):
    binding_api = UsdShade.MaterialBindingAPI(prim)
    direct_binding = binding_api.GetDirectBinding()
    if direct_binding.GetMaterial():
        yield direct_binding.GetMaterialPath()

    # Check for collection-based bindings
    collection_bindings = binding_api.GetCollectionBindings()
    for binding in collection_bindings:
        if binding.GetMaterial():
            yield binding.GetMaterialPath()

    # Recursively check children
    for child in prim.GetChildren():
        yield from get_material_bindings(child)