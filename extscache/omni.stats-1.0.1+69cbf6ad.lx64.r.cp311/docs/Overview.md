```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
This extension allows any value (statistics) with a unique desired category (scope) to be retrieved in real-time, information such as scene data, geometry and GPU stats. Currently, python bindings only provide access to reading the existing values and only C++ carb.stats plugin developers have access to the write APIs, in order to insert new values or modify existing ones.

## Important API List
- **get_scope_count**: Returns the number of the existing scopes or categories.
- **get_stats_count**: Returns the number of the stats within the specified scope.
- **get_scopes**: Returns the scope nodes as tuple of dictionaries, which contains the information of all the scopes.
- **get_stats**: Returns the stat nodes as tuple of dictionaries, which contains the information of all the stats within the specified scope.

## General Use Case
This extension is primarily used by developers working with NVIDIA's Omniverse Kit and omni.kit.window.stats extension to get the current statistics reported by plugins. Each plugin may define their own scope and the corresponding statistics can be displayed visually in an extension like omni.kit.window.stats.

## User Guide
- [](CHANGELOG)
- [](USAGE_PYTHON)
