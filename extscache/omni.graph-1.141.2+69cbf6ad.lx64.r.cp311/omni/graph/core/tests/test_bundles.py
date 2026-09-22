import omni.core as oc
import omni.graph.core as og
import omni.graph.core.tests as ogt


class BundleTestCase(ogt.OmniGraphTestCase):
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
        self.bundle5Name = "bundle5"

        # attribute names
        self.attr1Name = "attr1"
        self.attr2Name = "attr2"
        self.attr3Name = "attr3"
        self.attr4Name = "attr4"

        # attribute types
        self.attr1Type = og.Type(og.BaseDataType.INT)
        self.attr2Type = og.Type(og.BaseDataType.FLOAT)
        self.attr3Type = og.Type(og.BaseDataType.DOUBLE, 1, 1)
        self.attr4Type = og.Type(og.BaseDataType.BOOL, 1, 1)

        self.bundle1 = self.factory.create_bundle(self.context, self.bundle1Name)
        self.assertTrue(self.bundle1.valid)

    async def test_create_bundle(self):
        # Check bundle1 does not have a parent bundle.
        parent1 = self.bundle1.get_parent_bundle()
        self.assertFalse(parent1.valid)

        # Check bundle path.
        self.assertEqual(self.bundle1.get_path(), self.bundle1Name)

        # Test state of attributes.
        self.assertEqual(self.bundle1.get_attribute_count(), 0)
        self.assertEqual(len(self.bundle1.get_attribute_names()), 0)
        self.assertEqual(len(self.bundle1.get_attribute_types()), 0)
        self.assertEqual(len(self.bundle1.get_attributes()), 0)

        # Test state of child bundles.
        self.assertEqual(self.bundle1.get_child_bundle_count(), 0)
        self.assertEqual(len(self.bundle1.get_child_bundles()), 0)

    async def test_create_child_bundle(self):
        # Create bundle hierarchy: bundle1/bundle2/bundle3.
        bundle2 = self.bundle1.create_child_bundle(self.bundle2Name)
        self.assertTrue(bundle2.valid)
        self.assertEqual(bundle2.get_name(), self.bundle2Name)

        # Check number of children.
        self.assertEqual(self.bundle1.get_child_bundle_count(), 1)
        self.assertEqual(bundle2.get_child_bundle_count(), 0)  # leaf, no children

        self.assertEqual(len(self.bundle1.get_child_bundles()), 1)
        self.assertEqual(len(bundle2.get_child_bundles()), 0)

    async def test_create_child_bundles(self):
        # Create bundle hierarchy: bundle1/bundle2/bundle3.
        bundle_paths = [self.bundle2Name, self.bundle3Name]
        self.bundle1.create_child_bundles(bundle_paths)
        self.assertEqual(self.bundle1.get_child_bundle_count(), 2)

    async def test_bundle_parent(self):
        # Create hierarchy: bundle1/bundle2/bundle3.
        bundle2 = self.bundle1.create_child_bundle(self.bundle2Name)
        self.assertTrue(bundle2.valid)

        # Check children paths.
        self.assertEqual(bundle2.get_path(), "/".join([self.bundle1Name, self.bundle2Name]))

        # Check parents paths.
        bundle2_parent = bundle2.get_parent_bundle()
        self.assertTrue(bundle2_parent.valid)
        self.assertEqual(bundle2_parent.get_path(), self.bundle1.get_path())

    async def test_get_bundle_from_path(self):
        # Create bundle hierarchy: bundle1/bundle2
        bundle2 = self.bundle1.create_child_bundle(self.bundle2Name)

        bundle1_from_path = self.factory.get_bundle_from_path(self.context, self.bundle1Name)
        self.assertTrue(bundle1_from_path.valid)
        self.assertEqual(bundle1_from_path.get_path(), self.bundle1.get_path())

        bundle2_from_path = self.factory.get_bundle_from_path(
            self.context, "/".join([self.bundle1Name, self.bundle2Name])
        )
        self.assertTrue(bundle2_from_path.valid)
        self.assertEqual(bundle2_from_path.get_path(), bundle2.get_path())

    async def test_get_bundle_from_path_invalid(self):
        invalid_bundle_from_path = self.factory.get_bundle_from_path(self.context, "gibberish")
        self.assertFalse(invalid_bundle_from_path.valid)

    async def test_remove_child_bundle(self):
        # Create hierarchy: bundle1/bundle2/bundle3.
        bundle2 = self.bundle1.create_child_bundle(self.bundle2Name)
        self.assertTrue(bundle2.valid)

        bundle3 = bundle2.create_child_bundle(self.bundle3Name)
        self.assertTrue(bundle3.valid)

        # We can only remove intermediate children, remove children from bundle1 must fail.
        # Disabled because of: OM-48629. Re-enable after OM-48828 is solved.
        # with ExpectedError():
        #    self.assertEqual(self.bundle1.remove_all_child_bundles(), 0) # remove bundle2 from bundle1

        # bundle3 is not an intermediate child of bundle1.
        self.assertFalse(self.bundle1.remove_child_bundle(bundle3))
        self.assertEqual(bundle2.remove_child_bundle(bundle3), oc.Result.SUCCESS)
        self.assertEqual(self.bundle1.remove_child_bundle(bundle2), oc.Result.SUCCESS)

    async def test_remove_child_bundles(self):
        # Create bundle hierarchy.
        bundle2 = self.bundle1.create_child_bundle(self.bundle2Name)
        self.assertTrue(bundle2.valid)

        bundle3 = self.bundle1.create_child_bundle(self.bundle3Name)
        self.assertTrue(bundle3.valid)

        # Get child bundles.
        bundles = self.bundle1.get_child_bundles()
        self.assertEqual(len(bundles), 2)

        # Remove all child bundles that are in the array.
        self.bundle1.remove_child_bundles(bundles)
        self.assertEqual(self.bundle1.get_child_bundle_count(), 0)

    async def test_remove_child_bundles_by_name(self):
        _ = self.bundle1.create_child_bundle(self.bundle2Name)
        _ = self.bundle1.create_child_bundle(self.bundle3Name)
        _ = self.bundle1.create_child_bundle(self.bundle4Name)

        self.bundle1.remove_child_bundles_by_name([self.bundle2Name, self.bundle4Name])
        self.assertEqual(self.bundle1.get_child_bundle_count(), 1)

        children = self.bundle1.get_child_bundles()
        self.assertEqual(len(children), 1)
        self.assertEqual(children[0].get_path(), "{}/{}".format(self.bundle1Name, self.bundle3Name))

    async def test_copy_child_bundle(self):
        child = self.bundle1.create_child_bundle("child")
        new_bundle = self.factory.create_bundle(self.context, "new_bundle")
        new_bundle.copy_child_bundle(child)

        self.assertEqual(new_bundle.get_child_bundle_count(), 1)
        new_child = new_bundle.get_child_bundle_by_name("child")
        self.assertTrue(new_child.valid)

    async def test_copy_child_bundle_with_name(self):
        child = self.bundle1.create_child_bundle("child")
        new_bundle = self.factory.create_bundle(self.context, "new_bundle")
        new_bundle.copy_child_bundle(child, name="foo")

        self.assertEqual(new_bundle.get_child_bundle_count(), 1)
        new_child = new_bundle.get_child_bundle_by_name("child")
        self.assertFalse(new_child.valid)

        new_child = new_bundle.get_child_bundle_by_name("foo")
        self.assertTrue(new_child.valid)

    async def test_copy_child_bundles(self):
        children = self.bundle1.create_child_bundles(["childA", "childB"])
        new_bundle = self.factory.create_bundle(self.context, "new_bundle")
        new_bundle.copy_child_bundles(children)

        self.assertEqual(new_bundle.get_child_bundle_count(), 2)
        new_children = new_bundle.get_child_bundles_by_name(["childA", "childB"])
        self.assertEqual(len(new_children), 2)
        self.assertTrue(new_children[0].valid)
        self.assertTrue(new_children[1].valid)

    async def test_copy_child_bundles_with_names(self):
        children = self.bundle1.create_child_bundles(["childA", "childB"])
        new_bundle = self.factory.create_bundle(self.context, "new_bundle")
        new_bundle.copy_child_bundles(children, names=["foo", "bar"])

        self.assertEqual(new_bundle.get_child_bundle_count(), 2)
        new_children = new_bundle.get_child_bundles_by_name(["foo", "bar"])
        self.assertEqual(len(new_children), 2)
        self.assertTrue(new_children[0].valid)
        self.assertTrue(new_children[1].valid)

    async def test_get_child_bundles_by_name(self):
        _ = self.bundle1.create_child_bundle(self.bundle2Name)
        _ = self.bundle1.create_child_bundle(self.bundle3Name)

        search = [self.bundle2Name, self.bundle3Name, self.bundle4Name]
        bundles = self.bundle1.get_child_bundles_by_name(search)

        self.assertTrue(bundles[0].valid)
        self.assertTrue(bundles[1].valid)
        self.assertFalse(bundles[2].valid)

    async def test_get_child_bundle_by_name(self):
        _ = self.bundle1.create_child_bundle(self.bundle2Name)
        _ = self.bundle1.create_child_bundle(self.bundle3Name)

        b2 = self.bundle1.get_child_bundle_by_name(self.bundle2Name)
        self.assertTrue(b2.valid)

        b3 = self.bundle1.get_child_bundle_by_name(self.bundle3Name)
        self.assertTrue(b3.valid)

        b4 = self.bundle1.get_child_bundle_by_name(self.bundle4Name)
        self.assertFalse(b4.valid)

    async def test_create_and_get_attribute(self):
        # Create each attribute individually.
        _ = self.bundle1.create_attribute(self.attr1Name, self.attr1Type)
        self.assertEqual(self.bundle1.get_attribute_count(), 1)

        attr = self.bundle1.get_attribute_by_name(self.attr1Name)
        self.assertFalse(attr is None)
        self.assertEqual(attr.get_name(), self.attr1Name)

    async def test_get_attribute_invalid(self):
        # bundle1 has no attributes
        attr = self.bundle1.get_attribute_by_name(self.attr1Name)
        self.assertFalse(attr is None)
        self.assertFalse(attr.is_valid())

        _ = self.bundle1.create_attribute(self.attr1Name, self.attr1Type)
        self.assertEqual(self.bundle1.get_attribute_count(), 1)

        # bundle1 has no attribute named "gibberish"
        attr = self.bundle1.get_attribute_by_name("gibberish")
        self.assertFalse(attr is None)
        self.assertFalse(attr.is_valid())

    async def test_create_and_get_attributes(self):
        # Create attributes by providing array of names and types.
        names = [self.attr1Name, self.attr2Name, self.attr3Name]
        types = [self.attr1Type, self.attr2Type, self.attr3Type]
        self.bundle1.create_attributes(names, types)
        self.assertEqual(self.bundle1.get_attribute_count(), 3)

        # Get all attributes.
        attrs = self.bundle1.get_attributes()
        self.assertEqual(len(attrs), 3)

        attrs = {x.get_name(): x for x in attrs if x.is_valid()}
        self.assertEqual(len(attrs), 3)
        self.assertTrue(self.attr1Name in attrs)
        self.assertTrue(self.attr2Name in attrs)
        self.assertTrue(self.attr3Name in attrs)

        # Find existing attributes.
        attrs_query = [self.attr1Name, self.attr3Name]
        attrs = self.bundle1.get_attributes_by_name(attrs_query)
        self.assertEqual(len(attrs), 2)

        attrs = {x.get_name(): x for x in attrs if x}
        self.assertEqual(len(attrs), 2)
        self.assertTrue(self.attr1Name in attrs)
        self.assertTrue(self.attr3Name in attrs)
        self.assertTrue(attrs[self.attr1Name])
        self.assertTrue(attrs[self.attr3Name])

        # Attempt to find not existing attributes.
        attrs_query = [self.attr4Name]
        attrs = self.bundle1.get_attributes_by_name(attrs_query)
        self.assertEqual(len(attrs), 1)

        attrs = {x.get_name(): x for x in attrs if x}
        self.assertEqual(len(attrs), 0)

    async def test_get_attributes_invalid(self):
        # bundle1 has no attributes
        attrs = self.bundle1.get_attributes_by_name([self.attr1Name])
        self.assertEqual(len(attrs), 1)
        self.assertFalse(attrs[0].is_valid())

        names = [self.attr1Name, self.attr2Name, self.attr3Name]
        types = [self.attr1Type, self.attr2Type, self.attr3Type]
        self.bundle1.create_attributes(names, types)
        self.assertEqual(self.bundle1.get_attribute_count(), 3)

        # bundle1 has no attribute named "gibberish"
        attrs = self.bundle1.get_attributes_by_name(["gibberish"])
        self.assertEqual(len(attrs), 1)
        self.assertFalse(attrs[0].is_valid())

    async def test_create_array_attribute(self):
        # Create array attribute.
        attr3 = self.bundle1.create_attribute(self.attr3Name, self.attr3Type, 1000)
        self.assertTrue(attr3)
        self.assertEqual(attr3.size(), 1000)

        attr3 = self.bundle1.create_attribute(self.attr3Name, self.attr3Type, 0)
        self.assertEqual(attr3.size(), 0)

    async def test_create_attribute_like(self):
        attr1 = self.bundle1.create_attribute(self.attr1Name, self.attr1Type)

        # Create new bundle and create attribute like.
        bundle2 = self.factory.create_bundle(self.context, self.bundle2Name)
        like_attr1 = bundle2.create_attribute_like(attr1)
        self.assertTrue(like_attr1)
        self.assertEqual(like_attr1.get_name(), self.attr1Name)
        self.assertEqual(like_attr1.get_type(), self.attr1Type)

    async def test_create_attributes_like(self):
        # Create attributes in bundle1.
        names = [self.attr1Name, self.attr2Name]
        types = [self.attr1Type, self.attr2Type]
        attrs = self.bundle1.create_attributes(names, types)

        # Create bundle2 and create attributes like those from bundle1.
        bundle2 = self.factory.create_bundle(self.context, self.bundle2Name)
        like_attrs = bundle2.create_attributes_like(attrs)
        like_attrs = {x.get_name(): x for x in like_attrs if x}
        self.assertEqual(len(like_attrs), 2)
        self.assertTrue(self.attr1Name in like_attrs)
        self.assertTrue(self.attr2Name in like_attrs)

    async def test_remove_attributes(self):
        # Create attributes in bundle1.
        attr1 = self.bundle1.create_attribute(self.attr1Name, self.attr1Type)
        attr2 = self.bundle1.create_attribute(self.attr2Name, self.attr2Type)

        # Remove one attribute from bundle.
        self.assertEqual(self.bundle1.remove_attribute(attr2), oc.Result.SUCCESS)
        self.assertEqual(self.bundle1.get_attribute_count(), 1)

        # Try to remove non existing attributes.
        bundle2 = self.factory.create_bundle(self.context, self.bundle2Name)
        self.assertEqual(bundle2.remove_attributes([attr1, attr2]), 0)

    async def test_remove_attributes_by_name(self):
        _ = self.bundle1.create_attribute(self.attr1Name, self.attr1Type)
        _ = self.bundle1.create_attribute(self.attr2Name, self.attr2Type)
        _ = self.bundle1.create_attribute(self.attr3Name, self.attr3Type)

        self.bundle1.remove_attributes_by_name([self.attr1Name, self.attr3Name])
        self.assertEqual(self.bundle1.get_attribute_count(), 1)

        names = self.bundle1.get_attribute_names()
        self.assertEqual(len(names), 1)
        self.assertEqual(names[0], self.attr2Name)

    async def test_copy_attribute(self):
        attr1 = self.bundle1.create_attribute(self.attr1Name, self.attr1Type)
        self.assertTrue(attr1)

        # Create bundle2 and copy attr1 from bundle1.
        bundle2 = self.factory.create_bundle(self.context, self.bundle2Name)
        cpy_attr1 = bundle2.copy_attribute(attr1)
        self.assertTrue(cpy_attr1)
        self.assertEqual(cpy_attr1.get_type(), self.attr1Type)

    async def test_copy_attributes(self):
        # Create attributes.
        names = [self.attr1Name, self.attr2Name]
        types = [self.attr1Type, self.attr2Type]
        src_attrs1 = self.bundle1.create_attributes(names, types)

        names = [self.attr3Name, self.attr4Name]
        types = [self.attr3Type, self.attr4Type]
        bundle2 = self.factory.create_bundle(self.context, self.bundle2Name)
        src_attrs2 = bundle2.create_attributes(names, types)

        # Create bundle3 and copy attributes from bundle1 and bundle2.
        bundle3 = self.factory.create_bundle(self.context, self.bundle3Name)
        src_attrs = src_attrs2 + src_attrs1  # reversed elements
        cpy_attrs = bundle3.copy_attributes(src_attrs)
        self.assertEqual(len(cpy_attrs), 4)

        # Check if attributes are valid.
        cpy_attrs = {x.get_name(): x for x in cpy_attrs if x}
        self.assertEqual(len(cpy_attrs), 4)

        # Get copied attributes by name.
        cpy_attr1 = bundle3.get_attribute_by_name(self.attr1Name)
        cpy_attr2 = bundle3.get_attribute_by_name(self.attr2Name)
        cpy_attr3 = bundle3.get_attribute_by_name(self.attr3Name)
        cpy_attr4 = bundle3.get_attribute_by_name(self.attr4Name)

        # Copied attributes must be valid.
        self.assertTrue(cpy_attr1.is_valid())
        self.assertTrue(cpy_attr2.is_valid())
        self.assertTrue(cpy_attr3.is_valid())
        self.assertTrue(cpy_attr4.is_valid())

        # Check copied attributes types.
        self.assertEqual(cpy_attr1.get_type(), self.attr1Type)
        self.assertEqual(cpy_attr2.get_type(), self.attr2Type)
        self.assertEqual(cpy_attr3.get_type(), self.attr3Type)
        self.assertEqual(cpy_attr4.get_type(), self.attr4Type)

    async def test_copy_attributes_override(self):
        # create double on bundle1
        d_attr = self.bundle1.create_attribute(self.attr1Name, og.Type(og.BaseDataType.DOUBLE, 1, 1), 1000)
        self.assertEqual(d_attr.size(), 1000)

        # create bool on bundle2
        bundle2 = self.factory.create_bundle(self.context, self.bundle2Name)
        b_attr = bundle2.create_attribute(self.attr1Name, og.Type(og.BaseDataType.BOOL, 1, 1), 10)
        self.assertEqual(b_attr.size(), 10)

        # try copy double
        attr = bundle2.copy_attribute(d_attr, overwrite=False)
        self.assertFalse(attr.is_valid())

        # try copy double
        attr = bundle2.copy_attribute(d_attr, overwrite=True)
        self.assertTrue(attr.is_valid())
        self.assertEqual(attr.size(), 1000)
        self.assertEqual(attr.get_type().base_type, self.attr3Type.base_type)

    async def test_get_path(self):
        # Create hierarchy: bundle1/bundle2/bundle3.
        bundle1 = self.bundle1
        bundle2 = bundle1.create_child_bundle(self.bundle2Name)
        self.assertTrue(bundle2.valid)

    async def test_create_private_attribute(self):
        # This functionality is an implementation detail and should not be abused
        bundle = self.factory.create_bundle(self.context, "bundle")
        attrib = bundle.create_attribute("__bundle__private__attrib", og.Type(og.BaseDataType.INT))

        self.assertTrue(attrib.is_valid())
        self.assertEqual(bundle.get_attribute_count(), 0)

    async def test_target_attribute_type(self):
        target_type = og.Type(og.BaseDataType.RELATIONSHIP, 1, 0, og.AttributeRole.TARGET)
        bundle = self.bundle1
        bundle.create_attribute("targets", target_type)
        self.assertEqual(bundle.get_attribute_count(), 1)

        attrib = bundle.get_attributes()[0]
        self.assertTrue(attrib.is_valid())
        self.assertEqual(attrib.get_type().base_type, og.BaseDataType.RELATIONSHIP)
        self.assertEqual(attrib.get_type().role, og.AttributeRole.TARGET)


class TestBundlePrivateAttributeAndChild(ogt.OmniGraphTestCase):
    async def setUp(self):
        await super().setUp()

        self.graph = og.Controller.create_graph("/graph")
        self.context = self.graph.get_default_graph_context()
        self.factory = og.IBundleFactory.create()
        self.assertTrue(self.factory is not None)

    async def test_private_attribute(self):
        bundle = self.factory.create_bundle(self.context, "bundle")
        bundle.create_attribute("__test", og.Type(og.BaseDataType.INT))
        self.assertEqual(bundle.get_attribute_count(), 0)

        bundle.create_attribute("test__", og.Type(og.BaseDataType.INT))
        self.assertEqual(bundle.get_attribute_count(), 1)

        bundle.create_attribute("test__test", og.Type(og.BaseDataType.INT))
        self.assertEqual(bundle.get_attribute_count(), 2)

        bundle.create_attribute("__private_test", og.Type(og.BaseDataType.INT))
        self.assertEqual(bundle.get_attribute_count(), 2)

        self.assertTrue(bundle.get_attribute_by_name("__test").is_valid())

    async def test_private_child(self):
        bundle = self.factory.create_bundle(self.context, "bundle")
        bundle.create_child_bundle("__test")
        self.assertEqual(bundle.get_child_bundle_count(), 0)

        bundle.create_child_bundle("test__")
        self.assertEqual(bundle.get_child_bundle_count(), 1)

        bundle.create_child_bundle("test__test")
        self.assertEqual(bundle.get_child_bundle_count(), 2)

        bundle.create_child_bundle("__private_test")
        self.assertEqual(bundle.get_child_bundle_count(), 2)

        self.assertTrue(bundle.get_child_bundle_by_name("__test").valid)


class TestBundleMetadata(ogt.OmniGraphTestCase):
    """Test bundle metadata management"""

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
        self.bundle5Name = "bundle5"

        # attribute names
        self.attr1Name = "attr1"
        self.attr2Name = "attr2"
        self.attr3Name = "attr3"
        self.attr4Name = "attr4"

        # attribute types
        self.attr1Type = og.Type(og.BaseDataType.INT)
        self.attr2Type = og.Type(og.BaseDataType.FLOAT)
        self.attr3Type = og.Type(og.BaseDataType.DOUBLE, 1, 1)
        self.attr4Type = og.Type(og.BaseDataType.BOOL, 1, 1)

        self.bundle1 = self.factory.create_bundle(self.context, self.bundle1Name)
        self.assertTrue(self.bundle1.valid)

    async def test_bundle_metadata_create(self):
        # check content
        self.assertEqual(self.bundle1.get_attribute_count(), 0)
        self.assertEqual(self.bundle1.get_child_bundle_count(), 0)
        self.assertEqual(self.bundle1.get_bundle_metadata_count(), 0)

        # create bundle metadata
        field1 = self.bundle1.create_bundle_metadata(self.attr1Name, self.attr1Type)
        field2 = self.bundle1.create_bundle_metadata(self.attr2Name, self.attr2Type)

        # check content
        self.assertEqual(self.bundle1.get_attribute_count(), 0)
        self.assertEqual(self.bundle1.get_child_bundle_count(), 0)
        self.assertEqual(self.bundle1.get_bundle_metadata_count(), 2)
        self.assertTrue(field1.is_valid())
        self.assertTrue(field2.is_valid())

        # create attributes
        self.bundle1.create_attribute(self.attr1Name, self.attr1Type)
        self.bundle1.create_attribute(self.attr2Name, self.attr2Type)

        # check content
        self.assertEqual(self.bundle1.get_attribute_count(), 2)
        self.assertEqual(self.bundle1.get_child_bundle_count(), 0)
        self.assertEqual(self.bundle1.get_bundle_metadata_count(), 2)

        # create children
        self.bundle1.create_child_bundle(self.bundle2Name)
        self.bundle1.create_child_bundle(self.bundle3Name)

        self.assertEqual(self.bundle1.get_attribute_count(), 2)
        self.assertEqual(self.bundle1.get_child_bundle_count(), 2)
        self.assertEqual(self.bundle1.get_bundle_metadata_count(), 2)

    async def test_bundle_metadata_remove_bulk(self):
        self.bundle1.create_attribute(self.attr1Name, self.attr1Type)
        self.bundle1.create_bundle_metadata([self.attr1Name, self.attr2Name], [self.attr1Type, self.attr2Type])

        self.assertEqual(self.bundle1.get_attribute_count(), 1)
        self.assertEqual(self.bundle1.get_bundle_metadata_count(), 2)
        self.bundle1.remove_bundle_metadata([self.attr1Name, self.attr2Name])
        self.assertEqual(self.bundle1.get_attribute_count(), 1)
        self.assertEqual(self.bundle1.get_bundle_metadata_count(), 0)

    async def test_bundle_metadata_remove_single(self):
        self.bundle1.create_attribute(self.attr1Name, self.attr1Type)
        self.bundle1.create_bundle_metadata(self.attr1Name, self.attr1Type)
        self.bundle1.create_bundle_metadata(self.attr2Name, self.attr2Type)
        self.assertEqual(self.bundle1.get_attribute_count(), 1)
        self.assertEqual(self.bundle1.get_bundle_metadata_count(), 2)

        self.bundle1.remove_bundle_metadata(self.attr1Name)
        self.assertEqual(self.bundle1.get_attribute_count(), 1)
        self.assertEqual(self.bundle1.get_bundle_metadata_count(), 1)

        self.bundle1.remove_bundle_metadata(self.attr2Name)
        self.assertEqual(self.bundle1.get_attribute_count(), 1)
        self.assertEqual(self.bundle1.get_bundle_metadata_count(), 0)

    async def test_bundle_metadata_remove_none(self):
        self.assertEqual(self.bundle1.get_attribute_count(), 0)
        self.assertEqual(self.bundle1.get_bundle_metadata_count(), 0)

        self.bundle1.remove_bundle_metadata(self.attr1Name)

        self.assertEqual(self.bundle1.get_attribute_count(), 0)
        self.assertEqual(self.bundle1.get_bundle_metadata_count(), 0)

    async def test_bundle_metadata_info(self):
        """
        Counting number of attributes in metadata bundle.
        """
        self.assertEqual(self.bundle1.get_bundle_metadata_count(), 0)
        self.assertEqual(len(self.bundle1.get_bundle_metadata_names()), 0)
        self.assertEqual(len(self.bundle1.get_bundle_metadata_types()), 0)

        # create two metadata attributes
        _ = self.bundle1.create_bundle_metadata(self.attr1Name, self.attr1Type)
        _ = self.bundle1.create_bundle_metadata(self.attr2Name, self.attr2Type)

        # check bundle metadata
        self.assertEqual(len(set(self.bundle1.get_bundle_metadata_names())), 2)
        self.assertEqual(len(set(self.bundle1.get_bundle_metadata_types())), 2)
        self.assertTrue(self.attr1Name in self.bundle1.get_bundle_metadata_names())
        self.assertTrue(self.attr2Name in self.bundle1.get_bundle_metadata_names())

    async def test_bundle_metadata_storage(self):
        """
        Metadata storage is currently invalid
        """
        self.assertEqual(self.bundle1.get_bundle_metadata_count(), 0)
        self.assertEqual(len(self.bundle1.get_bundle_metadata_names()), 0)
        self.assertEqual(len(self.bundle1.get_bundle_metadata_types()), 0)

        # create two metadata attributes
        _ = self.bundle1.create_bundle_metadata(self.attr1Name, self.attr1Type)
        _ = self.bundle1.create_bundle_metadata(self.attr2Name, self.attr2Type)

        # check metadata storage
        metadata_storage = self.bundle1.get_metadata_storage()
        self.assertFalse(metadata_storage.valid)

    async def test_bundle_metadata_child_by_index(self):
        """
        Metadata bundle can not be returned in a list of children.

        This test confirms that get_child_bundle does not return metadata bundle.
        """
        # create two attributes
        _ = self.bundle1.create_attribute(self.attr1Name, self.attr1Type)
        _ = self.bundle1.create_attribute(self.attr2Name, self.attr2Type)

        # create children
        ref_paths = [self.bundle2Name, self.bundle3Name, self.bundle4Name, self.bundle5Name]
        for i, ref_path in enumerate(ref_paths):
            self.bundle1.create_child_bundle(ref_path)
            ref_paths[i] = "{}/{}".format(self.bundle1Name, ref_path)

        # get child by index
        unique_paths = set()
        for index in range(len(ref_paths)):
            child = self.bundle1.get_child_bundle(index)
            unique_paths.add(child.get_path())
            self.assertTrue(child.get_path())
            self.assertTrue(child.get_path() in ref_paths)

        self.assertEqual(len(unique_paths), 4)

    async def test_bundle_metadata_by_name(self):
        """
        Get bundle metadata by name.
        """
        # create two metadata attributes
        self.bundle1.create_bundle_metadata(self.attr1Name, self.attr1Type)
        self.bundle1.create_bundle_metadata(self.attr2Name, self.attr2Type)
        self.assertTrue(self.bundle1.get_bundle_metadata_count(), 2)

        attrs = self.bundle1.get_bundle_metadata_by_name([self.attr1Name, self.attr2Name])
        self.assertEqual(len(attrs), 2)
        self.assertEqual(attrs[0].get_name(), self.attr1Name)
        self.assertEqual(attrs[1].get_name(), self.attr2Name)

    async def test_bundle_metadata_by_name_invalid(self):
        # bundle1 has no metadata
        attrs = self.bundle1.get_bundle_metadata_by_name([self.attr1Name])
        self.assertEqual(len(attrs), 1)
        self.assertFalse(attrs[0].is_valid())

        self.bundle1.create_bundle_metadata(self.attr1Name, self.attr1Type)
        self.bundle1.create_bundle_metadata(self.attr2Name, self.attr2Type)
        self.assertTrue(self.bundle1.get_bundle_metadata_count(), 2)

        # bundle1 has no metadata named "gibberish"
        attrs = self.bundle1.get_bundle_metadata_by_name(["gibberish"])
        self.assertEqual(len(attrs), 1)
        self.assertFalse(attrs[0].is_valid())

    async def test_metadata_bundle_create_many_fields(self):
        self.bundle1.create_bundle_metadata([self.attr1Name, self.attr2Name], [self.attr1Type, self.attr2Type])
        self.assertTrue(self.bundle1.get_bundle_metadata_count(), 2)

        attrs = self.bundle1.get_bundle_metadata_by_name([self.attr1Name, self.attr2Name])
        self.assertEqual(len(attrs), 2)
        self.assertEqual(attrs[0].get_name(), self.attr1Name)
        self.assertEqual(attrs[1].get_name(), self.attr2Name)

    async def test_metadata_bundle_create_single_field(self):
        self.bundle1.create_bundle_metadata(self.attr1Name, self.attr1Type)
        self.bundle1.create_bundle_metadata(self.attr2Name, self.attr2Type)
        self.assertTrue(self.bundle1.get_bundle_metadata_count(), 2)

        attrs = self.bundle1.get_bundle_metadata_by_name([self.attr1Name, self.attr2Name])
        self.assertEqual(len(attrs), 2)
        self.assertEqual(attrs[0].get_name(), self.attr1Name)
        self.assertEqual(attrs[1].get_name(), self.attr2Name)

    async def test_attribute_metadata_create(self):
        # check content
        self.assertEqual(self.bundle1.get_attribute_count(), 0)
        self.assertEqual(self.bundle1.get_child_bundle_count(), 0)
        self.assertEqual(self.bundle1.get_attribute_metadata_count(self.attr1Name), 0)

        # Create attribute metadata for not existing attribute should fail
        # Disabled because of: OM-48629. Re-enable after OM-48828 is solved.
        # field2 = self.bundle1.create_attribute_metadata(self.attr1Name, self.attr2Name, self.attr2Type)
        # field3 = self.bundle1.create_attribute_metadata(self.attr1Name, self.attr3Name, self.attr3Type)
        # self.assertFalse(field2.is_valid())
        # self.assertFalse(field3.is_valid())

        # check content
        self.assertEqual(self.bundle1.get_attribute_count(), 0)
        self.assertEqual(self.bundle1.get_child_bundle_count(), 0)
        self.assertEqual(self.bundle1.get_attribute_metadata_count(self.attr1Name), 0)

        # create attribute and metadata for existing attribute
        self.bundle1.create_attribute(self.attr1Name, self.attr1Type)
        field2 = self.bundle1.create_attribute_metadata(self.attr1Name, self.attr2Name, self.attr2Type)
        field3 = self.bundle1.create_attribute_metadata(self.attr1Name, self.attr3Name, self.attr3Type)

        # check content
        self.assertEqual(self.bundle1.get_attribute_count(), 1)
        self.assertEqual(self.bundle1.get_child_bundle_count(), 0)
        self.assertEqual(self.bundle1.get_attribute_metadata_count(self.attr1Name), 2)
        self.assertEqual(self.bundle1.get_attribute_metadata_count(self.attr2Name), 0)
        self.assertTrue(field2.is_valid())
        self.assertTrue(field3.is_valid())

    async def test_attribute_metadata_create_with_ns(self):
        # create attribute
        self.bundle1.create_attribute(self.attr1Name, self.attr1Type)

        # create metadata for attribute that contains namespace in it
        name = "node:type"
        _ = self.bundle1.create_attribute_metadata(self.attr1Name, name, self.attr2Type)
        self.assertEqual(self.bundle1.get_attribute_metadata_count(self.attr1Name), 1)
        names = self.bundle1.get_attribute_metadata_names(self.attr1Name)
        self.assertTrue(name in names)

    async def test_attribute_metadata_names_and_types(self):
        self.bundle1.create_attribute(self.attr1Name, self.attr1Type)
        _ = self.bundle1.create_attribute_metadata(self.attr1Name, self.attr2Name, self.attr2Type)
        _ = self.bundle1.create_attribute_metadata(self.attr1Name, self.attr3Name, self.attr3Type)

        names = self.bundle1.get_attribute_metadata_names(self.attr1Name)
        types = self.bundle1.get_attribute_metadata_types(self.attr1Name)

        self.assertEqual(len(names), 2)
        self.assertEqual(len(types), 2)

        self.assertTrue(self.attr2Name in names)
        self.assertTrue(self.attr3Name in names)

    async def test_attribute_metadata_by_name(self):
        self.bundle1.create_attribute(self.attr1Name, self.attr1Type)

        # not existing
        field1 = self.bundle1.get_attribute_metadata_by_name(self.attr1Name, self.attr2Name)
        self.assertFalse(field1.is_valid())

        # create and query
        field1 = self.bundle1.create_attribute_metadata(self.attr1Name, self.attr2Name, self.attr2Type)
        self.assertTrue(field1.is_valid())

        field1 = self.bundle1.get_attribute_metadata_by_name(self.attr1Name, self.attr2Name)
        self.assertTrue(field1.is_valid())

    async def test_attribute_metadata_remove(self):
        self.bundle1.create_attribute(self.attr1Name, self.attr1Type)

        # create
        self.bundle1.create_attribute_metadata(self.attr1Name, self.attr2Name, self.attr2Type)
        self.bundle1.create_attribute_metadata(self.attr1Name, self.attr3Name, self.attr3Type)
        self.assertEqual(self.bundle1.get_attribute_metadata_count(self.attr1Name), 2)

        # remove single
        self.bundle1.remove_attribute_metadata(self.attr1Name, self.attr2Name)
        self.assertEqual(self.bundle1.get_attribute_metadata_count(self.attr1Name), 1)

        self.bundle1.remove_attribute_metadata(self.attr1Name, self.attr3Name)
        self.assertEqual(self.bundle1.get_attribute_metadata_count(self.attr1Name), 0)

        # create
        self.bundle1.create_attribute_metadata(self.attr1Name, self.attr2Name, self.attr2Type)
        self.bundle1.create_attribute_metadata(self.attr1Name, self.attr3Name, self.attr3Type)
        self.assertEqual(self.bundle1.get_attribute_metadata_count(self.attr1Name), 2)

        # remove bulk
        self.bundle1.remove_attribute_metadata(self.attr1Name, (self.attr2Name, self.attr3Name))
        self.assertEqual(self.bundle1.get_attribute_metadata_count(self.attr1Name), 0)

        # create
        self.bundle1.create_attribute_metadata(self.attr1Name, self.attr2Name, self.attr2Type)
        self.bundle1.create_attribute_metadata(self.attr1Name, self.attr3Name, self.attr3Type)
        self.assertEqual(self.bundle1.get_attribute_metadata_count(self.attr1Name), 2)

        # remove all
        self.bundle1.remove_attribute_metadata(self.attr1Name, ())
        self.assertEqual(self.bundle1.get_attribute_metadata_count(self.attr1Name), 0)

    async def test_attribute_remove_with_metadata(self):
        attr1 = self.bundle1.create_attribute(self.attr1Name, self.attr1Type)
        self.bundle1.create_attribute_metadata(self.attr1Name, self.attr2Name, self.attr2Type)
        self.bundle1.create_attribute_metadata(self.attr1Name, self.attr3Name, self.attr3Type)
        self.assertEqual(self.bundle1.get_attribute_metadata_count(self.attr1Name), 2)

        # remove attribute should remove metadata
        self.bundle1.remove_attribute(attr1)
        self.assertEqual(self.bundle1.get_attribute_metadata_count(self.attr1Name), 0)

    async def test_bundle_array_metadata(self):
        met1 = self.bundle1.create_bundle_metadata(self.attr3Name, self.attr3Type, 1000)
        self.assertTrue(met1)
        self.assertEqual(met1.size(), 1000)

    async def test_attribute_array_metadata(self):
        self.bundle1.create_attribute(self.attr1Name, self.attr1Type)
        met1 = self.bundle1.create_attribute_metadata(self.attr1Name, self.attr3Name, self.attr3Type, 1000)
        self.assertTrue(met1)
        self.assertEqual(met1.size(), 1000)

    async def test_copy_attributes_with_metadata(self):
        attr1 = self.bundle1.create_attribute(self.attr1Name, self.attr1Type)
        self.bundle1.create_attribute_metadata(self.attr1Name, self.attr2Name, self.attr2Type)
        self.bundle1.create_attribute_metadata(self.attr1Name, self.attr3Name, self.attr3Type)
        self.assertTrue(attr1)

        # Create bundle2 and copy attr1 from bundle1
        bundle2 = self.factory.create_bundle(self.context, self.bundle2Name)
        cpy_attr1 = bundle2.copy_attribute(attr1)
        self.assertTrue(cpy_attr1)
        self.assertEqual(cpy_attr1.get_type(), self.attr1Type)

        # metadata check
        self.assertEqual(bundle2.get_attribute_metadata_count(self.attr1Name), 2)

        names = bundle2.get_attribute_metadata_names(self.attr1Name)
        types = bundle2.get_attribute_metadata_types(self.attr1Name)

        self.assertEqual(len(names), 2)
        self.assertEqual(len(types), 2)

        self.assertTrue(self.attr2Name in names)
        self.assertTrue(self.attr3Name in names)

    async def test_copy_bundle(self):
        # create bundle metadata
        self.bundle1.create_bundle_metadata(self.attr2Name, self.attr2Type)
        self.bundle1.create_bundle_metadata(self.attr3Name, self.attr3Type)
        self.bundle1.create_bundle_metadata(self.attr4Name, self.attr4Type)

        # create attribute metadata
        self.bundle1.create_attribute(self.attr1Name, self.attr1Type)
        self.bundle1.create_attribute_metadata(self.attr1Name, self.attr2Name, self.attr2Type)
        self.bundle1.create_attribute_metadata(self.attr1Name, self.attr3Name, self.attr3Type)

        # Create bundle2 and copy attr1 from bundle1
        bundle2 = self.factory.create_bundle(self.context, self.bundle2Name)
        bundle2.copy_bundle(self.bundle1)

        # bundle metadata check
        self.assertEqual(bundle2.get_bundle_metadata_count(), 3)

        names = bundle2.get_bundle_metadata_names()
        types = bundle2.get_bundle_metadata_names()

        self.assertTrue(self.attr2Name in names)
        self.assertTrue(self.attr3Name in names)
        self.assertTrue(self.attr4Name in names)
        self.assertEqual(len(types), 3)

        # attribute metadata check
        self.assertEqual(bundle2.get_attribute_metadata_count(self.attr1Name), 2)

        names = bundle2.get_attribute_metadata_names(self.attr1Name)
        types = bundle2.get_attribute_metadata_types(self.attr1Name)

        self.assertTrue(self.attr2Name in names)
        self.assertTrue(self.attr3Name in names)
        self.assertEqual(len(types), 2)

    async def init_for_clear_contents(self):
        # attributes 3
        _ = self.bundle1.create_attribute(self.attr1Name, self.attr1Type)
        _ = self.bundle1.create_attribute(self.attr2Name, self.attr2Type)
        _ = self.bundle1.create_attribute(self.attr3Name, self.attr3Type)

        # children 2
        _ = self.bundle1.create_child_bundle(self.bundle2Name)
        _ = self.bundle1.create_child_bundle(self.bundle3Name)

        # bundle metadata 4
        self.bundle1.create_bundle_metadata(self.attr1Name, self.attr1Type)
        self.bundle1.create_bundle_metadata(self.attr2Name, self.attr2Type)
        self.bundle1.create_bundle_metadata(self.attr3Name, self.attr3Type)
        self.bundle1.create_bundle_metadata(self.attr4Name, self.attr4Type)

        # attr1 metadata 2
        self.bundle1.create_attribute_metadata(self.attr1Name, self.attr3Name, self.attr3Type)
        self.bundle1.create_attribute_metadata(self.attr1Name, self.attr4Name, self.attr4Type)

        # attr2 metadata 1
        self.bundle1.create_attribute_metadata(self.attr2Name, self.attr4Name, self.attr4Type)

    async def test_clear_contents(self):
        await self.init_for_clear_contents()

        self.assertEqual(self.bundle1.get_bundle_metadata_count(), 4)  # metadata is not destroyed by default
        self.bundle1.clear_contents()

        # confirm bundle is clear
        self.assertEqual(self.bundle1.get_attribute_count(), 0)
        self.assertEqual(self.bundle1.get_child_bundle_count(), 0)
        self.assertEqual(self.bundle1.get_bundle_metadata_count(), 0)  # metadata IS destroyed by default
        self.assertEqual(self.bundle1.get_attribute_metadata_count(self.attr1Name), 0)
        self.assertEqual(self.bundle1.get_attribute_metadata_count(self.attr2Name), 0)
        self.assertTrue(self.bundle1.valid)

    async def test_clear_contents_bundle_metadata(self):
        await self.init_for_clear_contents()

        self.assertEqual(self.bundle1.get_bundle_metadata_count(), 4)
        self.bundle1.clear_contents(bundle_metadata=True)

        self.assertEqual(self.bundle1.get_bundle_metadata_count(), 0)

    async def test_clear_contents_attributes(self):
        await self.init_for_clear_contents()

        self.assertEqual(self.bundle1.get_attribute_count(), 3)
        self.bundle1.clear_contents(attributes=False)
        self.assertEqual(self.bundle1.get_attribute_count(), 3)

    async def test_clear_contents_child_bundles(self):
        await self.init_for_clear_contents()

        self.assertEqual(self.bundle1.get_child_bundle_count(), 2)
        self.bundle1.clear_contents(child_bundles=False)
        self.assertEqual(self.bundle1.get_child_bundle_count(), 2)


class TestBundleFactoryInterface(ogt.OmniGraphTestCase):
    async def setUp(self):
        """Set up  test environment, to be torn down when done"""
        await super().setUp()

        self.graph = og.Controller.create_graph("/graph")
        self.context = self.graph.get_default_graph_context()
        self.factory = og.IBundleFactory.create()
        self.assertTrue(self.factory is not None)

        self.bundle1Name = "bundle1"
        self.bundle2Name = "bundle2"

    def test_bundle_conversion_method(self):
        """The factory used to allow the conversion from old Py_Bundle to new I(Const)Bundle interface.
        Depending on writability of Py_Bundle, IConstBundle2 or IBundle2 was returned. When Py_Bundle was removed
        backwards compatibility conversion methods were kept.
        As reported in OM-84762 factory fails to pass through IBundle2, and converts IBundle2 to IConstBundle2.
        Eventually this test should be removed in next release when get_bundle conversion method is hard deprecated.
        """
        bundle1 = self.factory.create_bundle(self.context, self.bundle1Name)
        bundle2 = self.factory.get_bundle(bundle1.get_context(), bundle1)
        self.assertTrue(isinstance(bundle2, og.IBundle2))
