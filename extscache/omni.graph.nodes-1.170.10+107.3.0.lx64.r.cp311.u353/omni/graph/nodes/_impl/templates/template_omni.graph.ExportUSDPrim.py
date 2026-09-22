from omni.kit.property.usd.custom_layout_helper import CustomLayoutFrame, CustomLayoutGroup, CustomLayoutProperty


class CustomLayout:
    def __init__(self, compute_node_widget):
        # print("\nInside template_omni.genproc.ExportUSDPrim.py, CustomLayout:__init__\n");
        # Enable template
        self.enable = True
        self.compute_node_widget = compute_node_widget
        self.compute_node_widget.get_bundles()

        bundle_items_iter = iter(self.compute_node_widget.bundles.items())
        _ = next(bundle_items_iter)[1][0].get_attribute_names_and_types()

    def apply(self, props):
        frame = CustomLayoutFrame(hide_extra=True)

        with frame:
            with CustomLayoutGroup("Export Parameters"):
                CustomLayoutProperty("outputs:prim", "Prim(s) to Export to")
                CustomLayoutProperty("inputs:bundle", "Source Data")
                CustomLayoutProperty("inputs:primPathFromBundle", "Export to primPath from Source")
                CustomLayoutProperty("inputs:exportToRootLayer", "Export to Root Layer")
                CustomLayoutProperty("inputs:layerName", "Layer Name")
            with CustomLayoutGroup("Attributes"):
                CustomLayoutProperty("inputs:attrNamesToExport", "Attributes to Export")
                CustomLayoutProperty("inputs:onlyExportToExisting", "Only Export Existing")
                CustomLayoutProperty("inputs:removeMissingAttrs", "Remove Missing")
                CustomLayoutProperty("inputs:renameAttributes", "Rename Attributes")
                CustomLayoutProperty("inputs:inputAttrNames", "Attributes to Rename")
                CustomLayoutProperty("inputs:outputAttrNames", "New Attribute Names")
                CustomLayoutProperty("inputs:excludedAttrNames", "Attributes to Exclude")
                CustomLayoutProperty("inputs:applyTransform", "Transform Attributes")
                CustomLayoutProperty("inputs:timeVaryingAttributes", "Time-varying Attributes")
                CustomLayoutProperty("inputs:usdTimecode", "USD Time")

        return frame.apply(props)


# print("\nIn template_omni.graph.ExportUSDPrim.py\n")
