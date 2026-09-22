# Examples

The most basic operation this extension can provide is to load a sound from disk and play it.  More detailed usages
can also wait for the sound to finish playing by periodically polling it, or query the length of a sound asset.
The example below will demonstrate all usages:

## Python

```python
import omni.kit.uiaudio
import time


def play_one_shot_ui_sound(filename: str, count: int = 1, delay_ms: int = 0, wait: bool = False) -> bool:
    uiaudio = omni.kit.uiaudio.get_ui_audio_interface()
    snd = uiaudio.create_sound(filename)

    if count <= 0:
        count = 1

    if snd == None:
        return False

    length = uiaudio.get_sound_length(snd)
    print(f"The sound asset is {length}s long.")

    for i in range(count - 1):
        uiaudio.play_sound(snd)
        # wait a bit before starting the next sound.  Note that a sleep like this shouldn't be used
        # in production code since it will lock up the UI or other threads.  An `asyncio.sleep()`
        # call should be used instead on async functions.
        time.sleep(delay_ms / 1000.0)

    uiaudio.play_sound(snd)

    if wait:
        while uiaudio.is_sound_playing(snd):
            time.sleep(0.250)

    snd = None
    print("done!")


play_one_shot_ui_sound("soundToPlay.mp3")
play_one_shot_ui_sound("soundToPlay.mp3", 2, 500, True)
play_one_shot_ui_sound("soundToPlay.mp3", 1, 5000, True)
play_one_shot_ui_sound("soundToPlay.mp3", 2, 500)
```

## C++

First, include the header files necessary for the example:

```{literalinclude} ../../../../source/extensions/omni.uiaudio/plugins/omni.uiaudio/Example.cpp
:language: c++
:start-after: example-begin omni-uiaudio-example-includes
:end-before: example-end omni-uiaudio-example-includes
```

Then create a helper function that can play a sound by a requested filename:

```{literalinclude} ../../../../source/extensions/omni.uiaudio/plugins/omni.uiaudio/Example.cpp
:language: c++
:start-after: example-begin omni-uiaudio-example-code
:end-before: example-end omni-uiaudio-example-code
```
