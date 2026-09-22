Description:
------------

This json describes which model to load for a particular controller. The model selection is done by selecting the highest
priority model that is available for the given input device (named like /user/hand/left etc) and that has the tags that
are required.

The model itself must be defined as inside an xrasset package.


Json file structure:
--------------------

The json has the following fields:

    version -> version of the scheme used to define the model (currently version 1)
    name -> description of the model
    priority -> priority of the model. Higher priority models are chosen over lower priority ones.
    tags [optional] -> tags required for selecting this model. This can be a single string or an array of strings.
    inputDevices -> input device names this is defined for as a string of an array of strings
    asset -> the name in xrasset to load


How to define openxr bindings in a different extension:
-------------------------------------------------------

Define these lines in the main config.toml:

[settings]
xr.manifests."omni.kit.xr.core" = "xrmanifests"

where "xrmanifests" refers to the directory name in which the xrmanifests are located.
The omni.kit.xr.system.openxr extension will look in the input_device_models folder inside the
xrmanifests folder to find the binding json files. The bindings can have an arbitrary name. This folder
will be scanned when the extension starts.


How to define xrassets in a different extension:
------------------------------------------------

[settings]
xr.assets."omni.kit.xr.core" = "xrassets"

where "xrassets" refers to the directory name in which the xrassets are located.

Each XRAsset is a directory with bunch of usd files, the directory is named xrasset.<package_name>.v<version>. The
references to these assest are in the form of: {package_name}/<internal_usd_path>
