# Audio Plugin Wrapper Extension

## Overview

The `carb.audio` extension wraps up the `carb.audio-forge` plugin and its associated Python bindings.
The plugin does have a C++ interface as well, but it is not exposed here through C++ header files.  Only the
audio playback interface is exposed through the Python API.  The audio capture and audio data management
interfaces are not fully exposed to Python here.  To use them, the C++ API should be used directly instead.

This extension has two main purposes:

* To expose the Python API for the plugin to Kit based apps.  Other extensions or app developers can simply
  import the `carb.audio` Python module and make use of its interfaces for audio playback.
* To act as a dependency for other extensions that want to use the C++ API and plugin.  If this extension is
  loaded as a dependency of another extension or an app, all of its interfaces become available through the
  normal interface framework.

Note that the Python API for this extension will operate on separate audio contexts from the one that is
associated with the current USD stage.  In the current version it is not possible to retrieve the audio
playback context used by the current USD stage.  Similarly, this Python API cannot be used to interoperate
with the objects returned from the USD stage audio API.
