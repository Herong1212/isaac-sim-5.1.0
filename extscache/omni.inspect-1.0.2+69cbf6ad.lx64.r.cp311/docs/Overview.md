```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

**omni.inspect** provides a set of interfaces that enable standardized object inspection within the Omniverse Kit SDK. This extension is designed to facilitate the integration of inspection capabilities into your ABI, bringing consistent debugging, data serialization, and memory usage reporting across different objects. It supports various inspection methods that allow thorough introspection without needing to couple complex implementation details.

## Concepts

- **[IInspector](omni.inspect/omni.inspect.IInspector)** is the foundational interface that defines common inspection behaviors such as flag management and help information retrieval.
- **[IInspectJsonSerializer](omni.inspect/omni.inspect.IInspectJsonSerializer)** and **[IInspectSerializer](omni.inspect/omni.inspect.IInspectSerializer)** offer mechanisms to capture and represent object states as JSON or string output. These interfaces simplify the process of serializing object data for debugging or logging purposes.
- **[IInspectMemoryUse](omni.inspect/omni.inspect.IInspectMemoryUse)** focuses on tracking and reporting memory usage, ensuring insight into resource consumption that is critical during development or troubleshooting.

## Functionality

- The serializer interfaces let you construct detailed JSON representations of an object's state. They support operations such as opening and closing JSON objects or arrays, writing values of various types, and even encoding binary data as base64.
- Memory inspection capabilities allow for resetting, recording, and querying the amount of memory used, providing a practical means to monitor resource utilization in real time.
- The inspection interfaces also include mechanisms for setting and checking inspection flags, as well as retrieving context-specific help information.

## Relationships

- By standardizing inspection capabilities through a common set of interfaces, **omni.inspect** facilitates better interoperability and easier debugging across different modules within your application.

## Considerations

- The interfaces provided are intended for integration into your existing ABI for enhanced inspection rather than as standalone debugging tools.  
- In performance-sensitive contexts be aware that inspection data logged to a file can introduce significant performance degradation due to disk I/O latency and increased resource consumption, especially if logging is synchronous or highly verbose.
- On the other hand, logging to a string may avoid immediate I/O costs, but can lead to excessive memory usage and potentially cause out-of-memory errors if the accumulated log data exceeds the standard string size limits or available heap space.