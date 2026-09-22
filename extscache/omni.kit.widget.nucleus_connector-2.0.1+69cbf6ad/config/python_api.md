# Public API for module omni.kit.widget.nucleus_connector:

## Functions

- def connect(name: str, url: str, on_success_fn: Callable = None, on_failed_fn: Callable = None)
- def connect_with_dialog(on_success_fn: Callable = None, on_failed_fn: Callable = None)
- def reconnect(url: str, on_success_fn: Callable = None, on_failed_fn: Callable = None)
- def disconnect(url: str)

## Variables

- NUCLEUS_CONNECTION_SUCCEEDED_EVENT: int
- NUCLEUS_CONNECTION_SUCCEEDED_GLOBAL_EVENT: str
