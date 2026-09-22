# Public API for module omni.kit.uiaudio:

## Classes

- class IUiAudio
  - def create_sound(self, filename: str) -> UiSound
  - def get_sound_length(self, sound: UiSound) -> float
  - def is_sound_playing(self, sound: UiSound) -> bool
  - def play_sound(self, sound: UiSound)
  - def stop_sound(self, sound: UiSound)

- class UiSound

## Functions

- def acquire_ui_audio_interface(plugin_name: str = None, library_path: str = None) -> IUiAudio
- def get_ui_audio_interface() -> IUiAudio
