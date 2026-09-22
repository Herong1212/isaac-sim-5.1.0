# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = [
    "IntModel",
    "FloatModel",
    "UsdAttributeModel",
    "GfVecAttributeSingleChannelModel",
    "TfTokenAttributeModel",
    "MdlEnumAttributeModel",
    "GfVecAttributeModel",
    "SdfAssetPathAttributeModel",
    "SdfAssetPathArrayAttributeSingleEntryModel",
    "SdfAssetPathArrayAttributeItemModel",
    "GfQuatAttributeModel",
    "GfQuatEulerAttributeModel",
    "GfMatrixAttributeModel",
    "UsdAttributeInvertedModel",
    "SdfTimeCodeModel",
]

import copy
import weakref
from typing import List
from urllib.parse import unquote

import omni.ui as ui
import omni.usd
from pxr import Ar, Gf, Sdf, Tf, Usd, UsdShade

from .usd_model_base import PlaceholderAttribute, StageAdapter, UsdBase
from .usd_model_items import (
    AllowedTokenItem,
    InvalidTokenItem,
    OptionItem,
    SdfAssetPathItem,
    UsdFloatItem,
    UsdMatrixItem,
    UsdQuatItem,
    UsdVectorItem,
)


class FloatModel(ui.SimpleFloatModel):
    """A model providing a simple interface for a floating-point value.

    This model is a thin wrapper around a float, allowing for easy integration with UI components that require a model to represent and manipulate floating-point numbers. It is particularly useful for scenarios where a float value needs to be observed or edited within a user interface.

    Args:
        parent: A weak reference to the parent of this model, allowing this model to notify the parent about changes to the value.
    """

    def __init__(self, parent):
        """Initializes a new instance of the FloatModel."""
        super().__init__()
        self._parent = weakref.ref(parent)

    def begin_edit(self):
        """Begins editing the value."""
        parent = self._parent()
        parent.begin_edit(None)

    def end_edit(self):
        """Ends editing the value."""
        parent = self._parent()
        parent.end_edit(None)


class IntModel(ui.SimpleIntModel):
    """A model providing a simple interface for a integer value.

    This model is a thin wrapper around a float, allowing for easy integration with UI components that require a model to represent and manipulate floating-point numbers. It is particularly useful for scenarios where a float value needs to be observed or edited within a user interface.

    Args:
        parent: A weak reference to the parent of this model, allowing this model to notify the parent about changes to the value.
    """

    def __init__(self, parent):
        """Initializes a new instance of the IntModel."""
        super().__init__()
        self._parent = weakref.ref(parent)

    def begin_edit(self):
        """Begins editing the value."""
        parent = self._parent()
        parent.begin_edit(None)

    def end_edit(self):
        """Ends editing the value."""
        parent = self._parent()
        parent.end_edit(None)


class BoolModel(ui.SimpleBoolModel):
    """A model providing a simple interface for a boolean value.

    This model is a thin wrapper around a float, allowing for easy integration with UI components that require a model to represent and manipulate floating-point numbers. It is particularly useful for scenarios where a float value needs to be observed or edited within a user interface.

    Args:
        parent: A weak reference to the parent of this model, allowing this model to notify the parent about changes to the value.
    """

    def __init__(self, parent):
        super().__init__()
        self._parent = weakref.ref(parent)

    def begin_edit(self):
        """Begins editing the value."""
        parent = self._parent()
        parent.begin_edit(None)

    def end_edit(self):
        """Ends editing the value."""
        parent = self._parent()
        parent.end_edit(None)


class UsdAttributeModel(ui.AbstractValueModel, UsdBase):
    """A value model that re-implements the AbstractValueModel interface in Python to observe a USD attribute path.

    Args:
        stage (:obj:`Usd.Stage`): The stage that contains the USD attribute.
        attribute_paths (List[:obj:`Sdf.Path`]): A list of paths to the USD attributes to be observed.
        self_refresh (bool): Whether the model should automatically refresh its value when changes occur in USD.
        metadata (dict): A dictionary of metadata relevant to the USD attribute.
        change_on_edit_end (bool): Indicates if the value should only change when the edit ends.

    Keyword Args:
        treat_array_entry_as_comp (bool): Treat array entries as components of a single value.
        is_normal_attribute (bool): Specify if the attribute is a normal attribute.

    This model provides a clean interface to interact with USD attributes, offering functions to begin and end edits, get and set attribute values in various data types, and handle value changes and updates.
    """

    def __init__(
        self,
        stage: Usd.Stage,
        attribute_paths: List[Sdf.Path],
        self_refresh: bool,
        metadata: dict,
        change_on_edit_end=True,
        **kwargs,
    ):
        """Initializes the value model that is reimplemented in Python to watch a USD attribute path."""
        UsdBase.__init__(self, stage, attribute_paths, self_refresh, metadata, change_on_edit_end, **kwargs)
        ui.AbstractValueModel.__init__(self)

    def clean(self):
        """Cleans up the model by delegating to the base clean-up method."""
        UsdBase.clean(self)

    def begin_edit(self):
        """Begins an editing session by notifying the USD base and the UI model."""
        UsdBase.begin_edit(self)
        ui.AbstractValueModel.begin_edit(self)

    def end_edit(self):
        """Ends an editing session by notifying the USD base and the UI model."""
        UsdBase.end_edit(self)
        ui.AbstractValueModel.end_edit(self)

    def get_value_as_string(self, elide_big_array=True) -> str:
        """Retrieves the value of the USD attribute as a string.

        Args:
            elide_big_array (bool): If True, elides long array displays.

        Returns:
            str: The attribute value formatted as a string."""
        self._update_value()
        if self._value is None:
            return ""
        if self._is_big_array and elide_big_array:
            return "[...]"
        return str(self._value)

    def get_value_as_float(self) -> float:
        """Retrieves the value of the USD attribute as a float.

        Returns:
            float: The attribute value as a float."""
        self._update_value()
        if self._value is None:
            return 0.0

        if self.is_value_array():
            return float(self._value[self._channel_index])
        return float(self._value)

    def get_value_as_bool(self) -> bool:
        """Retrieves the value of the USD attribute as a boolean.

        Returns:
            bool: The attribute value as a boolean."""
        self._update_value()
        if self._value is None:
            return False

        if self.is_value_array():
            return bool(self._value[self._channel_index])
        return bool(self._value)

    def get_value_as_int(self) -> int:
        """Retrieves the value of the USD attribute as an integer.

        Returns:
            int: The attribute value as an integer."""
        self._update_value()
        if self._value is None:
            return 0

        if self.is_value_array():
            return int(self._value[self._channel_index])
        return int(self._value)

    def set_value(self, value, comp: int = -1):
        """Sets the value of the USD attribute.

        Args:
            value: New value to set the attribute to.
            comp (int): Optional index for the component of the value to set."""
        if UsdBase.set_value(self, value):
            self._value_changed()

    def _on_dirty(self):
        self._value_changed()


class GfVecAttributeSingleChannelModel(UsdAttributeModel):
    """A model for handling single channel vector attributes in USD.

    This model is a specialized version of `UsdAttributeModel` that focuses on a single channel of a vector attribute.
    It is designed to be used with vector types such as GfVec3f where only one component of the vector is relevant at a time.

    Args:
        stage (:obj:`Usd.Stage`): The USD stage containing the attributes to be managed.
        attribute_paths (List[:obj:`Sdf.Path`]): A list of USD attribute paths for which the model is responsible.
        channel_index (int): The index of the channel in the vector to be managed by this model.
        self_refresh (bool): Whether the model should update itself automatically when changes occur.
        metadata (dict): A dictionary containing metadata information for the attribute.
        change_on_edit_end (bool): Whether the value of the attribute should only change when the user finishes editing.

    Keyword Args:
        treat_array_entry_as_comp (bool): Treats the array entry as a separate component if set to True.
    """

    def __init__(
        self,
        stage: Usd.Stage,
        attribute_paths: List[Sdf.Path],
        channel_index: int,
        self_refresh: bool,
        metadata: dict,
        change_on_edit_end=True,
        **kwargs,
    ):
        """Initializer for GfVecAttributeSingleChannelModel."""
        self._channel_index = channel_index
        super().__init__(stage, attribute_paths, self_refresh, metadata, change_on_edit_end, **kwargs)

    def is_value_array(self):
        """Indicates if the value is an array.

        Returns:
            bool: True if the value is an array, otherwise False."""
        return True

    def get_value_as_string(self, elide_big_array=True) -> str:
        """Retrieves the value as a string.

        Args:
            elide_big_array (bool): If True, elide arrays that are too large.

        Returns:
            str: The value of the attribute as a string."""
        self._update_value()
        if self._value is None:
            return ""

        return str(self._value[self._channel_index])

    def get_value_as_float(self) -> float:
        """Retrieves the value as a float.

        Returns:
            float: The value of the attribute as a float."""
        self._update_value()
        if self._value is None:
            return 0.0

        if self.is_value_array():
            return float(self._value[self._channel_index])
        return float(self._value)

    def get_value_as_bool(self) -> bool:
        """Retrieves the value as a boolean.

        Returns:
            bool: The value of the attribute as a boolean."""
        self._update_value()
        if self._value is None:
            return False

        if self.is_value_array():
            return bool(self._value[self._channel_index])
        return bool(self._value)

    def get_value_as_int(self) -> int:
        """Retrieves the value as an integer.

        Returns:
            int: The value of the attribute as an integer."""
        self._update_value()
        if self._value is None:
            return 0

        if self.is_value_array():
            return int(self._value[self._channel_index])
        return int(self._value)

    def set_value(self, value, comp: int = -1):
        """Sets the value of the attribute.

        Args:
            value: The new value to set.
            comp (int): The component index to set, -1 if not component-specific."""
        vec_value = copy.copy(self._value)
        vec_value[self._channel_index] = value

        if UsdBase.set_value(self, vec_value, self._channel_index):
            self._value_changed()

    def is_different_from_default(self):
        """Checks if the current value is different from the default value.

        Returns:
            bool: True if different, otherwise False."""
        if super().is_different_from_default():
            return self._comp_different_from_default[self._channel_index]
        return False


class BoolArrayAttributeSingleChannelModel(GfVecAttributeSingleChannelModel):
    """A model for handling single channel boolean array attributes in USD.

    This model extends the `GfVecAttributeSingleChannelModel` to specifically handle boolean array attributes.
    It provides functionality to set and get boolean values for a single channel of a boolean array attribute.
    """

    def __init__(
        self,
        stage: Usd.Stage,
        attribute_paths: List[Sdf.Path],
        channel_index: int,
        self_refresh: bool,
        metadata: dict,
        change_on_edit_end=True,
        **kwargs,
    ):
        """
        Initializer for BoolArrayAttributeSingleChannelModel.

        Args:
            stage (:obj:`Usd.Stage`): The USD stage containing the attributes to be managed.
            attribute_paths (List[:obj:`Sdf.Path`]): A list of USD attribute paths for which the model is responsible.
            channel_index (int): The index of the channel in the vector to be managed by this model.
            self_refresh (bool): Whether the model should update itself automatically when changes occur.
            metadata (dict): A dictionary containing metadata information for the attribute.
            change_on_edit_end (bool): Whether the value of the attribute should only change when the user finishes editing.
        """
        super().__init__(
            stage,
            attribute_paths,
            channel_index,
            self_refresh,
            metadata,
            change_on_edit_end,
            treat_array_entry_as_comp=True,
            **kwargs,
        )

    def set_value(self, value, comp: int = -1):
        """Sets the value of the attribute.

        Args:
            value: The new value to set.
            comp (int): The component index to set, -1 if not component-specific."""
        # convert to list because Vt.BoolArray cannot be pickled.
        vec_value = list(self._value)
        vec_value[self._channel_index] = value

        if UsdBase.set_value(self, vec_value, self._channel_index):
            self._value_changed()
            return True

        return False


class TfTokenAttributeModel(ui.AbstractItemModel, UsdBase):
    """A model for managing USD attributes of type 'TfToken'.

    This model allows for the interaction and manipulation of TfToken attributes within a USD stage. It keeps track of
    allowed tokens and provides functionality for selecting and updating the value of the attribute based on the
    allowed set of tokens.

    Args:
        stage (:obj:`Usd.Stage`): The USD stage where the attribute is located.
        attribute_paths (List[:obj:`Sdf.Path`]): The list of attribute paths to be managed by the model.
        self_refresh (bool): A flag indicating whether the model should automatically update itself when changes occur.
        metadata (dict): A dictionary containing metadata associated with the attribute.

    Keyword Args:
        change_on_edit_end (bool): A flag indicating whether the model should only apply changes when an edit ends.
        ambiguous (bool): A flag indicating whether the attribute has ambiguous values (true for multi-selection).
        treat_as_asset_path (bool): A flag indicating if the attribute should be treated as an asset path.
        treat_array_entry_as_comp (bool): A flag indicating whether array entries should be treated as components.
        allowed_tokens (List[str]): A list of strings representing the allowed tokens for the attribute.

    The model is a combination of ui.AbstractItemModel and UsdBase, which allows for both UI interaction and
    underlying USD functionality."""

    DUPLICATE_TAG = "** DUPLICATE **"
    """str: Represents a duplicate token, used when ui.Combobox's have duplicate items."""

    def __init__(self, stage: Usd.Stage, attribute_paths: List[Sdf.Path], self_refresh: bool, metadata: dict, **kwargs):
        """Initializer for TfTokenAttributeModel."""
        UsdBase.__init__(self, stage, attribute_paths, self_refresh, metadata, **kwargs)
        ui.AbstractItemModel.__init__(self)

        self._allowed_tokens = []

        self._current_index = ui.SimpleIntModel()
        self._current_index.add_value_changed_fn(self._current_index_changed)

        self._updating_value = False

        self._has_index = False
        self._update_value()
        self._has_index = True

    def clean(self):
        """Cleans up the model, removing any cached data."""
        UsdBase.clean(self)

    def get_item_children(self, item):
        """Retrieves the children of a given item in the model.

        Args:
            item: The item whose children are to be retrieved.

        Returns:
            list: A list of the allowed tokens."""
        self._update_value()

        # handle invalid values
        value = self._value or self.get_value_as_token()
        if (value is not None) and (value not in [item.token for item in self._allowed_tokens]):
            self._allowed_tokens.insert(0, InvalidTokenItem(value))

        return self._allowed_tokens

    def get_item_value_model(self, item, column_id):
        """Gets the value model associated with a given item and column.

        Args:
            item: The item for which to retrieve the value model.
            column_id (int): The column identifier.

        Returns:
            ui.AbstractValueModel: The value model for the specified item and column."""
        if item is None:
            return self._current_index

        return item.model

    def begin_edit(self, item=None):
        """Begins an edit operation on the model.

        Args:
            item: The item being edited."""
        UsdBase.begin_edit(self)

    def end_edit(self, item=None):
        """Ends an edit operation on the model.

        Args:
            item: The item that was edited."""
        UsdBase.end_edit(self)

    def _current_index_changed(self, model):
        if not self._has_index:
            return

        # if we're updating from USD notice change to UI, don't call set_value
        if self._updating_value:
            return

        index = model.as_int
        if self.set_value(self._get_value_from_index(index)):
            self._item_changed(None)

    def _get_allowed_tokens(self, attr):
        allowed_tokens = []
        token_list = attr.GetMetadata("allowedTokens") or self.metadata.get("allowedTokens", [])
        if token_list:
            for t in token_list:
                if t in allowed_tokens:
                    allowed_tokens.append(
                        f"{TfTokenAttributeModel.DUPLICATE_TAG} {t} {TfTokenAttributeModel.DUPLICATE_TAG}"
                    )
                else:
                    allowed_tokens.append(t)
        return allowed_tokens

    def _update_allowed_token(self, token_item=AllowedTokenItem):
        allowed_tokens = []

        for path in self._object_paths:
            self._valid_stage = self.get_valid_stage_adapter_write(path)
            if self._valid_stage:
                attr = self._valid_stage.GetAttributeAtPath(path)
                if attr:
                    if attr.IsHidden():
                        continue
                else:
                    prim = self._valid_stage.GetPrimAtPath(path.GetPrimPath())
                    attr = PlaceholderAttribute(name=path.name, prim=prim, metadata=self._metadata)

                tokens = self._get_allowed_tokens(attr)
                if tokens:
                    for t in tokens:
                        allowed_tokens.append(t)
        # should kept the order
        self._allowed_tokens = [token_item(t) for t in list(dict.fromkeys(allowed_tokens))]

    def _update_value(self, force=False):
        was_updating_value = self._updating_value
        self._updating_value = True
        if UsdBase._update_value(self, force):
            # TODO don't have to do this every time. Just needed when "allowedTokens" actually changed
            self._update_allowed_token()

            index = self._update_index()
            if index not in (-1, self._current_index.as_int):
                self._current_index.set_value(index)
                self._item_changed(None)
        self._updating_value = was_updating_value

    def _on_dirty(self):
        self._item_changed(None)

    def get_value_as_token(self):
        """Retrieves the current value as a token.

        Returns:
            str: The current value as a token or None if the current index is not valid."""
        index = self._current_index.as_int
        if 0 <= index < len(self._allowed_tokens):
            return self._allowed_tokens[index].token
        return None

    def is_allowed_token(self, token):
        """Checks if a token is allowed in the model.

        Args:
            token (str): The token to check.

        Returns:
            bool: True if the token is allowed, False otherwise."""
        if token.startswith(TfTokenAttributeModel.DUPLICATE_TAG) and token.endswith(
            TfTokenAttributeModel.DUPLICATE_TAG
        ):
            return False
        return token in [allowed.token for allowed in self._allowed_tokens if isinstance(allowed, AllowedTokenItem)]

    def set_value(self, value, comp: int = -1) -> bool:
        """Sets the value of the model.

        Args:
            value (str): The value to set in the model.
            comp (int): An optional component index when dealing with vector types."""
        if self.is_allowed_token(value) and super().set_value(value, comp):
            self._item_changed(None)
            return True
        return False

    def _get_value_from_index(self, index):
        return self._allowed_tokens[index].token

    def _update_index(self):
        index = -1
        for i, item in enumerate(self._allowed_tokens):
            if item.token == self._value:
                index = i
        return index


class MdlEnumAttributeModel(ui.AbstractItemModel, UsdBase):
    """A model representing an enumeration attribute in USD.

    This model provides an abstraction over a USD attribute that represents an enumeration. It allows querying and setting of the enumeration value, as well as observing changes to the enumeration option.

    Args:
        stage (:obj:`Usd.Stage`): The stage that the attribute is associated with.
        attribute_paths (List[Sdf.Path]): The list of attribute paths that this model is watching.
        self_refresh (bool): Whether the model should automatically refresh its value when changes occur.
        metadata (dict): A dictionary containing metadata for the model.

    Keyword Args:
        change_on_edit_end (bool): Whether to apply changes only when editing ends.
        treat_array_entry_as_comp (bool): Whether to treat array entries as components.

    """

    def __init__(self, stage: Usd.Stage, attribute_paths: List[Sdf.Path], self_refresh: bool, metadata: dict, **kwargs):
        """Initializes the MdlEnumAttributeModel with a USD stage and attribute paths."""
        UsdBase.__init__(self, stage, attribute_paths, self_refresh, metadata, **kwargs)
        ui.AbstractItemModel.__init__(self)

        self._options = []

        self._current_index = ui.SimpleIntModel()
        self._current_index.add_value_changed_fn(self._current_index_changed)

        self._updating_value = False

        self._has_index = False
        self._update_value()
        self._has_index = True

    def clean(self):
        """Cleans the internal state of the model."""
        UsdBase.clean(self)

    def get_item_children(self, item):
        """Retrieves the child items of the given item.

        Args:
            item: The item to retrieve children for."""
        self._update_value()
        return self._options

    def get_item_value_model(self, item, column_id):
        """Gets the value model for the given item and column ID.

        Args:
            item: The item to retrieve the value model for.
            column_id (int): The ID of the column."""
        if item is None:
            return self._current_index

        return item.model

    def begin_edit(self, item=None):
        """Begins an editing session for the given item.

        Args:
            item: The item to begin editing."""
        UsdBase.begin_edit(self)

    def end_edit(self, item=None):
        """Ends an editing session for the given item.

        Args:
            item: The item to end editing."""
        UsdBase.end_edit(self)

    def _current_index_changed(self, model):
        if not self._has_index:
            return

        # if we're updating from USD notice change to UI, don't call set_value
        if self._updating_value:
            return

        index = model.as_int
        if self.set_value(self._options[index].value):
            self._item_changed(None)

    def _update_option(self):
        self._options = []

        # For multi prim editing, the options should all be the same
        attributes = self._get_attributes()
        attr = attributes[0] if len(attributes) > 0 else None
        if not attr:
            return

        is_usd_attribute = isinstance(attr, Usd.Attribute)
        if not is_usd_attribute:
            # If adapter is enabled, omni.kit.property.adapter.fabric.scripts.fabric_adapter.FabricAttributeAdapter is used instead of Usd.Attribute
            # But it is not public, so use GetPropertyType for checking
            import carb.settings

            adapter_enabled = carb.settings.get_settings().get("/ext/omni.kit.property.usd/enableAdapter")
            if adapter_enabled and hasattr(attr, "GetPropertyType"):
                property_type = attr.GetPropertyType()
                from omni.kit.property.adapter.core import PropertyType

                is_usd_attribute = property_type == PropertyType.ATTRIBUTE

        if not is_usd_attribute and not isinstance(attr, PlaceholderAttribute):
            return

        options = []

        # If attribute exists get the options from the attribute's SDR metadata.
        # This allows us to edit the exposed options.
        if is_usd_attribute:
            sdr_metadata = attr.GetMetadata(UsdShade.Tokens.sdrMetadata) or {}
            options = sdr_metadata.get("options", [])

        # If options has not been set then get them from the models SDR metadata.
        if not options and self.metadata:
            sdr_metadata = self.metadata.get(UsdShade.Tokens.sdrMetadata, {})
            options = sdr_metadata.get("options", [])

        if options and isinstance(options, str):
            options = options.split("|")
            for idx, option in enumerate(options):
                (k, v) = option.split(":")
                options[idx] = (k, int(v))

        for kv in options:
            self._options.append(OptionItem(kv[0], kv[1]))

    def _update_value(self, force=False):
        was_updating_value = self._updating_value
        self._updating_value = True
        if UsdBase._update_value(self, force):
            # TODO don't have to do this every time. Just needed when "option" actually changed
            self._update_option()

            index = -1
            for i, item in enumerate(self._options):
                if item.value == self._value:
                    index = i

            if index not in (-1, self._current_index.as_int):
                self._current_index.set_value(index)
                self._item_changed(None)
        self._updating_value = was_updating_value

    def _on_dirty(self):
        self._item_changed(None)

    def get_value_as_string(self):
        """Gets the value of the model as a string."""
        index = self._current_index.as_int
        return self._options[index].model.as_string

    def is_allowed_enum_string(self, enum_str):
        """Checks if the given enum string is allowed.

        Args:
            enum_str (str): The enum string to check."""
        return enum_str in [allowed.model.as_string for allowed in self._options]

    def set_from_enum_string(self, enum_str):
        """Sets the value of the model from the given enum string.

        Args:
            enum_str (str): The enum string to set."""
        if not self.is_allowed_enum_string(enum_str):
            return

        new_index = -1
        for index, option in enumerate(self._options):
            if option.model.as_string == enum_str:
                new_index = index
                break
        if new_index != -1:
            self._current_index.set_value(new_index)


class GfVecAttributeModel(ui.AbstractItemModel, UsdBase):
    """A model for representing and manipulating GfVec typed attributes in USD.

    This model handles vector attributes with a specified number of components and a given type from the Gf library. It provides functionality to interact with the attribute's value, including getting and setting the vector components.

    Args:
        stage (:obj:`Usd.Stage`): The USD stage containing the attribute.
        attribute_paths (List[:obj:`Sdf.Path`]): A list of attribute paths to be managed by the model.
        comp_count (int): The number of components in the vector.
        tf_type (:obj:`Tf.Type`): The type of the vector from the Gf library.
        self_refresh (bool): Whether the model should refresh itself automatically.
        metadata (dict): Additional metadata associated with the attribute.

    Keyword Args:
        change_on_edit_end (bool): Whether to apply changes only when editing is finished.
        treat_array_entry_as_comp (bool): Treat array entries as components of the vector."""

    def __init__(
        self,
        stage: Usd.Stage,
        attribute_paths: List[Sdf.Path],
        comp_count: int,
        tf_type: Tf.Type,
        self_refresh: bool,
        metadata: dict,
        **kwargs,
    ):
        """Initializer for GfVecAttributeModel."""
        UsdBase.__init__(self, stage, attribute_paths, self_refresh, metadata, **kwargs)
        ui.AbstractItemModel.__init__(self)
        self._comp_count = comp_count
        self._data_type_name = "Vec" + str(self._comp_count) + tf_type.typeName[-1]
        self._data_type = getattr(Gf, self._data_type_name)

        # Create root model
        self._root_model = ui.SimpleIntModel()
        self._root_model.add_value_changed_fn(lambda a: self._on_value_changed(None))

        # Create three models per component
        if self._data_type_name.endswith("i"):
            self._items = [UsdVectorItem(IntModel(self)) for i in range(self._comp_count)]
        else:
            self._items = [UsdVectorItem(FloatModel(self)) for i in range(self._comp_count)]
        for item in self._items:
            item.model.add_value_changed_fn(lambda a, item=item: self._on_value_changed(item))

        self._edit_mode_counter = 0

    def clean(self):
        """Cleans up the model removing any stored data."""
        UsdBase.clean(self)

    def construct_vector_from_item(self):
        """Constructs a vector from the submodels.

        Returns:
            :obj:`Gf.Vec`: The constructed vector."""
        if self._data_type_name.endswith("i"):
            data = [item.model.get_value_as_int() for item in self._items]
        else:
            data = [item.model.get_value_as_float() for item in self._items]
        return self._data_type(data)

    def _on_value_changed(self, item):
        """Called when the submodel is changed.

        Args:
            item: The item that changed."""

        if self._edit_mode_counter > 0:
            vector = self.construct_vector_from_item()
            index = self._items.index(item)
            if vector and self.set_value(vector, index):
                # Read the new value back in case hard range clamped it
                item.model.set_value(self._value[index])
                self._item_changed(item)
            else:
                # If failed to update value in model, revert the value in submodel
                item.model.set_value(self._value[index])

    def _update_value(self, force=False):
        """Updates the value of the model.

        Args:
            force (bool): Whether to force the update."""
        if UsdBase._update_value(self, force):
            if not self._value:
                for item in self._items:
                    item.model.set_value(0.0)
                return
            for i, item in enumerate(self._items):
                item.model.set_value(self._value[i])

    def _on_dirty(self):
        self._item_changed(None)

    def get_item_children(self, item):
        """Returns the child items of the given item.

        Args:
            item: The item whose children to retrieve."""
        self._update_value()
        return self._items

    def get_item_value_model(self, item, column_id):
        """Retrieves the value model for the given item and column.

        Args:
            item: The item for which to retrieve the model.
            column_id: The ID of the column."""
        if item is None:
            return self._root_model
        return item.model

    def begin_edit(self, item=None):
        """Begins an edit operation on the given item.

        Args:
            item: The item to begin editing."""
        self._edit_mode_counter += 1
        UsdBase.begin_edit(self)

    def end_edit(self, item=None):
        """Ends an edit operation on the given item.

        Args:
            item: The item to end editing."""

        UsdBase.end_edit(self)
        self._edit_mode_counter -= 1

    def set_value(self, value, comp: int = -1) -> bool:
        if super().set_value(value, comp):
            self._item_changed(None)
            return True
        return False

    _construct_vector_from_item = construct_vector_from_item


class SdfAssetPathAttributeModel(UsdAttributeModel):
    """A value model for monitoring USD asset path attributes.

    This model is specifically designed to handle the Sdf.AssetPath attribute type in USD, providing
    additional functionality to resolve and validate asset paths.

    Args:
        stage (:obj:`Usd.Stage`): The USD stage associated with the attribute.
        attribute_paths (List[:obj:`Sdf.Path`]): A list of Sdf.Path objects representing the attribute paths to monitor.
        self_refresh (bool): Indicates whether the model should refresh itself when the attribute value changes.
        metadata (dict): Additional metadata that may be needed for the model.

    Keyword Args:
        treat_array_entry_as_comp (bool): If True, treat array entries as individual components. Default is False.

    """

    def __init__(self, stage: Usd.Stage, attribute_paths: List[Sdf.Path], self_refresh: bool, metadata: dict, **kwargs):
        """Constructor for SdfAssetPathAttributeModel."""
        super().__init__(stage, attribute_paths, self_refresh, metadata, True, treat_array_entry_as_comp=True, **kwargs)

    def get_value_as_string(self, elide_big_array=True) -> str:
        """Gets the string representation of the asset path value.

        Args:
            elide_big_array (bool): If True, large arrays will be shortened in the representation.

        Returns:
            str: The string representation of the asset path value."""
        self._update_value()
        return self._get_value_as_string(self._value)

    def is_valid_path(self) -> bool:
        """Determines if the stored asset path is valid.

        Returns:
            bool: True if the path is valid, False otherwise."""
        return self._is_valid_path(self._value)

    def get_resolved_path(self):
        """Gets the resolved path of the asset.

        Returns:
            str: The resolved asset path."""
        self._update_value()
        return self._get_resolved_path(self._value)

    def set_value(self, value, comp: int = -1, resolved_path: str = ""):
        """Sets the value of the asset path.

        Args:
            value (str): The new value for the asset path.
            comp (int): Component index when dealing with array attributes.
            resolved_path (str): The resolved path corresponding to the value."""
        if not isinstance(value, Sdf.AssetPath):
            if resolved_path:
                value = Sdf.AssetPath(value, resolved_path)
            else:
                value = Sdf.AssetPath(value)

        if UsdBase.set_value(self, value):
            self._value_changed()

    def _is_prev_same(self):
        # Strip the resolvedPath from the AssetPath for the comparison, since the prev values don't have resolvedPath.
        return [Sdf.AssetPath(value.path) for value in self._real_values] == self._prev_real_values

    def _save_real_values_as_prev(self):
        # Strip the resolvedPath from the AssetPath so that it can be recomputed.
        self._prev_real_values = [Sdf.AssetPath(value.path) for value in self._real_values]

    def _change_property(self, path: Sdf.Path, new_value, old_value):
        if path.name == "info:mdl:sourceAsset" and new_value.path and isinstance(new_value, Sdf.AssetPath):
            stage = omni.usd.get_context().get_stage()
            asset_path = new_value.path

            # compute the asset path relative to the root layer that is safe in Ar 1.0 and Ar 2.0
            asset_id = Sdf.ComputeAssetPathRelativeToLayer(stage.GetRootLayer(), asset_path)
            resolved_path = Ar.GetResolver().Resolve(asset_id)

            # make the path relative to current edit target layer
            relative_path = omni.usd.make_path_relative_to_current_edit_target(str(resolved_path))
            new_value = Sdf.AssetPath(relative_path, resolved_path)

        if path.name == "info:mdl:sourceAsset" and isinstance(new_value, Sdf.AssetPath):
            # "info:mdl:sourceAsset" when is changed update "info:mdl:sourceAsset:subIdentifier"
            stage = self.stage
            asset_attr = stage.GetAttributeAtPath(path)
            attr_path = path.AppendProperty("info:mdl:sourceAsset:subIdentifier")
            subid_attr = stage.GetAttributeAtPath(attr_path)
            if asset_attr and subid_attr:
                mdl_path = new_value.resolvedPath if new_value.resolvedPath else new_value.path
                if mdl_path:
                    import asyncio

                    baseclass = super()

                    def have_subids(id_list: list):
                        # pylint: disable=protected-access

                        if len(id_list) > 0:
                            with omni.kit.undo.group():
                                baseclass._change_property(subid_attr.GetPath(), str(id_list[0]), None)
                                baseclass._change_property(path, new_value, old_value)

                    asyncio.ensure_future(
                        omni.kit.material.library.get_subidentifier_from_mdl(
                            mdl_file=mdl_path, on_complete_fn=have_subids, use_functions=True, show_alert=True
                        )
                    )
                    return

                super()._change_property(subid_attr.GetPath(), "", None)

        super()._change_property(path, new_value, old_value)

    def _create_placeholder_attributes(self, attributes, on_create_fn=None):
        import inspect

        # some extensions use their own baseclass instead of UsdAttributeModel
        sig = inspect.signature(super()._create_placeholder_attributes)
        if "on_create_fn" in sig.parameters:

            def on_create_func(attr):
                omni.kit.commands.execute(
                    "ChangePropertyCommand",
                    prop_path=attr.GetPath(),
                    value=self.get_value(),
                    prev=type(self.get_value())(),
                )

            return super()._create_placeholder_attributes(attributes, on_create_fn=on_create_func)

        return super()._create_placeholder_attributes(attributes)

    # private functions to be shared with SdfAssetPathArrayAttributeSingleEntryModel
    def _get_value_as_string(self, value, **kwargs):
        return unquote(value.path) if value else ""

    def _is_valid_path(self, value) -> bool:
        if not value:
            return False
        path = value.resolvedPath
        # TODO: not sure why only support http url here, need Jihui to confirm
        if path.lower().startswith("http"):
            return False
        return bool(path)

    def _get_resolved_path(self, value):
        if self._ambiguous:
            return "Mixed"
        return value.resolvedPath.replace("\\", "/") if value else ""


class SdfAssetPathArrayAttributeSingleEntryModel(SdfAssetPathAttributeModel):
    """A model for a single entry in an array of SdfAssetPath attributes.

    This model represents an individual asset path entry within a larger array of SdfAssetPath attributes. It provides functionality to get and set the value of the asset path, as well as to check the validity of the path and retrieve the resolved path.

    Args:
        stage (:obj:`Usd.Stage`): The stage where the attribute is located.
        attribute_paths (List[:obj:`Sdf.Path`]): The paths to the attributes within the USD stage.
        index (int): The index of the entry in the array this model represents.
        self_refresh (bool): Indicates whether the model should self-refresh.
        metadata (dict): A dictionary containing metadata for the attribute."""

    def __init__(
        self, stage: Usd.Stage, attribute_paths: List[Sdf.Path], index: int, self_refresh: bool, metadata: dict
    ):
        """Initializes the SdfAssetPathArrayAttributeSingleEntryModel.

        Args:
            stage (:obj:`Usd.Stage`): The USD stage associated with the model.
            attribute_paths (List[:obj:`Sdf.Path`]): The attribute paths the model is tracking.
            index (int): The index this model represents in the attribute array.
            self_refresh (bool): Whether the model should self-refresh on changes.
            metadata (dict): Additional metadata for the model."""
        self._index = index
        super().__init__(stage, attribute_paths, self_refresh, metadata)

    @property
    def index(self):
        """Gets the index of the array entry this model represents.

        Returns:
            int: The index of the array entry."""
        return self._index

    def get_value_as_string(self, elide_big_array=True) -> str:
        """Gets the value of the asset path at the current index as a string.

        Args:
            elide_big_array (bool): Whether to elide large arrays for display.

        Returns:
            str: The asset path as a string."""
        self._update_value()
        if self._value is None:
            return ""
        if self._index >= len(self._value):
            return ""

        return self._get_value_as_string(self._value[self._index])

    def get_value(self):
        """Gets the value of the asset path at the current index.

        Returns:
            Any: The asset path value."""
        value = super().get_value()
        if value is None:
            return ""
        if self._index >= len(value):
            return ""

        return super().get_value()[self._index]

    def is_valid_path(self) -> bool:
        """Checks if the asset path at the current index is a valid path.

        Returns:
            bool: True if the path is valid, False otherwise."""
        self._update_value()
        value = super().get_value()
        if value is None:
            return ""
        if self._index >= len(value):
            return False

        return self._is_valid_path(self._value[self._index])

    def get_resolved_path(self):
        """Gets the resolved filesystem path for the asset at the current index.

        Returns:
            str: The resolved filesystem path."""
        self._update_value()
        if self._value is None:
            return ""
        if self._index >= len(self._value):
            return self._get_resolved_path("")

        return self._get_resolved_path(self._value[self._index])

    def set_value(self, value, comp: int = -1, resolved_path: str = ""):
        """Sets the value of the asset path at the current index.

        Args:
            value (str): The new asset path value.
            comp (int): The component index for vector types.
            resolved_path (str): The resolved filesystem path."""
        if isinstance(self._valid_stage, StageAdapter):
            vec_value = self._valid_stage.resolve_path_array(value, resolved_path, self._value, self._index)
        else:
            if not isinstance(value, Sdf.AssetPath):
                if resolved_path:
                    value = Sdf.AssetPath(value, resolved_path)
                else:
                    value = Sdf.AssetPath(value)

            vec_value = Sdf.AssetPathArray(self._value)
            vec_value[self._index] = value

        if UsdBase.set_value(self, vec_value, self._index):
            self._value_changed()

    def _is_prev_same(self):
        # Strip the resolvedPath from the AssetPath for the comparison, since the prev values don't have resolvedPath.
        return [
            [Sdf.AssetPath(value.path) for value in values] for values in self._real_values
        ] == self._prev_real_values

    def _save_real_values_as_prev(self):
        # Strip the resolvedPath from the AssetPath so that it can be recomputed.
        self._prev_real_values = [[Sdf.AssetPath(value.path) for value in values] for values in self._real_values]


class SdfAssetPathArrayAttributeItemModel(ui.AbstractItemModel):
    """A class for managing a collection of asset paths as attribute items within a USD stage.

    This model provides functionality to manipulate and retrieve data for asset paths stored in a USD stage. It supports self-refreshing and holds metadata and a delegate for advanced customization.

    Args:
        stage (:obj:`Usd.Stage`): The USD stage where the asset paths are located.
        attribute_paths (List[:obj:`Sdf.Path`]): A list of attribute paths within the USD stage.
        self_refresh (bool): If True, the model will automatically refresh its data when changes occur.
        metadata (dict): A dictionary containing metadata for the asset paths.
        delegate: A delegate object for custom behavior and data handling."""

    def __init__(self, stage: Usd.Stage, attribute_paths: List[Sdf.Path], self_refresh: bool, metadata: dict, delegate):
        """Initializes the SdfAssetPathArrayAttributeItemModel.

        This method does not require documentation of its parameters."""
        super().__init__()
        self._delegate = delegate  # keep a reference of the delegate os it's not destroyed
        self._value_model = UsdAttributeModel(stage, attribute_paths, False, metadata)
        value = self._value_model.get_value()
        self._entries = []
        self._repopulate_entries(value)

    def clean(self):
        """Cleans up the model, releasing any resources or references."""
        self._delegate = None

        for entry in self._entries:
            entry.destroy()
        self._entries.clear()

        if self._value_model:
            self._value_model.clean()
            self._value_model = None

    @property
    def value_model(self) -> UsdAttributeModel:
        """Gets the value model associated with this item model.

        Returns:
            :obj:`UsdAttributeModel`: The value model."""
        return self._value_model

    def get_item_children(self, item):
        """Returns the children of a given item.

        Args:
            item (:obj:`SdfAssetPathItem`): The item to retrieve children for."""
        if item is not None:
            # Since we are doing a flat list, we return the children of root only.
            # If it's not root we return.
            return []

        return self._entries

    def get_item_value_model_count(self, item):
        """Returns the number of value models for an item.

        Args:
            item (:obj:`SdfAssetPathItem`): The item to get the value model count for."""
        return 1

    def get_item_value_model(self, item, column_id):
        """Retrieves the value model for a given item and column ID.

        Args:
            item (:obj:`SdfAssetPathItem`): The item to retrieve the model for.
            column_id (int): The column ID."""
        return (item.sdf_asset_path_model, self._value_model)

    def get_drag_mime_data(self, item):
        """Retrieves the drag mime data for an item.

        Args:
            item (:obj:`SdfAssetPathItem`): The item to get the drag mime data for."""
        return str(item.sdf_asset_path_model.index)

    def drop_accepted(self, target_item, source, drop_location=-1):
        """Determines if a drop operation is accepted.

        Args:
            target_item (:obj:`SdfAssetPathItem`): The target item.
            source (:obj:`SdfAssetPathItem`): The source item being dropped.
            drop_location (int): The location where the drop is intended."""
        try:
            self._entries.index(source)
        except ValueError:
            # Not in the list. This is the source from another model.
            return False

        return not target_item and drop_location >= 0

    def drop(self, target_item, source, drop_location=-1):
        """Handles the drop operation.

        Args:
            target_item (:obj:`SdfAssetPathItem`): The target item.
            source (:obj:`SdfAssetPathItem`): The source item being dropped.
            drop_location (int): The location where the drop is intended."""
        try:
            source_id = self._entries.index(source)
        except ValueError:
            # Not in the list. This is the source from another model.
            return

        if source_id == drop_location:
            # Nothing to do
            return

        value = list(self._value_model.get_value())
        moved_entry_value = value[source_id]
        del value[source_id]

        if drop_location > len(value):
            # Drop it to the end
            value.append(moved_entry_value)
        else:
            if source_id < drop_location:
                # Because when we removed source, the array became shorter
                drop_location = drop_location - 1

            value.insert(drop_location, moved_entry_value)
        self._value_model.set_value(value)

    def _repopulate_entries(self, value: Sdf.AssetPathArray):
        for entry in self._entries:
            entry.destroy()
        self._entries.clear()

        stage = self._value_model.stage
        metadata = self._value_model.metadata
        attribute_paths = self._value_model.get_attribute_paths()

        for i in range(len(value)):
            asset_path_single_entry_model = SdfAssetPathArrayAttributeSingleEntryModel(
                stage, attribute_paths, i, False, metadata
            )

            model = SdfAssetPathItem(asset_path_single_entry_model)
            self._entries.append(model)

        self._item_changed(None)

    def _on_usd_changed(self, *args, **kwargs):
        # pylint: disable=protected-access

        # forward to all sub-models
        self._value_model._on_usd_changed(*args, **kwargs)
        for entry in self._entries:
            entry.sdf_asset_path_model._on_usd_changed(*args, **kwargs)

    def _set_dirty(self, *args, **kwargs):
        # pylint: disable=protected-access

        # forward to all sub-models
        self._value_model._set_dirty(*args, **kwargs)

        new_value = self._value_model.get_value()
        if new_value and len(new_value) != len(self._entries):
            self._repopulate_entries(new_value)
        else:
            for entry in self._entries:
                entry.sdf_asset_path_model._set_dirty(*args, **kwargs)

    def get_value(self, *args, **kwargs):
        """Retrieves the current value of the model.

        Keyword Args:
            args (list): Additional arguments for retrieving the value."""
        return self._value_model.get_value(*args, **kwargs)

    def set_value(self, *args, **kwargs):
        """Sets the value of the model.

        Args:
            args (list): The value to set.

        Keyword Args:
            kwargs (dict): Additional keyword arguments."""
        return self._value_model.set_value(*args, **kwargs)


class GfQuatAttributeModel(ui.AbstractItemModel, UsdBase):
    """A model for managing quaternion attributes in a USD stage.

    This model provides an interface to interact with quaternion attributes associated with USD prim paths. It supports updating the attribute values and responding to changes in the stage.

    Args:
        stage (:obj:`Usd.Stage`): The USD stage to associate with the model.
        attribute_paths (List[:obj:`Sdf.Path`]): A list of prim paths whose attributes this model will manage.
        tf_type (:obj:`Tf.Type`): The type of transformation (e.g., rotation, scale, translation) that the quaternion represents.
        self_refresh (bool): Whether the model should automatically refresh its data when changes occur in the stage.
        metadata (dict): Additional metadata that may be needed for managing the attributes."""

    def __init__(
        self, stage: Usd.Stage, attribute_paths: List[Sdf.Path], tf_type: Tf.Type, self_refresh: bool, metadata: dict
    ):
        """Initializes the GfQuatAttributeModel."""
        UsdBase.__init__(self, stage, attribute_paths, self_refresh, metadata)
        ui.AbstractItemModel.__init__(self)
        data_type_name = "Quat" + tf_type.typeName[-1]
        self._data_type = getattr(Gf, data_type_name)

        # Create root model
        self._root_model = ui.SimpleIntModel()
        self._root_model.add_value_changed_fn(lambda a: self._item_changed(None))

        # Create four models per component
        self._items = [UsdQuatItem(FloatModel(self)) for i in range(4)]
        for item in self._items:
            item.model.add_value_changed_fn(lambda a, item=item: self._on_value_changed(item))

        self._edit_mode_counter = 0

    def clean(self):
        """Cleans up the model, preparing it for deletion."""
        UsdBase.clean(self)

    def _on_value_changed(self, item):
        """Called when the submodel is chaged"""
        if self._edit_mode_counter > 0:
            quat = self._construct_quat_from_item()
            if quat and self.set_value(quat, self._items.index(item)):
                self._item_changed(item)

    def _update_value(self, force=False):
        if UsdBase._update_value(self, force):
            for i, item in enumerate(self._items):
                item.model.set_value(self._value.real if i == 0 else self._value.imaginary[i - 1])

    def _on_dirty(self):
        self._item_changed(None)

    def get_item_children(self, item):
        """Retrieves children of a given item.

        Args:
            item: The item to get children for."""
        self._update_value()
        return self._items

    def get_item_value_model(self, item, column_id):
        """Gets the value model for a specified item and column.

        Args:
            item: The item to get the value model for.
            column_id: The id of the column."""
        if item is None:
            return self._root_model
        return item.model

    def begin_edit(self, item=None):
        """Begins the editing process for a given item.

        Args:
            item: The item to start editing."""
        self._edit_mode_counter += 1
        UsdBase.begin_edit(self)

    def end_edit(self, item=None):
        """Ends the editing process for a given item.

        Args:
            item: The item to finish editing."""
        UsdBase.end_edit(self)
        self._edit_mode_counter -= 1

    def _construct_quat_from_item(self):
        data = [item.model.get_value_as_float() for item in self._items]

        return self._data_type(data[0], data[1], data[2], data[3])


# A data model for display orient(quaternion) as rotate(Euler)
class GfQuatEulerAttributeModel(ui.AbstractItemModel, UsdBase):
    """A class for managing the conversion between quaternion and Euler rotation attributes in USD stages.

    This model facilitates the representation and editing of quaternion-based rotation attributes as Euler angles, providing an intuitive interface for animators and artists. It supports updating and retrieving the rotation values in both formats, ensuring seamless integration with USD's quaternion attributes.

    Args:
        stage (:obj:`Usd.Stage`): The USD stage where the attribute resides.
        attribute_paths (List[:obj:`Sdf.Path`]): A list of paths to the quaternion attributes in the USD stage.
        tf_type (:obj:`Tf.Type`): The type of the transformation, indicating whether it's a rotation, scale, or translation.
        self_refresh (bool): Indicates whether the model should automatically refresh its value when the USD stage is changed.
        metadata (dict): Additional metadata associated with the quaternion attribute."""

    axes = [Gf.Vec3d(1, 0, 0), Gf.Vec3d(0, 1, 0), Gf.Vec3d(0, 0, 1)]
    """list of Gf.Vec3d: Axes used for quaternion to euler conversion."""

    def __init__(
        self, stage: Usd.Stage, attribute_paths: List[Sdf.Path], tf_type: Tf.Type, self_refresh: bool, metadata: dict
    ):
        """Constructor for GfQuatEulerAttributeModel."""
        UsdBase.__init__(self, stage, attribute_paths, self_refresh, metadata)
        ui.AbstractItemModel.__init__(self)

        # The underline USD data is still a quaternion
        data_type_name = "Quat" + tf_type.typeName[-1]
        self._data_type = getattr(Gf, data_type_name)

        self._root_model = ui.SimpleIntModel()
        self._root_model.add_value_changed_fn(lambda a: self._item_changed(None))

        # Create three models per component
        self._items = [UsdFloatItem(FloatModel(self)) for _ in range(3)]
        for item in self._items:
            item.model.add_value_changed_fn(lambda a, item=item: self._on_value_changed(item))

        self._edit_mode_counter = 0

    def clean(self):
        """Cleans up the model."""
        UsdBase.clean(self)

    # Should be used to set the self._items to USD attribute
    def _on_value_changed(self, item):
        if self._edit_mode_counter > 0:
            quat = self._compose([item.model.as_float for item in self._items])
            if quat and self.set_value(quat):
                self._item_changed(item)

    # Unlike normal Vec3 or Quat, we have to update all four values all together
    def update_to_submodels(self):
        """Updates submodels with the current quaternion value."""
        if self._edit_mode_counter != 0:
            return
        if self._value is not None:
            e = self._decompose(self._value)
            for i, item in enumerate(self._items):
                item.model.set_value(e[i])

    def _update_value(self, force=False):
        if UsdBase._update_value(self, force):
            self.update_to_submodels()

    def _on_dirty(self):
        self._item_changed(None)

    def get_item_children(self, item):
        """Gets the child items of the given item.

        Args:
            item (Optional[:obj:`UsdUIItem`]): The parent item to retrieve children for."""
        self._update_value()
        return self._items

    def get_item_value_model(self, item, column_id):
        """Retrieves the value model for a given item and column.

        Args:
            item (Optional[:obj:`UsdUIItem`]): The item to retrieve the value model for.
            column_id (int): The column id for which to retrieve the model."""
        if item is None:
            return self._root_model
        return item.model

    def begin_edit(self, item=None):
        """Begins an edit operation on the model.

        Args:
            item (Optional[:obj:`UsdUIItem`]): The item that is beginning an edit."""
        self._edit_mode_counter += 1
        UsdBase.begin_edit(self)

    def end_edit(self, item=None):
        """Ends an edit operation on the model.

        Args:
            item (Optional[:obj:`UsdUIItem`]): The item that has finished editing."""
        UsdBase.end_edit(self)
        self._edit_mode_counter -= 1

    def _compose(self, eulers):
        nrs = [Gf.Rotation(axis, eulers[i]) for i, axis in enumerate(self.axes)]
        nr = nrs[2] * nrs[1] * nrs[0]
        result = self._data_type(nr.GetQuat())
        return result

    def _decompose(self, value):
        if isinstance(self.stage, StageAdapter):
            rot = Gf.Rotation(self.stage.convert_data(value, "usd"))
        else:
            rot = Gf.Rotation(value)
        eulers = rot.Decompose(*self.axes)
        # round epsilons from decompose
        eulers = [round(angle + 1e-4, 3) for angle in eulers]
        return eulers

    def _get_comp_num(self):
        """Gets the number of components.

        Returns:
            int: The number of components."""
        return 3

    def _get_value_by_comp(self, value, comp: int):
        """Gets the value of the model by component.

        Args:
            value: The value to get.
            comp (int): The component index to get."""
        e = self._decompose(value)
        return e[comp]

    def _update_value_by_comp(self, value, comp: int):
        """Updates the value of the model by component.

        Args:
            value: The value to update.
            comp (int): The component index to update."""
        self_e = self._decompose(self._value)
        e = self._decompose(value)
        e[comp] = self_e[comp]
        value = self._compose(e)
        return value

    def _compare_value_by_comp(self, val1, val2, comp: int):
        """Compares the value of the model by component.

        Args:
            val1: The first value to compare.
            val2: The second value to compare.
            comp (int): The component index to compare.

        Returns:
            bool: True if the values are close, False otherwise.
        """
        return Gf.IsClose(self._get_value_by_comp(val1, comp), self._get_value_by_comp(val2, comp), 1e-6)


# Do not instantiate this class directly, derive from it.
class MatrixBaseAttributeModel(ui.AbstractItemModel, UsdBase):
    """A specialized model for handling Matrices in USD attributes.

    This model extends the capabilities of the UsdAttributeModel by providing additional functionality to manage Matrices values. It is particularly useful for working with attributes that represent Matrix data in USD.
    """

    def __init__(
        self,
        stage: Usd.Stage,
        attribute_paths: List[Sdf.Path],
        num_items: int,
        self_refresh: bool,
        metadata: dict,
    ):
        """A specialized model for handling Matrices in USD attributes.

        This model extends the capabilities of the UsdAttributeModel by providing additional functionality to manage Matrices values. It is particularly useful for working with attributes that represent Matrix data in USD.

        While similar in structure to UsdAttributeModel, this model overrides the method to save the previous real values as Matrix, ensuring proper initialization and handling of Matrix data types.

        Args:
            stage (:obj:`Usd.Stage`): The stage where the USD attributes are defined.
            attribute_paths (List[:obj:`Sdf.Path`]): A list of USD attribute paths for which the model is responsible.
            num_items (int): The number of items in the matrix.
            self_refresh (bool): Whether the model should update itself automatically when changes occur.
            metadata (dict): A dictionary containing metadata information for the attribute.
        """

        UsdBase.__init__(self, stage, attribute_paths, self_refresh, metadata)
        ui.AbstractItemModel.__init__(self)

        # Create root model
        self._root_model = ui.SimpleIntModel()
        self._root_model.add_value_changed_fn(lambda a: self._item_changed(None))

        # Create three models per component
        self._items = [UsdMatrixItem(FloatModel(self)) for i in range(num_items)]
        for item in self._items:
            item.model.add_value_changed_fn(lambda a, item=item: self._on_value_changed(item))

        self._edit_mode_counter = 0

    def clean(self):
        """Cleans the model.

        This method is called when the model is no longer needed and should be cleaned up. It removes all associated resources and resets the model to its initial state.
        """
        UsdBase.clean(self)

    def _on_value_changed(self, item):
        """
        Called when the submodel is changed
        Implement in derived.
        """
        raise NotImplementedError('Derived class must implement "_on_value_changed".')

    def _update_value(self, force=False):
        """
        Update child model values
        Implement in derived.
        """
        raise NotImplementedError('Derived class must implement "_update_value".')

    def _on_dirty(self):
        """
        Called when the model is dirty.
        Implement in derived.
        """
        # pylint: disable=protected-access
        self._item_changed(None)
        # it's still better to call _value_changed for all child items
        for child in self._items:
            child.model._value_changed()

    def get_item_children(self, item):
        """Reimplemented from the base class."""
        self._update_value()
        return self._items

    def get_item_value_model(self, item, column_id):
        """Reimplemented from the base class."""
        if item is None:
            return self._root_model
        return item.model

    def begin_edit(self, item=None):
        """
        Reimplemented from the base class.
        Called when the user starts editing.
        """
        self._edit_mode_counter += 1
        UsdBase.begin_edit(self)

    def end_edit(self, item=None):
        """
        Reimplemented from the base class.
        Called when the user finishes editing.
        """
        UsdBase.end_edit(self)
        self._edit_mode_counter -= 1


class GfMatrixAttributeModel(MatrixBaseAttributeModel):
    """A model for representing and manipulating GfMatrix attributes in USD.

    This model supports various matrix sizes as defined by the composition count and type. It provides functionality to edit individual matrix components and handles their synchronization with the USD attributes.

    Args:
        stage (:obj:`Usd.Stage`): The stage where the USD attributes are defined.
        attribute_paths (List[:obj:`Sdf.Path`]): A list of USD attribute paths to be managed by this model.
        comp_count (int): The number of components in each row or column of the matrix.
        tf_type (:obj:`Tf.Type`): The type of the matrix, typically representing the data precision (e.g., GfMatrix4f for a 4x4 float matrix).
        self_refresh (bool): Whether the model should automatically refresh its data when the USD stage changes.
        metadata (dict): A dictionary containing metadata for the matrix attributes."""

    def __init__(
        self,
        stage: Usd.Stage,
        attribute_paths: List[Sdf.Path],
        comp_count: int,
        tf_type: Tf.Type,
        self_refresh: bool,
        metadata: dict,
    ):
        """Constructor for GfMatrixAttributeModel.

        Initializes a new instance of GfMatrixAttributeModel.

        Args:
            stage (:obj:`Usd.Stage`): The stage where the USD attributes are defined.
            attribute_paths (List[:obj:`Sdf.Path`]): A list of USD attribute paths for which the model is responsible.
            comp_count (int): The number of components in each row or column of the matrix.
            tf_type (:obj:`Tf.Type`): The type of the matrix, typically representing the data precision (e.g., GfMatrix4f for a 4x4 float matrix).
            self_refresh (bool): Whether the model should update itself automatically when changes occur.
            metadata (dict): A dictionary containing metadata information for the attribute.
        """
        num_items = comp_count * comp_count
        super().__init__(stage, attribute_paths, num_items, self_refresh, metadata)

        self._comp_count = comp_count

        data_type_name = "Matrix" + str(comp_count) + tf_type.typeName[-1]
        self._data_type = getattr(Gf, data_type_name)

    def _update_value(self, force=False):
        """Updates the value of the model.

        This method updates the value of the model by setting the values of the child models to the corresponding components of the matrix. It also updates the value of the root model to the matrix as a whole.
        """
        # pylint: disable=protected-access

        if UsdBase._update_value(self, force):
            for i, item in enumerate(self._items):
                item.model.set_value(self._value[i // self._comp_count][i % self._comp_count])

    def _on_value_changed(self, item):
        """Called when the submodel is chaged"""

        if self._edit_mode_counter > 0:
            matrix = self._construct_matrix_from_item()
            if matrix and self.set_value(matrix, self._items.index(item)):
                self._item_changed(item)

    def _construct_matrix_from_item(self):
        """Constructs a matrix from the item.

        This method constructs a matrix from the item by iterating through the components of the matrix and appending them to the matrix row. It then appends the matrix row to the matrix.
        """
        data = [item.model.get_value_as_float() for item in self._items]
        matrix = []
        for i in range(self._comp_count):
            matrix_row = []
            for j in range(self._comp_count):
                matrix_row.append(data[i * self._comp_count + j])
            matrix.append(matrix_row)

        return self._data_type(matrix)


class UsdAttributeInvertedModel(UsdAttributeModel):
    """A model that inverts the boolean value from a USD attribute.

    This model extends the UsdAttributeModel and provides an inverted boolean representation of the USD attribute value. It can be particularly useful when working with toggles or switches in a user interface that require a reversed logic.

    The get_value_as_bool method returns the inverted state of the attribute's original boolean value. The set_value method sets the attribute's value to the opposite of the provided value.
    """

    def get_value_as_bool(self) -> bool:
        """Returns the inverted boolean value of the underlying USD attribute.

        Returns:
            bool: Inverted value of the USD attribute."""
        return not super().get_value_as_bool()

    def get_value_as_string(self, elide_big_array=True) -> str:
        """Returns the inverted boolean value as a string.

        Args:
            elide_big_array (bool): If True, large arrays are represented as [...].

        Returns:
            str: 'True' if original value is False, 'False' otherwise."""
        return str(self.get_value_as_bool())

    def set_value(self, value, comp: int = -1):
        """Sets the value of the USD attribute to the opposite of the given value.

        Args:
            value (bool): The value to set, after being inverted.
            comp (int): Component index for vector types, -1 for scalar."""
        super().set_value(not value)

    def get_value(self):
        """Returns the inverted value of the underlying USD attribute.

        Returns:
            bool: Inverted value of the USD attribute."""
        return not super().get_value()


class SdfTimeCodeModel(UsdAttributeModel):
    """A specialized model for handling SDF timecodes in USD attributes.

    This model extends the capabilities of the UsdAttributeModel by providing additional functionality to manage SDF timecode values. It is particularly useful for working with attributes that represent time-based data in USD.

    While similar in structure to UsdAttributeModel, this model overrides the method to save the previous real values as SDF TimeCodes, ensuring proper initialization and handling of timecode data types.
    """

    def _save_real_values_as_prev(self):
        # SdfTimeCode cannot be inited from another SdfTimeCode, only from float (double in C++)..
        self._prev_real_values = [Sdf.TimeCode(float(value)) for value in self._real_values]
