# Public API for module omni.kit.xr.advertise:

## Classes

- class XRAdvertizer
  - def __init__(self)
  - def set_profile_name(self, name: str)
  - def get_profile_name(self) -> str
  - def is_enabled(self) -> bool
  - def startZeroconf(self, ev)
  - def stopZeroconf(self, ev)
  - def destroy(self)
