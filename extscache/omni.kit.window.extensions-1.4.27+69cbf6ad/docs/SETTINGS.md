```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Settings

## Settings Provided by the Extension
### persistent.exts."omni.kit.window.extensions".publishingEnabled
   - **Default Value**: false
   - **Description**: Enables the option to publish and unpublish extensions directly from the UI.

### persistent.exts."omni.kit.window.extensions".openInVSCode
   - **Default Value**: false
   - **Description**: Determines whether folders and files should be opened in VSCode instead of the default OS file explorer.

### exts."omni.kit.window.extensions".docUrlInternal
   - **Default Value**: "http://omniverse-docs.s3-website-us-east-1.amazonaws.com/${extName}/${version}"
   - **Description**: Specifies the internal URL template for extension documentation.

### exts."omni.kit.window.extensions".docUrlExternal
   - **Default Value**: "https://docs.omniverse.nvidia.com/kit/docs/${extName}/${version}"
   - **Description**: Specifies the external URL template for extension documentation.

### exts."omni.kit.window.extensions".communityTabEnabled
   - **Default Value**: true
   - **Description**: Controls the visibility of the Community extensions tab in the UI.

### exts."omni.kit.window.extensions".communityTabOption
   - **Default Value**: true
   - **Description**: Provides an option in settings to enable or disable the Community extensions tab.

### exts."omni.kit.window.extensions".openExampleLinks
   - **Default Value**: [["Open Extension Template On Github", "https://github.com/NVIDIA-Omniverse/kit-extension-template"]]
   - **Description**: Sets links to create menu entries for opening examples on Github.

### exts."omni.kit.window.extensions".raster_nodes
   - **Default Value**: false
   - **Description**: Enables or disables raster nodes in the dependencies graph.

### exts."omni.kit.window.extensions".core_exts
   - **Default Value**: ["omni.anim.curve.core", "omni.graph.action", ...]
   - **Description**: Lists the core extensions included in the extension window.

### exts."omni.kit.window.extensions".example_exts
   - **Default Value**: []
   - **Description**: Contains a list of example extensions.

### exts."omni.kit.window.extensions".deprecated_exts
   - **Default Value**: []
   - **Description**: Contains a list of deprecated extensions.

### exts."omni.kit.window.extensions".internal_exts
   - **Default Value**: []
   - **Description**: Contains a list of internal extensions.