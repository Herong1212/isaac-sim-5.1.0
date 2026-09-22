# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = [
    "AllowedTokenItem",
    "InvalidTokenItem",
    "OptionItem",
    "SdfAssetPathItem",
    "UsdFloatItem",
    "UsdMatrixItem",
    "UsdQuatItem",
    "UsdVectorItem",
]

import omni.ui as ui


class AllowedTokenItem(ui.AbstractItem):
    """A class representing an item that is allowed as a token.

    This class encapsulates a single token item, providing a model to represent the
    item as a simple string within the user interface. It is derived from the
    `ui.AbstractItem` class in the Omni UI framework.

    Args:
        item (str): The token item to be represented."""

    def __init__(self, item):
        """Initializes a new instance of the AllowedTokenItem."""
        super().__init__()
        self.token = item
        self.model = ui.SimpleStringModel(item)


class InvalidTokenItem(ui.AbstractItem):
    """A class representing an item that is not allowed as a token.

    This class encapsulates a single token item, providing a model to represent the
    item as a simple string within the user interface. It is derived from the
    `ui.AbstractItem` class in the Omni UI framework.

    Args:
        item (str): The token item to be represented."""

    def __init__(self, item):
        """Initializes a new instance of the InvalidTokenItem."""
        super().__init__()
        self.token = item
        self.model = ui.SimpleStringModel(item)


class OptionItem(ui.AbstractItem):
    """A class representing an option item for UI selection.

    This class encapsulates an option item that can be used in UI components, representing a selectable option with a display name and an associated value.

    Args:
        display_name (str): The name of the option as displayed in the UI.
        value (int): The value associated with the option, typically used for identification or selection handling."""

    def __init__(self, display_name: str, value: int):
        """Initializes a new instance of the OptionItem."""
        super().__init__()
        self.model = ui.SimpleStringModel(display_name)
        self.value = value


class SdfAssetPathItem(ui.AbstractItem):
    """Single item of the model.

    Represents a single entry within the SdfAssetPath model.

    Args:
        asset_path_single_entry_model: The model associated with the asset path entry."""

    def __init__(self, asset_path_single_entry_model):
        """Initializes an instance of SdfAssetPathItem."""
        super().__init__()
        self.sdf_asset_path_model = asset_path_single_entry_model

    def destroy(self):
        """Cleans up resources used by the SdfAssetPathItem instance."""
        self.sdf_asset_path_model.clean()


class UsdFloatItem(ui.AbstractItem):
    """A class representing a USD float item for UI elements.

    This class encapsulates a single floating-point value for use in user interface constructs. It inherits from omni.ui.AbstractItem and holds a model that reflects the float value.

    Args:
        model (:obj:`ui.SimpleFloatModel`): The model storing the floating-point value."""

    def __init__(self, model):
        """Initializes a new instance of the UsdFloatItem."""
        super().__init__()
        self.model = model


class UsdMatrixItem(ui.AbstractItem):
    """A class representing a USD matrix item in the user interface.

    This class encapsulates a USD matrix item, typically used in user interfaces for visualizing or interacting with 4x4 transformation matrices. It is a specialized UI element that holds a model representing the matrix data.

    Args:
        model: The model holding the matrix data."""

    def __init__(self, model):
        """Initializes a new instance of UsdMatrixItem."""
        super().__init__()
        self.model = model


class UsdQuatItem(ui.AbstractItem):
    """A class representing a quaternion item in USD (Universal Scene Description).

    This class encapsulates a quaternion item, providing a consistent interface for manipulation and interaction within the USD environment. Quaternions are commonly used in graphics programming and 3D applications for representing rotations.

    Args:
        model: The model associated with this quaternion item."""

    def __init__(self, model):
        """Initializes a new instance of UsdQuatItem."""
        super().__init__()
        self.model = model


class UsdVectorItem(ui.AbstractItem):
    """A class representing an item that handles vectors in USD.

    This class is used to interact with vector-type data in USD (Universal Scene Description). It provides an interface for vector items that can be manipulated within the UI framework.

    Args:
        model (:obj:`ui.AbstractItemModel`): The model associated with this vector item."""

    def __init__(self, model):
        """Initializes a new instance of the UsdVectorItem."""
        super().__init__()
        self.model = model
