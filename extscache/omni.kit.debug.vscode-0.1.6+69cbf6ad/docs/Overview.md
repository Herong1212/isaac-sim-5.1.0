```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

The VSCode Kit Debugger extension integrates VS Code’s Python debugging support into the Omniverse Kit environment. It provides a simple mechanism to trigger a breakpoint in the running Python code and displays debugger status within a dedicated window. This helps developers quickly inspect application state and accelerate their debugging workflow.

```{image} ../../../../source/extensions/omni.kit.debug.vscode/data/docs_images/show_preview.png
---
align: center
---
```


## Concepts

- **Debug Break Command:** At the core of the extension is the [DebugBreak](omni.kit.debug.vscode_debugger/omni.kit.debug.vscode_debugger.DebugBreak) command, which allows developers to pause execution and invoke the Python debugger.
- **Debugger Connection:** The extension leverages the ptvsd module to attach the VS Code Python debugger to the running Omniverse Kit application. It monitors the debugger status and updates the UI accordingly.

## Functionality

- **Breakpoint Triggering:** The [DebugBreak](omni.kit.debug.vscode_debugger/omni.kit.debug.vscode_debugger.DebugBreak) API offers a straightforward way to insert a breakpoint. When invoked, it halts the application’s execution, enabling step-by-step inspection.
- **UI Integration:** The extension implements a menu helper and a dedicated window that displays debugger status and manages the VS Code debugger connection. This streamlined interface assists with real-time debugging sessions.
- **Startup Visibility:** As configured in the extension settings, the debugger interface is visible at application startup, ensuring that developers have immediate access to debugging tools when needed.

## Usage Examples

To pause execution and inspect application state, you can execute the [DebugBreak](omni.kit.debug.vscode_debugger/omni.kit.debug.vscode_debugger.DebugBreak) command from your code or command palette:

```python
import omni.kit.debug.vscode_debugger

# Trigger a breakpoint in the Python debugger
omni.kit.debug.vscode_debugger.DebugBreak().do()
```

This simple command call stops the code execution at that point, allowing you to inspect variables and application state using the connected VS Code Python debugger.

## Relationships

- **Dependencies:** This extension relies on several core modules including **omni.ui**, **omni.kit.commands**, **omni.kit.debug.python**, and **omni.kit.menu.utils.** Its integration with these modules ensures seamless support for command execution and consistent menu behaviors.
- **Integration with VS Code:** Designed to work directly with VS Code’s debugging tools, this extension enables a smoother debugging experience by bridging the Omniverse Kit environment with VS Code’s advanced debugger interface.

## Considerations

- This extension is specialized for enabling VS Code’s debugging workflow within Omniverse Kit using the ptvsd module. Ensure that your VS Code environment is properly set up and that the required dependencies are available.
- The breakpoint functionality is intended for development and debugging purposes. It should be used with care in production environments.

