"""Test the node that inspects attribute bundles"""

import omni.graph.core as og

ogts = og.tests


# ======================================================================
class TestConversion(ogts.test_case_class()):
    """Run simple unit tests that exercises auto conversion of attribute"""

    # ----------------------------------------------------------------------
    async def test_auto_conv_on_load(self):

        # This file contains a graph which has a chain of nodes connected through extended attributes
        # The begining of this chain forces type resolution to double, but a float is required at the end of the chain
        # The test makes sure that the type is correctly resolved/restored on this final attribute
        (result, error) = await ogts.load_test_file("TestConversionOnLoad.usda", use_caller_subdirectory=True)
        self.assertTrue(result, f"{error}")

        await og.Controller.evaluate()

        easing_node = og.Controller.node("/World/PushGraph/easing_function")
        attr = og.Controller.attribute("inputs:alpha", easing_node)
        attr_type = attr.get_resolved_type()

        self.assertTrue(attr_type.base_type == og.BaseDataType.FLOAT)
