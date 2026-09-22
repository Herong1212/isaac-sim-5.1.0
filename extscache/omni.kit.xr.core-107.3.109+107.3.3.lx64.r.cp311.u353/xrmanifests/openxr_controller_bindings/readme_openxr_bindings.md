Description:
------------

These OpenXR bindings are computer readable versions of the the OpenXR specifications for the input
system as described in https://registry.khronos.org/OpenXR/specs/1.1/html/xrspec.

html#semantic-paths-interaction-profiles and the various input components in https://registry.khronos.
org/OpenXR/specs/1.1/html/xrspec.html#extension-appendices-list .

These json files describe which buttons and poses are available for each "interaction profile" that
openxr defines. As OpenXR is an ever growing specification, new json files can be added to this
directory or to a similar directory in an extension to add more interaction profiles. Each of the known
interaction profiles will be sent to OpenXR and it will pick the most appropriate interaction profile.

These json files also contain the information on extensions that interaction profiles are defined in. If an extension is named in the json files and it is available in the runtime, omni.kit.xr.system.openxr will enable that extension and add that profile as a possible profile to use.

Json file structure:
--------------------

The json file has the following fields:
    version  ->  the json scheme version used in the file. Currently all of them are set to 1.
    apiVersion [optional] -> minimum api version of OpenXR this profile can be found in
    name -> Description of the profile
    interactionProfile -> the OpenXR interaction profile string
    extension [optional] -> extension name that this interaction profile is defined on
    bindings -> array of several controller layout bindings.

a controller binding has the following component:
    devices -> an array of json objects that define the controller paths for which this binding is valid
        each object in devices has:
        - devicePath -> OpenXR path to the controller, e.g /hand/user/left etc
        - deviceType -> Description of the type of device, e.g. "controller"

    inputs -> buttons that are defined on the controller. This is an array of json objects:
        each input object has:
        - input -> OpenXR name of the button, e.g a,b, thumbstick, trackpad, trigger, squeeze, etc
        - gestures -> Array of OpenXR names for the gestures each input has, like click, value, x, y, touch, etc.
        - apiVersion [optional] -> minimum OpenXR version that this input is defined on
        - extension [optional]-> extension to activate to enable this pose

    poses -> poses that are associated with each controller. This is an array of json objects:
        each pose object has:
        - pose -> name of the pose as in OpenXR specification, e.g. aim or pose
        - apiVersion [optional] -> minimum OpenXR version that this pose is defined on
        - extension [optional]-> extension to activate to enable this pose

    outputs -> outputs that are associated with each controller. This is an array of json objects:
        each output has:
        - output -> name of the output as in OpenXR specification, e.g. haptic
        - apiVersion [optional] -> minimum OpenXR version that this output is defined on
        - extension [optional]-> extension to activate to enable this output

    defaultPose -> which pose to use as the default pose information for this controller.

To define openxr bindings in a different extension:


Define these lines in the main config.toml:
-----------------------------------------

[settings]
xr.manifests."omni.kit.xr.core" = "xrmanifests"

where "xrmanifests" refers to the directory name in which the xrmanifests are located.
The omni.kit.xr.system.openxr extension will look in the openxr_controller_bindings folder inside the
xrmanifests folder to find the binding json files. The bindings can have an arbitrary name. This folder
will be scanned when the extension starts.
