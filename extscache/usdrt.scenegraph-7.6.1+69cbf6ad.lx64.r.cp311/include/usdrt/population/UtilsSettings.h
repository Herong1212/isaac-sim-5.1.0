// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

// The simplest way of sharing Carbonite Settings Keys without any linking between libraries

#define USDRT_POPULATION_UTILS_MERGEMATERIALS "/app/usdrt/population/utils/mergeMaterials"
#define USDRT_POPULATION_UTILS_READMATERIALS "/app/usdrt/population/utils/readMaterials"
#define USDRT_POPULATION_UTILS_READLIGHTS "/app/usdrt/population/utils/readLights"
#define USDRT_POPULATION_UTILS_READCURVES "/app/usdrt/population/utils/readCurves"
#define USDRT_POPULATION_UTILS_READVOLUMES "/app/usdrt/population/utils/readVolumes"
#define USDRT_POPULATION_UTILS_READPRIMVARS "/app/usdrt/population/utils/readPrimvars"
#define USDRT_POPULATION_UTILS_SINGLETHREADED "/app/usdrt/population/utils/singleThreaded"
#define USDRT_POPULATION_UTILS_INFERDISPLAYCOLORFROMMATERIAL "/app/usdrt/population/utils/inferDisplayColorFromMaterial"
#define USDRT_POPULATION_UTILS_IOBOUNDTHREADCOUNT "/app/usdrt/population/utils/ioBoundThreadCount"
#define USDRT_POPULATION_UTILS_ENABLEFASTDIFFING "/app/usdrt/population/utils/enableFastDiffing"
#define USDRT_POPULATION_UTILS_ENABLE_INTERMEDIATE_INSTANCE_PROXY_POPULATION "/app/usdrt/population/utils/enableIntermediateInstanceProxyPopulation"
#define USDRT_POPULATION_UTILS_ENABLE_RENDERER_INSTANCING "/app/usdrt/population/utils/enableRendererInstancing"
#define USDRT_POPULATION_UTILS_INSTANCES_WITH_COMPACT_TRANSFORMS "/app/usdrt/population/utils/instanceCompactTransforms"
#define USDRT_POPULATION_UTILS_EVALUATE_XFORMS_TIME_SAMPLES "/app/usdrt/population/utils/evaluateXformsTimeSamples"
#define USDRT_POPULATION_UTILS_POPULATE_ALL_AUTHORED_ATTRIBUTES "/app/usdrt/population/utils/populateAllAuthoredAttributes"
#define USDRT_HYDRA_SCENEDELEGATE_CREATE_LIGHTS_IN_ORDER "/app/usdrt/scene_delegate/createLightsInOrder"
#define USDRT_POPULATION_UTILS_CREATE_ALL_MATERIALS "/app/usdrt/population/utils/createAllMaterials"

// Extend this list as settings are added that affect caching behaviour
#define USDRT_POPULATION_UTILS_SETTINGS_AFFECTING_CACHE() \
        USDRT_POPULATION_UTILS_MERGEMATERIALS, \
        USDRT_POPULATION_UTILS_READMATERIALS,  \
        USDRT_POPULATION_UTILS_READLIGHTS, \
        USDRT_POPULATION_UTILS_READCURVES, \
        USDRT_POPULATION_UTILS_READVOLUMES, \
        USDRT_POPULATION_UTILS_READPRIMVARS, \
        USDRT_POPULATION_UTILS_INFERDISPLAYCOLORFROMMATERIAL, \
        USDRT_POPULATION_UTILS_ENABLE_INTERMEDIATE_INSTANCE_PROXY_POPULATION, \
        USDRT_POPULATION_UTILS_POPULATE_ALL_AUTHORED_ATTRIBUTES, \
        USDRT_HYDRA_SCENEDELEGATE_CREATE_LIGHTS_IN_ORDER, \
        USDRT_POPULATION_UTILS_CREATE_ALL_MATERIALS, \
        USDRT_POPULATION_UTILS_ENABLE_RENDERER_INSTANCING, \
        USDRT_POPULATION_UTILS_INSTANCES_WITH_COMPACT_TRANSFORMS, \
        USDRT_POPULATION_UTILS_EVALUATE_XFORMS_TIME_SAMPLES
