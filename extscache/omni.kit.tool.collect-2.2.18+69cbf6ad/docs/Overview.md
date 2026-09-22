```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview
The `omni.kit.tool.collect` extension provides functionality for collecting USD assets and their dependencies into a single directory, integrating with the Omniverse Kit extensions. It offers UI components and logic for the USD asset collection workflow, enabling users to specify various options for the collection process, such as USD only, material only, flat collection, and more. The extension also includes functionality for managing actions associated with the Collect Tool in Omniverse Kit.

## Important API List
The module consists of the following main components:
- **PublicExtension** : A class that manages the collection of USD assets, providing methods to collect individual or multiple USD files into a single directory.
- **get_instance** : A function that returns the singleton instance of the main class.

The following classes come from `omni.kit.usd.collect` and are introduced here only to ensure forward compatibility of this extension. They won't be importable from `omni.kit.tool.collect` after Kit version 107. For more information, please refer to the documentaion of `omni.kit.usd.collect`.
- **Collector** : Used for performing the actual collection of USD files and their dependencies.
- **CollectorTaskType** : Defining different task types for the collector.
- **CollectorException** : Representing errors that occur during the collection process.

## General Use Case
Users can utilize this extension to collect USD assets into a single location, preserving or flattening the folder structure and focusing on specific assets like USD files or materials. The extension also allows for the collection of assets from a specified folder, and it integrates with the Omniverse Kit extensions to offer a seamless collection workflow within content browsers. For examples of how to use the APIs, please consult the [Python](USAGE_PYTHON) usage pages.

## User Guide
- [](USAGE_PYTHON)
- [](CHANGELOG)
