"""Deprecated & not used. For updating old MdlSchema to MDLSchema."""
__all__ = ["MDLSchema"]

import carb
import omni.usd
from pxr import Usd, Sdf, UsdShade

# this isn't used anymore? only used for app.hydra.supportOldMdlSchema which is always false
class MDLSchema: # pragma: no cover
    """Deprecated & not used. For updating old MdlSchema to MDLSchema."""
    def on_menu_click_update_mdl_schema(menu, value):
        stage = omni.usd.get_context().get_stage()
        local_layers = stage.GetLayerStack()
        with Sdf.ChangeBlock():
            for prim in stage.Traverse():
                if prim.IsA(UsdShade.Material):
                    material = UsdShade.Material(prim)
                    shader, _, _ = material.ComputeSurfaceSource()
                    if not shader:
                        # Although the schema is new, there can still be old parameter overrides if the MDL is referenced into the stage. Need to convert those old overrides.
                        shader, _, _ = material.ComputeSurfaceSource("mdl")
                    if shader:
                        source = shader.GetImplementationSource()
                        if (
                            source == UsdShade.Tokens.id and shader.GetShaderId() == "mdlMaterial"
                        ) or source == UsdShade.Tokens.sourceAsset:
                            carb.log_warn("Updating " + prim.GetPath().pathString)

                            shader_prim = shader.GetPrim()
                            mdl_token = "mdl"
                            shader_out = shader.GetOutput("out")

                            # Update all layers
                            if source != UsdShade.Tokens.sourceAsset:
                                for material_prim_spec in reversed(prim.GetPrimStack()):
                                    layer = material_prim_spec.layer
                                    if layer not in local_layers:
                                        # if MDL is referenced in from the other USD file, conversion will fail
                                        carb.log_warn(
                                            "Could not modify material on layer "
                                            + layer.realPath
                                            + ". Please update the file manually"
                                        )
                                        continue

                                    for attr_spec in material_prim_spec.attributes:
                                        if attr_spec.name == "outputs:surface":
                                            layer_was_editable = layer.permissionToEdit
                                            layer.SetPermissionToEdit(True)
                                            layer.SetPermissionToSave(True)

                                            with Usd.EditContext(stage, layer):
                                                attr_spec.connectionPathList.explicitItems = []
                                                material.CreateSurfaceOutput(mdl_token).ConnectToSource(shader_out)
                                                material.CreateVolumeOutput(mdl_token).ConnectToSource(shader_out)
                                                material.CreateDisplacementOutput(mdl_token).ConnectToSource(shader_out)

                                            layer.SetPermissionToEdit(layer_was_editable)
                                            break

                            for shader_prim_spec in reversed(shader_prim.GetPrimStack()):
                                layer = shader_prim_spec.layer

                                prop_spec_to_remove = []
                                module = None
                                name = None
                                has_id = False
                                for prop_spec in shader_prim_spec.properties:
                                    if prop_spec.name == "module":
                                        prop_spec_to_remove.append(prop_spec)
                                        module = prop_spec.default
                                    if prop_spec.name == "name":
                                        prop_spec_to_remove.append(prop_spec)
                                        name = prop_spec.default
                                    if prop_spec.name == "info:id":
                                        prop_spec_to_remove.append(prop_spec)
                                        has_id = True
                                    if prop_spec.name == "shaderType":
                                        prop_spec_to_remove.append(prop_spec)

                                if not has_id and name == None and module == None and len(prop_spec_to_remove) == 0:
                                    continue

                                if layer not in local_layers:
                                    # if MDL is referenced in from the other USD file, conversion will fail
                                    carb.log_warn(
                                        "Could not modify material on layer "
                                        + layer.realPath
                                        + ". Please update the file manually"
                                    )
                                    continue

                                layer_was_editable = layer.permissionToEdit
                                layer.SetPermissionToEdit(True)
                                layer.SetPermissionToSave(True)

                                with Usd.EditContext(stage, layer):
                                    if has_id:
                                        shader.SetShaderId("")
                                        shader.GetImplementationSourceAttr().Set(UsdShade.Tokens.sourceAsset)

                                    if module is not None:
                                        shader.SetSourceAsset(module, mdl_token)

                                    if name is not None:
                                        shader.SetSourceAssetSubIdentifier(name, mdl_token)

                                    for prop_spec in prop_spec_to_remove:
                                        shader_prim_spec.RemoveProperty(prop_spec)

                                layer.SetPermissionToEdit(layer_was_editable)
