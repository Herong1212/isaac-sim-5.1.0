// SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#pragma once

namespace omni
{
namespace sensors
{
namespace nv
{

constexpr char kAtmosOpticalThickness[] = "/app/sensors/nv/atmos/opticalThickness";

/*
 * Sets output buffer of model to gpu.
 *
 * Examples: --/app/sensors/nv/lidar/outputBufferOnGPU=true
 */
constexpr char kLidarOutputBufferOnGPU[] = "/app/sensors/nv/lidar/outputBufferOnGPU";
constexpr char kRadarOutputBufferOnGPU[] = "/app/sensors/nv/radar/outputBufferOnGPU";
constexpr char kUltrasonicOutputBufferOnGPU[] = "/app/sensors/nv/ultrasonic/outputBufferOnGPU";
constexpr char kIDSOutputBufferOnGPU[] = "/app/sensors/nv/ids/outputBufferOnGPU";

/*
 * Output all points. This will potentially increase output size of the buffer.
 *
 * Examples: --/app/sensors/nv/lidar/skipDroppingInvalidPoints=true
 */
constexpr char kLidarSkipDroppingInvalidPoints[] = "/app/sensors/nv/lidar/skipDroppingInvalidPoints";

/*
 * Output aux information. This will potentially increase output size of the buffer.
 *
 * Examples: --/app/sensors/nv/lidar/auxOutputType=NONE or BASIC or EXTRA or FULL
 */
constexpr char kLidarAuxOutputType[] = "/app/sensors/nv/lidar/auxOutputType";
constexpr char kRadarAuxOutputType[] = "/app/sensors/nv/radar/auxOutputType";


/*
 * Sets output buffer frame of reference and corrdstype. Default: SENSOR and SPHERICAL.
 *
 * Examples: --/app/sensors/nv/lidar/kLidarOutputFrameOfReference=GLOBAL
 */
constexpr char kLidarOutputFrameOfReference[] = "/app/sensors/nv/lidar/outputFrameOfReference";
constexpr char kLidarCustomFrameOfReferenceTrafo[] = "/app/sensors/nv/lidar/customFrameOfReferenceTrafo";
constexpr char kLidarOutputCoordsType[] = "/app/sensors/nv/lidar/elementsCoordsType";
constexpr char kLidarOutputMotionCompensationState[] = "/app/sensors/nv/lidar/outputMotionCompensationState";
constexpr char kRadarOutputFrameOfReference[] = "/app/sensors/nv/radar/outputFrameOfReference";
constexpr char kRadarOutputCoordsType[] = "/app/sensors/nv/radar/elementsCoordsType";
constexpr char kRadarCustomFrameOfReferenceTrafo[] = "/app/sensors/nv/radar/customFrameOfReferenceTrafo";

/*
 * Enables inclusion of geometry data in rtxSensor returns
 *
 * Examples: --/app/sensors/nv/radar/enableRtxSensorGeometry=true
 * Default: disabled (setting not defined)
 */
constexpr char kEnableLidarRtxGeometries[] = "/app/sensors/nv/lidar/enableRtxSensorGeometry";
constexpr char kEnableRadarRtxGeometries[] = "/app/sensors/nv/radar/enableRtxSensorGeometry";
constexpr char kEnableUssRtxGeometries[] = "/app/sensors/nv/ultrasonic/enableRtxSensorGeometry";


////// IDS //////

/*
 * Sets additional base folders where ids profiles are read from.
 *
 * Examples: --/app/sensors/nv/ids/profileBaseFolder=["path_to_base_folder"]
 *           --/app/sensors/nv/ids/profileBaseFolder=["path_to_base_folder","another_base_folder"]
 */
constexpr char kIDSBaseFolderSetting[] = "/app/sensors/nv/ids/profileBaseFolder";

/*
 * Enables velocity information for ids point. Default is false for better runtime
 *
 * Examples: --/app/sensors/nv/ids/enableVelocity=true
 */
constexpr char kIDSEnableVelocitySetting[] = "/app/sensors/nv/ids/enableVelocity";

/*
 * Enable/disable determistic realm for ECU network channels
 *
 * Default: true
 * Examples: --/app/sensors/nv/determisticRealm/enabled=true
 */
constexpr char kSettingDetermisticRealm[] = "/app/sensors/nv/determisticRealm/enabled";

/*
 * Set to true to enable motion BVH for sensor motion effects
 *
 * Default: true
 * Examples: --/renderer/raytracingMotion/enabled=true
 */
constexpr char kSettingMotionBvh[] = "/renderer/raytracingMotion/enabled";


////// Materials //////

/*
 * Contains the a string with mappings from material name to id of the material.
 *
 * Default: ""
 * Examples:
 * --/rtx/materialDb/rtSensorNameToIdMap="DefaultMaterial:0;AsphaltStandardMaterial:1;AsphaltWeatheredMaterial:2;
 *   VegetationGrassMaterial:3;WaterStandardMaterial:4;GlassStandardMaterial:5;FiberGlassMaterial:6;
 *   MetalAlloyMaterial:7;MetalAluminumMaterial:8;MetalAluminumOxidizedMaterial:9;PlasticStandardMaterial:10;
 *   RetroMarkingsMaterial:11;RetroSignMaterial:12;RubberStandardMaterial:13;SoilClayMaterial:14;
 *   ConcreteRoughMaterial:15;ConcreteSmoothMaterial:16;OakTreeBarkMaterial:17;FabricStandardMaterial:18;
 *   PlexiGlassStandardMaterial:19;MetalSilverMaterial:20"
 */
constexpr char kSettingMaterialMapping[] = "/rtx/materialDb/rtSensorNameToIdMap";

/*
 * Contains the control flag for whether the material mapping is dependent on the legacy csv file or the new method
 * of encoding within usd.
 *
 * Examples: --/rtx/materialDb/nonVisualMaterialCSV/enabled=true
 * Default: disabled (setting not defined)
 */
constexpr char kSettingEnableRtxSensorCSVMapping[] = "/rtx/materialDb/nonVisualMaterialCSV/enabled";

/*
 * Contains the an encoding for which material index encodings to preserve for the BSDF behavior.
 *
 * Default: ""
 * Examples:
 * --/app/sensors/nv/materials/preserveMaterialFlags=0
 */
constexpr char kSettingPreserveMaterialFlags[] = "/app/sensors/nv/materials/preserveMaterialFlags";

/*
 * Contains the a string with remappings from material name to id of the material on a per modality basis.
 *
 * Default: ""
 * Examples:
 * --/app/sensors/nv/lidar/matNameToIdMapOverrides="AsphaltStandard:10;RubberStandard:2"
 */
constexpr char kSettingLidarMaterialReMapping[] = "/app/sensors/nv/lidar/matNameToIdMapOverrides";
constexpr char kSettingRadarMaterialReMapping[] = "/app/sensors/nv/radar/matNameToIdMapOverrides";
constexpr char kSettingUssMaterialReMapping[] = "/app/sensors/nv/ultrasonic/matNameToIdMapOverrides";

/*
 * Contains the a string with mappings from bsdf behavior name to id of the material.
 *
 * Default: ""
 * Examples:
 * --/app/sensors/nv/lidar/matBehaviorToIdOverrides="DefaultMaterial:0;CompositeMaterial:5;CoreMaterial:9"
 */
constexpr char kSettingLidarBSDFMaterialMapping[] = "/app/sensors/nv/lidar/matBehaviorToIdOverrides";
constexpr char kSettingRadarBSDFMaterialMapping[] = "/app/sensors/nv/radar/matBehaviorToIdOverrides";
constexpr char kSettingUssBSDFMaterialMapping[] = "/app/sensors/nv/ultrasonic/matBehaviorToIdOverrides";

/*
 * sets the flag for controlling a validation material for various usages
 *
 * Default: 0 - default BSDF behavior
 * Examples:
 * --/app/sensors/nv/materials/validationBSDFMode = 0
 */
constexpr char kSettingMaterialsValidationBSDFMode[] = "/app/sensors/nv/materials/validationBSDFMode";

/*
 * Enables visible band reflectance from rtxSensorReturn. This includes additional data such as
 * visible band diffuse and specular reflectance components. Default is false for better runtime
 *
 * Examples: --/app/sensors/nv/lidar/enableRtxReflectanceInformation=true
 * Default: disabled (setting not defined)
 */
constexpr char kEnableLidarRtxReflectanceInformationSetting[] = "/app/sensors/nv/lidar/enableRtxReflectanceInformation";
constexpr char kEnableRadarRtxReflectanceInformationSetting[] = "/app/sensors/nv/radar/enableRtxReflectanceInformation";
constexpr char kEnableUssRtxReflectanceInformationSetting[] =
    "/app/sensors/nv/ultrasonic/enableRtxReflectanceInformation";

constexpr char kRadarBaseFolderSetting[] = "/app/sensors/nv/radar/profileBaseFolder";

/*
 * Enables additional information from rtxSensorReturn. This includes additional data such as
 * visible band refractive index and roughness. Default is false for better runtime
 *
 * Examples: --/app/sensors/nv/lidar/enableAdditionalRtxReturnInformation=true
 * Default: disabled (setting not defined)
 */
constexpr char kEnableLidarAdditionalRtxReturnInformationSetting[] =
    "/app/sensors/nv/lidar/enableAdditionalRtxReturnInformation";
constexpr char kEnableRadarAdditionalRtxReturnInformationSetting[] =
    "/app/sensors/nv/radar/enableAdditionalRtxReturnInformation";
constexpr char kEnableUssAdditionalRtxReturnInformationSetting[] =
    "/app/sensors/nv/ultrasonic/enableAdditionalRtxReturnInformation";

/*
 * Enables beam polarization state computation for coherent systems
 *
 * Examples: --/app/sensors/nv/lidar/enablePolarization=true
 * Default: disabled (setting not defined)
 */
constexpr char kEnableLidarPolarization[] = "/app/sensors/nv/lidar/enablePolarization";
constexpr char kEnableRadarPolarization[] = "/app/sensors/nv/radar/enablePolarization";
constexpr char kEnableUssPolarization[] = "/app/sensors/nv/ultrasonic/enablePolarization";

/*
 * Flag for resetting materials for runtime redefinition of materials and associated properties.
 * This allows a full reset with the ability of adding new non visual materials
 *
 * Examples: --/app/sensors/nv/materials/resetMaterials=false
 * Default: disabled (setting not defined)
 */
constexpr char kResetMaterials[] = "/app/sensors/nv/materials/resetMaterials";

/*
 * Flag for updating materials for runtime redefinition of materials and associated properties
 * This allows only updating existing materials and not adding new ones
 *
 * Examples: --/app/sensors/nv/materials/updateMaterials=false
 * Default: disabled (setting not defined)
 */
constexpr char kUpdateMaterials[] = "/app/sensors/nv/materials/updateMaterials";

/*
 * Enables BSDF inter layer reflection and transmission calculations for more accurate results.
 *
 * Examples: --/app/sensors/nv/materials/enableInterLayerContributions=false
 * Default: disabled (setting not defined)
 */
constexpr char kEnableMaterialInterLayerContribution[] = "/app/sensors/nv/materials/enableMaterialInterLayerContribution";

/*
 * Add additional default material variants with corresponding reflectance factors.
 *
 * Examples: --/app/sensors/nv/materials/extraDefaultMaterialFactors=[0.05,0.1,0.84]
 */
constexpr char kDefaultMaterialsFactorsSetting[] = "/app/sensors/nv/materials/extraDefaultMaterialFactors";

/*
 * Adds lobewidth parameter to extra default materials.
 *
 * Examples: --/app/sensors/nv/materials/extraDefaultMaterialLobeWidths=[0.92,0.1,0.4]
 */
constexpr char kDefaultMaterialsLobewidthsSetting[] = "/app/sensors/nv/materials/extraDefaultMaterialLobeWidths";


////// Radar //////

/*
 * Set to true to force radar sensors to run even if motion BVH is disabled, they will run without motion effects
 *
 * Default: false
 * Examples: --/app/sensors/nv/radar/runWithoutMBVH=true
 */
constexpr char kSettingRunRadarWithoutMBVH[] = "/app/sensors/nv/radar/runWithoutMBVH";

/*
 * Set to true to enable ground truth output for radar sensors
 *
 * Default: false
 * Examples: --/app/sensors/nv/radar/enableGT=true
 */
constexpr char kSettingEnableRadarGT[] = "/app/sensors/nv/radar/enableGT";

/*
 * Set to true to skip sorting of detection list produced by radar sensors
 *
 * Default: false
 * Examples: --/app/sensors/nv/radar/skipDetectionsSorting=true
 */
constexpr char kSettingSkipDetectionsSorting[] = "/app/sensors/nv/radar/skipDetectionsSorting";

/*
 * Set to true to enable radar debug output
 *
 * Default: false
 * Examples: --/app/sensors/nv/radar/debug=true
 */
constexpr char kSettingRadarDebug[] = "/app/sensors/nv/radar/debug";

/*
 * Set to true to enable radar sensor setup matching. Radars will try to see if
 * they are in a known configuration, e.g. 5 sensors that make up an Hyp8.1
 * configuration. If they are, the sensors will adjust their timing behaviour to
 * match the real car.
 *
 * Default: false
 * Examples: --/app/sensors/nv/radar/enableSetupMatching=true
 */
constexpr char kSettingEnableRadarSetupMatching[] = "/app/sensors/nv/radar/enableSetupMatching";

////// Atmospherics ///////

/*
 * Sets the rain rate [mm/h] for the atmospherics simulation model. 0.0 deactivates rain based atmospheric modeling
 *
 * Examples: --/app/sensors/nv/atmospherics/rainRate=0.05
 */
constexpr char kAtmosRainRateSetting[] = "/app/sensors/nv/atmospherics/rainRate";

/*
 * Sets the threshold for false positive rain drop hits in the atmospherics.
 *
 * Examples: --/app/sensors/nv/atmospherics/rainDropHitThresh=0.015
 */
constexpr char kAtmosRainDropHitSetting[] = "/app/sensors/nv/atmospherics/rainDropHitThresh";

/*
 * Sets value for aerosol model in the atmospherics simulation, while a value of 0 deactivates the aerosolmodel.
 *
 * Examples: --/app/sensors/nv/atmospherics/aerosolModel=2.
 */
constexpr char kAtmosAeroSolModelSetting[] = "/app/sensors/nv/atmospherics/aerosolModel";

/*
 * Sets sun azimuth angle in degrees for aerosolmodel.
 *
 * Examples: --/app/sensors/nv/atmospherics/sunAzimuth=10.
 */
constexpr char kAtmosSunAzimuthSetting[] = "/app/sensors/nv/atmospherics/sunAzimuth";

/*
 * Sets sun elevation angle in degrees for aerosolmodel.
 *
 * Examples: --/app/sensors/nv/atmospherics/sunElevation=10.
 */
constexpr char kAtmosSunElevationSetting[] = "/app/sensors/nv/atmospherics/sunElevation";

/*
 * Sets the fractional amount of direct solar illumination to be applied
 *
 * Examples: --/app/sensors/nv/atmospherics/directSolarFraction=1.
 */
constexpr char kAtmosDirectSolarFractionSetting[] = "/app/sensors/nv/atmospherics/directSolarFraction";

////// LiDAR //////

/*
 * Sets additional base folders where lidar profiles are read from.
 *
 * Examples: --/app/sensors/nv/lidar/profileBaseFolder=["path_to_base_folder"]
 *           --/app/sensors/nv/lidar/profileBaseFolder=["path_to_base_folder","another_base_folder"]
 */
constexpr char kLidarBaseFolderSetting[] = "/app/sensors/nv/lidar/profileBaseFolder";

/*
 * Enables additional information for lidar point. This includes additional data such as
 * visible band diffuseReflectance, refractive index, and roughness. Default is false for better runtime
 *
 * Examples: --/app/sensors/nv/lidar/enableAdditionalReturnInformation=true
 * Default: disabled (setting not defined)
 */
constexpr char kLidarEnableAdditionalInformationSetting[] = "/app/sensors/nv/lidar/enableAdditionalInformation";

/*
 * Enables publishing of hitNormal information for lidar points. Default is false for less memory
 *
 * Examples: --/app/sensors/nv/lidar/publishNormals=true
 * Default: disabled (setting not defined)
 */
constexpr char kLidarPublishNormalsSetting[] = "/app/sensors/nv/lidar/publishNormals";

/*
 * Control setting for back face culling of intersected geometries within the scene.
 *
 * Examples: --/app/sensors/nv/lidar/cullBackFace=true
 */
constexpr char kSettingCullBackFace[] = "/app/sensors/nv/lidar/cullBackFace";

/*
 * Enable viz for lidar rig component sensor as follows
 * --/app/sensors/nv/lidar_#port/vizOnly= [true if no ecu is desired]
 * --/app/sensors/nv/lidar_#port/vizDataId= [-> has to be unique and between 0-10]
 * --/app/sensors/nv/lidar_#port/vizTransformation= [x,y,z,roll,pitch,yaw] [-> if not given then, the sensor mount will
 * be used]
 * --/app/sensors/nv/lidar_#port/colorCode= [0 - constant, 1 - intensity, 2 - height, 3 - range, 4 - objectId, 5 -
 * echoId, 6 - materialId]
 */


////// Ultrasonic //////

/**
 * Set to "<sensor_id>:<error_code>..." to inject errors into USS diagnostic data stream
 *
 * Default: ""
 * Examples: --/app/sensors/nv/ultrasonic/sensor_errors="1:12,4:12"
 */
constexpr char kSettingUltrasonicErrors[] = "/app/sensors/nv/ultrasonic/sensor_errors";

constexpr char kSettingUltrasonicRigVizDataId[] = "/app/sensors/nv/ultrasonic/rigVizDataId";
constexpr char kSettingUltrasonicRigVizAveragePeriod[] = "/app/sensors/nv/ultrasonic/rigVizAveragePeriod";
constexpr char kSettingUltrasonicRigVizOnly[] = "/app/sensors/nv/ultrasonic/rigVizOnly";
constexpr char kSettingUltrasonic64bitTimestamps[] = "/app/sensors/nv/ultrasonic/64bitTimestamps";

constexpr char kUltrasonicBaseFolderSetting[] = "/app/sensors/nv/ultrasonic/profileBaseFolder";

////// MemoryHandler FramesInFlight //////

/**
 * That is a constructed setting with the format /app/sensors/nv/<modality>/framesInFlight=<value>
 * modality can be (lidar, radar, ultrasonic, all)
 * value is the number of concurrent frames in flight
 *
 * Sets the frames in flight setting for a specific sensor modality (ex: radar) or for all,
 * if not set the default of the renderer will be used (currently 3), if set to 1 this means the sensor(s)
 * shouldn't multiply their buffers and the old syncWait mechanism will be active
 *
 * Default: "3"
 * Examples: --/app/sensors/nv/all/framesInFlight=3
 *           --/app/sensors/nv/radar/framesInFlight=1
 *
 * the above examples can be concurrent, user can set a setting for all sensors and override only for radar
 */

////// sensors file dump //////

// TODO: rename to match other sensor settings
/**
 * That is a constructed setting with the format /app/sensors/<modality>/<fileFormat>=<path>
 * modality can be (lidar, radar, ultrasonic, camera, all)
 * fileFormat can be (genericFilePath, dwBinFilePath, pcapFilePath, numpyFilePath)
 * path is the path where the file will be dumped
 *
 * enables dumping of sensor streams for a specific sensor modality or for all, the stream format can also
 * be set, there will be a file dump for each "sensor instance"
 *
 * Default: "" (empty = dumping disabled)
 * Examples: --/app/sensors/all/dwBinFilePath="recordings/all"
 *           --/app/sensors/radar/dwBinFilePath="recordings/radar"
 *
 * the above examples can be concurrent, user can set a setting for all sensors and override only for radar
 */

/**
 * The maximum amount of time for sync data.
 *
 * This value is used when the simulation is either in lockstep, or the value computed using kSyncDataWait is so large
 * as to exceed this value.Note this setting is in wall clock time, and units of seconds.
 */
constexpr char kMaxSyncDataWait[] = "/app/sensors/nv/syncdata/maxwait";

/**
 * The amount of time in ms to wait for a sync data event.
 *
 * Note wait is scaled to the time multiplier. However, this value will never exceed kMaxSyncDataWait. This value is
 * scaled by time multiplier. Note this setting is in wall clock time, and units of seconds.
 */
constexpr char kSyncDataWait[] = "/app/sensors/nv/syncdata/wait";

/**
 * The scale value for scling the wait time in sync data.
 */
constexpr char kSyncDataScale[] = "/app/sensors/nv/syncdata/scale";


////// Samples //////


/*
 * Enables/Disables publishing data dumps from wpm sample
 *
 * Examples: --/app/sensors/nv/samples/saveData=true
 * Default: disabled
 */
constexpr char kWpmSampleSaveData[] = "/app/sensors/nv/samples/saveWpmSampleData";


} // namespace nv
} // namespace sensors
} // namespace omni
