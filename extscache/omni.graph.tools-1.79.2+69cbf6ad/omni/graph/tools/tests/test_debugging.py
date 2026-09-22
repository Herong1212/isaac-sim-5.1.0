"""Tests that exercise the debugging utilities"""

import omni.graph.tools as ogt
import omni.kit.test


class TestDebugging(omni.kit.test.AsyncTestCase):
    # --------------------------------------------------------------------------------------------------------------
    async def test_destroy_property(self):
        """Test the destroy_property method"""

        class TestClass:
            """
            Trivial test class that contains member objects of various types along with an explicitly-defined
            deletion method.
            """

            def __init__(self):
                self._empty_object = None
                self._my_name = "TestClass"
                self._my_list = ["string_0", "string_1", ["string_2", "string_3"], {"key_0": 0}]
                self._my_dict = {"key_0": 0, "key_1": 1, "key_2": ["string_0", "string_1"], "key_3": {"key_4": 2}}

            def __del__(self):
                ogt.destroy_property(self, "_empty_object")
                ogt.destroy_property(self, "_my_name")
                ogt.destroy_property(self, "_my_list")
                ogt.destroy_property(self, "_my_dict")

        _ = TestClass()
