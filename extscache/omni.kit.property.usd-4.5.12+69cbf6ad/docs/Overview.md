```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
The `omni.kit.property.usd` extension provides a comprehensive set of classes and functions for working with USD properties within Omniverse Kit applications. It includes models for various USD attribute types, widgets for property manipulation, and utilities for managing selection and control states.

## Important API List
- [AllowedTokenItem](omni.kit.property.usd/omni.kit.property.usd.AllowedTokenItem): Represents an allowed token item in UI selection.
- [ControlStateManager](omni.kit.property.usd/omni.kit.property.usd.ControlStateManager): Manages control states for USD attributes and properties.
- [FloatModel](omni.kit.property.usd/omni.kit.property.usd.FloatModel): A simple floating-point value model for UI components.
- [GfMatrixAttributeModel](omni.kit.property.usd/omni.kit.property.usd.GfMatrixAttributeModel): Handles matrix attributes of various sizes in USD.
- [GfQuatAttributeModel](omni.kit.property.usd/omni.kit.property.usd.GfQuatAttributeModel): Manages quaternion attributes in a USD stage.
- [GfQuatEulerAttributeModel](omni.kit.property.usd/omni.kit.property.usd.GfQuatEulerAttributeModel): Facilitates conversion between quaternion and Euler rotation attributes.
- [GfVecAttributeModel](omni.kit.property.usd/omni.kit.property.usd.GfVecAttributeModel): Represents and manipulates GfVec typed attributes in USD.
- [GfVecAttributeSingleChannelModel](omni.kit.property.usd/omni.kit.property.usd.GfVecAttributeSingleChannelModel): Handles single channel vector attributes in USD.
- [IntModel](omni.kit.property.usd/omni.kit.property.usd.IntModel): A simple integer value model for UI components.
- [MdlEnumAttributeModel](omni.kit.property.usd/omni.kit.property.usd.MdlEnumAttributeModel): Represents an enumeration attribute in USD.
- [OptionItem](omni.kit.property.usd/omni.kit.property.usd.OptionItem): Represents an option item for UI selection.
- [PlaceholderAttribute](omni.kit.property.usd/omni.kit.property.usd.PlaceholderAttribute): Creates a placeholder attribute in USD.
- [PrimPathWidget](omni.kit.property.usd/omni.kit.property.usd.PrimPathWidget): A widget for interacting with USD Prim paths.
- [PrimSelectionPayload](omni.kit.property.usd/omni.kit.property.usd.PrimSelectionPayload): Encapsulates the selection payload for USD stage's prim paths.
- [SdfAssetPathArrayAttributeItemModel](omni.kit.property.usd/omni.kit.property.usd.SdfAssetPathArrayAttributeItemModel): Manages a collection of asset paths as attribute items.
- [SdfAssetPathArrayAttributeSingleEntryModel](omni.kit.property.usd/omni.kit.property.usd.SdfAssetPathArrayAttributeSingleEntryModel): Represents a single entry in an array of SdfAssetPath attributes.
- [SdfAssetPathAttributeModel](omni.kit.property.usd/omni.kit.property.usd.SdfAssetPathAttributeModel): Monitors SDF asset path attributes in USD.
- [SdfAssetPathItem](omni.kit.property.usd/omni.kit.property.usd.SdfAssetPathItem): Represents a single entry within the SdfAssetPath model.
- [SdfTimeCodeModel](omni.kit.property.usd/omni.kit.property.usd.SdfTimeCodeModel): Handles SDF timecodes in USD attributes.
- [TfTokenAttributeModel](omni.kit.property.usd/omni.kit.property.usd.TfTokenAttributeModel): Manages USD attributes of type 'TfToken'.
- [UsdAttributeInvertedModel](omni.kit.property.usd/omni.kit.property.usd.UsdAttributeInvertedModel): Inverts the boolean value from a USD attribute.
- [UsdAttributeModel](omni.kit.property.usd/omni.kit.property.usd.UsdAttributeModel): Observes and manipulates USD attribute values.
- [UsdBase](omni.kit.property.usd/omni.kit.property.usd.UsdBase): Base class for USD attributes and properties management.
- [UsdFloatItem](omni.kit.property.usd/omni.kit.property.usd.UsdFloatItem): Represents a USD float item for UI elements.
- [UsdMatrixItem](omni.kit.property.usd/omni.kit.property.usd.UsdMatrixItem): Represents a USD matrix item in the UI.
- [UsdPropertyWidgets](omni.kit.property.usd/omni.kit.property.usd.UsdPropertyWidgets): Provides USD property widgets in Omniverse Kit.
- [UsdQuatItem](omni.kit.property.usd/omni.kit.property.usd.UsdQuatItem): Represents a quaternion item in USD.
- [UsdVectorItem](omni.kit.property.usd/omni.kit.property.usd.UsdVectorItem): Handles vector items in USD.
- [get_large_selection_count](omni.kit.property.usd/omni.kit.property.usd.get_large_selection_count): Fetches the count of large selections from settings.

## General Use Case
This extension is used to create, manage, and interact with USD property widgets within Omniverse Kit applications. It allows developers to integrate USD property manipulation into their custom UIs, handle attribute changes, manage selections and control states, and work with a variety of USD data types through specialized models and widgets. Users can leverage these tools to build more interactive and feature-rich applications for USD data inspection and editing. For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](SETTINGS)
- [](USAGE_PYTHON)
- [](CHANGELOG)
