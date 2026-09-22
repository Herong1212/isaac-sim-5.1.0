import carb
import omni

from pxr import Sdf


# from omni.metropolis.utils.file_util import JSONFileUtil


class SceneTaggingData:
    def __init__(self):
        self.flammable_item_prim_paths_by_type = {}

    def add_flammable_item(self, prim_path: str, item_type: str):
        self.flammable_item_prim_paths_by_type.setdefault(item_type, set()).add(prim_path)

    def add_flammable_items(self, prim_paths: list, item_type: str):
        self.flammable_item_prim_paths_by_type.setdefault(item_type, set()).update(prim_paths)

    def remove_flammable_item(self, prim_path: str, item_type: str):
        if item_type not in self.flammable_item_prim_paths_by_type:
            return
        self.flammable_item_prim_paths_by_type[item_type].discard(prim_path)


class AttributeUSDTagger:
    """reads/writes SceneTaggingData from/to USD Attributes"""

    flammable_item_tag: str = "IsaacSim_Replicator_Incident_Attr:FlammableItem"
    flammable_item_types: list = ["Box"]

    def Read(self) -> SceneTaggingData:  # noqa: C901, N802
        scene_tagging_data = SceneTaggingData()

        stage = omni.usd.get_context().get_stage()

        for prim in stage.Traverse():
            if prim.HasAttribute(AttributeUSDTagger.flammable_item_tag):
                prim_path = str(prim.GetPrimPath())
                flammable_item_type = prim.GetAttribute(AttributeUSDTagger.flammable_item_tag).Get()
                scene_tagging_data.add_flammable_item(prim_path, flammable_item_type)

        return scene_tagging_data

    def Write(self, scene_tagging_data: SceneTaggingData):  # noqa: C901, N802
        stage = omni.usd.get_context().get_stage()

        for prim in stage.Traverse():
            if prim.HasAttribute(AttributeUSDTagger.flammable_item_tag):
                prim.RemoveProperty(AttributeUSDTagger.flammable_item_tag)

        for item_type, prim_paths in scene_tagging_data.flammable_item_prim_paths_by_type.items():
            for prim_path in prim_paths:
                prim = stage.GetPrimAtPath(prim_path)
                if not prim:
                    carb.log_warn("Couldn't find prim at path: " + prim_path)
                    continue

                attr = prim.CreateAttribute(
                    AttributeUSDTagger.flammable_item_tag, Sdf.ValueTypeNames.String, custom=True
                )
                attr.Set(item_type)

    def prim_has_flammable_item_tag(self, prim_path):
        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(prim_path)
        if not prim:
            return False

        return prim.HasAttribute(AttributeUSDTagger.flammable_item_tag)

    def get_flammable_item_tag(self, prim_path):
        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(prim_path)
        if not prim:
            return None

        if not prim.HasAttribute(AttributeUSDTagger.flammable_item_tag):
            return None

        return prim.GetAttribute(AttributeUSDTagger.flammable_item_tag).Get()
