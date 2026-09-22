```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
This extension provides functionality for managing USD stage templates, including registration, creation, and transformation of stages within Omniverse Kit. It offers a suite of APIs for registering new stage templates, creating stages with these templates, and applying transformations to USD primitives.

## Important API List
- **register_template**: Registers a new stage template and associates it with an action.
- **unregister_template**: Unregisters a previously registered stage template.
- **get_stage_template_list**: Returns a list of loaded new_stage templates.
- **get_stage_template**: Retrieves a specific stage template by name.
- **get_default_template**: Fetches the name of the default stage template.
- **new_stage**: Initiates the creation of a new USD stage using a specified template.
- **new_stage_with_callback**: Creates a new USD stage and applies post-creation operations via a callback.
- **new_stage_async**: Asynchronously creates a new USD stage based on a specified template.
- **set_transform_helper**: Applies a transformation to a specified USD primitive.

## General Use Case
The extension is designed for users who need to create, manage, and manipulate USD stages within Omniverse Kit. It allows for the registration and use of stage templates, facilitating the creation of stages with predefined settings and structures. Users can also apply transformations to USD primitives, aiding in the positioning, rotation, and scaling of scene elements. The extension supports both synchronous and asynchronous stage creation, providing flexibility in how stages are initialized and configured. For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](SETTINGS)
- [](CHANGELOG)
