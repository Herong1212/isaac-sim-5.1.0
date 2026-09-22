// Copyright (c) 2023-2025, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

// clang-format off
#define USDRT_POPULATION_LIGHT_PARAM_NAMES \
    (color) \
    (intensity) \
    (exposure) \
    (diffuse) \
    (specular) \
    (normalize) \
    (enableColorTemperature) \
    (colorTemperature) \
    (angle) \
    (radius) \
    (width) \
    (height) \
    ((textureFile, "texture:file")) \
    (treatAsPoint) \
    (length) \
    (treatAsLine) \
    ((textureFormat, "texture:format")) \
    ((shadowEnable, "shadow:enable")) \
    ((shadowColor, "shadow:color")) \
    ((shadowDistance, "shadow:distance")) \
    ((shadowFalloff, "shadow:falloff")) \
    ((shadowFalloffGamma, "shadow:falloffGamma")) \
    ((shapingFocus, "shaping:focus")) \
    ((shapingFocusTint, "shaping:focusTint")) \
    ((shapingConeAngle, "shaping:cone:angle")) \
    ((shapingConeSoftness, "shaping:cone:softness")) \
    ((shapingIesFile, "shaping:ies:file")) \
    ((shapingIesAngleScale, "shaping:ies:angleScale")) \
    ((shapingIesNormalize, "shaping:ies:normalize"))

#define USDRT_POPULATION_LIGHT_PARAM_NAMES_PREFIXED \
    (treatAsPoint) \
    (treatAsLine) \
    ((inputs_color, "inputs:color")) \
    ((inputs_intensity, "inputs:intensity")) \
    ((inputs_exposure, "inputs:exposure")) \
    ((inputs_diffuse, "inputs:diffuse")) \
    ((inputs_specular, "inputs:specular")) \
    ((inputs_normalize, "inputs:normalize")) \
    ((inputs_enableColorTemperature, "inputs:enableColorTemperature")) \
    ((inputs_colorTemperature, "inputs:colorTemperature")) \
    ((inputs_angle, "inputs:angle")) \
    ((inputs_radius, "inputs:radius")) \
    ((inputs_width, "inputs:width")) \
    ((inputs_height, "inputs:height")) \
    ((inputs_textureFile, "inputs:texture:file")) \
    ((inputs_length, "inputs:length")) \
    ((inputs_textureFormat, "inputs:texture:format")) \
    ((inputs_shadowEnable, "inputs:shadow:enable")) \
    ((inputs_shadowColor, "inputs:shadow:color")) \
    ((inputs_shadowDistance, "inputs:shadow:distance")) \
    ((inputs_shadowFalloff, "inputs:shadow:falloff")) \
    ((inputs_shadowFalloffGamma, "inputs:shadow:falloffGamma")) \
    ((inputs_shapingFocus, "inputs:shaping:focus")) \
    ((inputs_shapingFocusTint, "inputs:shaping:focusTint")) \
    ((inputs_shapingConeAngle, "inputs:shaping:cone:angle")) \
    ((inputs_shapingConeSoftness, "inputs:shaping:cone:softness")) \
    ((inputs_shapingIesFile, "inputs:shaping:ies:file")) \
    ((inputs_shapingIesAngleScale, "inputs:shaping:ies:angleScale")) \
    ((inputs_shapingIesNormalize, "inputs:shaping:ies:normalize"))

#define USDRT_POPULATION_RTX_LIGHT_PARAM_NAMES \
    (visibleInPrimaryRay) \
    (disableFogInteraction) \
    (isProjector) \
    ((lightEnableCaustics, "light:enableCaustics"))

#define USDRT_POPULATION_CAMERA_PARAM_NAMES \
    (horizontalAperture) \
    (verticalAperture) \
    (horizontalApertureOffset) \
    (verticalApertureOffset) \
    (focalLength) \
    (clippingRange) \
    (clippingPlanes) \
    (fStop) \
    (focusDistance) \
    ((shutterOpen, "shutter:open")) \
    ((shutterClose, "shutter:close")) \
    (shutterTimeTexturePath) \
    (stereoRole) \
    (projection) \
    (exposure)

#define USDRT_OMNI_SOUND_PARAM_NAMES \
    (filePath) \
    (auralMode) \
    (enableDoppler) \
    (enableDistanceDelay) \
    (enableInterauralDelay) \
    (loopCount) \
    (mediaOffsetStart) \
    (mediaOffsetEnd) \
    (startTime) \
    (endTime) \
    (priority) \
    (attenuationType) \
    (attenuationRange) \
    (gain) \
    (timeScale) \
    (coneAngles) \
    (coneVolumes) \
    (coneLowPassFilter) \
    ((default_, "default")) \
    (inverse) \
    (spatial)

#define USDRT_POPULATION_RTX_FISHEYE_CAMERA_PARAM_NAMES \
    (depthOfField) \
    (cameraProjectionType) \
    (fthetaWidth) \
    (fthetaHeight) \
    (fthetaCx) \
    (fthetaCy) \
    (openCVFx) \
    (openCVFy) \
    (fthetaMaxFov) \
    (fthetaPolyA) \
    (fthetaPolyB) \
    (fthetaPolyC) \
    (fthetaPolyD) \
    (fthetaPolyE) \
    (fthetaPolyF) \
    (p0) \
    (p1) \
    (s0) \
    (s1) \
    (s2) \
    (s3) \
    (interpupillaryDistance) \
    (isLeftEye) \
    (generalizedProjectionDirectionTexturePath) \
    (generalizedProjectionNDCTexturePath)

#define USDRT_POPULATION_SENSOR_MODEL_CAMERA_PARAM_NAMES \
    (cameraSensorType) \
    (sensorModelPluginName) \
    (sensorModelConfig) \
    (sensorModelSignals) \
    (crossCameraReferenceName)

// TODO: @sdawson - 2025-02-13 - Refactor once we no longer need to support old NuRec volume files
#define USDRT_POPULATION_OMNI_NUREC_VOLUME_PRIM_TYPES \
    (OmniNerfVolumeAPI) \
    (INGPFieldAsset) \
    (OmniNuRecVolume) \
    (OmniNuRecVolumeAPI) \
    (OmniNuRecFieldAsset)

/* NRE Volume parameters */
#define USDRT_POPULATION_OMNI_NUREC_VOLUME_PARAM_NAMES \
    ((omniNuRecCropMinBounds, "omni:nurec:crop:minBounds")) \
    ((omniNuRecCropMaxBounds, "omni:nurec:crop:maxBounds")) \
    ((omniNuRecOffset, "omni:nurec:offset")) \
    ((omniNuRecExposure, "omni:nurec:exposure")) \
    ((omniNuRecCcmR, "omni:nurec:ccmR")) \
    ((omniNuRecCcmG, "omni:nurec:ccmG")) \
    ((omniNuRecCcmB, "omni:nurec:ccmB")) \
    ((nerfCropMinBounds, "nerf:crop:minBounds")) \
    ((nerfCropMaxBounds, "nerf:crop:maxBounds")) \
    ((nerfOffset, "nerf:offset")) \
    ((nerfExposure, "nerf:exposure")) \
    ((nerfCcmR, "nerf:ccmR")) \
    ((nerfCcmG, "nerf:ccmG")) \
    ((nerfCcmB, "nerf:ccmB")) \
    (proxy) \
    (tracks) \
    ((omniNuRecIsNuRecVolume, "omni:nurec:isNuRecVolume")) \
    ((omniNuRecUseProxyTransform, "omni:nurec:useProxyTransform")) \
    (fieldRole) \
    (density) \
    (emissiveColor)

#define USDRT_POPULATION_FABRIC_PRIM_TYPES \
    (Gprim) \
    (PointBased) \
    (Curves) \
    (BasisCurves) \
    (Points) \
    (Camera) \
    (Mesh) \
    (Cube) \
    (Sphere) \
    (Cone) \
    (Cylinder) \
    (Capsule) \
    (RenderSettings) \
    (RenderVar) \
    (RenderProduct) \
    (Scope) \
    (Untyped) \
    (Xformable) \
    (Xform) \
    (Volume) \
    (OpenVDBAsset) \
    (openvdbAsset) /* Hydra prim type is different and not defined on hydra prim type tokens*/ \
    (FieldAsset) \
    USDRT_POPULATION_OMNI_NUREC_VOLUME_PRIM_TYPES \
    (Imageable) \
    (Boundable) \
    (Material) \
    (MaterialBindingAPI) \
    (MaterialNetwork) \
    (NodeGraph) \
    (Shader) \
    (PointInstancer) \
    (LightAPI) \
    ((LightShapingAPI, "ShapingAPI")) \
    ((LightShadowAPI, "ShadowAPI")) \
    (DistantLight) \
    (DiskLight) \
    (RectLight) \
    (SphereLight) \
    (CylinderLight) \
    (GeometryLight) \
    (DomeLight) \
    (PortalLight) \
    /* Instanced type names */ \
    (GeomInstanceAPI) \
    (GeomInstanceRootAPI) \
    (PrototypeRootAPI) \
    (MeshInstance) \
    (CubeInstance) \
    (SphereInstance) \
    (ConeInstance) \
    (CylinderInstance) \
    (CapsuleInstance) \
    (PointsInstance) \
    (BasisCurvesInstance) \
    (CurvesInstance) \
    (XformInstance) \
    (ScopeInstance) \
    (PointInstancerInstance) \
    (DistantLightInstance) \
    (DiskLightInstance) \
    (RectLightInstance) \
    (SphereLightInstance) \
    (CylinderLightInstance) \
    (GeometryLightInstance) \
    (DomeLightInstance) \
    (PortalLightInstance) \
    /* Placeholder lightweight prims to update deduplicated primitives */ \
    (MergedMaterial) \
    (MergedMesh) \
    /* optional subdivision property schema */ \
    (MeshSubdivision) \
    /* UsdSkel prims*/ \
    (SkelRoot) \
    (Skeleton) \
    (SkelAnimation) \
    (SkelBindingAPI_Skel) \
    (SkelBindingAPI_Geom) \
    (BlendShape) \
    /* RTX specific optional attributes*/ \
    (LightVisibleInPrimaryRayAPI) \
    (LightDisableFogInteractionAPI) \
    (LightIsProjectorAPI) \
    (LightEnableCausticsAPI) \
    /* Temp change tracking */ \
    (TempChangeTracking) \
    ((Empty, "")) \
    (PrimvarsAPI) \
    (NVSealedUsdArchive) \
    (NVSealedUsdArchiveFileSource) \
    (SemanticsAPI) \
    (SemanticsLabelsAPI) \
    (LODSelector) \
    (LODLevel) \
    (LODGeometries) \
    (LODErrorToNext) \
    (LODSwitchToNextDistance) \
    (LODSwitchToPreviousDistance) \
    (LODSelectedLOD) \
    (LODChangingLOD) \
    (LODLevels) \
    (archiveChildName) \
    (archiveState) \
    (unloaded) \
    (OmniTime) \
    (OmniRtx) \
    (OmniLensDistortion) \
    (ImageableInstance) \
    (OmniSound) \


#define USDRT_POPULATION_SPECIAL_PRIM_NAMES \
    (OmniverseKit_Front) \
    (OmniverseKit_Top) \
    (OmniverseKit_Right) \
    (OmniverseKit_Persp) \


#define USDRT_POPULATION_PRIMVARS_PREFIX "primvars:"
#define USDRT_POPULATION_PRIMVARS_INTERPOLATION_SUFFIX ":interpolation"
#define USDRT_POPULATION_PRIMVARS_INDICES_SUFFIX ":indices"

#define USDRT_POPULATION_PRIM_PARAM_NAMES \
    /* Special parameter names used in Fabric */ \
    ((_default, "default")) /* Used by the MaterialWatcher to store default values*/ \
    (_worldPosition) \
    (_worldOrientation) \
    (_worldScale) \
    (_worldExtent) \
    (_worldVisibility) \
    ((localMatrix, "omni:fabric:localMatrix")) \
    ((worldMatrix, "omni:fabric:worldMatrix")) \
    ((resetXformStack, "omni:fabric:resetXformStack")) \
    (translations) \
    (rotations) \
    (blendShapeWeights) \
    (_localMatrix) \
    (_hasAnimatedXform) \
    ((omni_rtx_skip, "omni:rtx:skip")) \
    /* RTX specific single sided parameter */ \
    (singleSided) \
    /* base attributes for rprims */ \
    (subsetMaterialId) /* To store materials assigned to subsets */ \
    (subsetIndices) /* To store subset assignment indices */ \
    (subsetIndicesCount) /* To store subset assignment indices count */ \
    (subsetIds) /* To store the paths of subsets*/ \
    /* Refinement level override for mesh */ \
    (refinementLevel) \
    (refinementEnableOverride) \
    /* Prototype prim names */ \
    ((protoIdFmt, "proto%zu")) \
    /* Prototype geo parameters */ \
    (GeomPrototypeAPI) \
    (_instancerPath) \
    (_protoPrimType) \
    (_protoIndex) \
    (_protoPath) \
    (_instanceMaterialBinding) /* To store material binding for instances - not as an array for speed */ \
    (_numberOfInstances) \
    /* Some prototypes get "relocated" during population, this is the original path to fetch primvars from */ \
    (_originalUsdPath) \
    /* UsdSkel parameters*/ \
    ((_evaluatedTranslations, "evaluatedTranslations")) \
    ((_evaluatedRotations, "evaluatedRotations")) \
    ((_evaluatedScales, "evaluatedScales")) \
    ((_evaluatedTransformPurpose, "evaluatedTransformPurpose")) \
    (_parentIndices) \
    /* (_skelAnimMap) */ \
    /* (_skelSkinningMap) */ \
    ((primvarsSkelSkinningBlendWeights, "primvars:skel:skinningBlendWeights")) \
    ((primvarsSkelSkinningBlendWeightsInterpolation, "primvars:skel:skinningBlendWeights:interpolation")) \
    ((primvarsSkelJointIndicesInterpolation, "primvars:skel:jointIndices:interpolation")) \
    ((primvarsSkelJointIndicesElementSize, "primvars:skel:jointIndices:elementSize")) \
    ((skelSkinningMethod, "skel:skinningMethod")) \
    (_timeVaryingBits) \
    (_restPoints) \
    (_subShapesCount) \
    (_weights) \
    (_offsetsCounts) \
    (_normalOffsetsCounts) \
    /* Volume parameters */ \
    ((fieldPrefix, "field:")) \
    USDRT_POPULATION_OMNI_NUREC_VOLUME_PARAM_NAMES \
    /* special tag to separate newly created prims in separate bucket for fast parallel population */ \
    (_primIsBeingInitialized) \
    /* Parameters on merged materials */ \
    (_materialSource) \
    /* Temp change tracking */ \
    (_deletedPrims) \
    (_needResyncSkeletonPrims) \
    (st) \
    ((st_indices, "st:indices")) \
    (LODlevel) \
    /* TODO: remove omni:ignorePrimType as we will just use omni:ignorePrim as an attribute */ \
    ((omniIgnorePrimType, "omni:ignorePrimType")) \
    ((omniIgnorePrim, "omni:ignorePrim")) \
    ((omniArrayContentHash, "omni:array_content_hash")) \
    /* Primvar parameter prefixes and suffixes */ \
    ((primvarsPrefix, USDRT_POPULATION_PRIMVARS_PREFIX)) \
    ((primvarsInterpolationSuffix, USDRT_POPULATION_PRIMVARS_INTERPOLATION_SUFFIX)) \
    ((primvarsIndicesSuffix, USDRT_POPULATION_PRIMVARS_INDICES_SUFFIX)) \
    ((primvarsNormals, USDRT_POPULATION_PRIMVARS_PREFIX "normals")) \
    ((normalsInterpolation, "normals" USDRT_POPULATION_PRIMVARS_INTERPOLATION_SUFFIX)) /*normals:interpolation W/O primvars prefix*/ \
    /* Store the order of lights in the original usd stage */ \
    (_orderOfLights) \
    (archive) \
    (primPath) \
    (_isInSceneGraphInstancingPrototype) \
    (_isSceneGraphInstancingRoot) \
    /* OmniSensor attributes */ \
    ((omniSensorPrefix, "omni:sensor:")) \
    /* OmniLensDistortion */ \
    ((omniLensDistortionPrefix, "omni:lensdistortion:")) \
    /* SemanticsAPI */ \
    ((paramsSemanticType, "params:semanticType")) \
    ((paramsSemanticData, "params:semanticData")) \
    ((semantic, "semantic")) \
    /* SemanticsLabelsPI */ \
    ((semanticsLabels, "semantics:labels")) \
    (renderSettings) \
    ((omniTime, "omni:time")) \
    ((worldInstanceTransform, "omni:fabric:worldInstanceTransform")) \
    (widthsInterpolation) \


#define USDRT_POPULATION_CONNECTION_TYPE_NAMES \
    (_usdrtRelationshipSource) \
    (_usdrtRenderSettingsChild) \
    (_usdrtRenderSettingsBaseCamera) \
    (_usdrtInstanceRootToProtoRoot) \


#define USDRT_POPULATION_MATERIAL_PARAM_NAMES \
    (MaterialPoolElem) \
    (_hash) \
    (timeVaryingAttributes) \
    (_paramColorSpace) \
    (colorSpace) \
    (_sdrMetadata) \
    ((info_implementationSource, "info:implementationSource")) \
    ((info_id, "info:id")) \
    ((info_sourceAsset, "info:sourceAsset")) \
    ((info_subIdentifier, "info:sourceAsset:subIdentifier")) \
    ((info_sourceCode, "info:sourceCode")) \
    ((inputsPrefix, "inputs:")) \
    ((outputsPrefix, "outputs:")) \
    ((infoPrefix, "info:")) \
    ((inputsNonvisualAttributesSuffix, ":attributes")) \
    ((inputsNonvisualCoatingSuffix, ":coating")) \
    ((inputsNonvisualBaseSuffix, ":base"))

#define STAGEINFO_PRIM_NAME "__Fabric_StageInfo"

#define USDRT_POPULATION_STAGE_INFO_PARAM_NAMES \
    (FabricStageInfo) \
    ((stageInfoPrimName, STAGEINFO_PRIM_NAME)) \
    (lastGlobalTime) \
    (materialPurpose) \
    (MaterialPool) \
    (Schemas)

// TODO: make this more sophisticated
#define USDRT_POPULATION_HASH_POINTS "points"
#define USDRT_POPULATION_HASH_FACE_VERTEX_COUNTS "faceVertexCounts"
#define USDRT_POPULATION_HASH_FACE_VERTEX_INDICES "faceVertexIndices"
#define USDRT_POPULATION_HASH_HOLE_INDICES "holeIndices"
#define USDRT_POPULATION_HASH_DISPLAY_COLORS "displayColors"
#define USDRT_POPULATION_HASH_DISPLAY_OPACITIES "displayOpacities"

#define USDRT_POPULATION_HASH_VALUE_NAME(attribute) "ujitso:population:" attribute ":hash:value"
#define USDRT_POPULATION_HASH_KEY_NAME(attribute) "ujitso:population:" attribute ":hash:key"
#define USDRT_POPULATION_HASH_FLAG_NAME(attribute) "ujitso:population:" attribute ":hash:exists"
#define USDRT_POPULATION_POPULATED_NAME(attribute) "ujitso:population:" attribute ":populated"
#define USDRT_POPULATION_ELEMCOUNT_NAME(attribute) "ujitso:population:" attribute ":elemCount"

#define USDRT_POPULATION_HASH_ATTRIBUTE_NAMES \
    ((points, USDRT_POPULATION_HASH_POINTS)) \
    ((faceVertexCounts, USDRT_POPULATION_HASH_FACE_VERTEX_COUNTS)) \
    ((faceVertexIndices, USDRT_POPULATION_HASH_FACE_VERTEX_INDICES)) \
    ((holeIndices, USDRT_POPULATION_HASH_HOLE_INDICES))

#define USDRT_POPULATION_HASH_METADATA_NAMES \
    ((points_hash_exists, USDRT_POPULATION_HASH_FLAG_NAME(USDRT_POPULATION_HASH_POINTS))) \
    ((faceVertexCounts_hash_exists, USDRT_POPULATION_HASH_FLAG_NAME(USDRT_POPULATION_HASH_FACE_VERTEX_COUNTS))) \
    ((faceVertexIndices_hash_exists, USDRT_POPULATION_HASH_FLAG_NAME(USDRT_POPULATION_HASH_FACE_VERTEX_INDICES))) \
    ((holeIndices_hash_exists, USDRT_POPULATION_HASH_FLAG_NAME(USDRT_POPULATION_HASH_HOLE_INDICES))) \
    /*((displayColors_hash_exists, USDRT_POPULATION_HASH_FLAG_NAME(USDRT_POPULATION_HASH_DISPLAY_COLORS)))*/ \
    /*((displayOpacities_hash_exists, USDRT_POPULATION_HASH_FLAG_NAME(USDRT_POPULATION_HASH_DISPLAY_OPACITIES)))*/ \
    \
    ((points_hash_value, USDRT_POPULATION_HASH_VALUE_NAME(USDRT_POPULATION_HASH_POINTS))) \
    ((faceVertexCounts_hash_value, USDRT_POPULATION_HASH_VALUE_NAME(USDRT_POPULATION_HASH_FACE_VERTEX_COUNTS))) \
    ((faceVertexIndices_hash_value, USDRT_POPULATION_HASH_VALUE_NAME(USDRT_POPULATION_HASH_FACE_VERTEX_INDICES))) \
    ((holeIndices_hash_value, USDRT_POPULATION_HASH_VALUE_NAME(USDRT_POPULATION_HASH_HOLE_INDICES))) \
    /*((displayColors_hash_value, USDRT_POPULATION_HASH_VALUE_NAME(USDRT_POPULATION_HASH_DISPLAY_COLORS)))*/ \
    /*((displayOpacities_hash_value, USDRT_POPULATION_HASH_VALUE_NAME(USDRT_POPULATION_HASH_DISPLAY_OPACITIES)))*/ \
    \
    ((points_hash_key, USDRT_POPULATION_HASH_KEY_NAME(USDRT_POPULATION_HASH_POINTS))) \
    ((faceVertexCounts_hash_key, USDRT_POPULATION_HASH_KEY_NAME(USDRT_POPULATION_HASH_FACE_VERTEX_COUNTS))) \
    ((faceVertexIndices_hash_key, USDRT_POPULATION_HASH_KEY_NAME(USDRT_POPULATION_HASH_FACE_VERTEX_INDICES))) \
    ((holeIndices_hash_key, USDRT_POPULATION_HASH_KEY_NAME(USDRT_POPULATION_HASH_HOLE_INDICES))) \
    /*((displayColors_hash_key, USDRT_POPULATION_HASH_KEY_NAME(USDRT_POPULATION_HASH_DISPLAY_COLORS)))*/ \
    /*((displayOpacities_hash_key, USDRT_POPULATION_HASH_KEY_NAME(USDRT_POPULATION_HASH_DISPLAY_OPACITIES)))*/ \
    \
    ((points_populated, USDRT_POPULATION_POPULATED_NAME(USDRT_POPULATION_HASH_POINTS))) \
    ((faceVertexCounts_populated, USDRT_POPULATION_POPULATED_NAME(USDRT_POPULATION_HASH_FACE_VERTEX_COUNTS))) \
    ((faceVertexIndices_populated, USDRT_POPULATION_POPULATED_NAME(USDRT_POPULATION_HASH_FACE_VERTEX_INDICES))) \
    ((holeIndices_populated, USDRT_POPULATION_POPULATED_NAME(USDRT_POPULATION_HASH_HOLE_INDICES))) \
    /*((displayColors_populated, USDRT_POPULATION_POPULATED_NAME(USDRT_POPULATION_HASH_DISPLAY_COLORS)))*/ \
    /*((displayOpacities_populated, USDRT_POPULATION_POPULATED_NAME(USDRT_POPULATION_HASH_DISPLAY_OPACITIES)))*/ \
    \
    ((points_elemCount, USDRT_POPULATION_ELEMCOUNT_NAME(USDRT_POPULATION_HASH_POINTS))) \
    ((faceVertexCounts_elemCount, USDRT_POPULATION_ELEMCOUNT_NAME(USDRT_POPULATION_HASH_FACE_VERTEX_COUNTS))) \
    ((faceVertexIndices_elemCount, USDRT_POPULATION_ELEMCOUNT_NAME(USDRT_POPULATION_HASH_FACE_VERTEX_INDICES))) \
    ((holeIndices_elemCount, USDRT_POPULATION_ELEMCOUNT_NAME(USDRT_POPULATION_HASH_HOLE_INDICES))) \
    /*((displayColors_elemCount, USDRT_POPULATION_ELEMCOUNT_NAME(USDRT_POPULATION_HASH_DISPLAY_COLORS)))*/ \
    /*((displayOpacities_elemCount, USDRT_POPULATION_ELEMCOUNT_NAME(USDRT_POPULATION_HASH_DISPLAY_OPACITIES)))*/

#define USDRT_POPULATION_HASH_ALL_NAMES \
    USDRT_POPULATION_HASH_ATTRIBUTE_NAMES \
    USDRT_POPULATION_HASH_METADATA_NAMES

#define USDRT_LIGHT_PARAM_REMAPPING(tokensIn, tokensOut) \
{ (tokensIn)->angle, (tokensOut)->inputs_angle }, \
{ (tokensIn)->color, (tokensOut)->inputs_color }, \
{ (tokensIn)->colorTemperature, (tokensOut)->inputs_colorTemperature }, \
{ (tokensIn)->diffuse, (tokensOut)->inputs_diffuse }, \
{ (tokensIn)->enableColorTemperature, (tokensOut)->inputs_enableColorTemperature }, \
{ (tokensIn)->exposure, (tokensOut)->inputs_exposure }, \
{ (tokensIn)->height, (tokensOut)->inputs_height }, \
{ (tokensIn)->intensity, (tokensOut)->inputs_intensity }, \
{ (tokensIn)->length, (tokensOut)->inputs_length }, \
{ (tokensIn)->normalize, (tokensOut)->inputs_normalize }, \
{ (tokensIn)->radius, (tokensOut)->inputs_radius }, \
{ (tokensIn)->specular, (tokensOut)->inputs_specular }, \
{ (tokensIn)->textureFile, (tokensOut)->inputs_textureFile }, \
{ (tokensIn)->textureFormat, (tokensOut)->inputs_textureFormat }, \
{ (tokensIn)->width, (tokensOut)->inputs_width }, \
{ (tokensIn)->shapingFocus, (tokensOut)->inputs_shapingFocus }, \
{ (tokensIn)->shapingFocusTint, (tokensOut)->inputs_shapingFocusTint }, \
{ (tokensIn)->shapingConeAngle, (tokensOut)->inputs_shapingConeAngle }, \
{ (tokensIn)->shapingConeSoftness, (tokensOut)->inputs_shapingConeSoftness }, \
{ (tokensIn)->shapingIesFile, (tokensOut)->inputs_shapingIesFile }, \
{ (tokensIn)->shapingIesAngleScale, (tokensOut)->inputs_shapingIesAngleScale }, \
{ (tokensIn)->shapingIesNormalize, (tokensOut)->inputs_shapingIesNormalize }, \
{ (tokensIn)->shadowEnable, (tokensOut)->inputs_shadowEnable }, \
{ (tokensIn)->shadowColor, (tokensOut)->inputs_shadowColor }, \
{ (tokensIn)->shadowDistance, (tokensOut)->inputs_shadowDistance }, \
{ (tokensIn)->shadowFalloff, (tokensOut)->inputs_shadowFalloff }, \
{ (tokensIn)->shadowFalloffGamma, (tokensOut)->inputs_shadowFalloffGamma },

// clang-format on
