import carb
import omni

from pxr import Sdf


# from omni.metropolis.utils.file_util import JSONFileUtil


class SceneTaggingData:
    def __init__(self):
        self.loose_item_prim_paths_by_type = {}
        self.topple_destinations_by_type = {}

    def add_loose_item(self, prim_path: str, item_type: str):
        self.loose_item_prim_paths_by_type.setdefault(item_type, set()).add(prim_path)

    def add_loose_items(self, prim_paths: list, item_type: str):
        self.loose_item_prim_paths_by_type.setdefault(item_type, set()).update(prim_paths)

    def remove_loose_item(self, prim_path: str, item_type: str):
        if item_type not in self.loose_item_prim_paths_by_type:
            return
        self.loose_item_prim_paths_by_type[item_type].discard(prim_path)

    def add_topple_destination(self, prim_path: str, item_type: str):
        self.topple_destinations_by_type.setdefault(item_type, set()).add(prim_path)

    def remove_topple_destination(self, prim_path: str, item_type: str):
        if item_type not in self.topple_destinations_by_type:
            return
        self.topple_destinations_by_type[item_type].discard(prim_path)


# class JSONTagger:
#     """reads/writes SceneTaggingData from/to JSON files"""

#     loose_items_key = "loose_items"
#     containers_key = "containers"
#     loose_item_collidables_key = "loose_item_collidables"
#     loose_item_collidable_exempt_key = "loose_item_collidable_exempt"

#     def __init__(self, filename: str):
#         self._filename: str = filename

#     def Read(self) -> SceneTaggingData:
#         filename: str = self._filename
#         json_data = JSONFileUtil.load_from_file(filename)
#         if not json_data:
#             carb.log_error("Loading custom commands json fails.")
#             return

#         required_keys = [
#             JSONTagger.loose_items_key,
#             JSONTagger.containers_key,
#             JSONTagger.loose_item_collidables_key,
#             JSONTagger.loose_item_collidable_exempt_key,
#         ]
#         for required_key in required_keys:
#             if not required_key in json_data:
#                 carb.log_error("JSON data from " + filename + " missing required field: " + required_key)

#         scene_tagging_data = SceneTaggingData()

#         scene_tagging_data.loose_item_prim_paths.update(json_data[JSONTagger.loose_items_key])
#         scene_tagging_data.container_prim_paths.update(json_data[JSONTagger.containers_key])
#         scene_tagging_data.loose_item_collidable_paths.update(json_data[JSONTagger.loose_item_collidables_key])
#         scene_tagging_data.loose_item_collidable_exempt_paths.update(
#             json_data[JSONTagger.loose_item_collidable_exempt_key]
#         )

#         return scene_tagging_data

#     def Write(self, scene_tagging_data: SceneTaggingData):
#         json_data = dict()

#         json_data[JSONTagger.loose_items_key] = list(scene_tagging_data.loose_item_prim_paths)
#         json_data[JSONTagger.containers_key] = list(scene_tagging_data.container_prim_paths)
#         json_data[JSONTagger.loose_item_collidables_key] = list(scene_tagging_data.loose_item_collidable_paths)
#         json_data[JSONTagger.loose_item_collidable_exempt_key] = list(
#             scene_tagging_data.loose_item_collidable_exempt_paths
#         )

#         filename = self._filename
#         JSONFileUtil.write_to_file(filename, json_data)


class AttributeUSDTagger:
    """reads/writes SceneTaggingData from/to USD Attributes"""

    loose_item_tag: str = "IsaacSim_Replicator_Incident_Attr:LooseItem"
    loose_item_types: list = ["NavMesh", "RandomDir", "ClosestWaypoint"]

    topple_destination_tag: str = "IsaacSim_Replicator_Incident_Attr:ToppleDestination"
    topple_destination_types: list = ["Sphere", "Cube"]

    def Read(self) -> SceneTaggingData:  # noqa: C901, N802
        scene_tagging_data = SceneTaggingData()

        stage = omni.usd.get_context().get_stage()

        for prim in stage.Traverse():
            if prim.HasAttribute(AttributeUSDTagger.loose_item_tag):
                prim_path = str(prim.GetPrimPath())
                loose_item_type = prim.GetAttribute(AttributeUSDTagger.loose_item_tag).Get()
                scene_tagging_data.add_loose_item(prim_path, loose_item_type)

            if prim.HasAttribute(AttributeUSDTagger.topple_destination_tag):
                prim_path = str(prim.GetPrimPath())
                topple_destination_type = prim.GetAttribute(AttributeUSDTagger.topple_destination_tag).Get()
                scene_tagging_data.add_topple_destination(prim_path, topple_destination_type)

        return scene_tagging_data

    def Write(self, scene_tagging_data: SceneTaggingData):  # noqa: C901, N802
        stage = omni.usd.get_context().get_stage()

        for prim in stage.Traverse():
            if prim.HasAttribute(AttributeUSDTagger.loose_item_tag):
                prim.RemoveProperty(AttributeUSDTagger.loose_item_tag)
            if prim.HasAttribute(AttributeUSDTagger.topple_destination_tag):
                prim.RemoveProperty(AttributeUSDTagger.topple_destination_tag)

        for item_type, prim_paths in scene_tagging_data.loose_item_prim_paths_by_type.items():
            for prim_path in prim_paths:
                prim = stage.GetPrimAtPath(prim_path)
                if not prim:
                    carb.log_warn("Couldn't find prim at path: " + prim_path)
                    continue

                attr = prim.CreateAttribute(AttributeUSDTagger.loose_item_tag, Sdf.ValueTypeNames.String, custom=True)
                attr.Set(item_type)

        for item_type, prim_paths in scene_tagging_data.topple_destinations_by_type.items():
            for prim_path in prim_paths:
                prim = stage.GetPrimAtPath(prim_path)
                if not prim:
                    carb.log_warn("Couldn't find prim at path: " + prim_path)
                    continue

                attr = prim.CreateAttribute(
                    AttributeUSDTagger.topple_destination_tag, Sdf.ValueTypeNames.String, custom=True
                )
                attr.Set(item_type)

    def prim_has_loose_item_tag(self, prim_path: str) -> bool:
        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(prim_path)
        if not prim:
            return False

        return prim.HasAttribute(AttributeUSDTagger.loose_item_tag)

    def get_loose_item_tag(self, prim_path: str) -> str | None:
        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(prim_path)
        if not prim:
            return None

        if not prim.HasAttribute(AttributeUSDTagger.loose_item_tag):
            return None

        return prim.GetAttribute(AttributeUSDTagger.loose_item_tag).Get()
