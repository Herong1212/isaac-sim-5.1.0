```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

**omni.kit.search_core** provides the foundational classes for implementing search functionality in Omniverse Kit SDK. It offers abstract definitions for search items, search models, and mechanisms to manage search operation lifetimes. The extension is designed to aid developers in creating custom search engines and integrating them seamlessly with content browsers and file pickers.

```{image} ../../../../source/extensions/omni.kit.search_core/data/preview.png
---
align: center
---
```


## Concepts

- **[AbstractSearchItem](omni.kit.search_core/omni.kit.search_core.AbstractSearchItem)**  
  Defines the interface for individual search results, encapsulating attributes like file path, display name, date, size, and icon. This allows search engines to standardize how items appear and behave in search result views.

- **[AbstractSearchModel](omni.kit.search_core/omni.kit.search_core.AbstractSearchModel)**  
  Represents a collection of search results. It supports asynchronous search operations by allowing an initial empty result set and later updating the view as results become available using an event notification mechanism.

- **[SearchLifetimeObject](omni.kit.search_core/omni.kit.search_core.SearchLifetimeObject)**  
  Manages the lifecycle of search callbacks. Implementers can use this to keep callback objects alive until the search has finished, ensuring that asynchronous operations update the view reliably.

- **[SearchEngineRegistry](omni.kit.search_core/omni.kit.search_core.SearchEngineRegistry)**  
  Provides a centralized registry for search engine implementations. This allows different search engines to be discovered, registered, and invoked from a common interface.

## Functionality

The extension is focused on delivering a consistent yet flexible interface for search operations:
  
- It supports asynchronous processing in search models. When a search engine takes time to produce results, the model can return an empty set and later notify the view of updates.
- The lifetime management design ensures that search callbacks remain active until search completion, making integration with long-running search operations more robust.
- By abstracting search items and models, the extension encourages developers to implement custom search logic while adhering to a standard interface, easing UI integration.

## Relationships

- **Dependencies**  
  **omni.kit.search_core** depends on **omni.kit.widget.nucleus_info** for accessing necessary server's search sevice information. This tight integration ensures that search results can be properly visualized in file pickers and content browsers within the Kit application.

## Considerations

- The extension establishes the baseline behavior for search operations but requires concrete implementations to provide the actual search logic.
- Asynchronous search handling is built into the abstract model, so developers must ensure that UI views subscribe to change events via the provided event mechanism.
- The standardized registry approach simplifies integrating multiple search engines but may require additional handling when mixing synchronous and asynchronous engines.

Overall, **omni.kit.search_core** is intended to serve as the backbone for search functionality, setting the stage for custom implementations and future extensions in the search domain.