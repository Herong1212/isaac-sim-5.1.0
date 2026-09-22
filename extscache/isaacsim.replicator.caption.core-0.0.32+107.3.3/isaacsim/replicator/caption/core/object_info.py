from typing import Any

import carb


class NodeInfo:
    """Store raw information related to target object"""

    def __init__(self, label, prim_path: str = "", properties_dict: dict[str, Any] | None = None):
        self.label: str = label  # object's semantic label
        self.prim_path: str = prim_path  # object's prim path
        if properties_dict is None:
            self.properties_dict = {}
        else:
            self.properties_dict = properties_dict

    def get_label(self) -> str:
        return self.label

    def get_prim_path(self) -> str:
        return self.prim_path

    def get_all_properties(self) -> dict[str:Any]:
        """get this objects attributes"""
        return self.properties_dict

    def update_annotator_data(self, annotator_name, data):
        """store annotator info base on annotator's name"""
        self.properties_dict[annotator_name] = data
        pass

    def get_all_info(self) -> dict[str, Any]:
        """helper method to get object information, return data into a dictionary"""
        return {"label": self.label, "prim_path": self.prim_path, "annotators": self.properties_dict}

    def get_property_info_with_key(self, property_name: str):
        """fetch property with attribute name"""
        if property_name not in self.properties_dict:
            carb.log_info(
                "Warning as message:: Node {node_prim_path} does not have: attribute :  [{annotator_name}].".format(
                    node_prim_path=self.prim_path, annotator_name=property_name
                )
            )
            return None
        else:
            return self.properties_dict[property_name]
