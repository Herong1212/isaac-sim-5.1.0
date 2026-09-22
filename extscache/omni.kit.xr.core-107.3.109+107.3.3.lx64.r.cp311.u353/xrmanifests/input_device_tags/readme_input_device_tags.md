Description:
------------

To define actionmaps and controller models, each input device is tagged with a series of keywords that can be used to
identify which type of controller/input device one has. The json files in this directory outline the criteria of each
tag. Each json file represents a single tag and the json definition describes when a tag is added.

There are a variety of tags:
- interaction profile tags. These tags mark a controller if a specific interaction profile was chosen for that controller
by the run time.

- button/pose configuration tags. These tags mark a controller if a specific set of buttons/poses is available. These
tags are generally more useful when deciding how to map buttons, as they do not require a interaction profile but rather
which buttons are defined by the controller. For instance a tag can check if all buttons for a vive or a quest controller
are there and switch between them. Any controller that has the same buttons (or more) can use the same action mapping as
they are compatible.

- tags for the system (e.g openxr, etc) that generated the input device. This is useful as some implementations have slightly different behavior.

Json file structure:
--------------------

version -> version of the scheme used to define the tag (currently version 1)
name -> name of the tag

requiredDeviceNameFragments [optional] -> array of strings to find in the device name as found in steamVR
requiredInteractionProfile [optional] -> which interaction profile to scan for (a single name)
requiredInputs [optional] -> array of OpenXR style button names that need to be available, e.g. squeeze, trigger, trackpad, thumbstick, etc
requiredPoses [optional] -> array of OpenXR style pose names that need to be available, e.g. aim, grip etc
requiredRuntimeNameFragments [optiona] -> array of strings to find in the name of the runtime


How to define openxr bindings in a different extension:
---------------------------------------------------

Define these lines in the main config.toml:

[settings]
xr.manifests."omni.kit.xr.core" = "xrmanifests"

where "xrmanifests" refers to the directory name in which the xrmanifests are located.
The omni.kit.xr.system.openxr extension will look in the input_device_tags folder inside the
xrmanifests folder to find the binding json files. The bindings can have an arbitrary name. This folder
will be scanned when the extension starts.
