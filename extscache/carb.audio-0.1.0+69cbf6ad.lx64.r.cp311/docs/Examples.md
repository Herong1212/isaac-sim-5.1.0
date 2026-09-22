# Examples

## Loading a Sound and Playing It

There are many different ways the `carb.audio` extension's API can be used.  The most basic usage is to load and
play a sound file.  The basic steps are as follows:

* Import the `carb.audio` python module.
```python
import carb.audio
```
* Acquire the `IAudioPlayback` and `IAudioData` interfaces.  These are the main entry points for all of the audio
  functionality.
```python
playback = carb.audio.acquire_playback_interface()
data = carb.audio.acquire_data_interface()
```
* Create a playback context.  This object isolates and manages all audio playback operations.  Note that only
  16 playback contexts are allowed per process at any given time.  Creating a new context will fail by
  returning `None` if too many already exist.
```python
context = playback.create_context()
```
* Load the audio file from disk.  WAV, FLAC, Ogg/Vorbis, MP3, and Opus files are supported for playback.
```python
sound_data = data.create_sound_from_file("soundToPlay.mp3")
```
* Play the sound and wait for it to finish.
```python
import time

voice = context.play_sound(sound_data)

while voice.is_playing():
    time.sleep(0.250)
```
* Clean up the playback context and sound data object.  Note that because of the limited number of available
  playback contexts, it is best practice to always explicitly clear out a context object when it is no longer
  needed instead of depending on Python's garbage collection to clean it up in a timely manner.  If the garbage
  collector is depended on, playback context objects may not be cleaned up immediately and could cause other
  attempts to create new contexts to fail unexpectedly.
```python
context = None
sound_data = None
```

This would be the full script of the above example.  Some additional functionality has also been added here to
demonstrate how to monitor the playback location as the voice plays:
```python
import carb.audio
import time

playback = carb.audio.acquire_playback_interface()
data = carb.audio.acquire_data_interface()

context = playback.create_context()

sound_data = data.create_sound_from_file("soundToPlay.mp3")

voice = context.play_sound(sound_data)

while voice.is_playing():
    pos = voice.get_play_cursor(carb.audio.UnitType.MILLISECONDS)
    print(f"Played the test sound for {pos / 1000.0}s so far.")
    time.sleep(0.250)

sound_data = None
context = None
print("done!")
```


## Enumerating Playback Devices

The `IAudioPlayback` interface contains functions that allow information about the system's connected
playback devices to be retrieved.  The information about each device consists of a name, a GUID, a
preferred channel count, a preferred frame rate, and a preferred data format.  A playback context
can be created to produce audio in any PCM format on any device, but using the device's preferred
format is typically the most efficient since the final stream from the playback engine doesn't need
to be converted to the device's format before submitting it.

```python
import carb.audio

playback = carb.audio.acquire_playback_interface()

device_count = playback.get_device_count()
print(f"found {device_count} playback devices on the system:")

for i in range(device_count):
    caps = playback.get_device_caps(i)
    print(f"    {i + 1}: '{caps.get_name()}':")
    print(f"        index = {caps.index}")
    print(f"        flags = {hex(caps.flags)}")
    print(f"        guid = {{{str(caps.guid)}}}")
    print(f"        channels = {caps.channels}")
    print(f"        frame_rate = {caps.frame_rate}")
    print(f"        format = {caps.format}")
```

### Selecting a Device For Playback

Once the available devices and their information have been enumerated, a device can be selected on a
playback context using the `Context.set_output()` function.  This example extends the device information
example above.

```python
import carb.audio
import time

playback = carb.audio.acquire_playback_interface()
data = carb.audio.acquire_data_interface()

sound_data = data.create_sound_from_file("soundToPlay.mp3")
context = playback.create_context()

device_count = playback.get_device_count()
print(f"found {device_count} playback devices on the system:")

for i in range(device_count):
    caps = playback.get_device_caps(i)
    print(f"    {i + 1}: '{caps.get_name()}':")
    print(f"        index = {caps.index}")
    print(f"        flags = {hex(caps.flags)}")
    print(f"        guid = {{{str(caps.guid)}}}")
    print(f"        channels = {caps.channels}")
    print(f"        frame_rate = {caps.frame_rate}")
    print(f"        format = {caps.format}")

print(f"choose which device to output to from the list above (1-{device_count} or 'q' to quit):")

index = -1
while True:
    index_str = input()

    if index_str == 'q':
        break

    index = int(index_str)

    if index > 0 and index <= device_count:
        break

    print(f"unexpected value.  Please enter a number from 1 to {device_count} or enter 'q' to quit.")

if index > 0:
    desc = carb.audio.OutputDesc()
    desc.device_index = index - 1
    caps = playback.get_device_caps(desc.device_index)

    result = context.set_output(desc)

    if result == carb.audio.AudioResult.OK:
        print(f"successfully set the device '{caps.get_name()}' as active.")

    else:
        print(f"failed to set the active device to '{caps.get_name()}': {result}")


    # play a sound on the new device.
    voice = context.play_sound(sound_data)

    while voice.is_playing():
        time.sleep(0.250)

sound_data = None
context = None
print("done!")
```


## Exceptions

Some functions in the `carb.audio` Python module will throw an exception if they fail instead of returning
`None` or an invalid object.  These exceptions can be caught and used to handle failure cases in Python
code.  The following example takes the simple playback example from above and adds exception handling to
it.

```python
import carb.audio
import time

playback = carb.audio.acquire_playback_interface()
data = carb.audio.acquire_data_interface()

try:
    context = playback.create_context()

    sound_data = data.create_sound_from_file("soundThatDefinitelyDoesNotExist.mp3")

    voice = context.play_sound(sound_data)

    while voice.is_playing():
        pos = voice.get_play_cursor(carb.audio.UnitType.MILLISECONDS)
        print(f"Played the test sound for {pos / 1000.0}s so far.")
        time.sleep(0.250)

except carb.audio.SoundDataError as err:
    print("got a sound data error exception:")
    print(f"    {err}")

except carb.audio.ContextError as err:
    print("got a context error exception:")
    print(f"    {err}")

except carb.audio.DecoderError as err:
    print("got a decoder error exception:")
    print(f"    {err}")

except Exception as err:
    print("got a generic exception:")
    print(f"    {err}")

sound_data = None
context = None
print("done!")
```
