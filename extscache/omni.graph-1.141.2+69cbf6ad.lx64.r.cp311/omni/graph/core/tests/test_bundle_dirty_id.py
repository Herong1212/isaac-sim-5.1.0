import omni.graph.core as og
import omni.graph.core.tests as ogt


class BundleTestSetup(ogt.OmniGraphTestCase):
    async def setUp(self):
        """Set up  test environment, to be torn down when done"""
        await super().setUp()

        self.graph = og.Controller.create_graph("/graph")
        self.context = self.graph.get_default_graph_context()
        self.factory = og.IBundleFactory.create()
        self.assertTrue(self.factory is not None)
        self.dirty = og._og_unstable.IDirtyID2.create(self.context)  # noqa: PLW0212
        self.assertTrue(self.dirty is not None)

        # bundle paths
        self.bundle2Name = "bundle2"
        self.bundle3Name = "bundle3"

        self.attr1Name = "attr1"
        self.attr1Type = og.Type(og.BaseDataType.INT)

        self.attr2Name = "attr2"
        self.attr2Type = og.Type(og.BaseDataType.FLOAT)

        self.attr3Name = "attr3"
        self.attr3Type = og.Type(og.BaseDataType.INT, 1, 1)

        self.attr4Name = "attr4"
        self.attr4Type = og.Type(og.BaseDataType.INT, 2, 0)


class TestBundleDirtyID(BundleTestSetup):
    async def setUp(self):
        """Set up  test environment, to be torn down when done"""
        await super().setUp()

    async def test_create_bundle(self):
        bundle1 = self.factory.create_bundle(self.context, "bundle1")
        bundle2 = self.factory.create_bundle(self.context, "bundle2")
        self.dirty.setup(bundle1, True)
        self.dirty.setup(bundle2, True)

        ids = self.dirty.get([bundle1, bundle2])
        self.assertTrue(self.dirty.is_valid(ids[0]))
        self.assertTrue(self.dirty.is_valid(ids[1]))
        self.assertNotEqual(ids[0], ids[1])

    async def test_create_attribute(self):
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.dirty.setup(bundle, True)
        ids0 = self.dirty.get([bundle])
        bundle.create_attribute(self.attr1Name, self.attr1Type)
        ids1 = self.dirty.get([bundle])
        self.assertTrue(self.dirty.is_valid(ids0[0]))
        self.assertTrue(self.dirty.is_valid(ids1[0]))
        self.assertNotEqual(ids0[0], ids1[0])

    async def test_create_child_bundle(self):
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.dirty.setup(bundle, True)

        ids0 = self.dirty.get([bundle])
        self.assertTrue(self.dirty.is_valid(ids0[0]))

        bundle.create_child_bundle(self.bundle2Name)
        ids1 = self.dirty.get([bundle])
        self.assertTrue(self.dirty.is_valid(ids1[0]))
        self.assertNotEqual(ids0[0], ids1[0])

    async def test_remove_attribute(self):
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.dirty.setup(bundle, True)

        bundle.create_attribute(self.attr1Name, self.attr1Type)
        ids0 = self.dirty.get([bundle])
        self.assertTrue(self.dirty.is_valid(ids0[0]))

        bundle.remove_attribute(self.attr1Name)
        ids1 = self.dirty.get([bundle])
        self.assertTrue(self.dirty.is_valid(ids1[0]))
        self.assertNotEqual(ids0[0], ids1[0])

    async def test_remove_child_bundles(self):
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.dirty.setup(bundle, True)

        bundle2 = bundle.create_child_bundle("child")

        ids0 = self.dirty.get([bundle])
        self.assertTrue(self.dirty.is_valid(ids0[0]))

        bundle.remove_child_bundle(bundle2)
        ids1 = self.dirty.get([bundle])
        self.assertTrue(self.dirty.is_valid(ids1[0]))
        self.assertNotEqual(ids0[0], ids1[0])

    async def test_clear_contents(self):
        """Test if clearing bundle results with new dirty id"""
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.dirty.setup(bundle, True)

        ids0 = self.dirty.get([bundle])
        self.assertTrue(self.dirty.is_valid(ids0[0]))

        bundle.clear_contents()
        ids1 = self.dirty.get([bundle])
        self.assertTrue(self.dirty.is_valid(ids1[0]))
        self.assertNotEqual(ids0[0], ids1[0])

    async def test_copy_attribute(self):
        bundle1 = self.factory.create_bundle(self.context, "bundle1")
        bundle2 = self.factory.create_bundle(self.context, "bundle2")
        self.dirty.setup(bundle1, True)
        self.dirty.setup(bundle2, True)

        attr1 = bundle1.create_attribute(self.attr1Name, self.attr1Type)
        ids0 = self.dirty.get([bundle2])
        self.assertTrue(self.dirty.is_valid(ids0[0]))

        bundle2.copy_attribute(attr1)
        ids1 = self.dirty.get([bundle2])
        self.assertTrue(self.dirty.is_valid(ids1[0]))
        self.assertNotEqual(ids0[0], ids1[0])

    async def test_copy_child_bundle(self):
        """Test if CoW reference is resolved."""
        bundle1 = self.factory.create_bundle(self.context, "bundle1")
        bundle2 = self.factory.create_bundle(self.context, "bundle2")
        self.dirty.setup(bundle1, True)
        self.dirty.setup(bundle2, True)

        ids0 = self.dirty.get([bundle1])
        self.assertTrue(self.dirty.is_valid(ids0[0]))

        bundle1.copy_child_bundle(self.bundle2Name, bundle2)
        ids1 = self.dirty.get([bundle1])
        self.assertTrue(self.dirty.is_valid(ids1[0]))
        self.assertNotEqual(ids0[0], ids1[0])

    async def test_copy_bundle(self):
        """Copying bundle creates a shallow copy - a reference.
        To obtain the dirty id the reference needs to be resolved"""
        bundle1 = self.factory.create_bundle(self.context, "bundle1")
        bundle2 = self.factory.create_bundle(self.context, "bundle2")
        self.dirty.setup(bundle1, True)
        self.dirty.setup(bundle2, True)

        ids0 = self.dirty.get([bundle1, bundle2])
        self.assertNotEqual(ids0[0], ids0[1])
        self.assertTrue(self.dirty.is_valid(ids0[0]))
        self.assertTrue(self.dirty.is_valid(ids0[1]))

        bundle2.copy_bundle(bundle1)
        ids1 = self.dirty.get([bundle1, bundle2])
        self.assertTrue(self.dirty.is_valid(ids1[0]))
        self.assertTrue(self.dirty.is_valid(ids1[1]))
        self.assertEqual(ids1[0], ids1[1])

    async def test_get_attribute_by_name(self):
        """Getting writable attribute data handle does not change dirty id.
        Only writing to an attribute triggers id to be changed."""
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.dirty.setup(bundle, True)

        bundle.create_attribute(self.attr1Name, self.attr1Type)
        ids0 = self.dirty.get([bundle])
        self.assertTrue(self.dirty.is_valid(ids0[0]))

        bundle.get_attribute_by_name(self.attr1Name)
        ids1 = self.dirty.get([bundle])
        self.assertTrue(self.dirty.is_valid(ids1[0]))
        self.assertEqual(ids0[0], ids1[0])

    async def test_get_child_bundle_by_name(self):
        """Getting writable bundle handle does not change dirty id.
        Only creating/removing attributes and children triggers id to be
        changed."""
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.dirty.setup(bundle, True)

        bundle.create_child_bundle(self.bundle2Name)
        ids0 = self.dirty.get([bundle])
        self.assertTrue(self.dirty.is_valid(ids0[0]))

        bundle.get_child_bundle_by_name(self.bundle2Name)
        ids1 = self.dirty.get([bundle])
        self.assertTrue(self.dirty.is_valid(ids1[0]))
        self.assertEqual(ids0[0], ids1[0])

    async def test_get_simple_attribute_data(self):
        """Getting simple attribute data should not change dirty id"""
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.dirty.setup(bundle, True)

        attr = bundle.create_attribute(self.attr1Name, self.attr1Type)
        attr.set(42)
        ids0 = self.dirty.get([bundle])
        self.assertTrue(self.dirty.is_valid(ids0[0]))

        self.assertEqual(attr.as_read_only().get(), 42)
        ids1 = self.dirty.get([bundle])
        self.assertTrue(self.dirty.is_valid(ids1[0]))
        self.assertEqual(ids0[0], ids1[0])

    async def test_get_array_attribute_data(self):
        """Getting array attribute data should not change dirty id"""
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.dirty.setup(bundle, True)

        attr = bundle.create_attribute(self.attr3Name, self.attr3Type)
        attr.set([42])
        ids0 = self.dirty.get([bundle])
        self.assertTrue(self.dirty.is_valid(ids0[0]))

        self.assertEqual(attr.as_read_only().get()[0], 42)
        ids1 = self.dirty.get([bundle])
        self.assertTrue(self.dirty.is_valid(ids1[0]))
        self.assertEqual(ids0[0], ids1[0])

    async def _get_array_rw_attribute_data(self, on_gpu):
        """Getting array attribute data for read-write"""
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.dirty.setup(bundle, True)

        attr = bundle.create_attribute(self.attr3Name, self.attr3Type)
        attr.set([42])
        ids0 = self.dirty.get([bundle])
        self.assertTrue(self.dirty.is_valid(ids0[0]))

        # no bump
        attr.as_read_only().get_array(on_gpu=on_gpu, get_for_write=False, reserved_element_count=1)
        ids1 = self.dirty.get([bundle])
        self.assertTrue(self.dirty.is_valid(ids1[0]))
        self.assertEqual(ids0[0], ids1[0])

        # bump
        attr.get_array(on_gpu=on_gpu, get_for_write=True, reserved_element_count=1)
        ids1 = self.dirty.get([bundle])
        self.assertTrue(self.dirty.is_valid(ids1[0]))
        self.assertNotEqual(ids0[0], ids1[0])

    async def test_get_array_attribute_data_cpu(self):
        await self._get_array_rw_attribute_data(False)

    async def test_get_array_attribute_data_gpu(self):
        await self._get_array_rw_attribute_data(True)

    async def test_resize_array_attribute(self):
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.dirty.setup(bundle, True)

        attr = bundle.create_attribute(self.attr3Name, self.attr3Type)
        ids0 = self.dirty.get([bundle])
        self.assertTrue(self.dirty.is_valid(ids0[0]))

        # no bump
        attr.size()
        ids1 = self.dirty.get([bundle])
        self.assertTrue(self.dirty.is_valid(ids1[0]))
        self.assertEqual(ids0[0], ids1[0])

        # bump
        attr.resize(10)
        ids1 = self.dirty.get([bundle])
        self.assertTrue(self.dirty.is_valid(ids1[0]))
        self.assertNotEqual(ids0[0], ids1[0])

    async def test_get_tuple_attribute_data(self):
        """Getting array attribute data should not change dirty id"""
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.dirty.setup(bundle, True)

        attr = bundle.create_attribute(self.attr4Name, self.attr4Type)
        attr.set([42, 24])
        ids0 = self.dirty.get([bundle])
        self.assertTrue(self.dirty.is_valid(ids0[0]))

        self.assertEqual(attr.as_read_only().get()[0], 42)
        self.assertEqual(attr.as_read_only().get()[1], 24)
        ids1 = self.dirty.get([bundle])
        self.assertTrue(self.dirty.is_valid(ids1[0]))
        self.assertEqual(ids0[0], ids1[0])

    async def test_change_child_and_propagate_changes_to_parent(self):
        r"""
        bundle1
         \_ child0
             \_ child1
                \_ child2 <-- create attribute
        Will propagate dirty id changes up to `bundle1`
        (child2 -> child1 -> child0 -> bundle1)
        """
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.dirty.setup(bundle, True)

        child0 = bundle.create_child_bundle("child0")
        child1 = child0.create_child_bundle("child1")
        child2 = child1.create_child_bundle("child2")
        ids0 = self.dirty.get([bundle, child0, child1])
        self.assertTrue(self.dirty.is_valid(ids0[0]))
        self.assertTrue(self.dirty.is_valid(ids0[1]))
        self.assertTrue(self.dirty.is_valid(ids0[2]))

        # creating attribute automatically bumps parent ids
        child2.create_attribute(self.attr1Name, self.attr1Type)
        ids1 = self.dirty.get([bundle, child0, child1])
        self.assertTrue(self.dirty.is_valid(ids1[0]))
        self.assertTrue(self.dirty.is_valid(ids1[1]))
        self.assertTrue(self.dirty.is_valid(ids1[2]))
        self.assertNotEqual(ids0[0], ids1[0])
        self.assertNotEqual(ids0[1], ids1[1])
        self.assertNotEqual(ids0[2], ids1[2])


class TestAttributeDirtyID(BundleTestSetup):
    async def setUp(self):
        """Set up  test environment, to be torn down when done"""
        await super().setUp()

    async def test_create_attribute(self):
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.dirty.setup(bundle, True)

        attr1 = bundle.create_attribute(self.attr1Name, self.attr1Type)
        ids0 = self.dirty.get([attr1])
        self.assertTrue(self.dirty.is_valid(ids0[0]))

        attr2 = bundle.create_attribute(self.attr2Name, self.attr2Type)
        ids1 = self.dirty.get([attr2])
        self.assertTrue(self.dirty.is_valid(ids1[0]))
        self.assertNotEqual(ids0[0], ids1[0])

    async def test_create_same_attribute(self):
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.dirty.setup(bundle, True)

        attr1 = bundle.create_attribute(self.attr1Name, self.attr1Type)
        ids0 = self.dirty.get([attr1])
        self.assertTrue(self.dirty.is_valid(ids0[0]))

        attr2 = bundle.create_attribute(self.attr1Name, self.attr1Type)
        ids1 = self.dirty.get([attr2])
        self.assertTrue(self.dirty.is_valid(ids1[0]))
        self.assertEqual(ids0[0], ids1[0])

    async def test_create_same_attribute_new_size(self):
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.dirty.setup(bundle, True)

        n = "attr"
        t = og.Type(og.BaseDataType.INT, 1, 1)

        attr = bundle.create_attribute(n, t, 100)
        ids0 = self.dirty.get([attr])
        self.assertTrue(self.dirty.is_valid(ids0[0]))

        # same size does not bump dirty ids
        attr = bundle.create_attribute(n, t, 100)
        ids1 = self.dirty.get([attr])
        self.assertTrue(self.dirty.is_valid(ids1[0]))
        self.assertEqual(ids0[0], ids1[0])

        # new size bumps dirty ids
        attr = bundle.create_attribute(n, t, 10)
        ids1 = self.dirty.get([attr])
        self.assertTrue(self.dirty.is_valid(ids1[0]))
        self.assertNotEqual(ids0[0], ids1[0])

    async def test_get_simple_attribute_data(self):
        """Getting simple attribute data should not change dirty id"""
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.dirty.setup(bundle, True)

        attr = bundle.create_attribute(self.attr1Name, self.attr1Type)
        attr.set(42)
        ids0 = self.dirty.get([attr])
        self.assertTrue(self.dirty.is_valid(ids0[0]))

        self.assertEqual(attr.as_read_only().get(), 42)
        ids1 = self.dirty.get([attr])
        self.assertTrue(self.dirty.is_valid(ids1[0]))
        self.assertEqual(ids0[0], ids1[0])

    async def test_get_array_attribute_data(self):
        """Getting array attribute data should not change dirty id"""
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.dirty.setup(bundle, True)

        attr = bundle.create_attribute(self.attr3Name, self.attr3Type)
        attr.set([42])
        ids0 = self.dirty.get([attr])
        self.assertTrue(self.dirty.is_valid(ids0[0]))

        self.assertEqual(attr.as_read_only().get()[0], 42)
        ids1 = self.dirty.get([attr])
        self.assertTrue(self.dirty.is_valid(ids1[0]))
        self.assertEqual(ids0[0], ids1[0])

    async def test_get_tuple_attribute_data(self):
        """Getting tuple attribute data should not change dirty id"""
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.dirty.setup(bundle, True)

        attr = bundle.create_attribute(self.attr4Name, self.attr4Type)
        attr.set([42, 24])
        ids0 = self.dirty.get([attr])
        self.assertTrue(self.dirty.is_valid(ids0[0]))

        self.assertEqual(attr.as_read_only().get()[0], 42)
        self.assertEqual(attr.as_read_only().get()[1], 24)
        ids1 = self.dirty.get([attr])
        self.assertTrue(self.dirty.is_valid(ids1[0]))
        self.assertEqual(ids0[0], ids1[0])

    async def test_set_simple_attribute_data(self):
        """Setting simple attribute data changes dirty id"""
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.dirty.setup(bundle, True)

        attr = bundle.create_attribute(self.attr1Name, self.attr1Type)
        ids0 = self.dirty.get([attr, bundle])
        self.assertTrue(self.dirty.is_valid(ids0[0]))
        self.assertTrue(self.dirty.is_valid(ids0[1]))
        attr.set(42)

        ids1 = self.dirty.get([attr, bundle])
        self.assertTrue(self.dirty.is_valid(ids1[0]))
        self.assertTrue(self.dirty.is_valid(ids1[1]))
        self.assertNotEqual(ids0[0], ids1[0])
        self.assertNotEqual(ids0[1], ids1[1])

    async def test_set_array_attribute_data(self):
        """Setting array attribute data changes dirty id"""
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.dirty.setup(bundle, True)

        attr = bundle.create_attribute(self.attr3Name, self.attr3Type)
        ids0 = self.dirty.get([attr, bundle])
        self.assertTrue(self.dirty.is_valid(ids0[0]))
        self.assertTrue(self.dirty.is_valid(ids0[1]))
        attr.set([42])

        ids1 = self.dirty.get([attr, bundle])
        self.assertTrue(self.dirty.is_valid(ids1[0]))
        self.assertTrue(self.dirty.is_valid(ids1[1]))
        self.assertNotEqual(ids0[0], ids1[0])
        self.assertNotEqual(ids0[1], ids1[1])

    async def test_set_tuple_attribute_data(self):
        """Setting tuple attribute data changes dirty id"""
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.dirty.setup(bundle, True)

        attr = bundle.create_attribute(self.attr4Name, self.attr4Type)
        ids0 = self.dirty.get([attr, bundle])
        self.assertTrue(self.dirty.is_valid(ids0[0]))
        self.assertTrue(self.dirty.is_valid(ids0[1]))
        attr.set([42, 24])

        ids1 = self.dirty.get([attr, bundle])
        self.assertTrue(self.dirty.is_valid(ids1[0]))
        self.assertTrue(self.dirty.is_valid(ids1[1]))
        self.assertNotEqual(ids0[0], ids1[0])
        self.assertNotEqual(ids0[1], ids1[1])

    async def test_create_attrs_without_write_block(self):
        """Creating multiple attributes without a write block bumps the bundle twice"""
        await self._test_create_attrs_write_block(False)

    async def test_create_attrs_with_write_block(self):
        """Creating multiple attributes under a write block bumps the bundle only once"""
        await self._test_create_attrs_write_block(True)

    async def _test_create_attrs_write_block(self, active: bool):
        with og.BundleWriteBlock(self.context, active):
            bundle = self.factory.create_bundle(self.context, "bundle")
            self.dirty.setup(bundle, True)

            bundle.create_attribute(self.attr1Name, self.attr1Type)
            ids1 = self.dirty.get([bundle])

            bundle.create_attribute(self.attr2Name, self.attr2Type)
            ids2 = self.dirty.get([bundle])

            if active:
                self.assertEqual(ids1[0], ids2[0])
            else:
                self.assertNotEqual(ids1[0], ids2[0])
