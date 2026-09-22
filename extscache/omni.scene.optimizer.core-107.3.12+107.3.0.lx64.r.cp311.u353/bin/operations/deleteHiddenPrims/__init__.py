__copyright__ = "Copyright (c) 2024, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""


import omni.kit
from omni.scene.optimizer.core.operation import Operation
from pxr import Usd, UsdGeom


class DeleteHiddenPrimsOperation(Operation):
    def __init__(self):
        super().__init__("deleteHiddenPrims", "Delete Hidden Prims", "Deletes all prims that are constantly hidden.")

    @property
    def author(self):
        return "Scene Optimizer (Internal)"

    @property
    def version(self):
        return (1, 0, 0)

    @property
    def visible(self):
        return False

    def execute(self, _args):
        stage = self.get_usd_stage()
        hidden_prim_paths = []

        # Does not include instance proxies
        it = iter(Usd.PrimRange.Stage(stage, Usd.PrimIsLoaded & ~Usd.PrimIsAbstract))

        for prim in Usd.PrimRange(stage.GetPseudoRoot()):
            imageable = UsdGeom.Imageable(prim)
            if imageable:
                vis_attr = imageable.GetVisibilityAttr()
                if vis_attr.Get() == UsdGeom.Tokens.invisible:
                    it.PruneChildren()
                    hidden_prim_paths.append(str(prim.GetPath()))

        args = {"primPaths": hidden_prim_paths}
        omni.kit.commands.execute("SceneOptimizerOperation", operation="deletePrims", args=args)

        return True


#####################################
# Register Scene Optimizer Plugin
#####################################


def sceneOptimizerPluginInit():
    return DeleteHiddenPrimsOperation()
