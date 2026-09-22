import os
import omni.kit.test
import omni.graph.core as og
import omni.graph.core.tests as ogts
from omni.graph.core.tests.omnigraph_test_utils import _TestGraphAndNode
from omni.graph.core.tests.omnigraph_test_utils import _test_clear_scene
from omni.graph.core.tests.omnigraph_test_utils import _test_setup_scene
from omni.graph.core.tests.omnigraph_test_utils import _test_verify_scene


class TestOgn(ogts.OmniGraphTestCase):

    async def test_data_access(self):
        test_file_name = "OgnExportUSDPrimTemplate.usda"
        usd_path = os.path.join(os.path.dirname(__file__), "usd", test_file_name)
        if not os.path.exists(usd_path):  # pragma: no cover
            self.assertTrue(False, f"{usd_path} not found for loading test")
        (result, error) = await ogts.load_test_file(usd_path)
        self.assertTrue(result, f'{error} on {usd_path}')
        test_node = og.Controller.node("/TestGraph/Template_omni_graph_ExportUSDPrim")
        self.assertTrue(test_node.is_valid())
        node_type_name = test_node.get_type_name()
        self.assertEqual(og.GraphRegistry().get_node_type_version(node_type_name), 1)

        def _attr_error(attribute: og.Attribute, usd_test: bool) -> str:  # pragma no cover
            test_type = "USD Load" if usd_test else "Database Access"
            return f"{node_type_name} {test_type} Test - {attribute.get_name()} value error"


        self.assertTrue(test_node.get_attribute_exists("inputs:applyTransform"))
        attribute = test_node.get_attribute("inputs:applyTransform")
        self.assertTrue(attribute.is_valid())
        expected_value = False
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:attrNamesToExport"))
        attribute = test_node.get_attribute("inputs:attrNamesToExport")
        self.assertTrue(attribute.is_valid())
        expected_value = ""
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:bundle"))
        attribute = test_node.get_attribute("inputs:bundle")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("inputs:excludedAttrNames"))
        attribute = test_node.get_attribute("inputs:excludedAttrNames")
        self.assertTrue(attribute.is_valid())
        expected_value = ""
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:exportToRootLayer"))
        attribute = test_node.get_attribute("inputs:exportToRootLayer")
        self.assertTrue(attribute.is_valid())
        expected_value = True
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:inputAttrNames"))
        attribute = test_node.get_attribute("inputs:inputAttrNames")
        self.assertTrue(attribute.is_valid())
        expected_value = ""
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:layerName"))
        attribute = test_node.get_attribute("inputs:layerName")
        self.assertTrue(attribute.is_valid())
        expected_value = ""
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:onlyExportToExisting"))
        attribute = test_node.get_attribute("inputs:onlyExportToExisting")
        self.assertTrue(attribute.is_valid())
        expected_value = False
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:outputAttrNames"))
        attribute = test_node.get_attribute("inputs:outputAttrNames")
        self.assertTrue(attribute.is_valid())
        expected_value = ""
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:primPathFromBundle"))
        attribute = test_node.get_attribute("inputs:primPathFromBundle")
        self.assertTrue(attribute.is_valid())
        expected_value = False
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:removeMissingAttrs"))
        attribute = test_node.get_attribute("inputs:removeMissingAttrs")
        self.assertTrue(attribute.is_valid())
        expected_value = False
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:renameAttributes"))
        attribute = test_node.get_attribute("inputs:renameAttributes")
        self.assertTrue(attribute.is_valid())
        expected_value = False
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:timeVaryingAttributes"))
        attribute = test_node.get_attribute("inputs:timeVaryingAttributes")
        self.assertTrue(attribute.is_valid())
        expected_value = False
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("inputs:usdTimecode"))
        attribute = test_node.get_attribute("inputs:usdTimecode")
        self.assertTrue(attribute.is_valid())
        expected_value = 0
        actual_value = og.Controller.get(attribute)
        ogts.verify_values(expected_value, actual_value, _attr_error(attribute, True))

        self.assertTrue(test_node.get_attribute_exists("state:prevApplyTransform"))
        attribute = test_node.get_attribute("state:prevApplyTransform")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevAttrNamesToExport"))
        attribute = test_node.get_attribute("state:prevAttrNamesToExport")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevBundleDirtyID"))
        attribute = test_node.get_attribute("state:prevBundleDirtyID")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevExcludedAttrNames"))
        attribute = test_node.get_attribute("state:prevExcludedAttrNames")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevExportToRootLayer"))
        attribute = test_node.get_attribute("state:prevExportToRootLayer")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevInputAttrNames"))
        attribute = test_node.get_attribute("state:prevInputAttrNames")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevLayerName"))
        attribute = test_node.get_attribute("state:prevLayerName")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevOnlyExportToExisting"))
        attribute = test_node.get_attribute("state:prevOnlyExportToExisting")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevOutputAttrNames"))
        attribute = test_node.get_attribute("state:prevOutputAttrNames")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevPrimDirtyIDs"))
        attribute = test_node.get_attribute("state:prevPrimDirtyIDs")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevPrimPathFromBundle"))
        attribute = test_node.get_attribute("state:prevPrimPathFromBundle")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevRemoveMissingAttrs"))
        attribute = test_node.get_attribute("state:prevRemoveMissingAttrs")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevRenameAttributes"))
        attribute = test_node.get_attribute("state:prevRenameAttributes")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevTimeVaryingAttributes"))
        attribute = test_node.get_attribute("state:prevTimeVaryingAttributes")
        self.assertTrue(attribute.is_valid())

        self.assertTrue(test_node.get_attribute_exists("state:prevUsdTimecode"))
        attribute = test_node.get_attribute("state:prevUsdTimecode")
        self.assertTrue(attribute.is_valid())
