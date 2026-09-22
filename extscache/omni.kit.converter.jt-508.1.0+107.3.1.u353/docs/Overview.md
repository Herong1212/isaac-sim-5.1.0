# Omniverse JT Converter [omni.kit.converter.jt]

## Overview

The Omniverse JT Converter converts Siemens JT files to OpenUSD format for use in NVIDIA's Omniverse platform. Built on the JT Open Toolkit, it ensures accurate conversion of 3D data to enable JT models in USD-based workflows.

The extension serves as the user-facing component that configures and initiates conversions, while delegating the conversion work to the core converter running in a separate process to maintain stability.

### Key Features

- **GUI-Based Workflow**: Provides an intuitive graphical interface for converting JT files within Omniverse applications
- **Configurable Parameters**: Allows users to adjust conversion settings through the UI
- **USD Format Support**: Converts JT files to USD format while preserving model data, metadata and structure
- **Integration with Core Converter**: Utilizes `omni.kit.converter.jt_core` for the actual conversion process
- **JT Format Support**: Specialized support for Siemens JT files with optimized conversion quality

## Supported CAD file formats

The following file formats are supported by JT Converter:

- JT Files (`*.jt`)

## Installation
To begin conversion of a JT file, open an Omniverse App. Once open, confirm the `omni.kit.converter.jt` is enabled:
- Navigate to Window -> Extension Manager
- Search for `omni.kit.converter.jt`
- Locate and click on the extension.
- If needed, download and enable the extension.

## Related Extensions

The JT Converter is composed of several extensions that work together to enable JT file conversion:

### JT Converter: [omni.kit.converter.jt](https://docs.omniverse.nvidia.com/kit/docs/omni.kit.converter.jt/latest/Overview.html)
UI extension for configuring and initiating JT file conversions.

### JT Converter Core: [omni.kit.converter.jt_core](https://docs.omniverse.nvidia.com/kit/docs/omni.kit.converter.jt_core/latest/Overview.html)
Core conversion engine that runs in a separate process to handle the actual JT file conversion.

### Converter Common: [omni.kit.converter.common](https://docs.omniverse.nvidia.com/kit/docs/omni.kit.converter.common/latest/Overview.html)
Shared utility functions and helpers used across different converter extensions.

## Getting Help

For support and issue reporting:

- **Enterprise Customers**: [NVIDIA Omniverse Enterprise Support](https://www.nvidia.com/en-us/omniverse/enterprise/support/)
- **All Users**: [NVIDIA Developer Forums](https://forums.developer.nvidia.com/t/how-to-report-an-issue-with-omniverse/199675)

## Licensing Terms of Use and Third-Party Notices
- NVIDIA Omniverse is licensed to use the Siemens Open JT Toolkit SDK for the Omniverse JT Converter.

- Omniverse JT Converter is free to use for NVIDIA End Users and Companies that agree to the [NVIDIA Software License Agreement, the Product-Specific Terms for NVIDIA Omniverse](https://docs.omniverse.nvidia.com/connect/latest/common/NVIDIA_Omniverse_License_Agreement.html), and the Siemens License Terms. The First Party user is prohibited from redistributing, transferring, or otherwise sharing the software with any third parties, without express written consent from the software provider.

- **Please read the Siemens License Terms in the [Third_Party_Notices.md](Third_Party_Notices.md) for details.**
