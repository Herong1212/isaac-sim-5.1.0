# Changelog

## [3.0.0] - 2025-07-02
removing pre-release tags from all extensions

## 2025-06-12
Added model validation checks and default dummy profile for invalid config

## 2025-04-08
Added POD format for Hesai AT360 ML3 Lidar sensor encoding/decoding

## 2024-12-11
Adaptations according to FrameAtTime struct
Fixing frame of refence and coordstype post processing

## 2024-11-04
Adaptations for GMO out of common extension

## 2024-12-18
fix lidar objId

## [2.7.0-coreapi] - 2024-12-17
updating to openUSD 0.24.05 and python3.11

## 2024-11-27
Update lidar KPI tools, add lidar KPI test and validation score

## [2.6.3-coreapi] - 2024-11-25
Fix memory violations in lidar

## [2.6.2-coreapi] - 2024-11-22
Fix output size bugs and race conditions

## [2.6.1-coreapi] - 2024-11-22
Fix compaction default for schema based sensors

## [2.6.0-coreapi] - 2024-11-21
Add schema based setting of auxiliary data type + disabling of compaction
Add output of modelToAppTranform
Fill new modality field of GMO

## 2024-11-12
Fix setting of outputsize for extra auxiliary data

## 2024-11-07
Fix init bug in schema based lidar profile

## 2024-10-29
Add compaction of output buffer

## 2024-10-28
Fix profile alignment that did not enforce 8 byte alignment of buffers

## 2024-10-22
Specify field name in error logs in LidarProfileReaderHelper

## 2024-09-26
Minor update on bindings for material tools support

## 2024-08-20
Fix sonar cube high security hotspots

## 2024-09-06
Fix updating of pre-calculated values

## 2024-09-03
Changes for schema based sensors

## 2024-07-19
Move to RtxSensor 2.0

## 2024-07-24
Fix transcoder and numTicks calculation

## 2024-07-23
Fix setting of tick state to fix downstream encoding

## 2024-07-22
Fix TranscoderLidar

## 2024-07-15
Add Hesai AT360 support + fix hesai decoder

## 2024-07-11
Add LidarTestBufferConversion and VizSender script

## 2024-07-04
Fix for HesaiDecoder

## 2024-06-26
Fix for Lidar AuxData not being a CPU_PINNED memory

## 2024-06-18
changes to use visual roughness
using source divergence for material evaluation

## 2024-06-12
Updated project structure

## 2024-05-28
LidarProfile rework + conversion to common ProfileReader

## 2024-05-28
Minor bugfix for the issue with lidar point accumulator field not being correctly initialized in the showcase app

## 2024-05-06
Updated lidar docs

## 2024-04-26
Updated TranscoderLidar and PC converter

## 2024-05-02
init outputType

## 2024-04-12
Adaptations to use GenericModelOutput

## 2024-02-27
Fix OM-119538 and OM-119539

## 2024-04-10
carb setting fix

## 2024-04-4
changes for more robust computing of peak powers in solid state

## 2024-03-13
Fix DRIVE-17165 bug in solid state (calculation of number of emitters)

## 2024-03-12
Run time modification of material property and behavior

## 2024-03-11
New materials implementation

## 2024-02-27
Fix OM-119538 and OM-119539

## 2024-02-27
Fix configuration to run with windows

## 2024-02-02
First published extension from omni/sensors repo


The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
