# Overview

The `omni.uiaudio` extension allows an app to play sound clips as part of the UI.  The sounds played
through this interface will not interfere with any sounds coming from a currently playing USD stage.
A maximum of 8 separate sounds can be played simultaneously.  Sounds can be loaded as needed and
stored to play again later.  Sound assets that are in WAV, MP3, FLAC, Ogg/Vorbis, and Opus are
supported for playback with `omni.uiaudio`.

There is a C++ and Python API exported from this extension.  They both wrap the same set of interface
calls and behave identically to one another.  The main interface is the `omni::audio::IUiAudio` on
the C++ side and `omni.kit.audio.IUiAudio` on the Python side.
