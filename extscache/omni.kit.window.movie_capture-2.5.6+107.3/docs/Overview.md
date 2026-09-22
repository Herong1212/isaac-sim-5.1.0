```{csv-table}
**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`
```

# Overview

The Movie Capture extension provides a dedicated interface for capturing the viewport, either as a single frame or as a sequence. It is designed to offer a complete, ready-to-use solution for users who need to quickly capture high-quality images or video directly from the viewport. The extension integrates several capture settings and UI panels for adjusting camera, render, output, and farm options to streamline the capturing process.

```{image} ../../../../source/extensions/omni.kit.window.movie_capture/data/preview.png
---
align: center
---
```


## Functionality

- **Settings Panels:** The extension presents several UI components including panels for **General Capture Settings**, **Rendering Settings**, **Queue Settings**, **Output Settings**. These panels guide users through adjusting capture parameters without needing to write any code.
- **General Capture Settings:** Users can choose movie type, camera and configure frame rates, durations, resolution, and other settings.
- **Rendering Settings:** It supports multiple render modes such as "RaytracedLighting," "PathTracing," and "iray." Settings for samples per pixel, subframes, motion blur shutter values, and even IRay parameters are available for fine-tuning quality and performance.
- **Queue Settings:** For larger capturing tasks, Movie Capture integrates with Omniverse Farm Queue, allowing users to submit capturing jobs, check farm status, and even navigate directly to learn more about Farm Queue.
- **Output Settings:** Users can choose between capturing still images (e.g., .png, .tga, .exr) and video files (e.g., .mp4) with the output directory and file name.

## Configuration

- **Default Settings:** Key parameters such as default FPS (e.g., 24), default capture type (e.g., “.png”), render preset, and various quality settings (like spp and subframe counts) are specified in the extension’s settings.
- **Farm Options:** Settings include the job name for farm submissions, the endpoint for the settings service, and a list of available farm queues. An option to validate USD files before capturing ensures reliability in production workflows.
- **OVC Mode:** An option exists to enable or disable OVC mode, tailoring the extension behavior for specific Omniverse environments.

## Relationships

- **Dependencies:** The extension depends on several core Omniverse modules such as **omni.kit.capture.viewport**, **omni.ui**, **omni.timeline**, and others. Integration with services like **omni.kit.window.filepicker** and **omni.kit.menu.utils** ensures seamless UI and system-wide consistency.
- **Collaboration with Render and Timeline Modules:** Movie Capture works closely with the render settings and timeline functionalities, ensuring that changes in the viewport render or animation timeline are captured accurately.

## Considerations

- **Advanced Rendering Support:** Features related to advanced rendering — such as handling multi-GPU setups, advanced quality controls — are specific to the rendering mode selected. Users should consult the detailed documentation provided in the module’s docs for guidance on these advanced features.
- **User Workflow:** The extension is intended to be used directly from its UI, with typical user workflows involving adjusting settings, previewing changes, and then capturing either an image or a video. The interface is designed to minimize the need for external scripting.

This overview should help users understand the essential features and setup of the Movie Capture extension, enabling them to efficiently use its capabilities for high-quality viewport capture.