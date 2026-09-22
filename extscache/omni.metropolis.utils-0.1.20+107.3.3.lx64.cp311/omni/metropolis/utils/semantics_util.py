from typing import List, Tuple
import Semantics
import carb
from pxr import Usd, Sdf
from typing import Dict


class SemanticsUtils:

    METROSIM_INSTANCE_NAME = "Semantics_metrosim"

    @staticmethod
    def add_update_prim_metrosim_semantics(prims, type_value, name):
        with Sdf.ChangeBlock():
            for prim in prims:
                sem = None
                if prim.HasAPI(Semantics.SemanticsAPI, SemanticsUtils.METROSIM_INSTANCE_NAME):
                    carb.log_info(f"Will overwrite prim {prim.GetPrimPath()} metrosim semantic labels.")
                    sem = Semantics.SemanticsAPI.Get(prim, SemanticsUtils.METROSIM_INSTANCE_NAME)
                else:
                    sem = Semantics.SemanticsAPI.Apply(prim, SemanticsUtils.METROSIM_INSTANCE_NAME)
                    sem.CreateSemanticTypeAttr(SemanticsUtils.METROSIM_INSTANCE_NAME)
                    sem.CreateSemanticDataAttr(SemanticsUtils.METROSIM_INSTANCE_NAME)

                type_attr = sem.GetSemanticTypeAttr()
                type_attr.Set(type_value)
                data_attr = sem.GetSemanticDataAttr()
                data_attr.Set(name)

    @staticmethod
    def remove_prim_metrosim_semantics(prims):
        with Sdf.ChangeBlock():
            for prim in prims:
                if prim.HasAPI(Semantics.SemanticsAPI, SemanticsUtils.METROSIM_INSTANCE_NAME):
                    sem = Semantics.SemanticsAPI.Get(prim, SemanticsUtils.METROSIM_INSTANCE_NAME)
                    type_attr = sem.GetSemanticTypeAttr()
                    data_attr = sem.GetSemanticDataAttr()
                    if type_attr:
                        prim.RemoveProperty(type_attr.GetName())
                    if data_attr:
                        prim.RemoveProperty(data_attr.GetName())
                    prim.RemoveAPI(Semantics.SemanticsAPI, SemanticsUtils.METROSIM_INSTANCE_NAME)

    @staticmethod
    def get_prim_semantics(prim) -> List[Tuple[str, str]]:
        results = []
        if not prim.HasAPI(Semantics.SemanticsAPI):
            return []
        for prim_property in prim.GetProperties():
            if not Semantics.SemanticsAPI.IsSemanticsAPIPath(prim_property.GetPath()):
                continue
            instance_name = prim_property.SplitName()[1]
            sem = Semantics.SemanticsAPI.Get(prim, instance_name)
            type_attr = sem.GetSemanticTypeAttr()
            data_attr = sem.GetSemanticDataAttr()
            results.append((type_attr.Get(), data_attr.Get()))
        return results

    @staticmethod
    def add_update_semantics_timecode(
        prim, semantic_label: str, type_label: str = "class", suffix: str = "", time: float | None = None
    ) -> None:
        """Apply a semantic label to a prim or update an existing label

        Args:
            prim (Usd.Prim): Usd Prim to add or update semantics on
            semantic_label (str): The label we want to apply
            type_label (str): The type of semantic information we are specifying (default = "class")
            suffix (str): Additional suffix used to specify multiple semantic attribute names.
            By default the semantic attribute name is "Semantics", and to specify additional
            attributes a suffix can be provided. Simple string concatenation is used :"Semantics"
            + suffix (default = "")
            time (float): The time to set the semantic label at
        """
        with Sdf.ChangeBlock():
            if time is None:
                time = Usd.TimeCode.Default()
            # Apply or acquire the existing SemanticAPI
            semantic_api = Semantics.SemanticsAPI.Get(prim, suffix)
            if not semantic_api:
                semantic_api = Semantics.SemanticsAPI.Apply(prim, suffix)
                semantic_api.CreateSemanticTypeAttr()
                semantic_api.CreateSemanticDataAttr()

            type_attr = semantic_api.GetSemanticTypeAttr()
            data_attr = semantic_api.GetSemanticDataAttr()

            # Set the type and data for the SemanticAPI
            if type_label is not None:
                type_attr.Set(type_label, time)
            if semantic_label is not None:
                data_attr.Set(semantic_label, time)
        return

    @staticmethod
    def extract_children_semantic_labels(prim: Usd.Prim) -> Dict[str, List[Tuple[str, str]]]:
        """extract semantic labels attached on all sub prims for the parent prim"""
        path_to_semantics = {}
        for child_prim in Usd.PrimRange(prim):
            prim_path = str(child_prim.GetPrimPath())
            semantics_info = SemanticsUtils.get_prim_semantics(prim=child_prim)
            if semantics_info:
                path_to_semantics[prim_path] = semantics_info
        return path_to_semantics
