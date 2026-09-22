# Settings

The `omni.uiaudio` extension does not create or maintain any settings of its own, but some of its behaviour
can be affected by setting modified elsewhere.  This extension will modify its behaviour based on the values
of the following settings:

* `/app/audio/enabled`: Boolean setting to indicate whehter any of the audio systems should initialize.
  When set to `true`, the `omni.uiaudio` extension will startup and behave normally.  When set to `false`,
  the `omni.uiaudio` extension will not startup and any calls into it will be silently ignored.
* `/persistent/audio/context/uiVolume`: Floating point setting to indicate the relative volume level to use
  when playing back UI sounds.  This should be 1.0 for full volume, 0.0 for silence, or any value in between
  to make linear volume level changes to UI sounds.  This volume level is always relative to the 'master'
  volume level specified in `/persistent/audio/context/masterVolume`.  Changing this setting at any point
  during a session will be picked up by the `omni.uiaudio` extension to adjust the playback volume.  This
  defaults to 1.0.
* `/persistent/audio/context/masterVolume`: Floating point setting to indicate the relative volume level to use
  for the selected playback device.  This should be 1.0 for full volume, 0.0 for silence, or any value in between
  to make linear volume level changes to UI sounds.  This volume level is always relative to the device's current
  maximum volume level.  Changing this setting at any point during a session will be picked up by the
  `omni.uiaudio` extension to adjust the playback volume.  This defaults to 1.0.
* `/persistent/audio/context/deviceName`: String setting to indicate the name and ID of the device to use for
  playback of UI sounds.  If this device is still connected to the system when the `omni.uiaudio` extension
  starts up, it will be used for playback.  Any time this setting changes during a session, the `omni.uiaudio`
  extension will use that to change to a new playback device immediately.  This default to the system's default
  audio playback device.
