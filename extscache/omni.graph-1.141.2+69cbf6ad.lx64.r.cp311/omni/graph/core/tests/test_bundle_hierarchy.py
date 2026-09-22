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

        # bundle paths
        self.bundle1Name = "bundle1"
        self.bundle2Name = "bundle2"
        self.bundle3Name = "bundle3"
        self.bundle4Name = "bundle4"

        # attribute names
        self.attr1Name = "attr1"
        self.attr2Name = "attr2"

        # attribute types
        self.attr1Type = og.Type(og.BaseDataType.INT)
        self.attr2Type = og.Type(og.BaseDataType.FLOAT)

        self.bundle1 = self.factory.create_bundle(self.context, self.bundle1Name)
        self.assertTrue(self.bundle1.valid)


# ------------------------------------------------------------------ #
#  FOLLOWING TESTS ARE IMPLEMENTATION DETAILS AND MUST NOT BE USED!  #
# ------------------------------------------------------------------ #


class TestBundleHierarchyCleanup(BundleTestSetup):
    """This tests exercises cleanup of internals of the bundles."""

    async def setUp(self):
        """Set up  test environment, to be torn down when done"""
        await super().setUp()

    def test_recursive_child_bundle_removal(self):
        # create hierarchy of bundles
        b0 = self.bundle1
        b1 = b0.create_child_bundle(self.bundle2Name)
        b2 = b1.create_child_bundle(self.bundle3Name)

        self.assertTrue(b0)
        self.assertTrue(b1)
        self.assertTrue(b2)

        p0 = f"{self.bundle1Name}"
        p1 = f"{self.bundle1Name}/{self.bundle2Name}"
        p2 = f"{self.bundle1Name}/{self.bundle2Name}/{self.bundle3Name}"

        self.assertTrue(self.factory.get_const_bundle_from_path(self.context, p0))
        self.assertTrue(self.factory.get_const_bundle_from_path(self.context, p1))
        self.assertTrue(self.factory.get_const_bundle_from_path(self.context, p2))

        b0.clear_contents()

        # p0 is not removed, only the descendants will be gone
        self.assertTrue(self.factory.get_const_bundle_from_path(self.context, p0))
        self.assertFalse(self.factory.get_const_bundle_from_path(self.context, p1))
        self.assertFalse(self.factory.get_const_bundle_from_path(self.context, p2))

    def test_recursive_child_bundle_metadata_removal(self):
        b0 = self.bundle1
        b1 = b0.create_child_bundle(self.bundle2Name)

        # create bundle metadata
        b0.create_bundle_metadata(self.attr1Name, self.attr1Type)
        b1.create_bundle_metadata(self.attr1Name, self.attr1Type)

        # create bundle attributes
        b0.create_attribute(self.attr1Name, self.attr1Type)
        b1.create_attribute(self.attr1Name, self.attr1Type)

        # create attribute metadata
        b0.create_attribute_metadata(self.attr1Name, self.attr2Name, self.attr2Type)
        b1.create_attribute_metadata(self.attr1Name, self.attr2Name, self.attr2Type)

        # TODO: Investigate why passing c-string does not work. The conversion from c-string to PathC produces different ids.
        p0 = f"{self.bundle1Name}/__metadata__bundle__"
        p1 = f"{self.bundle1Name}/__metadata__bundle__/{self.attr1Name}"
        p2 = f"{self.bundle1Name}/{self.bundle2Name}/__metadata__bundle__"
        p3 = f"{self.bundle1Name}/{self.bundle2Name}/__metadata__bundle__/{self.attr1Name}"

        get = self.factory.get_const_bundle_from_path
        self.assertTrue(get(self.context, p0))
        self.assertTrue(get(self.context, p1))
        self.assertTrue(get(self.context, p2))
        self.assertTrue(get(self.context, p3))

        b0.clear_contents()

        self.assertFalse(get(self.context, p0))
        self.assertFalse(get(self.context, p1))
        self.assertFalse(get(self.context, p2))
        self.assertFalse(get(self.context, p3))

    def test_recursive_child_remove_with_cow(self):
        child_names = [self.bundle2Name, self.bundle3Name]
        b0 = self.bundle1
        children = b0.create_child_bundles(child_names)

        # Copy-on-Write child bundles
        b1 = self.factory.create_bundle(self.context, self.bundle4Name)
        b1.copy_child_bundles(child_names, children)

        # check content
        get = self.factory.get_const_bundle_from_path

        # original bundle
        p0 = f"{self.bundle1Name}"
        p1 = f"{self.bundle1Name}/{self.bundle2Name}"
        p2 = f"{self.bundle1Name}/{self.bundle3Name}"

        self.assertTrue(get(self.context, p0))
        self.assertTrue(get(self.context, p1))
        self.assertTrue(get(self.context, p2))

        # copied children
        p0 = f"{self.bundle4Name}"
        p1 = f"{self.bundle4Name}/{self.bundle2Name}"
        p2 = f"{self.bundle4Name}/{self.bundle3Name}"

        self.assertTrue(get(self.context, p0))
        self.assertTrue(get(self.context, p1))
        self.assertTrue(get(self.context, p2))

        # remove shallow copies, but not the original location
        b1.clear_contents()

        # shallow children are gone
        self.assertTrue(get(self.context, p0))
        self.assertFalse(get(self.context, p1))
        self.assertFalse(get(self.context, p2))

        # but original location stays intact
        p0 = f"{self.bundle1Name}"
        p1 = f"{self.bundle1Name}/{self.bundle2Name}"
        p2 = f"{self.bundle1Name}/{self.bundle3Name}"

        self.assertTrue(get(self.context, p0))
        self.assertTrue(get(self.context, p1))
        self.assertTrue(get(self.context, p2))
