# Python Scripting Component [omni.kit.scripting]

Supports adding Python Scripting Components to USD Prims for script execution.

Enables new features to the Content window for Python Script creation and editing.

Supports live script hot-reloading for quick workflows and works well with the VS Code Link extension to support Python debugging.

## Warning

There is currently no limitation on what code can be executed by USD files that have Python Scripting Components with assigned scripts. This means that a USD that contains scripts should only be used when the author of the USD content is trusted. 

For example arbitrary code could reference in script asset used in the USD, which will be executed with the same system credentials as the user who opens the file in Kit.

_