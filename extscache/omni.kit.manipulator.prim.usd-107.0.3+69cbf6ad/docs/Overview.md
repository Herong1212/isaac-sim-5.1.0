```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
The `omni.kit.manipulator.prim.usd` extension provides classes and functionalities for manipulating USD prims within the Omniverse Kit. It includes a custom data accessor specifically designed for USD contexts, enabling operations such as accessing and modifying USD stages and primitives, registering callbacks for USD object changes, and performing transformations on USD prims.

## Important API List
- **UsdDataAccessor**: A class that extends `DataAccessor` for handling data access and manipulation in USD contexts.

## General Use Case
The extension is used for integrating USD-specific data access and manipulation capabilities into the Omniverse Kit. This includes managing USD stages, transforming USD primitives, and providing USD context to other parts of the application that require access to USD data. For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](SETTINGS)
- [](USAGE_PYTHON)
- [](CHANGELOG)