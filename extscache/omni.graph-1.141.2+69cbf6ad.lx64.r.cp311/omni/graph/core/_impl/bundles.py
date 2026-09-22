# The information bracketed here with begin/end describes the interface that is recommended for use with bundled
# attributes. The documentation uses these markers to perform a literal include of this code into the docs so that
# it can be the single source of truth. Note that the interface described here is not the complete set of functions
# functions available, merely the ones that make sense for the user to access when dealing with bundles.
#
# begin-bundle-interface-description
"""
# A bundle can be described as an opaque collection of attributes that travel together through the graph, whose
# contents and types can be introspected in order to determine how to deal with them. This section describes how
# the typical node will interface with the bundle content access. Use of the attributes within the bundles is the
# same as for the extended type attributes, described with their access methods.
#
# An important note regarding GPU bundles is that the bundle itself always lives on the CPU, specifying a memory
# space of "GPU/CUDA" for the bundle actually means that the default location of the attributes it contains will
# be on the GPU.
#
# The main bundle is extracted the same as any other attribute, by referencing its generated database location.
# For this example the bundle will be called "color" and it will have members that could either be the set
# ("r", "g", "b", "a") or the set ("c", "m", "y", "k") with the obvious implications of implied color space.

# As with other attribute types the bundle attribute functions are available through an accessor
color_bundle = db.inputs.color

# The accessor can determine if it points to valid data through a property
valid_color = color_bundle.valid

# If you want to call the underlying Bundle ABI directly you can access the og.Bundle object
bundle_object = color_bundle.bundle

# It can be queried for the number of attributes it holds
bundle_attribute_count = color_bundle.size

# It can have its contents iterated over, where each element in the iteration is an accessor of the bundled attribute
for (bundled_attribute in color_bundle.attributes)
    pass

# It can be queried for an attribute in it with a specific name
bundled_attribute = color_bundle.attribute_by_name(db.tokens.red)

# You can get naming information to identify where the bundle is stored you can also get a path
bundle_path = color_bundle.path

# *** The rest of these methods are for output bundles only, as they change the makeup of the bundle

# It can have its contents (i.e. attribute membership) cleared
computed_color_bundle.clear()

# It can be assigned to an output bundle, which merely transfers ownership of the bundle.
# The property setter for the bundle member is the mechanism for this.
color_bundle.bundle = some_other_bundle

# This is accomplished with the insert utility function, which can insert a number of different types of objects
# into a bundle. (The type of data it is passed determines what will be inserted.)
#
# The above function uses this variation, which inserts the bundle members into an existing bundle
computed_color_bundle.insert(color_bundle)

# It can have a single attribute from another bundle inserted into its current list, like if you don't want
# the transparency value in your output color
computed_color_bundle.clear()
computed_color_bundle.insert(color_bundle.attribute_by_name(db.tokens.red))
computed_color_bundle.insert(color_bundle.attribute_by_name(db.tokens.green))
computed_color_bundle.insert(color_bundle.attribute_by_name(db.tokens.blue))

# Optionally, the attribute can be renamed when adding to the bundle by passing the attribute and name as a 2-tuple
red_attribute = color_bundle.attribute_by_name(db.tokens.red)
computed_color_bundle.insert((red_attribute, db.tokens.scarlett))

# It can also add a brand new attribute with a specific type and name as a 2-tuple
og.Type FLOAT_TYPE(og.BaseDataType.FLOAT)
computed_color_bundle.insert((FLOAT_TYPE, db.tokens.opacity)

# *** When attributes are extracted from a bundle they will also be enclosed in a wrapper class og.RuntimeAttribute

# The wrapper class has access to the attribute description information, specifically the name and type
red_name = red_attribute.name
red_type = red_attribute.type

# Array attributes have a "size" property, which can also be set on output or state attributes
point_array = db.inputs.mesh.attribute_by_name(db.tokens.points)
deformed_point_array = db.outputs.mesh.attribute_by_name(db.tokens.points)
deformed_point_array.size = point_array.size

# Default value access is done through the value property, which is writable on output or state attributes
red_input = db.inputs.color.attribute_by_name(db.tokens.red)
red_output = db.outputs.color.attribute_by_name(db.tokens.red)
red_output.value = 1.0 - red_input.value

# By default the above functions operate in the same memory space as was defined by the bundled that contained the
# attribute. If you wish to be more explicit about where the memory lives you can access the specific versions of
# value properties that force either CPU or GPU memory space
if on_gpu:
    call_cuda_code(red_output.gpu_value, red_input.gpu_value)
else:
    red_output.cpu_value = 1.0 - red_input.cpu_value

# Lastly, on the rare occasion you need direct access to the attribute's ABI through the underlying type
# og.AttributeData you can access it through the abi property
my_attribute_data = red_attribute.abi
"""
# end-bundle-interface-description
from __future__ import annotations

from contextlib import suppress
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import omni.graph.core as og
import omni.graph.tools.ogn as ogn
from carb import log_warn

from .runtime import RuntimeAttribute
from .utils import non_const

# Information required to create a new bundled attribute from scratch
AttributeDescription = Tuple[og.Type, str]


# ================================================================================
class BundleChanges:
    """----- FOR USE BY GENERATED CODE ONLY -----

    BundleChanges is designed for inspecting modifications within a bundle during its lifetime.

    The BundleChanges class enables the inspection of changes in a bundle's attributes and child bundles
    during the lifetime of the BundleChanges instance. It keeps a record of modifications that have occurred,
    providing a suite of functionalities to inspect these changes.

    An important aspect of the BundleChanges class is that it automatically clears the changes upon its
    destruction, i.e., when the instance goes out of scope. This ensures that the lifetime of the recorded changes is
    tied to the lifetime of the BundleChanges instance.

    Example usage:

        def compute(db) -> bool:
            with db.inputs.bundle.changes() as bundle_changes:
                if bundle_changes:
                    # inspect changes
                else:
                    return True  # early exit, no changes
    """

    # __bundle_changes: The bundle change tracking instance
    # __bundle: The top level bundle that is being tracked
    # __clear_at_exit: Bool flag to clear the changes when BundleChanges exit scope

    def __init__(
        self,
        bundle_changes: og.IBundleChanges,
        bundle: og.IConstBundle2,
        clear_at_exit: bool = True,
    ):
        """Initialize bundle change tracking system for a bundle

        Args:
            context: Evaluation context from which this bundle was extracted
            bundle: Bundle for which changes are being tracked
        """
        self.__bundle_changes = bundle_changes
        self.__bundle = bundle
        self.__clear_at_exit = clear_at_exit

    def __enter__(self):
        return self

    def __exit__(self, *_):
        if self.__clear_at_exit:
            self.clear_changes()

    def activate(self):
        """
        Activates the change tracking system for a bundle.

        This method controls the change tracking system of a bundle. It's only applicable
        for read-write bundles (when readOnly template parameter is false). For read-only
        bundles, this method will cause a compilation error if called.
        """
        if self.__bundle.is_read_only():
            raise TypeError("Can't activate change tracking for read-only bundle.")

        self.__bundle_changes.activate_change_tracking(self.__bundle)

    def deactivate(self):
        """
        Deactivates the change tracking system for a bundle.

        This method controls the change tracking system of a bundle. It's only applicable
        for read-write bundles (when readOnly template parameter is false). For read-only
        bundles, this method will cause a compilation error if called.
        """
        if self.__bundle.is_read_only():
            raise TypeError("Can't activate change tracking for read-only bundle.")

        self.__bundle_changes.deactivate_change_tracking(self.__bundle)

    def __bool__(self):
        """
        Implicit conversion to bool.

        This method allows an instance of BundleChanges to be automatically converted to a bool.
        The boolean value indicates whether the bundle has undergone any changes within its lifetime.
        """
        return self.has_changed()

    def clear_changes(self):
        """
        Clears the recorded changes.

        This method is used to manually clear the recorded changes of the bundle.
        """
        assert self.__bundle_changes is not None, "bundle_changes is None"
        self.__bundle_changes.clear_changes()

    def has_changed(self):
        """
        Checks if the bundle has changed.

        This method is used to check if any changes have been made to the bundle's attributes or child bundles
        within the lifetime of the BundleChanges instance.
        """
        assert self.__bundle_changes is not None, "bundle_changes is None"
        return self.__bundle_changes.get_change(self.__bundle) != og.BundleChangeType.NONE

    def get_change(self, entry: Union[BundleContents, RuntimeAttribute, og.AttributeData, og.IConstBundle2]):
        """
        Retrieves the change status of a abundle or attribute.

        This method is used to check if a specific bundle or attribute has been modified
        within the lifetime of the BundleChanges instance.

        Args:
            entry: None, RuntimeAttribute or BundleContents to check if dirty.
        """
        if isinstance(entry, BundleContents):
            return self.__bundle_changes.get_change(entry.bundle)

        if isinstance(entry, RuntimeAttribute):
            return self.__bundle_changes.get_change(entry.abi)

        return self.__bundle_changes.get_change(entry)


# ================================================================================
class BundleContents:
    """----- FOR USE BY GENERATED CODE ONLY -----

    Manage the allowed types of attributes, providing a static set of convenience values

    Attributes:
        context (GraphContext): Evaluation context from which this bundle was extracted
        read_only (bool): Is the bundle data read-only?
    """

    # __bundle: The bundle attached to the attribute
    # __gpu_by_default: Are the bundle members on the GPU by default?
    # __gpu_ptr_kind: Where do the array bundle members on the GPU store their array pointers?

    def __init__(
        self,
        context: og.GraphContext,
        node: og.Node,
        attribute_name: str,
        read_only: bool,
        gpu_by_default: bool,
        gpu_ptr_kind: og.PtrToPtrKind = og.PtrToPtrKind.NA,
    ):
        """Initialize the access points for the bundle attribute

        Args:
            context: Evaluation context from which this bundle was extracted
            node: Node owning the bundle
            attribute_name: Name of the bundle attribute
            read_only: Is the bundle data read-only?
            gpu_by_default: Are the bundle members on the GPU by default?
            gpu_ptr_kind: On which device to pointers to GPU bundles live?
        """
        self.context = context
        self.read_only = read_only
        self.__gpu_by_default = gpu_by_default
        self.__gpu_ptr_kind = gpu_ptr_kind
        if read_only:
            self.__bundle = context.get_input_bundle(node, attribute_name)
        else:
            self.__bundle = context.get_output_bundle(node, attribute_name)

        self.__bundle_changes = None

    # ------------------------------------------------------------------------------------------
    @property
    def size(self) -> int:
        """int: the number of attributes within this bundle, 0 if the bundle is not valid"""
        return self.__bundle.get_attribute_count() if self.__bundle.is_valid() else 0

    # ------------------------------------------------------------------------------------------
    @property
    def valid(self) -> bool:
        """bool: Validity of the underlying bundle"""
        return self.__bundle.is_valid()

    # ------------------------------------------------------------------------------------------
    @non_const
    def clear(self):
        """Empties out the bundle contents

        Raises:
            og.OmniGraphError: if the bundle is not writable
        """
        # Silently accept that clearing an invalid bundle is a null operation
        if self.__bundle.is_valid():
            self.__bundle.clear_contents()

    # ------------------------------------------------------------------------------------------
    @non_const
    def add_attributes(self, types: List[og.Type], names: List[str]):
        """Add attributes to the bundle

        Args:
            types: Vector of types
            names: The names of each attribute

        Note it is required that size(types) == size(names)
        """
        if not self.__bundle.is_valid:
            log_warn("Attempting to insert something into an invalid bundle")
            return

        if len(types) != len(names):
            log_warn("mismatched size of types and names")
            return

        self.__bundle.create_attributes(names, types)

    # ------------------------------------------------------------------------------------------
    @non_const
    def remove_attributes(self, names: List[str]):
        """Remove attributes from the bundle

        Args:
            names: The names of each attribute to be removed

        Note it is required that size(types) == size(names)
        """
        if not self.__bundle.is_valid:
            log_warn("Attempting to remove something from an invalid bundle")
            return

        self.__bundle.remove_attributes(names)

    # ------------------------------------------------------------------------------------------
    @non_const
    def insert(
        self, to_insert: Union[BundleContents, RuntimeAttribute, Tuple[RuntimeAttribute, str], AttributeDescription]
    ) -> RuntimeAttribute:
        """Insert new content in the existing bundle

        Args:
            to_insert: Object to insert. It can be one of three different types of object:

                *Bundle*: Another bundle, whose contents are entirely copied into this one

                *RuntimeAttribute*: A single attribute from another bundle to be copied with the same name

                *(RuntimeAttribute, str)*: A single attribute from another bundle and the name to use for the copy

                *AttributeDescription*: Information required to create a brand new typed attribute

        Returns:
            RuntimeAttribute: wrapper to the new attribute if inserting an attribute, else None
        """
        if not self.__bundle.is_valid:
            log_warn("Attempting to insert something into an invalid bundle")
            return None

        if isinstance(to_insert, BundleContents):
            self.__bundle.copy_bundle(to_insert.__bundle)  # noqa: PLW0212
            return None

        if isinstance(to_insert, RuntimeAttribute):
            new_attribute = self.__bundle.insert_attribute(to_insert.attribute_data, to_insert.name)
            return RuntimeAttribute(
                new_attribute, self.context, self.read_only, self.__gpu_by_default, self.__gpu_ptr_kind
            )

        if isinstance(to_insert, tuple):
            if isinstance(to_insert[0], og.Type):
                new_attribute = self.__bundle.add_attribute(to_insert[0], to_insert[1])
                return RuntimeAttribute(
                    new_attribute, self.context, self.read_only, self.__gpu_by_default, self.__gpu_ptr_kind
                )
            with suppress(AttributeError):
                new_attribute = self.__bundle.insert_attribute(to_insert[0].attribute_data, to_insert[1])
                return RuntimeAttribute(
                    new_attribute, self.context, self.read_only, self.__gpu_by_default, self.__gpu_ptr_kind
                )

        raise og.OmniGraphError(f"Unknown type of object being inserted into a bundle ({to_insert})")

    # ------------------------------------------------------------------------------------------
    def attribute_by_name(self, attribute_name: str) -> Optional[RuntimeAttribute]:
        """Returns the named attribute within the bundle, or None if no such attribute exists in the bundle

        Args:
            attribute_name: Name of the attribute to retrieve

        Returns:
            RuntimeAttribute: Bundle member with the given name, None if it was not found
        """
        all_attributes = self.__bundle.get_attributes() if self.__bundle.is_valid() else []
        for attribute in all_attributes:
            if attribute.get_name() == attribute_name:
                return RuntimeAttribute(
                    attribute, self.context, self.read_only, self.__gpu_by_default, self.__gpu_ptr_kind
                )
        return None

    # ------------------------------------------------------------------------------------------
    def remove(self, attribute_name: str):
        """Removes the attribute with the given name from the bundle, silently succeeding if it is not in the bundle

        Args:
            attribute_name: Name of the attribute to remove
        """
        if not self.__bundle.is_valid():
            log_warn(f"Attempted to remove attribute {attribute_name} from an invalid bundle")
        else:
            self.__bundle.remove_attribute(attribute_name)

    # ------------------------------------------------------------------------------------------
    @property
    def bundle(self) -> og.Bundle:
        """Bundle: Underlying bundle of this object"""
        return self.__bundle

    @bundle.setter
    @non_const
    def bundle(self, bundle_to_assign: BundleContents):
        """Copies the contents of the bundle into this one, clearing first.
        Use insert() to add to the contents of a bundle without clearing.
        Good for assigning the entire contents of an input bundle to an output bundle before performing operations:

            db.outputs.transformedBundle = db.inputs.bundle
        """
        if self.__bundle.is_valid() and bundle_to_assign.bundle.is_valid():
            self.insert(bundle_to_assign)
        else:
            log_warn("Attempting to assign a bundle to an invalid bundle")

    # ------------------------------------------------------------------------------------------
    @property
    def attributes(self) -> List[RuntimeAttribute]:
        """list[RuntimeAttribute]: interface objects corresponding to the attributes contained within the bundle"""
        all_attributes = self.__bundle.get_attributes() if self.__bundle.is_valid() else []
        return [
            RuntimeAttribute(attribute, self.context, self.read_only, self.__gpu_by_default, self.__gpu_ptr_kind)
            for attribute in all_attributes
        ]

    @attributes.setter
    @non_const
    def attributes(self, attributes_to_assign: List[RuntimeAttribute]):
        """Populate the bundle with the list of attributes, clearing before assignment.
        Good for assigning a subset of the contents of another bundle's attributes to this one:

            db.outputs.filteredBundle = db.inputs.bundle.attributes[0:3]
        """
        if not self.__bundle.is_valid():
            log_warn("Attempted to assign attributes to invalid bundle")
            return
        self.clear()
        raise og.OmniGraphError("TODO: Assigning list of attributes to a bundle not implemented")

    # ------------------------------------------------------------------------------------------
    @property
    def path(self) -> str:
        """str: the path where this bundle's data is stored"""
        return self.__bundle.get_prim_path()

    # ------------------------------------------------------------------------------------------
    def changes(self, clear_at_exit: bool = True):
        if self.__bundle_changes is None:
            self.__bundle_changes = og.IBundleChanges.create(self.context)
        return BundleChanges(self.__bundle_changes, self.__bundle, clear_at_exit)


# ================================================================================
class BundleContainer:
    """----- FOR USE BY GENERATED CODE ONLY -----

    Simple container to manage the set of bundle objects used during a compute function by a node.
    This is initialized alongside attribute data in order to minimize the generated code. It will house
    a set of BundleContents objects, one per attribute that is a bundle type, with properties named after
    the attributes they represent

    Attributes:
        context (GraphContext): Evaluation context for these bundles
        node (Node): Owner of these bundles
        attributes (list[Attribute]): Subset of node attributes to check for being bundles
        gpu_bundles (list[str]): Subset of bundle attributes whose memory lives on the GPU
        read_only (bool): True if these attributes are read-only
        gpu_ptr_kinds (dict[str, PtrToPtrKind]): Attribute array pointer locations for GPU-based array attributes
    """

    # TODO: gpu_bundles is a hacky way of passing the information "is the bundle on the GPU by default".
    #       It's probably better in the long run to make this a property of the attribute.
    #       The gpu_ptr_kinds is an even hackier way of deciding if the GPU bundle returns pointers on the CPU or not,
    #       but it was a tradeoff between that and creating a new version of this container class.
    def __init__(
        self,
        context: og.GraphContext,
        node: og.Node,
        attributes,
        gpu_bundles: List[str],
        read_only: bool = False,
        gpu_ptr_kinds: Optional[Dict[str, og.PtrToPtrKind]] = None,
    ):
        """Set up the list of members based on the list of node attributes. These will usually be a subset,
        e.g. just the inputs, to keep the higher level access simple

        Args:
            context (GraphContext): Evaluation context for these bundles
            node (Node): Owner of these bundles
            attributes (list[Attribute]): Subset of node attributes to check for being bundles
            gpu_bundles (list[str]): Subset of bundle attributes whose memory lives on the GPU
            read_only (bool): True if these attributes are read-only
            gpu_ptr_kinds (dict[str, PtrToPtrKind]): Attribute array pointer locations for GPU-based array attributes
        """
        for property_name in vars(attributes):
            attribute = getattr(attributes, property_name)
            if not isinstance(attribute, og.Attribute):
                continue
            if attribute.get_type_name() == "bundle":
                attribute_name = attribute.get_name()
                gpu_by_default = attribute_name in gpu_bundles
                gpu_ptr_kind = og.PtrToPtrKind.GPU if gpu_by_default else og.PtrToPtrKind.NA
                if gpu_ptr_kinds is not None and attribute_name in gpu_ptr_kinds:
                    gpu_ptr_kind = gpu_ptr_kinds[attribute_name]
                full_name = attribute_name
                setattr(
                    self,
                    ogn.attribute_name_as_python_property(full_name),
                    BundleContents(context, node, full_name, read_only, gpu_by_default, gpu_ptr_kind),
                )


# ================================================================================
class Bundle:
    """----- FOR USE BY GENERATED CODE ONLY -----

    Deferred implementation of the bundle concept
    """

    def __init__(self, attribute_name: str, read_only: bool):
        """Initialize the access points for the bundle attribute

        Args:
            attribute_name: the bundle's name. This name will only be used if the bundle is nested.
            read_only: Is the bundle data read-only?
        """
        self.__buffer: Dict[str, Union[Bundle, OmniAttribute]] = {}
        self.__delete_buffer: Set[str] = set()
        self._bundle_contents = None
        self._attribute_name = attribute_name
        self.read_only = read_only

    # ------------------------------------------------------------------------------------------
    @classmethod
    def from_accessor(cls, bundle_contents: BundleContents):
        """-------- FOR GENERATED CODE USE ONLY --------
        Convert a BundleContents object to a python Bundle.

        Args:
            bundle_contents: the graph object representing the bundle
        """
        bundle = cls("bundle", False)
        if bundle_contents.valid:
            bundle._bundle_contents = bundle_contents
        return bundle

    # ------------------------------------------------------------------------------------------
    @property
    def runtime_accessor(self) -> BundleContents:
        """exposes the runtime bundle accessor.

        Returns:
            the BundleContents object if it exists, None otherwise.
        """
        return self._bundle_contents

    # ------------------------------------------------------------------------------------------
    def create_attribute(self, name: str, type_desc: type) -> OmniAttribute:
        """Create an attribute inside the buffered bundle data structure

        Args:
            name: name of the attribute to create
            type_desc: python type object of the attribute to create. Accepts all Omnigraph types.
                       Will attempt to convert non-omnigraph types, but raise an error if it fails.

        Returns:
            the OmniAttribute it created.

        Raises:
            OmniGraphError if no type conversion was found.
        """
        attr = OmniAttribute(name, type_desc)
        self.insert(attr)
        return attr

    # ------------------------------------------------------------------------------------------
    @property
    def is_runtime_resident(self):
        """bool: Does the bundle content exist and is it valid"""
        return self._bundle_contents is not None and self._bundle_contents.valid

    # ------------------------------------------------------------------------------------------
    @property
    def size(self) -> int:
        """int: Returns the number of attributes within this bundle, 0 if the bundle is not valid"""
        return len(self.attribute_names)

    # ------------------------------------------------------------------------------------------
    @property
    def valid(self) -> Optional[bool]:
        """bool: Is the underlying bundle valid, or None if it does not even exist"""
        if self.is_runtime_resident:
            return self._bundle_contents.valid

        return None

    # ------------------------------------------------------------------------------------------
    @non_const
    def clear(self):
        """Empties out the bundle contents

        Raises:
            og.OmniGraphError: if the bundle is not writable
        """
        # Silently accept that clearing an invalid bundle is a null operation
        if self.is_runtime_resident:
            for attr in self._bundle_contents.attributes:
                self.__delete_buffer.add(attr)
        else:
            self.__buffer.clear()

    # ------------------------------------------------------------------------------------------
    @non_const
    def insert(self, to_insert: Union[Bundle, OmniAttribute, Tuple[OmniAttribute, str], AttributeDescription]):
        """Insert new content in the existing bundle

        Args:
            to_insert: Object to insert. It can be one of three different types of object:

                *Bundle*: Another bundle, whose contents are entirely copied into this one

                *RuntimeAttribute*: A single attribute from another bundle to be copied with the same name

                *(RuntimeAttribute, str)*: A single attribute from another bundle and the name to use for the copy

                *AttributeDescription*: Information required to create a brand new typed attribute

        Returns:
            Attribute object of the new attribute if inserting an attribute, else None
        """
        name = to_insert.name
        if isinstance(to_insert, Bundle):
            self.__buffer[to_insert.attribute_name] = to_insert
            self.__delete_buffer.discard(name)
            return to_insert
        if isinstance(to_insert, OmniAttribute):
            self.__buffer[to_insert.name] = to_insert
            self.__delete_buffer.discard(name)
            return to_insert

        raise og.OmniGraphError(f"Unknown type of object being inserted into a bundle ({to_insert})")

    # ------------------------------------------------------------------------------------------
    def attribute_by_name(self, attribute_name: str) -> Optional[RuntimeAttribute]:
        """
        Get an attribute by name from the underlying buffer or the buffer masking it.

        Args:
            attribute_name: the attribute being queried.

        Returns:
            the named attribute within the bundle, or None if no such attribute exists in the bundle"""
        if attribute_name in self.__delete_buffer:
            return None
        if attribute_name in self.__buffer:
            return self.__buffer.get(attribute_name, None)
        if self.is_runtime_resident:
            attr = self._bundle_contents.attribute_by_name(attribute_name)
            if attr is None:
                return None
            self.__buffer[attribute_name] = attr
            return attr
        return None

    # ------------------------------------------------------------------------------------------
    def remove(self, attribute_name: str):
        """Removes the attribute with the given name from the bundle, silently succeeding if it is not in the bundle.

        Args:
            attribute_name: attribute to be deleted.

        """
        if self.is_runtime_resident:
            self.__delete_buffer.add(attribute_name)
        else:
            self.__buffer.pop(attribute_name, None)

    # --------------------------------------------------------------------------------------------
    @property
    def name(self):
        """The bundle's name"""
        return self._attribute_name

    # ------------------------------------------------------------------------------------------
    @property
    def attribute_names(self) -> List[OmniAttribute]:
        """Returns the list of interface objects corresponding to the attributes contained within the bundle"""
        attributes = set(self.__buffer)
        if self.is_runtime_resident:
            attributes.update(attr.name for attr in self._bundle_contents.attributes)
        for name in self.__delete_buffer:
            attributes.discard(name)
        return list(attributes)


# ================================================================================
class OmniAttribute:
    """----- FOR USE BY GENERATED CODE ONLY -----
    Simple attribute type to use for python bundles
    """

    def __init__(self, name: str, type_desc: type, read_only: bool = False, required: bool = True):
        self.__name = name
        self.__value = None
        self.__type_desc = type_desc
        self.__metadata = {}

        self._runtime_attr = None

        self.required = required
        self.read_only = read_only

    # ------------------------------------------------------------------------------------------
    @property
    def name(self):
        """The attribute's name"""
        return self.__name

    # ------------------------------------------------------------------------------------------
    @property
    def is_runtime_resident(self) -> bool:
        """Property indidcating whether the attribute represents a concrete graph/fastcache attribtue."""
        return self._runtime_attr is not None

    # ------------------------------------------------------------------------------------------
    @property
    def runtime_accessor(self) -> RuntimeAttribute:
        return self._runtime_attr

    # ------------------------------------------------------------------------------------------
    @property
    def is_dirty(self) -> bool:
        """Whether the python representation of this value needs to update the graph representation"""
        return not self.is_runtime_resident and self.__value is not None

    # ------------------------------------------------------------------------------------------
    @property
    def metadata(self):
        return self.__metadata

    # ------------------------------------------------------------------------------------------
    @property
    def type(self):  # noqa: A003
        return self.__type_desc

    # ------------------------------------------------------------------------------------------
    @property
    def value(self):
        """Get the local value, if it masks the underlying context representation value.
        Otherwise get the value from the context representation.
        """
        if self.is_runtime_resident:
            return self.__value or self._runtime_attr.value
        return self.__value

    # ------------------------------------------------------------------------------------------
    @value.setter
    def value(self, val: Any):
        self.__value = val


# ================================================================================


class BundleWriteBlock:
    """Creates a thread-local scope to ensure that each bundle
    is marked as changed only once, regardless of the number of
    operations performed within the block.

    This optimization is an integral part of the bundle change tracking system,
    designed to minimize overhead associated with high-volume operations
    during frequent bundle manipulations.

    Example usage:

    with omni.graph.core.BundleWriteBlock(graph_context):
        # ...each bundle written to will be bumped exactly once...

    You can optionally pass in a second parameter to deactivate the block:

    with omni.graph.core.BundleWriteBlock(graph_context, False):
        # ...the block is not active here...

    """

    def __init__(self, context: og.GraphContext, activate=True):
        self.scope_id = None
        self.idirtyid = og._og_unstable.IDirtyID3.create(context) if activate else None  # noqa: PLW0212

    def __enter__(self):
        if self.idirtyid is not None:
            self.scope_id = self.idirtyid.open()
        return self

    def __exit__(self, _type, _value, _traceback):
        if self.scope_id:
            self.idirtyid.close(self.scope_id)
            self.scope_id = None

    def __bool__(self):
        return self.scope_id is not None
