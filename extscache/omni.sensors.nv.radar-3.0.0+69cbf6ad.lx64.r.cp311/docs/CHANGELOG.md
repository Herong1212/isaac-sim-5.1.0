# Changelog

## [3.0.0] - 2025-07-02
removing pre-release tags from all extensions

## 2025-04-29
Added support for custom radar antenna gain patterns

## 2025-03-31
Add at least one dummy detection as downstream components expect that

## 2025-01-21
Fixed and re-enabled radar compute stability test
Fixed random number generator indexing for deterministic results
Fixed output of GenericModelOutput on CPU

## 2025-01-24
Fix out of bounds memory access for more than 2500 detections

## 2025-01-14
Fixed radar timestamps for start and end frame
Added radar setup matching to simulate timestamping behaviour as in real multi-radar setups

## 2024-12-11
Adaptations according to new members in GMO + adding new schema attributes

## 2024-11-04
Adaptations for GMO out of common extension

## 2025-01-10
Deprecated old radar model (DmatApproxRadarPlugin)

## [2.8.0-coreapi] - 2024-12-17
updating to openUSD 0.24.05 and python3.11

## [2.7.0-coreapi] - 2024-12-05
after reaching parity between new and old material systems

## [2.6.1-coreapi] - 2024-11-22
Fix output size bugs and race conditions

## [2.6.0-coreapi] - 2024-11-21
Add schema based setting of auxiliary data type
Add output of modelToAppTranform
Fill new modality field of GMO

## 2024-11-07
Fix initialization of device side numDetections variable

## 2024-10-29
Add compaction of output buffer
Removed objId, semId and numDetections from RadarAuxiliaryData

## 2024-10-17
Fixed race in transcoder and cleaned transcoder up

## 2024-10-08
Correctly freeing pinned memory

## 2024-10-08
Fixed bug that gave wrong aux data if GPU or CPU output was queried multiple times.
Using pinned CPU memory instead of malloc.

## 2024-10-07
Fixed missing output type in radar and clearing valid flags after every trace

## 2024-09-06
Bug fix

## 2024-09-03
Changes for schema based sensors

## 2024-08-20
Fix sonar cube high security hotspots

## 2024-07-19
Move to RtxSensor 2.0

## 2024-07-25
Updated transcoder

## 2024-07-11
new cuda version
fixed uninitialized pinned context
fixed race with thrust code
fixed host-stream sync with thrust code

## 2024-07-09
fix radar race in GMO buffer
add debug prints with setting
fix implicit sync

## 2024-07-04
Fix radar race, due to missing sync data in GMO buffer

# 2024-06-26
Updated dependency list for radar

## 2024-06-18
changes to use visual roughness
using source divergence for material evaluation
radar tuning
radar perf improvements

## 2024-06-12
Updated project structure

## 2024-06-06
DriveSim specific adaptations

## 2024-05-28
Conversion to common ProfileReader

## 2024-05-28
Bugfix for incorrect color output in radar visualization

## 2024-05-27
Updated radar docs

## 2024-04-18
Updated documentation for radar extension

## 2024-05-17
Fix passing of memhandler in metadata

## 2024-05-15
Fixed timestamp in radar

## 2024-04-12
Adaptations to use GenericModelOutput

## 2024-04-10
carb setting fix

## 2024-03-22
Run time modification of material property and behavior

## 2024-03-18
4DCFAR Bugfix and noise behaviour now in line with 2DCFAR
Tuning for wpm_dmat generic high resolution sensor
CFAR performance improvements

## 2024-03-11
New materials implementation

## 2024-02-27
Fix configuration to run with windows

## 2024-02-02
First published extension from omni/sensors repo


The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
