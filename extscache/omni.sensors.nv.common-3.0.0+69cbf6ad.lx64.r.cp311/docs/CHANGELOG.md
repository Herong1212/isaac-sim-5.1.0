# Changelog

## [3.0.0] - 2025-07-02
removing pre-release tags from all extensions

## 2025-04-29
Adding support for custom radar antenna gain pattern

## 2025-04-08
Adding POD format for Hesai AT360 ML3 Lidar sensor encoding/decoding

## 2024-11-04
Moving GMO out of common extension

## 2024-12-18
fix lidar objId

## [2.7.0-coreapi] - 2024-12-17
updating to openUSD 0.24.05 and python3.11

## [2.6.0-coreapi] - 2024-12-05
after reaching parity between new and old material systems

## [2.5.0-coreapi] - 2024-11-21
Update GMO docs
Added auxOutputType to lidar and radar profiles
Added modality field to GMO

## 2024-10-29
Fixing misalignment error in auxiliary data

## 2024-10-17
Added GMO Python bindings for RadarAuxiliaryData
Fixed typename of GMO outputTye PointCloud
Moved filledAuxMembers or lidar and radar to use uint32_t

## 2024-09-10
Fix cufft dll version

## 2024-09-03
Changes for schema based sensors

## 2024-07-24
Publish to packman

## 2024-07-19
Add ROI support to profile reader helper

## 2024-07-18
updated visualizer types

## 2024-07-15
Fixed a performance regression in the USS

## 2024-07-11
Updated cuda to version 12

## 2024-07-10
Add velocities and IDSAuxHas to IDSAuxiliaryData

## 2024-07-09
fix GMO buffer validation
add debug setting for radar

## 2024-07-04
Modifications in GMO helpers to support GMO buffer in place usage

## 2024-06-26
Fix for the implicit synchronization in memcpy

## 2024-06-19
Additional fix for potential races in GMO IO

## 2024-06-18
changes to use visual roughness
using source divergence for material evaluation

## 2024-06-12
Fixed a bug with multiple sensors recording data without async rendering

## 2024-06-06
DriveSim specific adaptations

## 2024-06-05
Activate hdf5 for windows

## 2024-05-28
Conversion to common ProfileReader

## 2024-05-28
Updated IDS data to contain material IDs

## 2024-05-15
Fix bug corresponding to Radar aux data

## 2024-04-18
Added missing parameters to radar .jsons and removed unused parameters

## 2024-04-12
Update to new structure of GenericModelOutput

## 2024-03-12
Run time modification of material property and behavior

## 2024-03-11
New materials implementation

## 2024-02-27
Fix configuration to run with windows

## 2024-02-02
First published extension from omni/sensors repo


The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
