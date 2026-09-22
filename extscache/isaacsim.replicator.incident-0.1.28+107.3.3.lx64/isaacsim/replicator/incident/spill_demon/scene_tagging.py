import carb
import omni

from pxr import Sdf


# from isaacsim.replicator.metropolis.utils.file_util import JSONFileUtil


class SceneTaggingData:
    def __init__(self):
        self.leakable_item_prim_paths_by_type = {}
        self.spillable_area_prim_paths_by_type = {}

    def add_leakable_item(self, prim_path: str, item_type: str):
        self.leakable_item_prim_paths_by_type.setdefault(item_type, set()).add(prim_path)

    def add_spillable_area(self, prim_path: str, item_type: str):
        self.spillable_area_prim_paths_by_type.setdefault(item_type, set()).add(prim_path)

    def remove_leakable_item(self, prim_path: str, item_type: str):
        if item_type not in self.leakable_item_prim_paths_by_type:
            return
        self.leakable_item_prim_paths_by_type[item_type].discard(prim_path)

    def remove_spillable_area(self, prim_path: str, item_type: str):
        if item_type not in self.spillable_area_prim_paths_by_type:
            return
        self.spillable_area_prim_paths_by_type[item_type].discard(prim_path)


class AttributeUSDTagger:
    """reads/writes SceneTaggingData from/to USD Attributes"""

    leakable_item_tag: str = "IsaacSim_Replicator_Incident_Attr:LeakableItem"
    leakable_item_types: list = ["Item"]

    spillable_area_tag: str = "IsaacSim_Replicator_Incident_Attr:SpillableArea"
    spillable_area_types: list = ["Floor"]

    def Read(self) -> SceneTaggingData:  # noqa: C901, N802
        scene_tagging_data = SceneTaggingData()

        stage = omni.usd.get_context().get_stage()

        for prim in stage.Traverse():
            if prim.HasAttribute(AttributeUSDTagger.leakable_item_tag):
                prim_path = str(prim.GetPrimPath())
                leakable_item_type = prim.GetAttribute(AttributeUSDTagger.leakable_item_tag).Get()
                scene_tagging_data.add_leakable_item(prim_path, leakable_item_type)

            if prim.HasAttribute(AttributeUSDTagger.spillable_area_tag):
                prim_path = str(prim.GetPrimPath())
                spillable_area_type = prim.GetAttribute(AttributeUSDTagger.spillable_area_tag).Get()
                scene_tagging_data.add_spillable_area(prim_path, spillable_area_type)

        return scene_tagging_data

    def Write(self, scene_tagging_data: SceneTaggingData):  # noqa: C901, N802
        stage = omni.usd.get_context().get_stage()

        for prim in stage.Traverse():
            if prim.HasAttribute(AttributeUSDTagger.leakable_item_tag):
                prim.RemoveProperty(AttributeUSDTagger.leakable_item_tag)

            if prim.HasAttribute(AttributeUSDTagger.spillable_area_tag):
                prim.RemoveProperty(AttributeUSDTagger.spillable_area_tag)

        for item_type, prim_paths in scene_tagging_data.leakable_item_prim_paths_by_type.items():
            for prim_path in prim_paths:
                prim = stage.GetPrimAtPath(prim_path)
                if not prim:
                    carb.log_warn("Couldn't find prim at path: " + prim_path)
                    continue

                attr = prim.CreateAttribute(
                    AttributeUSDTagger.leakable_item_tag, Sdf.ValueTypeNames.String, custom=True
                )
                attr.Set(item_type)

        for item_type, prim_paths in scene_tagging_data.spillable_area_prim_paths_by_type.items():
            for prim_path in prim_paths:
                prim = stage.GetPrimAtPath(prim_path)
                if not prim:
                    carb.log_warn("Couldn't find prim at path: " + prim_path)
                    continue

                attr = prim.CreateAttribute(
                    AttributeUSDTagger.spillable_area_tag, Sdf.ValueTypeNames.String, custom=True
                )
                attr.Set(item_type)

    def prim_has_leakable_item_tag(self, prim_path):
        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(prim_path)
        if not prim:
            return False

        return prim.HasAttribute(AttributeUSDTagger.leakable_item_tag)

    def get_leakable_item_tag(self, prim_path):
        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(prim_path)
        if not prim:
            return None

        if not prim.HasAttribute(AttributeUSDTagger.leakable_item_tag):
            return None

        return prim.GetAttribute(AttributeUSDTagger.leakable_item_tag).Get()

    def prim_has_spillable_area_tag(self, prim_path):
        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(prim_path)
        if not prim:
            return False

        return prim.HasAttribute(AttributeUSDTagger.spillable_area_tag)

    def get_spillable_area_tag(self, prim_path):
        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(prim_path)
        if not prim:
            return None

        if not prim.HasAttribute(AttributeUSDTagger.spillable_area_tag):
            return None

        return prim.GetAttribute(AttributeUSDTagger.spillable_area_tag).Get()
