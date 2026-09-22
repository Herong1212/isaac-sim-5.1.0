import omni.graph.core as og
import omni.graph.core.tests as ogt


class TestBundleAttributeAccess(ogt.OmniGraphTestCase):
    async def setUp(self):
        await super().setUp()

        self.graph = og.Controller.create_graph("/graph")
        self.context = self.graph.get_default_graph_context()
        self.factory = og.IBundleFactory.create()
        self.assertTrue(self.factory is not None)

        self.bundle1Name = "bundle1"
        self.rwBundle = self.factory.create_bundle(self.context, self.bundle1Name)
        self.assertTrue(self.rwBundle.valid)

        self.attr1Name = "attr1"
        self.tupleType = og.Type(og.BaseDataType.INT, 2, 0)
        self.arrayType = og.Type(og.BaseDataType.INT, 1, 1)
        self.arrayTupleType = og.Type(og.BaseDataType.INT, 2, 1)

    async def test_tuple_write_permissions(self):
        attr = self.rwBundle.create_attribute(self.attr1Name, self.tupleType)
        with self.assertRaises(ValueError):
            data = attr.as_read_only().get()
            data[0] = 42  # writing to data will throw

        data = attr.get()
        data[0] = 42  # writing to data will not throw

    async def test_array_type_write_permissions(self):
        attr = self.rwBundle.create_attribute(self.attr1Name, self.arrayType)

        # GPU = False, Write = True
        # calling get_array will throw
        with self.assertRaises(ValueError):
            attr.as_read_only().get_array(False, True, 10)

        # GPU = False, Write = False
        # calling get_array will not throw
        attr.as_read_only().get_array(False, False, 10)

    async def test_array_of_tuple_write_permissions(self):
        attr = self.rwBundle.create_attribute(self.attr1Name, self.arrayTupleType)

        # GPU = False, Write = True
        # calling get_array will throw
        with self.assertRaises(ValueError):
            attr.as_read_only().get_array(False, True, 10)

        # GPU = False, Write = False
        # calling get_array will not throw
        attr.get_array(False, False, 10)
