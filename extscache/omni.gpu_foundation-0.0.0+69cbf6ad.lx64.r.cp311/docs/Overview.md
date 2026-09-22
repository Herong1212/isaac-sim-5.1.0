
```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

GPU foundation is a mostly internal layer of low-level subsystems that provide the basis for RTX rendering and Kit UI presentation. This includes device enumeration, graphics abstraction layers, shader compilation and caching, as well as resource lifetime and GPU workload management.

There are no public Python or C++ interfaces available to access this low-level functionality directly.