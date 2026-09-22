"""This module provides utilities for material binding in USD stages, including defining constants, updating material data, retrieving material bindings for primitives, and creating non-persistent attributes for materials."""

__all__ = ["Constant", "get_binding_from_prims"]

import carb
import omni.usd
from pxr import Sdf, Usd, UsdShade


class Constant:
    """A class that defines constants for a USD stage material binding tool.

    This class contains various constants such as icon size, label width, font size, and
    special identifiers for missing paths or mixed values. It also ensures that its
    attributes are immutable by raising a ValueError if an attempt is made to
    set an attribute. The class checks the validity of certain constants during
    initialization to ensure correctness of the defined values."""

    def __setattr__(self, name, value):  # pragma: no cover
        raise ValueError(f"Can't change Constant.{name}")

    ICON_SIZE = 96
    """int: Icon display size in pixels."""
    BOUND_LABEL_WIDTH = 50
    """int: Width of the bound label in pixels."""
    FONT_SIZE = 14.0
    """float: Font size for text elements."""
    SDF_PATH_INVALID = "$NONE$"
    """str: Represents an invalid SDF path."""
    PERSISTENT_SETTINGS_PREFIX = "/persistent"
    """str: Prefix for persistent settings paths."""
    MIXED = "Mixed"
    """str: Indicates a mixed value state."""
    MIXED_COLOR = 0xFFCC9E61
    """int: Color code for mixed value indication."""
    # verify SDF_PATH_INVALID is invalid
    if Sdf.Path.IsValidPathString(SDF_PATH_INVALID):  # pragma: no cover
        raise ValueError("SDF_PATH_INVALID is Sdf.Path.IsValidPathString - FIXME")


def _populate_data(stage, material_data, collection_or_prim, material=None, relationship=None, material_missing=False):
    def update_strength(value, strength):
        if value is None:
            value = strength
        elif value != strength:
            value = Constant.MIXED
        return value

    if isinstance(collection_or_prim, Usd.CollectionAPI):  # pragma: no cover
        prim_path = collection_or_prim.GetCollectionPath()
    else:
        prim_path = collection_or_prim.GetPath()

    inherited = False
    strength_default = carb.settings.get_settings().get(
        Constant.PERSISTENT_SETTINGS_PREFIX + "/app/stage/materialStrength"
    )
    strength = strength_default
    material_name = Constant.SDF_PATH_INVALID

    if material:
        relationship_source_path = None
        if relationship:
            relationship_source_path = relationship.GetPrim().GetPath()
            if isinstance(collection_or_prim, Usd.CollectionAPI):  # pragma: no cover
                relationship_source_path = relationship.GetTargets()[0]

        if material and relationship and prim_path.pathString != relationship_source_path.pathString:
            # If we have a material, but it's not assigned directly to us, it must be inherited
            inherited = True
        if relationship:
            strength = UsdShade.MaterialBindingAPI.GetMaterialBindingStrength(relationship)

        if isinstance(material, Sdf.Path):
            material_name = material.pathString
        else:
            material_name = material.GetPrim().GetPath().pathString

    if material_name not in material_data["material"]:
        material_data["material"][material_name] = {
            "bound": set(),
            "inherited": set(),
            "bound_info": set(),
            "inherited_info": set(),
            "relationship": set(),
            "strength": None,
            "missing": material_missing,
        }

    if inherited:
        material_data["material"][material_name]["inherited"].add(collection_or_prim)
        material_data["material"][material_name]["inherited_info"].add((prim_path.pathString, material_name, strength))
        material_data["inherited"].add(collection_or_prim)
        material_data["inherited_info"].add((prim_path.pathString, material_name, strength))
    else:
        material_data["material"][material_name]["bound"].add(collection_or_prim)
        material_data["material"][material_name]["bound_info"].add((prim_path.pathString, material_name, strength))
        material_data["bound"].add(collection_or_prim)
        material_data["bound_info"].add((prim_path.pathString, material_name, strength))

    if relationship:
        material_data["relationship"].add(relationship)
        material_data["material"][material_name]["relationship"].add(relationship)

    if strength is not None:
        material_data["material"][material_name]["strength"] = update_strength(
            material_data["material"][material_name]["strength"], strength
        )
        material_data["strength"] = update_strength(material_data["strength"], strength)


def get_binding_from_prims(stage, prim_paths, material_purpose=UsdShade.Tokens.allPurpose):
    """Retrieves material bindings for a given set of primitive paths on a USD stage.

    Args:
        stage (:obj:`Usd.Stage`): The USD stage from which to retrieve material bindings.
        prim_paths (List[:obj:`Sdf.Path`]): A list of SDF paths representing the primitives for which material bindings are to be retrieved.
        material_purpose (str, optional): The purpose of the material binding to retrieve. Defaults to UsdShade.Tokens.allPurpose.

    Returns:
        dict: A dictionary containing material binding information for the specified primitives."""
    material_data = {
        "material": {},
        "bound": set(),
        "bound_info": set(),
        "inherited": set(),
        "inherited_info": set(),
        "relationship": set(),
        "strength": None,
        "missing": False,
    }
    material_missing = False

    for prim_path in prim_paths:
        if prim_path.IsPrimPath():
            prim = stage.GetPrimAtPath(prim_path)
            if prim:
                material, relationship = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial(material_purpose)
                if not material and relationship:
                    # material is missing, get path to material
                    material_missing = True
                    material_data["missing"] = material_missing
                    db = UsdShade.MaterialBindingAPI(prim).GetDirectBinding(material_purpose)
                    if db:
                        if not db.GetMaterialPath():
                            # if its inherited material, need to find parent prim with binding
                            mprim = prim.GetParent()
                            max_loop = 100
                            while max_loop > 0:
                                db = UsdShade.MaterialBindingAPI(mprim).GetDirectBinding(material_purpose)
                                if not db or db.GetMaterialPath():
                                    break
                                mprim = mprim.GetParent()
                                max_loop -= 1
                        material = db.GetMaterialPath() if db else None

                _populate_data(stage, material_data, prim, material, relationship, material_missing=material_missing)
        elif Usd.CollectionAPI.IsCollectionAPIPath(prim_path):  # pragma: no cover
            real_prim_path = prim_path.GetPrimPath()
            prim = stage.GetPrimAtPath(real_prim_path)
            binding_api = UsdShade.MaterialBindingAPI(prim)
            all_bindings = binding_api.GetCollectionBindings()
            collection_name = prim_path.pathString[prim_path.pathString.find(".collection:") + 12 :]

            # TODO: test this when we have multiple collections on a prim
            if all_bindings:
                for b in all_bindings:
                    collection = b.GetCollection()
                    if collection_name == collection.GetName():
                        relationship = b.GetBindingRel()
                        material = b.GetMaterial()
                        _populate_data(stage, material_data, collection, material, relationship)
            else:
                # If there are no bindings we want to set up defaults anyway so the widget appears with "None" assigned
                collection = Usd.CollectionAPI.Get(stage, prim_path)
                _populate_data(stage, material_data, collection)

    return material_data


# this function is same as one in usdshade\utils.py and not used
async def create_nonpersistant_attribute(material_paths, name, sdf_value_type_name, value):  # pragma: no cover
    """Creates non-persistent attributes for a set of material paths.

    This function generates attribute specifications on the current stage's session layer for each
    material path provided. These attributes are marked as non-persistent and hidden. The attributes
    are created with a specified SDF value type and a default value.

    Args:
        material_paths (List[:obj:`Sdf.Path`]): A list of SDF Paths where the attributes will be created.
        name (str): The name of the attribute to create.
        sdf_value_type_name (str): The SDF value type name for the attribute.
        value (Any): The default value to set for the created attribute.
    """

    async def create_attribute_specs(material_paths, name, sdf_value_type_name, value):
        stage = omni.usd.get_context().get_stage()
        session_layer = stage.GetSessionLayer()
        with Sdf.ChangeBlock():
            for prim_path in material_paths:
                attr_path = prim_path.AppendProperty(name)
                attr_spec = stage.GetAttributeAtPath(attr_path)

                if not attr_spec:
                    Sdf.JustCreatePrimAttributeInLayer(
                        session_layer, attr_path, sdf_value_type_name, Sdf.VariabilityUniform, True
                    )
                    attr_spec = session_layer.GetAttributeAtPath(attr_path)

                if attr_spec:
                    attr_spec.customData["nonpersistant"] = True
                    attr_spec.hidden = True

                    if attr_spec.default != value:
                        attr_spec.default = value

    with Sdf.ChangeBlock():
        await create_attribute_specs(material_paths, name, sdf_value_type_name, value)
