# Usage Examples

## Basic Usage of DebugBreak

```python
import omni.kit.commands
from omni.kit.debug.vscode_debugger import DebugBreak

# This example demonstrates the two ways to trigger breakpoints
# Note: Both methods require a VS Code debugger to be attached,
# otherwise they will raise a RuntimeError

# Method 1: Using the command system (recommended for most scenarios)
try:
    print("About to trigger breakpoint via command...")
    omni.kit.commands.execute("DebugBreak")
except RuntimeError as e:
    print("Note: This command requires a debugger to be attached")

# Method 2: Creating and using the DebugBreak command directly
try:
    print("About to trigger breakpoint via direct command object...")
    debug_break = DebugBreak()
    debug_break.do()
except RuntimeError as e:
    print("Note: DebugBreak.do() requires a debugger to be attached")

print("Execution continues after the breakpoints")
```
## Basic Usage of DebugBreak

```python
import omni.kit.commands
from omni.kit.debug.vscode_debugger import DebugBreak

# This example demonstrates the two ways to trigger breakpoints
# Note: Both methods require a VS Code debugger to be attached,
# otherwise they will raise a RuntimeError

# Method 1: Using the command system (recommended for most scenarios)
try:
    print("About to trigger breakpoint via command...")
    omni.kit.commands.execute("DebugBreak")
except RuntimeError as e:
    print("Note: This command requires a debugger to be attached")

# Method 2: Creating and using the DebugBreak command directly
try:
    print("About to trigger breakpoint via direct command object...")
    debug_break = DebugBreak()
    debug_break.do()
except RuntimeError as e:
    print("Note: DebugBreak.do() requires a debugger to be attached")

print("Execution continues after the breakpoints")
```
## Integrating DebugBreak in a UI Application

```python
import omni.ui as ui
import omni.kit.commands
from omni.kit.debug.vscode_debugger import DebugBreak

# Create a demo application with debugging capabilities
window = ui.Window("Debug Demo Application", width=400, height=200)

# Function with debug point for demonstration
def calculate_with_debug(value):
    result = value * 5

    # Debug point to inspect the state when needed
    try:
        omni.kit.commands.execute("DebugBreak")  # Execution pauses here when debugger is attached
    except RuntimeError:
        print(f"Debug point reached with result: {result}")

    return result + 10

with window.frame:
    with ui.VStack(spacing=5):
        ui.Label("VS Code Debugger Integration Demo", height=30)

        # Create a slider to manipulate values
        slider_model = ui.SimpleFloatModel(5.0)
        ui.Label("Adjust value:")
        # Use FloatDrag instead of Slider which isn't available
        ui.FloatDrag(model=slider_model, min=0, max=20)

        result_label = ui.Label("Result: 0")

        # Button to calculate with a breakpoint
        def on_calculate_click():
            value = slider_model.get_value_as_float()
            result = calculate_with_debug(value)
            result_label.text = f"Result: {result}"

        ui.Button("Calculate with Breakpoint", clicked_fn=on_calculate_click)

        ui.Spacer(height=10)
        ui.Line(style={"color": 0xFF808080})
        ui.Spacer(height=10)

        # Button to demonstrate conditional breakpoints
        def on_conditional_debug():
            values = [5, 15, 25, 35]
            for i, val in enumerate(values):
                processed = val * 2
                if processed > 50:  # Only break on certain conditions
                    try:
                        print(f"Breaking at value: {val}")
                        omni.kit.commands.execute("DebugBreak")  # Conditional breakpoint
                    except RuntimeError:
                        print(f"Conditional breakpoint would trigger here (value={val})")

                print(f"Processed item {i}: {processed}")

        ui.Button("Run With Conditional Breakpoints", clicked_fn=on_conditional_debug)
```
