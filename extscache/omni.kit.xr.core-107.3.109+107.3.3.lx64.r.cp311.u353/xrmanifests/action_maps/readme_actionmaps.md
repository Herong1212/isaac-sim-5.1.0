Description:
------------

These json describes how buttons are mapped to tools. The actionmap is a defined for a certain tool layout and a given dominant hand.

There are different actionmaps for different controller layouts. The system scans the tags assigned to each controller and see which actionmap within the requirements has the highest priority.


Json file structure:
--------------------

The json has the following fields:

    version -> version of the scheme used to define the action map (currently version 1)
    name -> description of the action map
    priority -> priority of the action map. Higher priority action maps are chosen over lower priority ones.
    toolsLayout -> the layout of the tools that this actionmap is used for, e.g. "vr" for the vr tools
    dominantHand -> what is the dominant hand for this layout: "left" or "right"

    tags -> which tags are required per input_device. This is an array of json objects.
        each json objects has the following fields:
        - inputDevice -> name of the device
        - tag -> which tag is required

    tools -> the tools which are enabled for this actionmap

    actions -> dictionary of actions to as defined in the tools to a input button on the controller.


How to define openxr bindings in a different extension:
-------------------------------------------------------

Define these lines in the main extension.toml:

[settings]
xr.manifests."omni.kit.xr.core" = "xrmanifests"

where "xrmanifests" refers to the directory name in which the xrmanifests are located.
The omni.kit.xr.system.openxr extension will look in the action_maps folder inside the
xrmanifests folder to find the binding json files. The bindings can have an arbitrary name. This folder
will be scanned when the extension starts.
