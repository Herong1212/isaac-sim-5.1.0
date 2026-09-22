import omni.graph.core as og
import omni.graph.core.tests as ogt


class TestBundleCow(ogt.OmniGraphTestCase):
    async def setUp(self):
        await super().setUp()

        self.graph = og.Controller.create_graph("/graph")
        self.context = self.graph.get_default_graph_context()
        self.factory = og.IBundleFactory.create()
        self.assertTrue(self.factory is not None)

        self.bundle1Name = "bundle1"
        self.bundle2Name = "bundle2"

        self.attr1Name = "attr1"
        self.attr1Type = og.Type(og.BaseDataType.BOOL, 1, 1)

        self.bundle1 = self.factory.create_bundle(self.context, self.bundle1Name)
        self.assertTrue(self.bundle1.valid)

        self.bundle2 = self.factory.create_bundle(self.context, self.bundle2Name)
        self.assertTrue(self.bundle2.valid)

    async def test_copy_and_remove_attribute_with_metadata(self):
        meta_name = "meta1"
        meta_type = og.Type(og.BaseDataType.INT, 1, 1)

        attr1 = self.bundle1.create_attribute(self.attr1Name, self.attr1Type)
        attr1.set([False, True])

        meta1 = self.bundle1.create_attribute_metadata(self.attr1Name, meta_name, meta_type)
        meta1.set([1, 2, 3, 4])

        # copy attribute with metadata
        self.bundle2.copy_attribute(attr1)

        # confirm data is accurate after setting it
        cpy_meta1 = self.bundle2.get_attribute_metadata_by_name(self.attr1Name, meta_name)
        cpy_meta1.set([4, 3, 2, 1])
        self.assertTrue((meta1.get() == [1, 2, 3, 4]).all())
        self.assertTrue((cpy_meta1.get() == [4, 3, 2, 1]).all())

        # remove copied attribute should leave original attribute intact
        self.bundle2.remove_attributes_by_name([self.attr1Name])

        # confirm source data is intact
        attr1 = self.bundle1.get_attribute_by_name(self.attr1Name)
        self.assertTrue(attr1.is_valid())
        self.assertTrue((attr1.get() == [False, True]).all())

        self.assertEqual(self.bundle1.get_attribute_metadata_count(self.attr1Name), 1)
        meta1 = self.bundle1.get_attribute_metadata_by_name(self.attr1Name, meta_name)
        self.assertTrue(meta1.is_valid())
        self.assertTrue((meta1.get() == [1, 2, 3, 4]).all())

        # confirm removed metadata is gone
        self.assertEqual(self.bundle2.get_attribute_metadata_count(self.attr1Name), 0)
        attr1 = self.bundle2.get_attribute_metadata_by_name(self.attr1Name, meta_name)
        self.assertFalse(attr1.is_valid())

    async def test_copy_bundle_and_remove_attribute_with_metadata(self):
        meta_name = "meta1"
        meta_type = og.Type(og.BaseDataType.INT, 1, 1)

        attr1 = self.bundle1.create_attribute(self.attr1Name, self.attr1Type)
        attr1.set([False, True])

        meta1 = self.bundle1.create_attribute_metadata(self.attr1Name, meta_name, meta_type)
        meta1.set([1, 2, 3, 4])

        # copy attribute with metadata
        self.bundle2.copy_bundle(self.bundle1)

        #
        # Do NOT materialize attribute - keep shallow copy of entire bundle
        #

        # remove copied attribute should leave original attribute intact
        self.bundle2.remove_attributes_by_name([self.attr1Name])

        # confirm source data is intact
        attr1 = self.bundle1.get_attribute_by_name(self.attr1Name)
        self.assertTrue(attr1.is_valid())
        self.assertTrue((attr1.get() == [False, True]).all())

        self.assertEqual(self.bundle1.get_attribute_metadata_count(self.attr1Name), 1)
        meta1 = self.bundle1.get_attribute_metadata_by_name(self.attr1Name, meta_name)
        self.assertTrue(meta1.is_valid())
        self.assertTrue((meta1.get() == [1, 2, 3, 4]).all())

        # confirm copied metadata is gone
        self.assertEqual(self.bundle2.get_attribute_metadata_count(self.attr1Name), 0)
        attr1 = self.bundle2.get_attribute_metadata_by_name(self.attr1Name, meta_name)
        self.assertFalse(attr1.is_valid())

    async def test_remove_attribute_metadata(self):
        attr1 = self.bundle1.create_attribute(self.attr1Name, self.attr1Type)
        attr1.set([False, True])

        meta_name1 = "meta1"
        meta_type1 = og.Type(og.BaseDataType.INT, 1, 1)
        meta1 = self.bundle1.create_attribute_metadata(self.attr1Name, meta_name1, meta_type1)
        meta1.set([1, 2, 3, 4])

        meta_name2 = "meta2"
        meta_type2 = og.Type(og.BaseDataType.BOOL, 1, 1)
        meta1 = self.bundle1.create_attribute_metadata(self.attr1Name, meta_name2, meta_type2)
        meta1.set([False, True])

        # copy attribute with metadata
        self.bundle2.copy_bundle(self.bundle1)

        #
        # Materialize metadata for bundle2!
        #

        self.bundle2.remove_attribute_metadata(self.attr1Name, (meta_name1))

        # check if source is intact
        self.assertEqual(self.bundle1.get_attribute_metadata_count(self.attr1Name), 2)
        names = self.bundle1.get_attribute_metadata_names(self.attr1Name)
        self.assertEqual(len(names), 2)
        self.assertTrue(meta_name1 in names)
        self.assertTrue(meta_name2 in names)

        # check if shallow copied metadata bundle has been materialized
        self.assertEqual(self.bundle2.get_attribute_metadata_count(self.attr1Name), 1)
        names = self.bundle2.get_attribute_metadata_names(self.attr1Name)
        self.assertEqual(len(names), 1)
        self.assertFalse(meta_name1 in names)
        self.assertTrue(meta_name2 in names)

    async def test_copy_child_bundle(self):
        org_child = self.bundle1.create_child_bundle("org_child")

        # create bundle for modifications
        mod_bundle = self.factory.create_bundle(self.context, "mod_bundle")
        mod_child = mod_bundle.copy_child_bundle(org_child)

        mod_child.create_attribute("attr", og.Type(og.BaseDataType.BOOL, 1, 1))

        # original child can not change, but modified change must
        self.assertEqual(org_child.get_attribute_count(), 0)
        self.assertEqual(mod_child.get_attribute_count(), 1)

    async def test_attribute_resize(self):
        src_bundle = self.factory.create_bundle(self.context, "src_bundle")
        src_attrib = src_bundle.create_attribute(
            "attrib",
            og.Type(
                og.BaseDataType.FLOAT,
                tuple_count=1,
                array_depth=1,
            ),
            element_count=100,
        )

        dst_bundle = self.factory.create_bundle(self.context, "dst_bundle")
        dst_bundle.copy_bundle(src_bundle)

        self.assertEqual(dst_bundle.get_attribute_count(), 1)

        dst_attrib = dst_bundle.create_attribute(
            "attrib",
            og.Type(
                og.BaseDataType.FLOAT,
                tuple_count=1,
                array_depth=1,
            ),
            element_count=200,
        )

        self.assertEqual(src_attrib.size(), 100)
        self.assertEqual(dst_attrib.size(), 200)
