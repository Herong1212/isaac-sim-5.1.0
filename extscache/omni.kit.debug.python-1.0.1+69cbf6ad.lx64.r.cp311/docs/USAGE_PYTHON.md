# Usage Examples

## Check Debug Client Attachment

```python
import omni.kit.debug.python

# Check if a debug client is attached
is_attached = omni.kit.debug.python.is_attached()
print(f"Debug client attached: {is_attached}")
```
---


## Get Debugging Listen Address

```python
import omni.kit.debug.python

# Get the listen address for the debugger
listen_address = omni.kit.debug.python.get_listen_address()
print(f"Debugger listen address: {listen_address}")
```
---


## Use Extension Class Methods

```python
import omni.kit.debug.python

# Instantiate the Extension class
debug_extension = omni.kit.debug.python.Extension()

# Start debugging environment based on settings in the on_startup method
debug_extension.on_startup()
```
---


## Enable Debug Logging

```python
import omni.kit.debug.python
import debugpy

# Attempt to enable logging only if it hasn't been enabled already
try:
    omni.kit.debug.python.enable_logging()
except RuntimeError as e:
    if str(e) != "logging has already begun":
        raise
```
---


## Wait for Debug Client Connection

```python
import omni.kit.debug.python
import debugpy

# Attempt to listen for a client to attach to the debugger
# only if the address is not already in use
try:
    # Check if a server is already listening
    if not debugpy.is_client_connected():
        debugpy.listen(("0.0.0.0", 5678))
except Exception as e:
    if "Address already in use" in str(e):
        print("Debugpy server already running, not attempting to listen again.")
    else:
        raise

# Proceed to wait for a client only if debugpy is able to listen
try:
    omni.kit.debug.python.wait_for_client()
except RuntimeError as e:
    if "listen() or connect() must be called first" in str(e):
        print("Debugpy server is not listening, cannot wait for client.")
    else:
        raise
```

---

## Set Breakpoint in Code

```python
import omni.kit.debug.python
import debugpy

# Attempt to listen for a client and wait for it to attach to the debugger
# only if the address is not already in use and no client is connected
try:
    if not debugpy.is_client_connected():
        debugpy.listen(("0.0.0.0", 5678))
except Exception as e:
    if "Address already in use" in str(e):
        print("Debugpy server already running, not attempting to listen again.")
    else:
        raise

# Proceed to wait for a client only if debugpy is able to listen
try:
    debugpy.wait_for_client()

    # Set a breakpoint in the code
    omni.kit.debug.python.breakpoint()
except RuntimeError as e:
    if "listen() or connect() must be called first" in str(e):
        print("Debugpy server is not listening, cannot set breakpoint.")
    else:
        raise
```
