# Overview

The `omni.kit.audiodeviceenum` extension exposes two main bits of functionality:

* A C++ and Python API that allows information about attached audio devices to be retrieved.  The device count
  and information about each device such as name, system specific ID, frame rate, channel count, sample format,
  etc can be collected.
* An audio preferences page that is added to the Kit preferences window when this extension loads.  Changing
  values in the various controls on this preferences page modifies several persistent settings that affects
  audio playback and capture behavior in the current Omniverse app.  These settings include device selection,
  global volume settings, asset streaming behavior, and some debugging functionality.

The audio preferences page is added automatically to the calling app's preferences window if it exists.  The
page will be removed if the extension is unloaded.

The C++ and Python APIs provide individual access to each device's various capabilities but do not allow them
to be modified.  These APIs are intended to be used to collect device information to allow the user to decide
on an appropriate device to choose or to allow an app to automatically find the most suitable device.  The
audio preferences page makes use of the Python API for this to present device information to the user for
selection.
