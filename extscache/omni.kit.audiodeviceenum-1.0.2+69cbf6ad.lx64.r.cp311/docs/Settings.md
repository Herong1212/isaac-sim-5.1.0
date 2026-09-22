# Settings

The `IAudioDeviceEnum` interface does not modify or consume any settings itself.  However, the audio preferences
page does consume and allow the user to modify them indirectly.  The following settings will be modified by
the preferences page and will affect how other audio related components behave in the app:

* Audio Device Selection:

  * `/persistent/audio/context/deviceName`: String setting that contains the system specific ID of the device
    that should be chosen for audio playback if it is still connected to the system.  If the device is no
    longer connected to the system at the time it needs to be opened, the system's default playback device will
    be used instead.  By default, the system's default playback device will be used.
  * `/persistent/audio/context/captureDeviceName`: Seting setting that contains the system specific ID of the
    device that should be chosen for audio capture if it is still connected to the system.  If the device is
    no longer connected to the system at the time it needs to be opened, the system's default capture device
    will be used instead.  By default, the system's default capture device will be used.
  * `/persistent/audio/context/speakerMode`: The speaker layout to use for audio playback.  The selected
    speaker layout does not necessarily need to be directly supported by the output device.  If the device
    does not natively support the selected layout, the output signal will be automatically mixed to match
    the device's supported layout.  For example, if a '5.1 surround' layout is selected, six channels of
    output data will be produced even on a stereo device.  The final output to the device however will
    automatically downmix the signal to stereo before outputting.  This setting may be one of the following
    industry standard speaker layout names:

    * `auto-detect`: Use the device's preferred speaker layout.  This is device specific and will often
      default to stereo for most devices.  For devices that report a preferred layout with higher channel
      counts such as 5.1, that layout will be selected instead.  This is the default setting.
    * `mono`: Only use a single channel of output.  The way this plays back may be device specific.  For
      example, some devices may output the same signal to all speakers whereas other devices may output
      to only a single speaker such as the front left or front center speaker.
    * `stereo`: Output the signal to the front left and front right speakers.  Two channels of output data
      will be produced.
    * `2.1`: Output the signal to the front left and right speakers plus the low frequency effect channel.
      Three channels of output data will be produced.
    * `quad`: Output the signal to the front and back left and right speakers.  Four channels of output data
      will be produced.
    * `4.1 surround`: The same layout as 'quad' plus the low frequency effect channel.  Five channels of
      output data will be produced.
    * `5.1 surround`: Output the signal to the front left and right, side left and right, front center, and
      the low frequency effect speakers.  Six channels of output data will be produced.
    * `7.1 surround`: Output the signal to the front, side, and back left and right speakers plus the low
      frequency effect speaker.  Eight channels of output data will be produced.
    * `7.1.4 surround`: Output the signal to the front, side, and back left and right speakers, the low
      frequency effect speaker, and the top front and top back left and right speakers.  Twelve channels
      of output data will be produced.
    * `9.1 surround`: Output the signal to the front, front wide, side, and back left and right speakers,
      plus the low frequency effect speaker.  Ten channels of output data will be produced.
    * `9.1.4 surround`: Output the signal to the front, front wide, side, back, top front, and top back left
      and right speakers, plus the low frequency effect speaker.  Fourteen channels of output data will be
      produced.
    * `9.1.6 surround`: Output the signal to the front, front wide, side, back, top front, top back, and
      top side left and right speakers, plus the low frequency effect speaker.  Fourteen channels of
      output data will be produced.

* Audio Player Extension Settings:

  * `/persistent/audio/context/closeAudioPlayerOnStop`: Boolean setting to indicate that the audio player
    window should automatically close when it finishes playing the current sound.  This defaults to 'false'.
  * `/persistent/audio/context/audioPlayerAutoStreamThreshold`: Integer setting to indicate the minimum
    decoded size in kilobytes of an audio asset that the audio player extension
    should stream a compressed sound instead of decoding it into memory first.  Setting this to 0 will always
    decode the asset into memory on load.  This setting defaults to 256KiB.

* Global Volume Settings:

  * `/persistent/audio/context/masterVolume`: Floating point setting to indicate the maximum volume level
    that all audio output from the USD stage can have.  This volume level is relative to the device's current
    system volume level.  Changing this value will not modify the current system volume level for the device.
    A value of 1.0 will match the device's volume level.  A value of 0.0 will be silence.  A value larger
    than 1.0 will increase the volume level beyond the device's volume level, but is likely to cause audio
    artifacts due to clipping.  This defaults to 1.0.
  * `/persistent/audio/context/usdVolume`: Floating point setting to indicate the maximum relative volume
    level for the USD stage audio.  This setting has the same characteristics as the master volume setting.
    This defaults to 1.0.
  * `/persistent/audio/context/spatialVolume`: Floating point setting to indicate the maximum relative volume
    level for the spatial audio prims in the USD stage.  This setting has the same characteristics as the
    master volume setting.  This defaults to 1.0.
  * `/persistent/audio/context/nonSpatialVolume`: Floating point setting to indicate the maximum relative volume
    level for the non-spatial audio prims in the USD stage.  This setting has the same characteristics as the
    master volume setting.  This defaults to 1.0.
  * `/persistent/audio/context/uiVolume`: Floating point setting to indicate the maximum relative volume
    level for the sound played by the `omni.uiaudio` extension.  This setting has the same characteristics as the
    master volume setting.  This defaults to 1.0.

* Audio Preferences Page Settings:

  * `/exts/omni.kit.window.preferences/show_audio`: Boolean setting to indicate whether the audio preferences
    page will be installed on extension load or not.  Set to `true` to have the audio preferences page be
    installed when `omni.kit.audiodeviceenum` loads.  The page will be removed if and when the extension is
    unloaded.  Set to `false` to skip installing the audio preferences page.  Defaults to `true`.

* Asset Streaming Settings:

  * `/persistent/audio/context/autoStreamThreshold`: Integer setting to indicate the minimum decoded size in
    bytes of an audio asset that the USD stage audio manager should stream a compressed sound instead of
    decoding it into memory first.  If this is set to 0, sound assets will always be decoded into memory by
    default unless specifically overridden in the USD prim.  This setting defaults to 0KiB.

* Debugging Settings:

  * `/persistent/audio/context/streamerFile`: String setting to indicate the path of the .wav file that will
    be used to capture the USD stage's audio output to file if enabled.  This defaults to an empty string.
  * `/audio/context/enableStreamer`: Boolean setting to indicate whether the USD stage's audio should be
    captured to the file named by `/persistent/audio/context/streamerFile`.  This defaults to `false` and
    will not persist from one session to another.
