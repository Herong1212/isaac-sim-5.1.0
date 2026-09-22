# Usage Examples

## Create and Serialize JSON Data

```python
import omni.inspect
import tempfile

# Create a JSON serializer
json_serializer = omni.inspect.IInspectJsonSerializer()

# Begin creating a JSON object
json_serializer.open_object()

# Add properties of different types
json_serializer.write_key("name")
json_serializer.write_string("Omniverse")

json_serializer.write_key("version")
json_serializer.write_float(2023.1)

json_serializer.write_key("enabled")
json_serializer.write_bool(True)

# Add a nested object
json_serializer.write_key("config")
json_serializer.open_object()
json_serializer.write_key("mode")
json_serializer.write_string("advanced")
json_serializer.close_object()

# Add an array of values
json_serializer.write_key("tags")
json_serializer.open_array()
json_serializer.write_string("graphics")
json_serializer.write_string("simulation")
json_serializer.close_array()

# Close the main object and finish
json_serializer.close_object()
json_serializer.finish()

# Get JSON as string
json_string = json_serializer.as_string()
print(json_string)

# Write to a file
with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
    json_serializer.clear()
    json_serializer.output_to_file_path = tmp.name
    
    # Create simple JSON in the file
    json_serializer.open_object()
    json_serializer.write_key("file_output")
    json_serializer.write_string("JSON written to file")
    json_serializer.close_object()
    json_serializer.finish()
    
    print(f"JSON written to: {tmp.name}")
```
## Use Basic Text Serializer

```python
import omni.inspect
import tempfile
from pathlib import Path

# Create a basic text serializer
serializer = omni.inspect.IInspectSerializer()

# Write text to the serializer's buffer
serializer.write_string("Hello, Omniverse!\n")
serializer.write_string("This is a text serialization example.\n")

# Get the serialized content
content = serializer.as_string()
print("Serialized content:")
print(content)

# Output to a file
with tempfile.TemporaryDirectory() as tmp_dir:
    output_file = Path(tmp_dir) / "serializer_output.txt"
    
    # Redirect output to file
    serializer.output_to_file_path = str(output_file)
    
    # Write content to the file
    serializer.write_string("This content is written directly to a file.\n")
    
    print(f"Content written to: {output_file}")
    
    # Switch back to string output
    serializer.set_output_to_string()
    serializer.clear()
    
    # Write new content to string buffer
    serializer.write_string("New content in string buffer.")
    print(f"New buffer content: {serializer.as_string()}")
```
## Set and Get Inspector Flags

```python
import omni.inspect

# Create an inspector using a concrete implementation since IInspector can't be instantiated directly
inspector = omni.inspect.IInspectSerializer()  # Using a derived class that implements IInspector

# Set flags to control inspection behavior
inspector.set_flag("debug", True)
inspector.set_flag("verbose", True)

# Check if flags are set
if inspector.is_flag_set("debug"):
    print("Debug mode is enabled")

# Set help information for the inspector
inspector.help = "This inspector provides basic functionality."

# Get the standard help flag name
help_flag = inspector.help_flag()  # Returns "help" by default
print(f"Help flag name: {help_flag}")

# Get help information
help_info = inspector.help_information()
print(f"Help information: {help_info}")
```
## Track Memory Usage

```python
import omni.inspect
import ctypes  # For creating C-compatible memory objects

# Create a memory usage tracker
memory_tracker = omni.inspect.IInspectMemoryUse()

# In real applications, memory usage is tracked by passing memory pointers
# to the use_memory() method, which requires capsule objects (C/C++ pointers)

# Create some C-compatible memory buffers
buffer1 = (ctypes.c_char * 1024)()  # 1KB buffer
buffer2 = (ctypes.c_char * 4096)()  # 4KB buffer

# Get memory addresses as integers (for demonstration only)
ptr1 = ctypes.addressof(buffer1)
ptr2 = ctypes.addressof(buffer2)

# Show initial memory tracked
print(f"Initial memory tracked: {memory_tracker.total_used()} bytes")

# Note: use_memory requires a capsule type which is difficult to create properly in Python
# This is just to demonstrate the API interface

# Reset memory tracking
memory_tracker.reset()
print(f"After reset: {memory_tracker.total_used()} bytes tracked")
```
