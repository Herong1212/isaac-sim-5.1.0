```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Settings

## Settings Provided by the Extension
### exts."omni.kit.async_engine".spinLoopOncePerUpdate
   - **Default Value**: False
   - **Description**: Controls whether the asynchronous event loop should run only once per application update.

## Settings Used by the Extension but Provided by Another Extension
### /exts/omni.kit.async_engine/keep_loop_running
   - **Description**: Determines if the asyncio event loop should keep running continuously.

### /exts/omni.kit.async_engine/event_loop_policy_windows
   - **Description**: Specifies the asyncio event loop policy for Windows operating systems.

### /exts/omni.kit.async_engine/event_loop_policy_unix
   - **Description**: Specifies the asyncio event loop policy for Unix operating systems.

### /exts/omni.kit.async_engine/event_loop_windows
   - **Description**: Determines the asyncio event loop type for Windows operating systems.

### /exts/omni.kit.async_engine/event_loop_unix
   - **Description**: Determines the asyncio event loop type for Unix operating systems.

### /exts/omni.kit.async_engine/updateSubscriptionOrder
   - **Description**: Sets the order in which the update subscription is processed in relation to other update events.