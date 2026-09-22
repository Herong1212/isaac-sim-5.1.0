from omni.kit.property.usd.custom_layout_helper import CustomLayoutFrame, CustomLayoutGroup, CustomLayoutProperty


class CustomLayout:
    def __init__(self, compute_node_widget):
        # print("\nInside template_omni.genproc.ImportUSDPrim.py, CustomLayout:__init__\n");
        # Enable template
        self.enable = True
        self.compute_node_widget = compute_node_widget
        self.compute_node_widget.get_bundles()

        bundle_items_iter = iter(self.compute_node_widget.bundles.items())
        _ = next(bundle_items_iter)[1][0].get_attribute_names_and_types()

    def apply(self, props):
        frame = CustomLayoutFrame(hide_extra=True)

        with frame:
            with CustomLayoutGroup("Import Parameters"):
                CustomLayoutProperty("inputs:prim", "Prim(s) to Import")
                CustomLayoutProperty("inputs:usdTimecode", "Timecode")
                CustomLayoutProperty("inputs:keepPrimsSeparate", "Allow Multiple Prims")
                CustomLayoutProperty("inputs:importTransform", "Import Transforms")
                CustomLayoutProperty("inputs:computeBoundingBox", "Compute Bounding Boxes")
                CustomLayoutProperty("inputs:importType", "Import Types")
                CustomLayoutProperty("inputs:importPath", "Import Paths")
                CustomLayoutProperty("inputs:importTime", "Import Time")
            with CustomLayoutGroup("Attributes"):
                CustomLayoutProperty("inputs:importAttributes", "Import Attributes")
                CustomLayoutProperty("inputs:attrNamesToImport", "Attributes to Import")
                CustomLayoutProperty("inputs:renameAttributes", "Rename Attributes")
                CustomLayoutProperty("inputs:inputAttrNames", "Attributes to Rename")
                CustomLayoutProperty("inputs:outputAttrNames", "New Attribute Names")
                CustomLayoutProperty("inputs:applyTransform", "Transform Attributes")
                CustomLayoutProperty("inputs:timeVaryingAttributes", "Time Varying Attributes")
                CustomLayoutProperty("inputs:importPrimvarMetadata", "Import Metadata")
                CustomLayoutProperty("inputs:applySkelBinding", "Apply SkelBinding")

        return frame.apply(props)
