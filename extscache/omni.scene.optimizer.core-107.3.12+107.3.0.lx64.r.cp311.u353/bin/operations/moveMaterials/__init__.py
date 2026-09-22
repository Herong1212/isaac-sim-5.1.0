__copyright__ = "Copyright (c) 2024, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""


import omni.kit.commands
from omni.scene.optimizer.core.operation import Operation
from pxr import Sdf, UsdGeom, UsdShade


class MoveMaterialsOperation(Operation):
    def __init__(self):
        super().__init__(
            "moveMaterials",
            "Move Materials",
            'Moves all materials under a prim location such as "/World/Looks" and can also set the root prim of '
            + 'the path (e.g. "/World") as the default prim',
        )
        self.add_argument(
            "materialsPath",
            "Materials Root",
            Operation.ArgumentDisplayTypePrimPath,
            "The prim path that all materials will be moved under.",
            "/World/Looks",
        )
        self.add_argument(
            "makeRootDefault",
            "Make Root Default",
            Operation.ArgumentDisplayTypeBool,
            "Whether the root of materialsPath should be set as the default prim if the stage has no defaultPrim set.",
            True,
        )

    @property
    def author(self):
        return "Scene Optimizer (Internal)"

    @property
    def version(self):
        return (1, 0, 0)

    @property
    def visible(self):
        return False

    def execute(self, args):
        stage = self.get_usd_stage()

        # resolve the root prim path
        materials_path = Sdf.Path(args["materialsPath"])
        root_path = materials_path
        parent_path = root_path
        while parent_path and parent_path != Sdf.Path("/"):
            root_path = parent_path
            parent_path = root_path.GetParentPath()

        # set the root path as the default prim?
        default_prim = stage.GetDefaultPrim()
        if args["makeRootDefault"] and not default_prim:
            default_prim = UsdGeom.Xform.Define(stage, root_path)
            stage.SetDefaultPrim(default_prim.GetPrim())

        looks_scope = UsdGeom.Scope.Define(stage, materials_path)

        # discover all materials in the stage
        materials = []
        for prim in stage.Traverse():
            prefixes = prim.GetPath().GetPrefixes()
            if prefixes:
                if (
                    "Environment" in str(prefixes[0])
                    or "LightRig" in str(prefixes[0])
                    or "TeleportTools" in str(prefixes[0])
                ):
                    continue

            if prim.IsA(UsdShade.Material):
                materials.append(prim)

        # move the materials
        for material in materials:
            path_from = str(material.GetPath())

            if omni.usd.check_ancestral(material.GetPrim()):
                continue

            path_to = looks_scope.GetPath().AppendChild(material.GetName())

            omni.kit.commands.execute(
                "MovePrim", path_from=path_from, path_to=path_to, keep_world_transform=True, destructive=False
            )

        return True


#####################################
# Register Scene Optimizer Plugin
#####################################


def sceneOptimizerPluginInit():
    return MoveMaterialsOperation()
