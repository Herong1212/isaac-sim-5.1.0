# Settings

The `carb.audio-forge` plugin itself has a few settings that affect its behavior.  However, for the
most part it is controlled programmatically by extensions and plugins that depend on it.  The settings it
does have mostly cover debugger assistance and device behavior.  For almost all applications, the default
settings will be sufficient.

The following settings will affect the behavior of the `carb.audio` extension:

## Device Selection

The `carb.audio` extension supports multiple system specific device selection backends.
These backends provide an abstraction layer for various platform specific audio APIs and is a common base
that the `carb.audio-forge` plugin operates on.  Only one backend may be selected and it cannot be changed
at runtime once selected.  All supported backends for a platform provide the same functionality, just based
on top of different system specific APIs.  When multiple backends are available for a platform, choosing a
different backends could however provide a way to get different performance characteristics such as lower
latency or access to a different set of audio devices.  For almost all applications however, allowing the
`carb.audio-forge` plugin to automatically choose the backend is sufficient.

* `/audio/deviceBackend`: Accepts a string containing the name of the backend to use.  Backend names are
  case insensitive.  All platforms support a backend called 'null'.  The 'null' backend simply ignores
  all output sent to it.  The following additional backends are supported:

  * Windows: The Windows platform only supports the `WASAPI` backend.  This will use the Windows Audio
    System API.  There are however two versions of the `WASAPI` backend available.  See the
    `/audio/WASAPI/legacyBackend` setting for more information on this.
  * Linux: The Linux platform supports the `ALSA` and `PuseAudio` backends.  These use the Advanced Linux
    Sound Architecture and PulseAudio APIs respectively.  The `ALSA` backend typically has lower latency
    but the `PulseAudio` backend is typically more friendly to end users and system hardware cooperation.
    Both backends are identically functional otherwise.
  * Backends also exist for the Mac and Android platforms, but those platforms are not supported by Omniverse.

* `/audio/WASAPI/legacyBackend`: Allows the legacy version of the `WASAPI` backend to be used.  This backend
  was superseded by the newer default `WASAPI` backend but is still functional.  The legacy backend is
  identically functional to the new one, but can still be useful for debugging device communication issues.
  This setting is only used on Windows.
* `/audio/pulseAudio/enumerateMonitors`: Allows all 'monitor' devices to also be enumerated when using the
  `PulseAudio` backend.  A monitor device is a capture device that is attached to a playback device.  Each
  playback device in the system has an associated monitor device.  Each monitor device is just a loopback
  to the output that is playing on the assicated playback device though (ie: as it the output device's
  speaker port had been connected to a line in port with a patch cable).  By default monitor devices will
  not be enumerated since they will not be external data sources (ie: connected to a microphone).  This
  setting is only used on Linux when the `PulseAudio` backend is selected.
* `/audio/maxDefaultChannels`: Limits the number of reported channels on all devices if they are not limited
  by the system specific backend API.  Some devices, especially virtual devices, can report supporting very
  large channel counts (ie: 64, 99, etc).  If these devices are used, it can lead to `carb.audio-forge` not
  being able to automatically map the playback context's channel count to the device's preferred channel layout.
  In general, only channel counts up to 16 have industry standard consumer level channel mappings and speaker
  layouts.  If `carb.audio-forge` cannot do this automatic mapping, it is left up to the host app to
  programmatically define the speaker layout for the context.  Arbitrary speaker layouts are supported by
  `carb.audio-forge` by explicitly specifying the position of each speaker.  This only affects the device's
  'preferred' channel count.  It is still possible to create a playback context with more than this number
  of channels by explicitly setting the desired channel count when creating a new context or setting a new
  output.  By default the max channel count will be capped to 8 channels.  This will be picked up by
  `carb.audio-forge` as a 7.1 surround sound layout.


## Null Device

The `null` backend device simply ignores all output buffers that are sent to it for playback
and only produces silent buffers for capture.  All playback and capture timing is still maintained by this
backend.  The `null` backend does have some controls that can affect its behavior though.

* `/audio/nullBackend/DeviceCount`: Sets the number of devices that should be reported by the `null` backend.
  All enumerated devices will be identical except for the name.  This is mostly used for testing purposes.
  By default only one device will be reported for playback and one for capture.
* `/audio/nullBackend/IsFunctional`: This setting indicates whether the devices enumerated by the `null`
  backend are considered functional.  If this is set to `true`, the null devices will always open successfully
  and be able to be interacted with.  If this is set to `false`, the null devices will fail to open.  This
  can be used for testing purposes to verify that nothing fails or crashes if no devices are found in the
  system.  This defaults to `true`.
* `/audio/nullBackend/CaptureTestMode`: Testing setting to indicate whether the null backend should produce
  patterned data or silence for capture contexts.  When set to `true`, patterned data will be returned in
  each buffer.  When set to `false`, only silent buffers will be produced.  This defaults to `false`.
* `/audio/nullBackend/ReportOverruns`: Testing setting to indicate whether the null backend should randomly
  report device underrun and overrun events.  An underrun occurs when a playback context isn't producing
  new data fast enough and the device runs out of data to play.  An overrun occurs when a capture context
  isn't reading new data fast enough from the device and its buffers fill up.  This defaults to `false`.


## Debugging Settings

These settings help aid in debugging efforts of audio issues.  Some of these settings
can produce a very large amount of extra debugging output if enabled and should be used with care.  Enabling
some of these settings can produce so much output that it affects audio processing performance.  If this occurs,
there will be audible pops or static during playback.

* `/audio/debugChannels`: Specifies the extra logging channels to enable or disable in the `carb.audio-forge`
  plugin.  These logging channels provide a lot of extra information about what is happening, but can also
  produce a very large amount of logging output.  Using these channels can help narrow down the logging
  information to only a subset of the possible log messages.  This setting is intended to take a string
  that specifies the channels and logging levels to enable or disable.  The string is split into set of
  one or more comma separated channel specifiers.  Each specifier takes the form "[<level>]{+-}<channel>".
  The `<level>` value is one of "verbose", "info", "warn", "error", or "fatal".  If the level is omitted,
  all logging levels are enabled for the specified channel.  The `{+-}` is either a '+' character to enable
  the named channel and level, or '-' to disable that channel and level.  The channel name is one of the
  following:

  * `all`: Special channel name that affects all channels.
  * `audio`: Generic messages from the audio library.
  * `balance`: Messages related to Balance and fade calculations.
  * `bus`: Messages related to playback bus assignments and calculations.
  * `capture`: Messages related to audio capture.
  * `codec`: Messages related to encoding and decoding audio data.
  * `context`: Messages related to playback and capture context management.
  * `convert`: Messages related to data format conversions.
  * `data`: Messages related to audio data processing.
  * `device`: Messages related to device detection, enumeration, and selection.
  * `eventpoint`: Messages related to event point and loop point processing and calculations.
  * `flac`: Messages related to FLAC data format processing.
  * `group`: Messages related to the `carb::audio::IAudioGroup` interface.
  * `heap`: Messages related to voice heap management.
  * `load`: Messages related to loading audio data from disk or memory.
  * `metadata`: Messages related to processing audio file metadata.
  * `mp3`: Messages related to MP3 data format processing.
  * `notify`: Messages related to the notification of device changes.
  * `ogg`: Messages related to OGG data processing.
  * `ogg_seek`: Messages related to seek operations in OGG data.
  * `opus`: Messages related to OPUS data format processing.
  * `output`: Messages related to output device selection and processing.
  * `outputstream`: Messages related to output stream conversion usage.
  * `pcm`: Messages related to raw PCM codec operations.
  * `playback`: Generic messages related to audio playback.
  * `riff`: Messages related to RIFF data format processing.
  * `stream_decoder`: Messages related to dynamically decoding a file as it plays.
  * `voice`: Messages related to voice management.
  * `vorbis`: Messages related to Vorbis data format processing.

  As an example, the channels string "-all,+flac,+mp3" will disable all channels followed by enabling only the
  `flac` and `mp3` channels.  The channel string "+all,-data,-bus" will enable all channels except the `bus`
  and `data` channels.  The channel string "warn+all,error+all" will enable warning and error messages for
  all channels.

* `/audio/forgeChannels`: Enables extra logging channels in the `ForgeAudio` library that `carb.audio` uses.
  Enabling these can produce an extreme amount of logging output and significantly affect audio processing
  performance.  These should be used with care.  The format for specifying channels to enable here is the
  same as for `/audio/debugChannels` above except that the channel names are different.  There are too many
  channels to list all of them here, but the main audio related channels that may be interesting are:

  * `forgeaudio`: Generic hardware API abstraction layer messages.
  * `forgeaudio_backend`: Messages related to the selected backend.
  * `forgeaudio_data`: Messages related to device data processing.
  * `forgeaudio_latency`: Messages related to backend latency calculations.
  * `forgeaudio_stats`: Messages related to data processing statistics.
  * `thread`: Include the thread ID with each message.
  * `x3daudio`: Messages related to spatial audio calculations.
  * `xapofx`: Messages related to audio effect plugin processing.
  * `xaudio`: Generic messages related to audio data processing and low-level voice management.
  * `xaudio_debug`: Messages related to debugging low-level object management such a reference counts.
  * `xaudio_process`: Messages related to processing the audio graph.
  * `xaudio_simd`: Messages related to SIMD processing of audio data.

* `/audio/allowThreadTermination`: Enables or disables the behavior of forcibly terminating the audio processing
  engine thread if it does not respond to stop requests within 5 seconds.  Enabling this setting will guarantee
  that the engine thread is always terminated when requested, however it could leave the audio system in an
  unknown state.  Most cases of stopping the engine thread will trivially succeed within 10ms.  It is possible
  however that the engine thread could get stuck in certain rare situations though.  Disabling this setting
  just allows the engine thread to be leaked if it does not terminate on its own when requested.  This defaults
  to `true`.
* `/audio/context/forceDecodeLargeSound`: Allows sound files that would decode to take up more than half of the
  system's physical RAM will always be decoded into memory instead of streaming them from their original source
  (ie: file on disk, blob in memory, etc).  By default, sound files over this limit will always be streamed from
  their original source.  If the system has less than 2GB of RAM, all sound files will be streamed from their
  original source.  This setting can be used to debug potential issues with voice streaming of large files.  This
  setting defaults to `false`.
