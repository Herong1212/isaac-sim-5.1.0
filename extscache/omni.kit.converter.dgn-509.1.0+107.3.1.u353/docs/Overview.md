# Omniverse DGN Converter [omni.kit.converter.dgn]

## Overview

The Omniverse DGN Converter converts Bentley Microstation DGN files to OpenUSD format for use in NVIDIA's Omniverse platform. Built on the Open Design Alliance (ODA) Drawings SDK, it ensures accurate conversion of 3D data to enable DGN models in USD-based workflows.

The extension serves as the user-facing component that configures and initiates conversions, while delegating the conversion work to the core converter running in a separate process to maintain stability.

### Key Features

- **GUI-Based Workflow**: Provides an intuitive graphical interface for converting DGN files within Omniverse applications
- **Configurable Parameters**: Allows users to adjust conversion settings like surface tolerance through the UI
- **USD Format Support**: Converts DGN files to USD format while preserving model data and structure
- **Integration with Core Converter**: Utilizes `omni.kit.converter.dgn_core` for the actual conversion process


## Supported CAD file formats

The following file formats are supported by DGN Converter:

- DGN (`*.DGN`)

## Installation
To begin conversion of a DGN file, open an Omniverse App. Once open, confirm the `omni.kit.converter.dgn` is enabled:
- Navigate to Window -> Extension Manager
- Search for `omni.kit.converter.dgn`
- Locate and click on the extension.
- If needed, download and enable the extension.

## Related Extensions

The DGN Converter is composed of several extensions that work together to enable DGN file conversion:

### DGN Converter: [omni.kit.converter.dgn](https://docs.omniverse.nvidia.com/kit/docs/omni.kit.converter.dgn/latest/Overview.html)
UI extension for configuring and initiating DGN file conversions.

### DGN Converter Core: [omni.kit.converter.dgn_core](https://docs.omniverse.nvidia.com/kit/docs/omni.kit.converter.dgn_core/latest/Overview.html)
Core conversion engine that runs in a separate process to handle the actual DGN file conversion.

### Converter Common: [omni.kit.converter.common](https://docs.omniverse.nvidia.com/kit/docs/omni.kit.converter.common/latest/Overview.html)
Shared utility functions and helpers used across different converter extensions.

## Getting Help

For support and issue reporting:

- **Enterprise Customers**: [NVIDIA Omniverse Enterprise Support](https://www.nvidia.com/en-us/omniverse/enterprise/support/)
- **All Users**: [NVIDIA Developer Forums](https://forums.developer.nvidia.com/t/how-to-report-an-issue-with-omniverse/199675)

## Licensing Terms of Use and Third-Party Notices
The `omni.kit.converter.dgn` and related CAD converter Extensions are Omniverse Core Extensions.
Do not redistribute or sublicense without express permission or agreement.
Please read the [Omniverse License Agreements](https://docs.omniverse.nvidia.com/extensions/latest/common/NVIDIA_Omniverse_License_Agreement.html) and the [Third_Party_Notices.md](Third_Party_Notices.md) for detailed license information.
