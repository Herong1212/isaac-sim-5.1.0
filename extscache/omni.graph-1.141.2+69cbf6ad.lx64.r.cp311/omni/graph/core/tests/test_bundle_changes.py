import omni.graph.core as og
import omni.graph.core.tests as ogt


class BundleTestSetup(ogt.OmniGraphTestCase):
    async def setUp(self):
        """Set up test environment, to be torn down when done"""
        await super().setUp()

        self.graph = og.Controller.create_graph("/graph")
        self.context = self.graph.get_default_graph_context()

        self.factory = og.IBundleFactory.create()
        self.assertTrue(self.factory is not None)

        self.bundle_changes = og.IBundleChanges.create(self.context)
        self.assertTrue(self.bundle_changes is not None)


class TestBundleTopologyChanges(BundleTestSetup):
    async def setUp(self):
        """Set up test environment, to be torn down when done"""
        await super().setUp()

    async def test_bundle_changes_interface(self):
        bundle_changes = og.IBundleChanges.create(self.context)
        self.assertTrue(bundle_changes is not None)

    async def test_create_bundle(self):
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.bundle_changes.activate_change_tracking(bundle)

        with og.BundleChanges(self.bundle_changes, bundle) as changes:
            self.assertEqual(changes.get_change(bundle), og.BundleChangeType.MODIFIED)

        # cleaned after leaving the scope
        self.assertEqual(self.bundle_changes.get_change(bundle), og.BundleChangeType.NONE)

    async def test_create_attribute(self):
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.bundle_changes.activate_change_tracking(bundle)

        # setup tracking
        self.bundle_changes.get_change(bundle)
        self.bundle_changes.clear_changes()

        # check if everything is clean
        self.assertEqual(self.bundle_changes.get_change(bundle), og.BundleChangeType.NONE)

        # modify
        attrib = bundle.create_attribute("attrib", og.Type(og.BaseDataType.INT))

        # check for changes
        with og.BundleChanges(self.bundle_changes, bundle) as changes:
            self.assertTrue(changes.has_changed())
            self.assertEqual(changes.get_change(bundle), og.BundleChangeType.MODIFIED)
            self.assertEqual(changes.get_change(attrib), og.BundleChangeType.MODIFIED)

        # cleaned after leaving the scope
        self.assertEqual(self.bundle_changes.get_change(bundle), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(attrib), og.BundleChangeType.NONE)

    async def test_create_attribute_like(self):
        bundle1 = self.factory.create_bundle(self.context, "bundle1")
        bundle2 = self.factory.create_bundle(self.context, "bundle2")
        self.bundle_changes.activate_change_tracking(bundle1)
        self.bundle_changes.activate_change_tracking(bundle2)

        attrib1 = bundle1.create_attribute("attrib", og.Type(og.BaseDataType.INT))

        # setup tracking
        self.bundle_changes.get_change(bundle1)
        self.bundle_changes.get_change(bundle2)
        self.bundle_changes.get_change(attrib1)
        self.bundle_changes.clear_changes()

        # check if everything is clean
        self.assertEqual(self.bundle_changes.get_change(bundle1), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(bundle2), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(attrib1), og.BundleChangeType.NONE)

        # command: create attrib based on attrib1
        attrib2 = bundle2.create_attribute_like(attrib1)

        # check for changes
        with og.BundleChanges(self.bundle_changes, bundle2) as changes:
            self.assertTrue(changes.has_changed())
            self.assertEqual(changes.get_change(bundle1), og.BundleChangeType.NONE)
            self.assertEqual(changes.get_change(attrib1), og.BundleChangeType.NONE)
            self.assertEqual(changes.get_change(bundle2), og.BundleChangeType.MODIFIED)
            self.assertEqual(changes.get_change(attrib2), og.BundleChangeType.MODIFIED)

        # cleaned after leaving the scope
        self.assertEqual(self.bundle_changes.get_change(bundle1), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(bundle2), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(attrib1), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(attrib2), og.BundleChangeType.NONE)

    async def test_create_child_bundle(self):
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.bundle_changes.activate_change_tracking(bundle)

        # setup tracking
        self.bundle_changes.get_change(bundle)
        self.bundle_changes.clear_changes()

        # check if everything is clean
        self.assertEqual(self.bundle_changes.get_change(bundle), og.BundleChangeType.NONE)

        # modify
        bundle.create_child_bundle("child")

        # check for changes and clear them
        with og.BundleChanges(self.bundle_changes, bundle) as changes:
            self.assertTrue(changes.has_changed())
            self.assertEqual(changes.get_change(bundle), og.BundleChangeType.MODIFIED)

        # cleaned after leaving the scope
        self.assertEqual(self.bundle_changes.get_change(bundle), og.BundleChangeType.NONE)

    async def test_remove_attribute(self):
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.bundle_changes.activate_change_tracking(bundle)

        bundle.create_attribute("attrib", og.Type(og.BaseDataType.INT))

        # setup tracking
        self.bundle_changes.get_change(bundle)
        self.bundle_changes.clear_changes()

        # check if everything is clean
        self.assertEqual(self.bundle_changes.get_change(bundle), og.BundleChangeType.NONE)

        # modify
        bundle.remove_attribute("attrib")

        # check for changes and clear them
        with og.BundleChanges(self.bundle_changes, bundle) as changes:
            self.assertTrue(changes.has_changed())
            self.assertEqual(changes.get_change(bundle), og.BundleChangeType.MODIFIED)

        # cleaned after leaving the scope
        self.assertEqual(self.bundle_changes.get_change(bundle), og.BundleChangeType.NONE)

    async def test_remove_child_bundles(self):
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.bundle_changes.activate_change_tracking(bundle)

        child = bundle.create_child_bundle("child")

        # setup tracking
        self.bundle_changes.get_change(bundle)
        self.bundle_changes.clear_changes()

        # check if everything is clean
        self.assertEqual(self.bundle_changes.get_change(bundle), og.BundleChangeType.NONE)

        # modify
        bundle.remove_child_bundle(child)

        # check for changes and clear them
        with og.BundleChanges(self.bundle_changes, bundle) as changes:
            self.assertTrue(changes.has_changed())
            self.assertEqual(changes.get_change(bundle), og.BundleChangeType.MODIFIED)

        # cleaned after leaving the scope
        self.assertEqual(self.bundle_changes.get_change(bundle), og.BundleChangeType.NONE)

    async def test_clear_contents(self):
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.bundle_changes.activate_change_tracking(bundle)

        # setup tracking
        self.bundle_changes.get_change(bundle)
        self.bundle_changes.clear_changes()

        # check if everything is clean
        self.assertEqual(self.bundle_changes.get_change(bundle), og.BundleChangeType.NONE)

        # modify
        bundle.clear_contents()

        # check for changes and clear them
        with og.BundleChanges(self.bundle_changes, bundle) as changes:
            self.assertTrue(changes.has_changed())
            self.assertEqual(changes.get_change(bundle), og.BundleChangeType.MODIFIED)

        # cleaned after leaving the scope
        self.assertEqual(self.bundle_changes.get_change(bundle), og.BundleChangeType.NONE)

    async def test_copy_attribute(self):
        bundle1 = self.factory.create_bundle(self.context, "bundle1")
        bundle2 = self.factory.create_bundle(self.context, "bundle2")
        self.bundle_changes.activate_change_tracking(bundle1)
        self.bundle_changes.activate_change_tracking(bundle2)

        attrib1 = bundle1.create_attribute("attrib1", og.Type(og.BaseDataType.INT))

        # setup tracking
        self.bundle_changes.get_change(bundle1)
        self.bundle_changes.get_change(bundle2)
        self.bundle_changes.get_change(attrib1)
        self.bundle_changes.clear_changes()

        # check if everything is clean
        self.assertEqual(self.bundle_changes.get_change(bundle1), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(bundle2), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(attrib1), og.BundleChangeType.NONE)

        # modify
        # only bundle2 is affected, but source bundle1 and attrib1 not
        bundle2.copy_attribute(attrib1)

        # check for changes and clear them
        with og.BundleChanges(self.bundle_changes, bundle2) as changes:
            self.assertTrue(changes.has_changed())
            self.assertEqual(changes.get_change(bundle1), og.BundleChangeType.NONE)
            self.assertEqual(changes.get_change(bundle2), og.BundleChangeType.MODIFIED)
            self.assertEqual(changes.get_change(attrib1), og.BundleChangeType.NONE)

        # cleaned after leaving the scope
        self.assertEqual(self.bundle_changes.get_change(bundle1), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(bundle2), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(attrib1), og.BundleChangeType.NONE)

    async def test_copy_child_bundle(self):
        """Test if CoW reference is resolved."""
        bundle1 = self.factory.create_bundle(self.context, "bundle1")
        bundle2 = self.factory.create_bundle(self.context, "bundle2")
        self.bundle_changes.activate_change_tracking(bundle1)
        self.bundle_changes.activate_change_tracking(bundle2)

        # setup tracking
        self.bundle_changes.get_change(bundle1)
        self.bundle_changes.get_change(bundle2)
        self.bundle_changes.clear_changes()

        # check if everything is clean
        self.assertEqual(self.bundle_changes.get_change(bundle1), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(bundle2), og.BundleChangeType.NONE)

        # modify
        # only bundle1 is dirty, but bundle2 stays intact
        bundle1.copy_child_bundle(bundle2)
        self.assertEqual(self.bundle_changes.get_change(bundle2), og.BundleChangeType.NONE)

        # check for changes and clear them
        with og.BundleChanges(self.bundle_changes, bundle1) as changes:
            self.assertTrue(changes.has_changed())
            self.assertEqual(changes.get_change(bundle1), og.BundleChangeType.MODIFIED)

        # cleaned after leaving the scope
        self.assertEqual(self.bundle_changes.get_change(bundle1), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(bundle2), og.BundleChangeType.NONE)

    async def test_copy_bundle(self):
        """Copying bundle creates a shallow copy - a reference.
        To obtain the dirty id the reference needs to be resolved"""
        bundle1 = self.factory.create_bundle(self.context, "bundle1")
        bundle2 = self.factory.create_bundle(self.context, "bundle2")
        self.bundle_changes.activate_change_tracking(bundle1)
        self.bundle_changes.activate_change_tracking(bundle2)

        # setup tracking
        self.bundle_changes.get_change(bundle1)
        self.bundle_changes.get_change(bundle2)
        self.bundle_changes.clear_changes()

        # check if everything is clean
        self.assertEqual(self.bundle_changes.get_change(bundle1), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(bundle2), og.BundleChangeType.NONE)

        # modify
        # bundle2 is modified, but bundle1 stays intact
        bundle2.copy_bundle(bundle1)
        self.assertEqual(self.bundle_changes.get_change(bundle1), og.BundleChangeType.NONE)

        # check for changes and clear them
        with og.BundleChanges(self.bundle_changes, bundle2) as changes:
            self.assertTrue(changes.has_changed())
            self.assertEqual(changes.get_change(bundle2), og.BundleChangeType.MODIFIED)

        # cleaned after leaving the scope
        self.assertEqual(self.bundle_changes.get_change(bundle1), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(bundle2), og.BundleChangeType.NONE)

    async def test_get_attribute_by_name(self):
        """Getting writable attribute data handle does not change dirty id.
        Only writing to an attribute triggers id to be changed."""
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.bundle_changes.activate_change_tracking(bundle)

        attrib = bundle.create_attribute("attrib", og.Type(og.BaseDataType.INT))

        # setup tracking
        self.bundle_changes.get_change(bundle)
        self.bundle_changes.get_change(attrib)
        self.bundle_changes.clear_changes()

        # check if everything is clean
        self.assertEqual(self.bundle_changes.get_change(bundle), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(attrib), og.BundleChangeType.NONE)

        # getting attribute doesn't mark any changes
        attrib = bundle.get_attribute_by_name("attrib")

        # check for changes and clear them
        with og.BundleChanges(self.bundle_changes, bundle) as changes:
            self.assertFalse(changes.has_changed())
            self.assertEqual(changes.get_change(bundle), og.BundleChangeType.NONE)
            self.assertEqual(changes.get_change(attrib), og.BundleChangeType.NONE)

        # cleaned after leaving the scope
        self.assertEqual(self.bundle_changes.get_change(bundle), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(attrib), og.BundleChangeType.NONE)

    async def test_get_child_bundle_by_name(self):
        """Getting writable bundle handle does not change dirty id.
        Only creating/removing attributes and children triggers id to be
        changed."""
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.bundle_changes.activate_change_tracking(bundle)

        child = bundle.create_child_bundle("child")

        # setup tracking
        self.bundle_changes.get_change(bundle)
        self.bundle_changes.get_change(child)
        self.bundle_changes.clear_changes()

        # check if everything is clean
        self.assertEqual(self.bundle_changes.get_change(bundle), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(child), og.BundleChangeType.NONE)

        # bundle and child must be clean
        child = bundle.get_child_bundle_by_name("child")

        # check for changes and clear them
        with og.BundleChanges(self.bundle_changes, bundle) as changes:
            self.assertFalse(changes.has_changed())
            self.assertEqual(changes.get_change(bundle), og.BundleChangeType.NONE)
            self.assertEqual(changes.get_change(child), og.BundleChangeType.NONE)

        # cleaned after leaving the scope
        self.assertEqual(self.bundle_changes.get_change(bundle), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(child), og.BundleChangeType.NONE)

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
        self.bundle_changes.activate_change_tracking(bundle)

        child0 = bundle.create_child_bundle("child0")
        child1 = child0.create_child_bundle("child1")
        child2 = child1.create_child_bundle("child2")

        # setup tracking
        self.bundle_changes.get_change(bundle)
        self.bundle_changes.get_change(child0)
        self.bundle_changes.get_change(child1)
        self.bundle_changes.get_change(child2)
        self.bundle_changes.clear_changes()

        # check if everything is clean
        self.assertEqual(self.bundle_changes.get_change(child2), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(child1), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(child0), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(bundle), og.BundleChangeType.NONE)

        # creating attribute automatically make all hierarchy dirty
        child2.create_attribute("attrib", og.Type(og.BaseDataType.INT))

        # check for changes and clear them
        with og.BundleChanges(self.bundle_changes, bundle) as changes:
            self.assertTrue(changes.has_changed())
            self.assertEqual(changes.get_change(child2), og.BundleChangeType.MODIFIED)
            self.assertEqual(changes.get_change(child1), og.BundleChangeType.MODIFIED)
            self.assertEqual(changes.get_change(child0), og.BundleChangeType.MODIFIED)
            self.assertEqual(changes.get_change(bundle), og.BundleChangeType.MODIFIED)

        # cleaned after leaving the scope
        self.assertEqual(self.bundle_changes.get_change(child2), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(child1), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(child0), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(bundle), og.BundleChangeType.NONE)


class TestBundleAttributeDataChanges(BundleTestSetup):
    async def setUp(self):
        """Set up  test environment, to be torn down when done"""
        await super().setUp()

    async def test_set_get_simple_attribute_data(self):
        """Getting simple attribute data should not change dirty id"""
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.bundle_changes.activate_change_tracking(bundle)

        attrib = bundle.create_attribute("attrib", og.Type(og.BaseDataType.INT))

        # setup tracking
        self.bundle_changes.get_change(bundle)
        self.bundle_changes.get_change(attrib)
        self.bundle_changes.clear_changes()

        self.assertEqual(self.bundle_changes.get_change(bundle), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(attrib), og.BundleChangeType.NONE)

        # command: set modifies attribute and bundle
        attrib.set(42)

        # check for changes and clear them
        with og.BundleChanges(self.bundle_changes, bundle) as changes:
            self.assertTrue(changes.has_changed())
            self.assertEqual(changes.get_change(bundle), og.BundleChangeType.MODIFIED)
            self.assertEqual(changes.get_change(attrib), og.BundleChangeType.MODIFIED)

        # cleaned after leaving the scope
        self.assertEqual(self.bundle_changes.get_change(bundle), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(attrib), og.BundleChangeType.NONE)

        # query: get does not modify attribute and bundle
        self.assertEqual(attrib.as_read_only().get(), 42)

        # check for changes and clear them
        with og.BundleChanges(self.bundle_changes, bundle) as changes:
            self.assertFalse(changes.has_changed())
            self.assertEqual(changes.get_change(bundle), og.BundleChangeType.NONE)
            self.assertEqual(changes.get_change(attrib), og.BundleChangeType.NONE)

        # cleaned after leaving the scope
        self.assertEqual(self.bundle_changes.get_change(bundle), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(attrib), og.BundleChangeType.NONE)

    async def test_set_get_array_attribute_data(self):
        """Getting simple attribute data should not change dirty id"""
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.bundle_changes.activate_change_tracking(bundle)

        attrib = bundle.create_attribute("attrib", og.Type(og.BaseDataType.INT, 1, 1))

        # setup tracking
        self.bundle_changes.get_change(bundle)
        self.bundle_changes.get_change(attrib)
        self.bundle_changes.clear_changes()

        self.assertEqual(self.bundle_changes.get_change(bundle), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(attrib), og.BundleChangeType.NONE)

        # command: set modifies attribute and bundle
        attrib.set([42])

        # check for changes and clear them
        with og.BundleChanges(self.bundle_changes, bundle) as changes:
            self.assertTrue(changes.has_changed())
            self.assertEqual(changes.get_change(bundle), og.BundleChangeType.MODIFIED)
            self.assertEqual(changes.get_change(attrib), og.BundleChangeType.MODIFIED)

        # cleaned after leaving the scope
        self.assertEqual(self.bundle_changes.get_change(bundle), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(attrib), og.BundleChangeType.NONE)

        # query: get does not modify attribute and bundle
        self.assertEqual(attrib.as_read_only().get()[0], 42)

        # check for changes and clear them
        with og.BundleChanges(self.bundle_changes, bundle) as changes:
            self.assertFalse(changes.has_changed())
            self.assertEqual(changes.get_change(bundle), og.BundleChangeType.NONE)
            self.assertEqual(changes.get_change(attrib), og.BundleChangeType.NONE)

        # cleaned after leaving the scope
        self.assertEqual(self.bundle_changes.get_change(bundle), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(attrib), og.BundleChangeType.NONE)

    async def test_set_get_tuple_attribute_data(self):
        """Getting simple attribute data should not change dirty id"""
        bundle = self.factory.create_bundle(self.context, "bundle")
        self.bundle_changes.activate_change_tracking(bundle)

        attrib = bundle.create_attribute("attrib", og.Type(og.BaseDataType.INT, 2, 0))

        # setup tracking
        self.bundle_changes.get_change(bundle)
        self.bundle_changes.get_change(attrib)
        self.bundle_changes.clear_changes()

        self.assertEqual(self.bundle_changes.get_change(bundle), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(attrib), og.BundleChangeType.NONE)

        # command: set modifies attribute and bundle
        attrib.set([42, 24])

        # check for changes and clear them
        with og.BundleChanges(self.bundle_changes, bundle) as changes:
            self.assertTrue(changes.has_changed())
            self.assertEqual(changes.get_change(bundle), og.BundleChangeType.MODIFIED)
            self.assertEqual(changes.get_change(attrib), og.BundleChangeType.MODIFIED)

        # cleaned after leaving the scope
        self.assertEqual(self.bundle_changes.get_change(bundle), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(attrib), og.BundleChangeType.NONE)

        # query: get does not modify attribute and bundle
        self.assertEqual(attrib.as_read_only().get()[0], 42)
        self.assertEqual(attrib.as_read_only().get()[1], 24)

        # check for changes and clear them
        with og.BundleChanges(self.bundle_changes, bundle) as changes:
            self.assertFalse(changes.has_changed())
            self.assertEqual(changes.get_change(bundle), og.BundleChangeType.NONE)
            self.assertEqual(changes.get_change(attrib), og.BundleChangeType.NONE)

        # cleaned after leaving the scope
        self.assertEqual(self.bundle_changes.get_change(bundle), og.BundleChangeType.NONE)
        self.assertEqual(self.bundle_changes.get_change(attrib), og.BundleChangeType.NONE)
