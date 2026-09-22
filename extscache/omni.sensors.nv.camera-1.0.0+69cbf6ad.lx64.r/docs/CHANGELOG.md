# Changelog

## [1.0.0] - 2025-07-02
removing pre-release tags from all extensions

## [0.21.0-coreapi] - 2024-12-17
updating to openUSD 0.24.05 and python3.11

## 2024-12-06
Add depth sensor based on synthetic depth disparity. Enable disparity sim on CamTextureRead node
and pass to CamDepthSyntheticBlur node. Requires DistanceToCameraSD AOV.

## [0.20.1-coreapi] - 2024-11-19
New ISP SmodelAdapter with lower glibc and CUDA compute requirements
Add '/app/sensors/nv/camera/CameraISPSaveIntermediateFrames' option to save CameraISP pipeline frames

## [0.20.0-coreapi] - 2024-11-07
Update CameraISPGeneric model params

## 2024-10-22
Improve texture read error handling

## 2024-10-16
Removed problematic dependencies

## 2024-09-26
Minor update on bindings for material tools support

## 2024-09-24
Isp Smodel Adapter is upgraded to version 1.3
Dynamic Resolution support added for Isp Smodel.

## 2024-09-18
Isp Smodel Adapter is upgraded to version 1.2
Added option to load program into adapter from binary blob

## 2024-10-11
Switch CameraISPGeneric color correction to 16bit

## 2024-09-24
Fix for ISP program loading

## 2024-09-24
Isp Smodel Adapter is upgraded to version 1.3
Dynamic Resolution support added for Isp Smodel.

## 2024-09-18
Isp Smodel Adapter is upgraded to version 1.2
Added option to load program into adapter from binary blob

## 2024-09-03
Enable external timestamp and frameId for embedded lines in DriveSim

## 2024-08-28
Add CameraIsp generic model

## 2024-07-31
Fixes for float32 HDR processing

## 2024-07-24
Publish to packman

## 2024-07-18
Added ISP Smodel processing as OG node.

## 2024-07-11
Updated cuda to version 12

## 2024-06-26
Move camera viz node from visualizer extension to camera extension.

## 2024-06-06
DriveSim specific adaptations

## 2024-06-06
added a generalb ISP 2x2 CFA Demosaicing Task

## 2024-05-15
adding general purpose noise task
Migrate to NVIDIA Omniverse Sensors project

## 2023-09-15
adding Resize Task
adding ISP Decompanding
adding ISP RGGB Demosaicing
adding RGBA Conversion

## 2023-06-30
supports multiple new AOVs like HDR Color, Depth maps and segmentation map
adding MJPEG as output
major refactoring, using GpuInteropRenderProductEntry as trigger

## 2022-06-30
adding CameraComSinkTask, which transmits the camera signal to the ECU
timecode are now signed. A negative timecode indicates data which has been produced before scenario started and should not consumed by the receiving application

## 2021-11-30
adding CameraComSinkTask, which transmits the camera signal to the ECU
timecode are now signed. A negative timecode indicates data which has been produced before scenario started and should not consumed by the receiving application

## 2021-09-18
adding MIPI transition task

## 2021-08-18
adding CFA 2x2 encoder task
adding companding task
adding default embedded lines task
adding embedded lines slicer
adding dark noise task
adding HDR support for the post processing pipeline
file reader supports now also float16, float32 and uint32

## 2021-03-18
adding compressed video transmission to SiL
adding timecode in buffers (for compressed streams) and as node attributes (for native streams)
GPU to host mem copy: replace the cuda synchronize by a callback (Performance Improvements)

## 2020-12-11
adding SiL interface: SiL Task, RGB and YUV task

## 2020-10-17
Building a simple camera pipeline with Raw Data Reader and Color Correction Matrix
Record to file task
