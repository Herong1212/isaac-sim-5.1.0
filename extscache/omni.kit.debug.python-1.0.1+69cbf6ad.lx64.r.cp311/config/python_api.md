# Public API for module omni.kit.debug.python:

## Classes

- class Extension(omni.ext.IExt)
  - class def get_listen_address(cls) -> str | None
  - def on_startup(self)
  - def on_shutdown(self)

## Functions

- def trigger_breakpoint()
- def is_attached() -> bool
- def enable_logging()
- def get_listen_address() -> str | None

## Other

- os: builtin module
- sys: builtin module
- carb.tokens: public module
- carb.settings: public module
- omni.ext: public module
- omni.kit.app: public module
- omni.kit.pipapi: public module
