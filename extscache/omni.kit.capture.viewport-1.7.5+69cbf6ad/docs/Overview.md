```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

**omni.kit.capture.viewport** is an Omniverse Kit extension that enables capturing images and videos directly from the viewport. It provides users with a structured set of APIs to define capture parameters, choose between different rendering and debug modes, and control the capture lifecycle from start to finish. With this extension, you can capture high-quality stills or movies using flexible options designed for different workflows such as traditional frame sequences or sun study mode.

## Concepts

- **[CaptureOptions](omni.kit.capture.viewport/omni.kit.capture.viewport.CaptureOptions)**: A key API that encapsulates all capture-related settings such as resolution, frame range or time range, render preset, and output file configurations. It allows you to easily serialize and recreate capture setups.
- **[CaptureRangeType](omni.kit.capture.viewport/omni.kit.capture.viewport.CaptureRangeType)**: Enumerations that let you define whether the capture range is specified in frames or seconds.
- **[CaptureMovieType](omni.kit.capture.viewport/omni.kit.capture.viewport.CaptureMovieType)**: Enumerations that let you definewhether the capture is a sequence of images or a sun study movie.
- **[CaptureRenderPreset](omni.kit.capture.viewport/omni.kit.capture.viewport.CaptureRenderPreset)**: Enums that determine the rendering mode to be used during capture, helping balance quality with performance.
- **[CaptureDebugMaterialType](omni.kit.capture.viewport/omni.kit.capture.viewport.CaptureDebugMaterialType)**: Enums that determine the debug material style to be used during capture.

## Functionality

- **Capture Lifecycle Management**: The extension offers methods to start, pause, resume, and cancel the capture process. It also provides callbacks for progress updates and completion events.
- **Output Generation**: Whether capturing a single frame, a sequence for high-quality images, or a video file, the extension integrates with renderer and timeline components to produce the final output.
- **Customization**: You can adjust detailed settings such as frames per second, output folder, and additional encoding parameters. Object conversion methods make it simple to pass capture settings between components.

## Relationships

- **Dependencies**: This extension relies on several other Omniverse Kit modules such as **omni.usd**, **omni.kit.viewport.utility**, **omni.timeline**, **omni.ui**, and **omni.appwindow.** Optional dependencies like **omni.videoencoding**, **omni.kit.renderer.core**, and **omni.kit.renderer.capture** can extend functionality further.
- **Integration**: Designed to work closely with viewport actions, the extension integrates with rendering and timeline management tools to ensure that captures sync accurately with frame updates and post-processing steps.

Overall, **omni.kit.capture.viewport** provides a practical framework for capturing viewport content with a focus on configurable quality and flexible workflows, fitting seamlessly into varied Omniverse Kit applications.