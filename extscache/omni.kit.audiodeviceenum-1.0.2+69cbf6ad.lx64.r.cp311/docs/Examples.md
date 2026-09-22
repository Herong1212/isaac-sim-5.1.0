# Examples

## Enumerating Playback Devices

Collecting information about the connected audio devices is relatively straightforward.  The only information
that is needed is the device direction (playback or capture), and the index of the device to colelct the
information for.  The index of the device is just an integer ranging from 0 to one less than the total
device count for the requested direction.

### Python

The example below collects the information about all of the playback devices that are currently connected
to the system.  To enumerate the capture devices instead, the only change needed is to change line 5 to
set `direction` to the following:
```python
direction = omni.kit.audiodeviceenum.Direction.CAPTURE
```

Enumerating playback devices:
```python
import omni.kit.audiodeviceenum

device_enum = omni.kit.audiodeviceenum.get_audio_device_enum_interface()

direction = omni.kit.audiodeviceenum.Direction.PLAYBACK

count = device_enum.get_device_count(direction)

name = device_enum.get_device_name(direction, 0)
id = device_enum.get_device_id(direction, 0)
channels = device_enum.get_device_channel_count(direction, 0)
frame_rate = device_enum.get_device_frame_rate(direction, 0)
sample_size = device_enum.get_device_sample_size(direction, 0)
format = device_enum.get_device_sample_type(direction, 0)

print("Default playback device:")
print(f"    name = '{name}'")
print(f"    id = '{id}'")
print(f"    channels = '{channels}'")
print(f"    frame_rate = '{frame_rate}'")
print(f"    sample_size = '{sample_size}'")
print(f"    format = '{format}'")

if count > 1:
    print("Other playback devices:")

    for i in range(1, count):
        name = device_enum.get_device_name(direction, i)
        id = device_enum.get_device_id(direction, i)
        channels = device_enum.get_device_channel_count(direction, i)
        frame_rate = device_enum.get_device_frame_rate(direction, i)
        sample_size = device_enum.get_device_sample_size(direction, i)
        format = device_enum.get_device_sample_type(direction, i)

        print(f"    {i}: name = '{name}'")
        print(f"         id = '{id}'")
        print(f"         channels = '{channels}'")
        print(f"         frame_rate = '{frame_rate}'")
        print(f"         sample_size = '{sample_size}'")
        print(f"         format = '{format}'")
```


### C++

Using the `IAudioDeviceEnum` interface on the C++ side is largely the same.  The same set of interface functions
are still supported and behave in the same manner.  The following is an example of using the C++ interface to
perform the same task:

First, include the `IAudioDeviceEnum` interface's main header and a couple of other helpful headers:

```{literalinclude} ../../../../source/extensions/omni.kit.audiodeviceenum/plugins/omni.kit.audiodeviceenum/Example.cpp
:language: c++
:start-after: example-begin omni-kit-audiodeviceenum-example-includes
:end-before: example-end omni-kit-audiodeviceenum-example-includes
```


Then make a helper function that writes the connected devices' information to the app log:

```{literalinclude} ../../../../source/extensions/omni.kit.audiodeviceenum/plugins/omni.kit.audiodeviceenum/Example.cpp
:language: c++
:start-after: example-begin omni-kit-audiodeviceenum-examples
:end-before: example-end omni-kit-audiodeviceenum-examples
```
