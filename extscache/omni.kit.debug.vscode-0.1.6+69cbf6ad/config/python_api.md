# Public API for module omni.kit.debug.vscode_debugger:

## Classes

- class DebugBreak(omni.kit.commands.Command)
  - def do(self)

- class VSCodeExtension(omni.ext.IExt, MenuHelperExtensionFull)
  - WINDOW_NAME: str
  - MENU_GROUP: str
  - ATTACH_DISPLAY: Dict
  - def __init__(self)
  - def on_startup(self)
  - def on_shutdown(self)
