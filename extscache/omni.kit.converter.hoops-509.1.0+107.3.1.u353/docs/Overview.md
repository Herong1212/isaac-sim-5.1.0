# Omniverse Hoops Converter [omni.kit.converter.hoops]

## Overview

The Omniverse HOOPS Converter converts CAD files to OpenUSD format for use in NVIDIA's Omniverse platform. Built on the HOOPS Exchange SDK, it ensures accurate conversion of 3D data to enable CAD models in USD-based workflows.

The extension serves as the user-facing component that configures and initiates conversions, while delegating the conversion work to the core converter running in a separate process to maintain stability.

### Key Features

- **GUI-Based Workflow**: Provides an intuitive graphical interface for converting CAD files within Omniverse applications
- **Configurable Parameters**: Allows users to adjust conversion settings like UV generation and instancing through the UI
- **USD Format Support**: Converts CAD files to USD format while preserving model data, metadata and structure
- **Integration with Core Converter**: Utilizes `omni.kit.converter.hoops_core` for the actual conversion process
- **Extensive Format Support**: Supports a wide range of CAD formats including CATIA, SolidWorks, NX, Inventor and many more


## Supported CAD file formats

The following file formats are supported by Hoops Converter:

- CATIA V5 Files (`*.CATPart, *.CATProduct, *.CGR`)
- CATIA V6 Files (`*.3DXML`)
- Collada Files (`.dae`)
- IFC Files (`*.ifc, *.ifczip`)
- Siemens NX Files (`*.prt`)
- Parasolid Files (`*.xmt, *.x_t, *.x_b, *.xmt_txt`)
- SolidWorks Files (`*.sldprt, *.sldasm`)
- STL Files (`*.stl`)
- ACIS Files (`*.SAT, *.SAB`)
- Autodesk Inventor Files (`*.IPT, *.IAM`)
- Autodesk 3DS Files (`*.3DS`)
- AutoCAD 3D Files (`*.DWG, *.DXF`)
- Creo - Pro/E Files (`*.ASM, *.PRT`)
- Revit Files (`*.RVT, *.RFA`)
- Rhino Files (`*.3dm`)
- Solid Edge Files (`*.ASM, *.PAR, *.PWD, *.PSM`)
- Step/Iges (`*.STEP, *.IGES`)
- JT Files (`*.jt`)
- DGN Files (`*.DGN`)
- OBJ Files (`*.OBJ`)
- FBX Files (`*.FBX`)
- 3MF Files (`*.3MF`)
- GLTF Files (`*.GLTF, *.GLB`)

## Installation
To begin conversion of a CAD file, open an Omniverse App. Once open, confirm the `omni.kit.converter.hoops` is enabled:
- Navigate to Window -> Extension Manager
- Search for `omni.kit.converter.hoops`
- Locate and click on the extension.
- If needed, download and enable the extension.

## Related Extensions

The HOOPS Converter is composed of several extensions that work together to enable CAD file conversion:

### HOOPS Converter: [omni.kit.converter.hoops](https://docs.omniverse.nvidia.com/kit/docs/omni.kit.converter.hoops/latest/Overview.html)
UI extension for configuring and initiating CAD file conversions.

### HOOPS Converter Core: [omni.kit.converter.hoops_core](https://docs.omniverse.nvidia.com/kit/docs/omni.kit.converter.hoops_core/latest/Overview.html)
Core conversion engine that runs in a separate process to handle the actual CAD file conversion.

### Converter Common: [omni.kit.converter.common](https://docs.omniverse.nvidia.com/kit/docs/omni.kit.converter.common/latest/Overview.html)
Shared utility functions and helpers used across different converter extensions.

## Getting Help

For support and issue reporting:

- **Enterprise Customers**: [NVIDIA Omniverse Enterprise Support](https://www.nvidia.com/en-us/omniverse/enterprise/support/)
- **All Users**: [NVIDIA Developer Forums](https://forums.developer.nvidia.com/t/how-to-report-an-issue-with-omniverse/199675)

## Known Issues

- Please refer to [Known Issues](Known_Issues.md#known-issues) for more information.

## Licensing Terms of Use and Third-Party Notices
The `omni.kit.converter.hoops` and related CAD converter Extensions are Omniverse Core Extensions.
Do not redistribute or sublicense without express permission or agreement.
Please read the [Omniverse License Agreements](https://docs.omniverse.nvidia.com/extensions/latest/common/NVIDIA_Omniverse_License_Agreement.html) and the [Third_Party_Notices.md](Third_Party_Notices.md) for detailed license information.