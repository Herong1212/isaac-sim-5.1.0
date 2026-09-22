# Usage Examples

## Connect to a Nucleus Server Directly

```python
from omni.kit.widget.nucleus_connector import reconnect
import asyncio

# Callback functions for success and failure
def on_success(name, url):
    print(f"Successfully connected to {name} at {url}")

def on_failure(name, url):
    print(f"Failed to connect to {name} at {url}")

# Connect to Nucleus server
connect("My Server", "omniverse://my-server-url", on_success_fn=on_success, on_failed_fn=on_failure)
```


## Connect to Nucleus Server with Dialog

```python
from omni.kit.widget.nucleus_connector import connect_with_dialog
import asyncio

# Callback functions for success and failure
def on_success(name, url):
    print(f"Successfully connected to {name} at {url}")

def on_failure(name, url):
    print(f"Failed to connect to {name} at {url}")

connect_with_dialog(on_success_fn=on_success, on_failed_fn=on_failure)
```

## Reconnect to Nucleus Server

```python
from omni.kit.widget.nucleus_connector import reconnect
import asyncio

# Callback functions for success and failure
def on_success(name, url):
    print(f"Successfully connected to {name} at {url}")

def on_failure(name, url):
    print(f"Failed to connect to {name} at {url}")

# Server URL
server_url = "omniverse://ov-test"

# Reconnect to Nucleus server
reconnect(server_url, on_success_fn=on_success, on_failed_fn=on_failure)
print(f"Reconnected to {server_url}")
```

## Disconnect from Nucleus Server

```python
from omni.kit.widget.nucleus_connector import disconnect

# Server URL
server_url = "omniverse://ov-test"

# Disconnect from Nucleus server
disconnect(server_url)
print(f"Disconnected from {server_url}")
```
---

Please note that for the examples to work, you would need to have a running instance of the Omniverse environment with the `omni.kit.widget.nucleus_connector` extension installed and enabled. The examples here are designed for illustrative purposes and may require adaptation to work in specific Omniverse applications or environments.