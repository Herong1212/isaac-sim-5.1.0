# eXtended Reality Extension [omni.kit.xr.core]

# XRCore Documentation

## Overview

XRCore is a collection of classes and functions that are used to create and manage XR experiences.
It is the central system for Extended Reality (XR) experiences that manages the lifecycle of XR experiences and the interactions with the scene:

* XRCore manages - through a plugin system - the interaction with the VR system runtime (OpenXR, OpenVR, CloudXR etc)
* It manages scheduling of the frames that need to be rendered. It splits up the pieces that need to be rendered into different views and composites them to do things like stereoscopic rendering, foveated rendering etc. It contains a compositor system that can combine multiple views into a single image.
* XRCore manages the input coming from devices, such as buttons pressed, but also the poses of the controllers and head mounted displays.
* XRCore manages the scheduling of polling for inputs, requesting images, updating in scene UI components and negotiates with the other components in kit sdk on how to schedule the XR experience around in.
* XRCore manages a range of events that guide the business logic of the XR experience, such as switching off the selection beam etc.
* XRCore contains the basic components to be build a XR UI to guide the user through the experience.


## XRCore System Plugins

The actual handling with the XR runtime such as OpenXR, OpenVR, CloudXR etc is handled through plugins. The plugin has the specifics to know how to handle inputs and send images back to the XR runtime. XRCore exposes a basic interface that is common to all plugins and that is used to handle the communication with the XR runtime. Currently there are two plugins:

* OpenXR (omni.kit.xr.system.openxr): Handles the interaction with the OpenXR runtime.
* SimulatedXR (omni.kit.xr.system.simulatedxr): A system that simulates an XR system and is used for performance testing and for development purposes as it does not require an actual XR system to be present on the machine.

Once the plugin is loaded it will register itself to the XRCore and will be used for the XR experience.



## XRCore Scheduling

One of the first things to understand about XRCore is how XR experiences are scheduled. The Kit SDK is based on the Universal Scene Description (USD) standard architecture and that brings with it some unique challenges. The main issue is that USD is a data model for representing scene data, and it is not optimized for real-time applications, like XR experiences. The main issue with with USD is that it consists of many layers with many different opinions on what is in the "scene" and resolving that in real-time is expensive. To overcome this, the Kit SDK uses a system called USD-RT (Real-Time), which bypasses the usd composition stage and directly overrides the locations of scene objects. Both USD and USD-RT are currently used in a side by side process where objects are created in USD and then once a frame updates from USD and USD-RT are merged together to form the final scene.

To improve latency, the XRCore scheduling mechanism is designed to resolve poses of controllers and head mounted displays as late as possible in the frame and this happens after USD-RT and USD updates have been merged for that frame. To allow objects like controllers rendered into the scene to be in sync with the actual controller poses, XRCore implements a late stage update of USD-RT through a set of managed objects that form the basis of the XR UI in the stage. These last minute updates are constrained to several usd objects connected to the controllers such as the selection beam and the teleporter arc. Although these objects are created inside the usd scene, they are managed by XRCore to ensure they are updated last minute in a fast fashion as to not introduce any additional latency.

Another aspect of XRCore scheduling is that it tries to push event handing, such as switching off the selection beam etc (the business logic of the XR experience) to the next frame. Once USD-RT handling is done the scene objects are frozen in place and are then scheduled for rendering. The process of scheduling the rendering is currently a costly operation and is done on a separate thread. To minimize the cost of single frame, we update the business logic that controls the UI objects in scene for the next frame in parallel with the rendering being scheduled for the current frame. This results in most events being handled in the next frame, which is a good compromise between latency and convenience.

To summarize the scheduling process:

* A frame in the XR experience starts with the simulation thread doing animations, physics updates, scripted changes like moving cars, robots etc. Some updates are done in USD and others are done in USD-RT.
* Once the simulation thread is done the changes are collected inside USD-RT for rendering.
* At this point in time XRCore reads the poses of the controllers and head mounted displays and caches them.
* After internal structures in XRCore are updated, it sends out events to execute python code that needs to be executed in sync with the rendering.
* After the python code is executed it will update all the internally managed objects through USD-RT and will make sure that selection beams, teleporter arcs, objects attached to the controllers are updated in time for the rendering.
* It will then schedule the rendering of the scene.
* When the rendering thread is starting to schedule the rendering of the scene, the simulation thread is used to issue a second batch of events that will be executed with a single frame delay. These events are mostly events that capture for instance button presses and other events that can be processed on the next frame.
* While that is happening the scene makes it through all the planning stages for ray tracing pipeline and is finally scheduled for rendering.
* While the simulation thread is busy with the next frame, data on the previous frame is sent to the GPU for rendering.

Due to these complexities in scheduling process, the XR pipeline is generally about 2 frames behind. In order to ensure that rendering does not lag too far behind from the scheduling, the capture of the poses for the next frame is gated by the rendering thread having scheduled the next frame on the GPU.

## XRCore Python

XRCore contains a python layer that is used to handle the business logic of the XR experience and allows you to create custom components and expand the tools. There are three main components:

* Python classes to read the current state of the XR system like how many controllers are connected, what the poses of the controllers are, which buttons are pressed etc.
* Python classes that are base classes for XR GUI components, like for instance tools and UI layers
* Python classes to handle the events that allow you to send and register callbacks for events that happen in the XR system

To get access to the python layer you need to import the `omni.kit.xr.core` package. The main access point is the `XRCore` class which gives you access to the current state of the XR system:

```python
import omni.kit.xr.core

xr_core: XRCore = omni.kit.xr.core.XRCore()
```

## XRCore Profiles

The current implementation of XRCore uses a profile system to manage the setup of various XR Experiences. There are currently three main profiles:

* VR profile (omni.kit.xr.profile.vr): Used for Virtual Reality experiences
* AR profile (omni.kit.xr.profile.ar): Used for Augmented Reality experiences
* TabletAR profile (omni.kit.xr.profile.tabletar): Used for Tablet experiences

To enable a profile you can use the `request_enable_profile` method:

```python
xr_core.request_enable_profile("VR")
```

This will start the XR system and setup a the rendering pipeline for a certain type of XR experience. Each of the profiles is configured in an extension. To ensure that the profile is available you must include the extension in your project.

You can switch off a profile by calling the `request_disable_profile` method:

```python
xr_core.request_disable_profile()
```

This will stop the XR system and clean up the rendering pipeline. After this call the application will switch back to the non-XR mode. To list all the profiles that are available you can use the `get_profile_name_list` method:

```python
profile_names: list[str] = xr_core.get_profile_name_list()
```

Most of what a profile defines is a set of extra render settings for the graphics pipeline, such as the use of transparency for Augmented Reality experiences. It will switch on foveation for VR and AR experiences, but not tablet experiences. The list of customized render settings is defined in the `extension.toml` file in each profile extension.

## XRCore Input Devices

XRCore manages the input devices that are connected to the system. These are devices like controllers, head mounted displays and other input devices. To get the list of all input devices you can use the `get_input_devices` method:

```python
input_devices: list[XRInputDevice] = xr_core.get_input_devices()
```

Each input device has a name and a type that can be used to identify the device. To get the name and type of an input device you can use the `get_name` and `get_type` methods:

```python
name_token: XRToken = input_device.get_name()
type_token: XRToken = input_device.get_type()
```

The `XRToken` is a unique identifier for the xr system, it marks an immutable string. To get the string connected to the token you can use the `str` function:

```python
name: str = str(name_token)
type: str = str(type_token)
```

The most common input devices are the controllers and the head mounted display with the following names:

* /user/head
* /user/hand/left
* /user/hand/right
* /user/eye/left
* /user/eye/right

These names are derived from the OpenXR standard and are used to identify the input devices.

To get a specific input device you can use the `get_input_device` method:

```python
input_device: XRInputDevice = xr_core.get_input_device("/user/hand/left")
```

Note: that the input can be either an XRToken or a string. On parameter for functions a string will be automatically be converted to an XRToken for convenience.

Each input device is a class that contains the current state of the device. It contains the poses associated with the device, and the state of the buttons pressed. To get the poses of the input device you can use the `get_pose` method:

```python
pose: Gf.Matrix4d = input_device.get_pose()
```

The pose is a 4x4 USD matrix that represents the position and orientation of the input device. To get the position and orientation of the input device you can use the `ExtractTranslation` and `ExtractRotation` methods:

```python
position: Gf.Vec3d = pose.ExtractTranslation()
orientation: Gf.Quatd = pose.ExtractRotation()
```

For more details on the USD matrix and how to use it, please refer to the [USD documentation](https://openusd.org/release/api).

There are three types of poses associated with an input device:

* Raw pose: The raw pose is the pose of the input device as reported by the XR system.
* Pose: The pose in real world coordinates that is filtered by the XR system.
* Virtual pose: The virtual pose is the pose of the input device inside the USD Stage.

To get the different poses you can use the following methods:

```python
raw_pose: Gf.Matrix4d = input_device.get_raw_pose()
pose: Gf.Matrix4d = input_device.get_pose()
virtual_pose: Gf.Matrix4d = input_device.get_virtual_world_pose()
```

Some devices also support multiple poses per device. For instance the controllers support a "grip" pose and a "aim" pose. To get the list of poses supported by a device you can use the `get_pose_names` method:

```python
pose_names: list[XRToken] = input_device.get_pose_names()
```

To get a specific pose you can use the `get_pose` method:

```python
pose: Gf.Matrix4d = input_device.get_pose(pose_name)
```

Typical pose names are:

* grip
* aim

If no pose name is provided to the `get_pose` method, the default pose is returned. The default pose is the "aim" pose for controllers.

The input device also contains the state of the buttons pressed. To get the state of the buttons pressed you can use the `get_input_gesture_value` method:

```python
button_value: float = input_device.get_input_gesture_value(button_name, gesture_name)
```

Each button on an input device has a button name and a gesture name. The gesture name is the name of the gesture you can make with the button. Typical gesture names are:

* click
* touch
* value
* x (for thumbstick) and y (for thumbstick)

The button name is the name as defined by the OpenXR standard. Typical button names are:

* trigger
* squeeze
* menu
* trackpad
* thumbstick
* a
* b
* x
* y

For example to get the state of a thumbstick on the controller you can use the following python code:

```python
thumbstick_x: float = input_device.get_input_gesture_value("thumbstick", "x")
thumbstick_y: float = input_device.get_input_gesture_value("thumbstick", "y")
```

To find out which buttons are available on an input device you can use the `get_input_names` method:

```python
input_names: list[XRToken] = input_device.get_input_names()
```

For each input name you can get the gesture names with the `get_input_gesture_names` method:

```python
gesture_names: list[XRToken] = input_device.get_input_gesture_names(input_name)
```

All the state values of the buttons are floating point values between 0 and 1. For buttons that are not pressed the value is 0, for buttons that are pressed the value is 1. For thumbsticks the value is a value between -1 and 1 for both the x and y axis.

One can also query if an input is available on an input device with the `has_input` method:

```python
has_input: bool = input_device.has_input(input_name)
```

Similarly one can check if an input gesture is available on an input device with the `has_input_gesture` method:

```python
has_input_gesture: bool = input_device.has_input_gesture(input_name, gesture_name)
```

Besides the physical buttons on an input device, XRCore also simulates a number of input buttons. For instance if the controller has a trackpad or a thumbstick, XRCore will emulate a dpad on the controller. Values of these simulated buttons are also shown as available in the `get_input_names` and `get_input_gesture_names` methods. Examples of simulated input names are:

* dpad_up
* dpad_down
* dpad_left
* dpad_right

To check if a button is simulated you can check the input it is based on with the `get_input_base` method:

```python
input_base: XRToken = input_device.get_input_base(input_name)
```

Since these simulated inputs are based on other inputs, it does not make sense to bind a simulated button and its base button at the same time. To avoid this, XRCore allows you to check if an input is overlapping with another input with the `get_overlapping_inputs` method:

```python
overlapping_inputs: list[XRToken] = input_device.get_overlapping_inputs(input_name)
```


## XRCore Events

To get access to the message bus used by kit to communicate with the rest of the SDK, you can use the `get_message_bus` method:

```python
message_bus: carb.events.IEventStream = xr_core.get_message_bus()
```

This message bus is the same as the message bus used by the rest of the SDK and can be used to send and receive events and hence can be used to trigger callbacks when certain events happen in the XR system.


## XRCore Input Events

The input devices can generate events when buttons are pressed or released or can send out events every frame with the state of the buttons. To start generating events from an input device you need to bind an event generator to the input device. An input event generator is a class that can be used to generate events when certain events happen in the XR system. They are configured to send a specific event when a certain gesture is done, like a button being pressed or a thumbstick being moved.

To bind an event generator to an input device you can use the `bind_event_generator` method:

```python
event_generator: XREventGenerator = input_device.bind_event_generator(input_name, event_name, event_list, tooltips)
```

For example to bind an event generator to the input device that sends out an event when the "menu" button is pressed and released you can use the following code:

```python
event_generator: XREventGenerator = input_device.bind_event_generator("menu", "xr_menu", ("press", "release"))
```

The event generator will now send out an event with the name "xr_menu.press" when the "menu" button is pressed and an event with the name "xr_menu.release" when the "menu" button is released. The extra step of adding an event generator to an input device is to allow to customize the event name and to only send the events that are needed. The event generator sends out the events to the message bus and you can subscribe to them with the following code:

```python
import carb

def on_xr_menu(event: carb.events.IEvent):
    print(f"XR menu button pressed")

message_bus: carb.events.IEventStream = xr_core.get_message_bus()
message_type: int = carb.events.type_from_string("xr_menu.press")
message_bus.create_subscription_to_pop_by_type(message_type, on_xr_menu)
```

The event generator monitors a given input button and can generate the following events:

* press: button is pressed
* release: button is released
* update: button is pressed and the state of the button is packaged in the event. This event is sent each frame
* touch: button is touched
* lift: button is no longer touched
* suspend: some other event generator is grabbing focus from the button
* resume: the other event generator relinquished control
* state: send each frame with values of all the gesture state for the button

The name of the event that is sent out is a combination of the input name and the gesture name. In the example above the event name is "xr_menu" and the input name is "menu" and the gesture name is "press". This will result in an event with the name "xr_menu.press" being sent out.

The state of the button is also packaged in the event and is a dictionary with the following keys:

* touch: the button is touched
* click: the button is clicked
* value: for buttons like trigger or squeeze indicating how much the button is pressed
* x: x value of the thumbstick/trackpad
* y: y value of the thumbstick/trackpad

To make it easier to extract the state from the event, we added a class "XRInputDeviceGeneratorEvent" that can be used to wrap the event and extract the state from it.

```python
def on_xr_left_trackpad(event: carb.events.IEvent):
    input_event: XRInputDeviceGeneratorEvent = XRInputDeviceGeneratorEvent(event)

    # you can get the state of the button from the event
    trackpad_x: float = input_event.x
    trackpad_y: float = input_event.y
    click: bool = input_event.click
    touch: bool = input_event.touch
    value: float = input_event.value
    dt: float = input_event.dt # time passed since last event

    # You can also access who sent the event
    input: str = input_event.input # the input name
    input_device: str = input_event.input_device # the input device name
    input_device_type: str = input_event.input_device_type # the input device type

input_device: XRInputDevice = xr_core.get_input_device("/user/hand/left")
event_generator: XREventGenerator = input_device.bind_event_generator("trackpad", "xr_left_trackpad", ("state"))
message_bus: carb.events.IEventStream = xr_core.get_message_bus()
message_type: int = carb.events.type_from_string("xr_left_trackpad.state")
message_bus.create_subscription_to_pop_by_type(message_type, on_xr_left_trackpad)

```

The other advantage of using input event generators is that they can be used to temporarily take over the input of an input device. To do this you can define an input generator for an input that is already bound. When you release the input generator, the input device will go back to the previous input generator. This can be used to implement things like move an object when the user is pointing at an object and bind movement of the object to the trackpad. When the user has moved the object, the input generator is released and the input device goes back to allowing the user to fly through the scene.

```python

input_device: XRInputDevice = xr_core.get_input_device("/user/hand/left")
event_generator: XREventGenerator = input_device.bind_event_generator("trackpad", "fly_through_scene", ("state"))

# bound to fly through scene

second_event_generator: XREventGenerator = input_device.bind_event_generator("trackpad", "move_object", ("state"))

# Do logic here

second_event_generator = None # release input generator

# Back to fly through scene

```

By default an event generator is setup to stop generating events when the event generator that is returned is released. If the function "set_auto_unbind" is set to False, the event generator will not stop generating events and you need to manually stop it by calling "unbind_event_generator" on the input device.

```python
event_generator: XREventGenerator = input_device.bind_event_generator("trackpad", "fly_through_scene", ("state"))
event_generator.set_auto_unbind(False)

# Do logic here

input_device.unbind_event_generator("fly_through_scene")
```

## XRCore Action Maps

Now controllers do not always have the same buttons and each controller may have to be bound in a different way and buttons may be mapped differently. To simplify this, we added the concept of action maps. An action map is a class that contains a set of actions that can be mapped to a controller. The action maps are defined in a json file that is located in the `omni.kit.xr.configuration` extension. Action maps are defined per controller set and one action map contains the list of actions for both the left and right controller.

The list of available action maps can be viewed in the `omni.kit.xr.configuration` extension, in the directory `xrmanifests.action_maps`. The action maps are organized by controller layout, e.g. there are action maps for Oculus, HTC Vive, Valve Index etc. More action maps can be added by the user. The action maps are defined for both left handed and right handed users and some even have layouts for single controllers.

The following settings control which action map is used:
* "/xr/profile/<name_profile>/tools/layout" : This controls the set of tools and set actions that is bound. The default tools/layout is "vr" and that will enable the default toolset in the experience.
* "/xr/dominate_hand" : This controls which hand is used to bind the actions. The default is "right" and that will map the more common actions to the right controller. For left handed users one can set this to "left" to map the dominant actions to the left controller.

Both the AR and VR profiles by default have a set of action maps defined by default. The "vr" action map is the default one. To not use any of the default tools, one can set the tools/layout to a custom key to search for:

```python
import carb.settings

settings = carb.settings.get_settings()
settings.set("/xr/profile/vr/tools/layout", "custom")
```

To check what the currently mapped action map is, one can use the following code:

```python
action_map: XRActionMap = xr_core.get_action_map()
```

When using an action map, events are no longer bound per input device. Since actions can be mapped on either the left or right controller, to bind an event generator, one can use the following code:

```python
event_generator: Optional[XREventGenerator] = xr_core.bind_input_event_generator("xr_menu", ("press", "release"))
```

This will look up in the action map where "xr_menu" should be bound and then binds the event generator to the right controller. To know how an event generator is bound, one can use the following code:

```python
event_generator: Optional[XREventGenerator] = xr_core.bind_input_event_generator("xr_menu", ("press", "release"))

if event_generator is not None:
    input_device_name: str = str(event_generator.get_input_device_name())
    input_name: str = str(event_generator.get_input_name())
else:
    print("xr_menu is not bound to any input device")
```

The same rules for these input event generators apply as for the input event generators bound to an input device directly: when it is already bound, this new binding will replace the old one, until the event generator is released.


## XRCore General Events

Besides events for input devices, XRCore also sends out general XR events that track the state of the XR system. These events are also sent over the message bus and can be subscribed to.

### XRCore enabled/disabled events

The following events are sent when XR mode is enabled or disabled:

* "xr.enable":  This event is sent when XR mode is enabled.
* "xr.disable": This event is sent when XR mode is disabled.
* "xr.update": This event is sent each frame when XR mode is enabled.

In order to listen to these events, one can use the following code:

```python
import carb

def on_xr_enable(event: carb.events.IEvent):
    print("XR mode is enabled")

def on_xr_disable(event: carb.events.IEvent):
    print("XR mode is disabled")

def on_xr_update(event: carb.events.IEvent):
    print("XR mode is updated")

message_bus: carb.events.IEventStream = XRCore.get_singleton().get_message_bus()
message_type: int = carb.events.type_from_string("xr.enable")
subscription1: carb.events.ISubscription = message_bus.create_subscription_to_pop_by_type(message_type, on_xr_enable)

message_type: int = carb.events.type_from_string("xr.disable")
subscription2: carb.events.ISubscription =  message_bus.create_subscription_to_pop_by_type(message_type, on_xr_disable)

message_type: int = carb.events.type_from_string("xr.update")
subscription3: carb.events.ISubscription = message_bus.create_subscription_to_pop_by_type(message_type, on_xr_update)

```

### XRCore display events

The following events are sent when XR displays are enabled or disabled:

* "xr_display.enable": This event is sent when an XR display is enabled.
* "xr_display.disable": This event is sent when an XR display is disabled.
* "xr_display.update": This event is sent each frame when an XR display is enabled.

The xr_display state tracks that actual images are being sent to the head mounted display. Even though xr mode is enabled, it is possible that no display is enabled. For example when the display is switched off, or the run time is waiting for a connection.

### XRCore profile events

The following events are sent when XR profiles are enabled or disabled:

* "xr_profile.<profile_name>.enable": This event is sent when an XR profile is enabled.
* "xr_profile.<profile_name>.disable": This event is sent when an XR profile is disabled.
* "xr_profile.<profile_name>.update": This event is sent each frame when an XR profile is enabled.
* "xr_profile.list_change": This event is sent when the list of profiles changes.
* "xr_profile.change": This event is sent when a new profile is active.

For each profile that is enabled or disabled these events are sent and one can subscribe to them with the following code:

```python
import carb

def on_xr_profile_enable(event: carb.events.IEvent):
    profile_event: XRProfileEvent = XRProfileEvent(event)
    profile_name: str = profile_event.profile
    print(f"XR profile {profile_name} is enabled")

def on_xr_profile_disable(event: carb.events.IEvent):
    print("XR profile is disabled")

def on_xr_profile_update(event: carb.events.IEvent):
    print("XR profile is updated")

message_bus: carb.events.IEventStream = XRCore.get_singleton().get_message_bus()
message_type: int = carb.events.type_from_string("xr_profile.vr.enable")
subscription1: carb.events.ISubscription = message_bus.create_subscription_to_pop_by_type(message_type, on_xr_profile_enable)

message_type: int = carb.events.type_from_string("xr_profile.vr.disable")
subscription2: carb.events.ISubscription = message_bus.create_subscription_to_pop_by_type(message_type, on_xr_profile_disable)

message_type: int = carb.events.type_from_string("xr_profile.vr.update")
subscription3: carb.events.ISubscription = message_bus.create_subscription_to_pop_by_type(message_type, on_xr_profile_update)

```

### XRCore system events

The following events are sent when XR systems are enabled or disabled. An xr system is a plugin like openxr or simulatedxr:

* "xr_system.<system_name>.enable": This event is sent when an XR system is enabled.
* "xr_system.<system_name>.disable": This event is sent when an XR system is disabled.
* "xr_system.<system_name>.update": This event is sent each frame when an XR system is enabled.
* "xr_system.list_change": This event is sent when the list of systems changes.
* "xr_system.change": This event is sent when a new system is active.

For each system that is enabled or disabled these events are sent and one can subscribe to them with the following code:

```python
import carb

def on_xr_system_enable(event: carb.events.IEvent):
    system_event: XRSystemEvent = XRSystemEvent(event)
    system_name: str = system_event.system
    print(f"XR system {system_name} is enabled")

message_bus: carb.events.IEventStream = XRCore.get_singleton().get_message_bus()
message_type: int = carb.events.type_from_string("xr_system.openxr.enable")
subscription1: carb.events.ISubscription = message_bus.create_subscription_to_pop_by_type(message_type, on_xr_system_enable)

```

### XRCore action map events

The following events are sent when a new action map is enabled

* "xr_action_map.change": This event is sent when a new action map is active.


### XRCore input device events

Besides the events for buttons on an input device, XRCore also sends out events when the input device is connected or disconnected.

* "xr_input.<input_device_name>.enable": This event is sent when an input device is connected.
* "xr_input.<input_device_name>.disable": This event is sent when an input device is disconnected.

In the event name that is used as the key, the name of the input device is altered and forward slashes are replaced with underscores. For example the input device "/user/hand/left" becomes "xr_input.user_hand_left".


## XRCore Components

To simplify the creation of tools, XRCore has a couple of classes that can be used to build tools and gui layers.
In this context a tool is a class that encapsulates logic for a specific task, like moving an object or opening a menu.
A gui layer is a class that encapsulates the ui components like controllers and tooltips. Each component is activated and deactivated by sending events to the message bus to enable or disable it. To communicate with the rest of the system, each component listens to the message bus for certain events and reacts to them.

Each component is derived from a base class "XRComponentBase" that takes care of the registration and unregistration of the component with the message bus. It also takes care of binding member functions to the message bus events, ensuring that subscriptions to member functions are properly unsubscribed when the component is destroyed. For the component to be able to react to events, the component needs to start listening to the message bus with the following code:

```python

# Basic structure of a component (tool or gui layer)

class MyTool(XRToolComponentBase):
    def __init__(self):
        super().__init__("my_tool")

    def on_xr_menu(self):
        print("XR menu button pressed")

    def on_enable(self):

        # Register to listen to events
        self.__subs = [
            self.register_message_bus_event_handler("xr_menu.release", self.on_xr_menu),
            self.bind_input_event_generator("xr_menu", ("press", "release"))
        ]
        print("My tool is enabled")

    def on_update(self):
        print("My tool is updated (called each frame, when tool is active)")

    def on_disable(self):

        print("My tool is disabled")

        self.__subs = []

```

If using an action map, whenever the action map changes, all current tools are disabled and the new action map is loaded, after that events are sent out to activate all the tools that are bound to the new action map. The tools are activated in the order they are mentioned in the action map. Since tools are activated by event, any order piece of code can listen to the message bus and execute additional logic when tools are activated or deactivated.

To listen to tool events, one can use the following code:

```python

def on_tool_enable(event: carb.events.IEvent):
    print("Tool is enabled")

def on_tool_disable(event: carb.events.IEvent):
    print("Tool is disabled")

tool_name: str = "my_tool"

message_bus: carb.events.IEventStream = XRCore.get_singleton().get_message_bus()
message_type: int = carb.events.type_from_string("xr_tool.my_tool.enable")
subscription1: carb.events.ISubscription = message_bus.create_subscription_to_pop_by_type(message_type, on_tool_enable)

message_type: int = carb.events.type_from_string("xr_tool.my_tool.disable")
subscription2: carb.events.ISubscription = message_bus.create_subscription_to_pop_by_type(message_type, on_tool_disable)

```

Similar to tools, gui layers follow the same pattern. They are activated and deactivated by sending events to the message bus to enable or disable them. Unlike tools, gui layers are enabled by the "/xr/profile/<profile_name>/gui_layers" setting. Each profile has a predefined list of gui layers that are enabled by default. Currently there are two gui layers:

* "controllers": This is the default gui layer and contains the controller models
* "tooltips": This is an additional gui layer that displays tooltips next to the controllers

Gui layers are created by deriving from the "XRGuiLayerComponentBase" class. It follows the same structure as a tool component. To listen to gui layer events, one can use the following code:

```python

def on_gui_layer_enable(event: carb.events.IEvent):
    print("Gui layer is enabled")

def on_gui_layer_disable(event: carb.events.IEvent):
    print("Gui layer is disabled")

gui_layer_name: str = "my_gui_layer"

message_bus: carb.events.IEventStream = XRCore.get_singleton().get_message_bus()
message_type: int = carb.events.type_from_string(f"xr_gui.{gui_layer_name}.enable")
subscription1: carb.events.ISubscription = message_bus.create_subscription_to_pop_by_type(message_type, on_gui_layer_enable)

message_type: int = carb.events.type_from_string(f"xr_gui.{gui_layer_name}.disable")
subscription2: carb.events.ISubscription = message_bus.create_subscription_to_pop_by_type(message_type, on_gui_layer_disable)

```

## XRCore Managed Usd Object

To deal with the complexity of the USD/USD-RT stage, XRCore has a collection of managed USD objects. These managed objects are meant to simplify the creation a basic XR UI. These managed objects are stored in a special class called "XRUsdLayer". The default "XRUsdLayer" that is created when an XR experience starts and is stored under a dedicated path in the stage under "/_xr/gui". Both the "controller" and the "tooltips" gui layers us this object to create managed objects to deal with for instance the selection beam and the teleport arc. The XRUsdLayer also deals with scale and up axis transformations, so that the XR UI is always rendered in the correct scale and orientation. By default the XRUsdLayer is using a scale of 1.0cm and y axis as up. If needed a new XRUsdLayer can be created in python:

```python
xr_usd_layer: XRUsdLayer = XRCore.get_singleton().create_xr_usd_layer("path/to/usd/layer", meters_per_unit=0.01, up_axis="y" )
```

The XRUsdLayer is created on the session layer of the usd stage. If one is creating tools or gui_layers, the base class already has a reference to the XRUsdLayer and one does get the reference to the XRUsdLayer, using the following code:

```python

class MyTool(XRToolComponentBase):
    def __init__(self):
        super().__init__("my_tool")
        self._controllers_usd_layer: XRUsdLayer = self.get_usd_layer("controllers")
        # This will create a new XRUsdLayer on the session layer of the usd stage at path "/_xr/gui/controllers"

```


There are several types of managed usd primitives (or collection of primitives) that can be created inside the XRUsdLayer:

* "asset": This object contains a usd asset. Unlike a normal usd reference to an asset, the managed object will automatically read the scale and orientation from the usd file and apply it to the parent prim under which the asset is added to ensure that an asset like a controller is always scaled correctly.
* "beam": This object contains a selection beam. A beam is a cylinder that is used to visualize a ray cast. It contains all the logic to ensure it is scaled to the length from the origin of the beam to the point where it hits the object. The beam also contains the logic to resolve which object is hit.
* "teleportArc": This object contains a teleport arc. A teleport arc is a curved version of the beam object, and stretches from the origin of the beam to the point where it hits the floor. In this case it also tracks where on the floor the beam is hitting. The teleport arc is aware of what is up and will start at a given inclination angle and then turn downwards to the floor.
* "reorient": This is a special transform, that can be linked to an input device. A reorient object is a transform that is used to reorient the object to the correct orientation. It can automatically align an object with a controller or ensure an object is pointing upwards.
* "link": This object contains a link to another usd prim in the scene. A link is a transform that is used to link two objects together. The linked object will be updated each frame to match the position of the link. This is useful for instance to grab an object by linking it to the controller.
* "reference": This object contains a reference to another usd prim in the scene. The reference differs from a normal usd reference in the sense that it will automatically read the scale and orientation from the referenced prim and apply it to the parent prim under which the asset is added to ensure that it is scaled correctly.
* "transform": This object contains a transform primitive. It is a short cut to making a transform in USD. It has a simplified interface to set the position, rotation and scale, in stage space as well as local space.

Besides the managed usd primitives, the XRUsdLayer also contains a few builtin transforms that can be used follow the poses of the various input devices. These poses are updated automatically just before rendering in XRCore for each XRUsdLayer available. XRCore will ensure that USD-RT is update for these prim hierarchies. To make a primitive transform available in XRUsdLayer, call the following python code:

```python

class MyTool(XRToolComponentBase):
    def __init__(self):
        super().__init__("my_tool")
        usd_layer: XRUsdLayer = self.get_usd_layer("controllers")

        base_path: str = usd_layer.ensure_device_prim_path("/user/hand/left")

```


### XRCore Managed Usd primitives

A XRUsdLayer asset can be constructed as follows:

```python

class MyTool(XRToolComponentBase):
    def __init__(self):
        super().__init__("my_tool")
        usd_layer: XRUsdLayer = self.get_usd_layer("controllers")

        base_path: str = usd_layer.ensure_device_prim_path("/user/hand/left")
        asset_prim_path: str = base_path + "/controller"

        usd_layer.add_asset(asset_prim_path, group="controllers", file_path="path/to/usd/file", visible=True, pickable=False)
```

Each managed primitive in the XRUsdLayer has a "pickable" and "visible" attribute with which to control if the primitive is visible and whether it can be hit by a ray cast (More about ray casting below). To change these attributes after the primitive has been made call the following python functions:

```python

    usd_layer.hide(asset_prim_path) # to hide the primitive
    usd_layer.show(asset_prim_path) # to show the primitive

    usd_layer.set_pickable(asset_prim_path, False) # To set whether the asset is pickable
```

To remove a set of managed primitives, you can use the "remove" function:

```python

    usd_layer.remove_group("controllers")
```

### XRCore Managed Usd beam

To create a managed beam use the following function:

```python
class MyTool(XRToolComponentBase):
    def __init__(self):
        super().__init__("my_tool")
        usd_layer: XRUsdLayer = self.get_usd_layer("controllers")

        base_path: str = usd_layer.ensure_device_prim_path("/user/hand/left")
        beam_prim_path: str = base_path + "/beam"

        # create a beam with a maximum length of 10000 cm , a tube radius of 2 cm, visible and not pickable
        usd_layer.add_beam(beam_prim_path, group="controllers", material_reference="prim_path_to_material", max_length=10000, tube_radius=2, visible=True, pickable=False)

```

This will create a beam pointing from a pose given by its parent prim. The beam will resolve what it points at every frame, using a ray cast. To check what the ray is pointing at use the following code:

```python

    target_info: XRTargetInfo = usd_layer.get_target_info(beam_prim_path)
    hit_point: Gf.Point3d = target_info.hit_point
    hit_normal: Gf.Vector3d = target_info.hit_normal
    hit_distance: float = target_info.hit_distance
    hit_prim_path: str = target_info.hit_prim_path

```

To access a primitive that is attached to the end of the beam, use the following code:

```python

    end_point_prim_path: str = usd_layer.get_end_prim_path(beam_prim_path)

    # For example: add an asset at the end point of the beam
    usd_layer.add_asset(end_point_prim_path + "/end_point_asset", group="end_beam", file_path="path/to/usd/file", visible=True, pickable=False)
```

### XRCore Managed Usd Teleport Arc

To create a managed teleport arc use the following function:

```python

class MyTool(XRToolComponentBase):
    def __init__(self):
        super().__init__("my_tool")
        usd_layer: XRUsdLayer = self.get_usd_layer("controllers")

        base_path: str = usd_layer.ensure_device_prim_path("/user/hand/left")
        teleport_arc_prim_path: str = base_path + "/teleport_arc"

        usd_layer.add_teleport_arc(teleport_arc_prim_path, group="controllers", material_reference="prim_path_to_material", max_height=10000, tube_radius=2, visible=True, pickable=False)

```

Similar to the beam, the teleport arc will resolve what it points at every frame, using a ray cast. To check what the ray is pointing at use the following code:

```python

    target_info: XRTargetInfo = usd_layer.get_target_info(teleport_arc_prim_path)

```

### XRCore Managed Usd Link

To create a managed link use the following function:

```python

    class MyTool(XRToolComponentBase):
        def __init__(self):
            super().__init__("my_tool")
            usd_layer: XRUsdLayer = self.get_usd_layer("controllers")

            base_path: str = usd_layer.ensure_device_prim_path("/user/hand/left")
            link_prim_path: str = base_path + "/link"

            usd_layer.add_link(link_prim_path, group="controllers", link_path="prim_path_to_link", link_path="/usd/path/to/linkable_object")

```

This will link "/usd/path/to/linkable_object" to the link primitive. So when the link primitive is moved, the linked object will follow. XRCore will update the linked primitive each frame to match the position of the link primitive. This is done in USD-RT, when the link is removed, the new location of the linked primitive in USD can be updated using the following code:

```python

    usd_layer.commit_link_transform(link_prim_path)

```


## XRCore Ray casts

Another tool that is available in XRCore is the ability to cast a ray and check what it is hitting. This is useful as the USD primitives do not always have a bounding box that can be used to check what is being hit. So instead we use the ray tracing engine to check what is being hit. To cast a ray use the following code:

```python

    def callback(rays: Iterable[XRRay], results: Iterable[XRRayQueryResult]):
        """
        Function called when ray cast completes
        """

        for ray, result in zip(rays, results):
            if result.valid:
                print(f"Ray hit {result.get_target_enclosing_model_usd_path()} at {result.hit_position}")
            else:
                print("Ray did not hit anything")

    rays: list[XRRay] = []

    for direction in [ Gf.Vec3d(1,0,0), Gf.Vec3d(0,1,0), Gf.Vec3d(0,0,1)]:
        # add sample ray
        rays.append(XRRay(Gf.Vec3d(0,0,0), direction, 0.0, 10000.0))

    XRCore.get_singleton().submit_multi_raycast_query(rays, callback)

```

Ray casts are done asynchronously and the callback is called within 1 or 2 frames, when the ray cast is complete.
