```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

Render Prim Property Widgets provides a user interface for viewing and editing render-specific properties on USD prims. This extension integrates seamlessly into the property window, enabling users to inspect and adjust render attributes with ease. It is designed to simplify the process of managing render properties through an intuitive, multi-schema based widget interface.

## Concepts

- **Property Widgets:** The extension leverages a multi-schema properties widget to display various render prim properties. This approach makes it simple to work with a range of render-related attributes.
- **UI Integration:** Once enabled, the extension adds render property panels directly into the property window, providing immediate access to editable attributes.

## Functionality

- **View and Edit:** Users can both view and modify render prim property values through a dedicated UI panel. The widget organizes properties by schema, enabling clear separation and presentation of various render settings.
- **Seamless Integration:** Operating within the USD ecosystem, the extension works in concert with other property and window extensions. It benefits from the existing USD data model and Omniverse Kit UI components, ensuring consistency and predictability.
- **Dynamic Updates:** When property payloads change, the widget refreshes the display to reflect the current state of the render prims, making it useful for iterative design and real-time adjustments.

## Integration

- **Built-in Dependencies:** The extension builds on core components from modules such as **omni.usd**, **omni.ui**, **omni.kit.window.property**, and **omni.kit.property.usd.** This ensures that render property widgets are well integrated into the broader USD and Omniverse Kit ecosystem.
- **User Workflow:** Once the extension is enabled, users can access render property widgets as part of the main property window. This provides a workflow where properties are directly modified within the familiar Omniverse Kit interface without requiring additional programming.

## Considerations

- **Self-Contained and Immediate Use:** The extension is designed for direct interaction through the UI. There is no need to call public APIs to utilize its functionality, making it ideal for users who prefer a plug-and-play experience.
- **Focus on Render Prim Properties:** The extension specifically targets render prim attributes. Users looking to manipulate other types of properties should consider complementary extensions within the USD property suite.
- **Data Consistency:** Changes made via the widget update the underlying USD structure. Users should ensure modifications follow their project's data management practices to avoid unintended side effects.

Render Prim Property Widgets enhances the user experience by providing a clear, accessible way to manage render properties directly within the Omniverse Kit environment.
