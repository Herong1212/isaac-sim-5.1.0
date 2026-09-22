//
// Copyright 2016 Pixar
//
// Licensed under the Apache License, Version 2.0 (the "Apache License")
// with the following modification; you may not use this file except in
// compliance with the Apache License and the following modification to it:
// Section 6. Trademarks. is deleted and replaced with:
//
// 6. Trademarks. This License does not grant permission to use the trade
//    names, trademarks, service marks, or product names of the Licensor
//    and its affiliates, except as required to comply with Section 4(c) of
//    the License and to reproduce the content of the NOTICE file.
//
// You may obtain a copy of the Apache License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the Apache License with the above modification is
// distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, either express or implied. See the Apache License for the specific
// language governing permissions and limitations under the Apache License.
//
#ifndef RANGESENSOR_TOKENS_H
#define RANGESENSOR_TOKENS_H

/// \file rangeSensorSchema/tokens.h

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
// 
// This is an automatically generated file (by usdGenSchema.py).
// Do not hand-edit!
// 
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

#include "pxr/pxr.h"
#include ".//api.h"
#include "pxr/base/tf/staticData.h"
#include "pxr/base/tf/token.h"
#include <vector>

PXR_NAMESPACE_OPEN_SCOPE


/// \class RangeSensorTokensType
///
/// \link RangeSensorTokens \endlink provides static, efficient
/// \link TfToken TfTokens\endlink for use in all public USD API.
///
/// These tokens are auto-generated from the module's schema, representing
/// property names, for when you need to fetch an attribute or relationship
/// directly by name, e.g. UsdPrim::GetAttribute(), in the most efficient
/// manner, and allow the compiler to verify that you spelled the name
/// correctly.
///
/// RangeSensorTokens also contains all of the \em allowedTokens values
/// declared for schema builtin attributes of 'token' scene description type.
/// Use RangeSensorTokens like so:
///
/// \code
///     gprim.GetMyTokenValuedAttr().Set(RangeSensorTokens->adjacencyList);
/// \endcode
struct RangeSensorTokensType {
    RANGESENSORSCHEMA_API RangeSensorTokensType();
    /// \brief "adjacencyList"
    /// 
    /// RangeSensorUltrasonicEmitter
    const TfToken adjacencyList;
    /// \brief "attenuationAlpha"
    /// 
    /// RangeSensorUltrasonicArray
    const TfToken attenuationAlpha;
    /// \brief "drawLines"
    /// 
    /// RangeSensorRangeSensor
    const TfToken drawLines;
    /// \brief "drawPoints"
    /// 
    /// RangeSensorRangeSensor
    const TfToken drawPoints;
    /// \brief "emitterModes"
    /// 
    /// RangeSensorUltrasonicFiringGroup
    const TfToken emitterModes;
    /// \brief "emitterPrims"
    /// 
    /// RangeSensorUltrasonicArray
    const TfToken emitterPrims;
    /// \brief "enabled"
    /// 
    /// RangeSensorRangeSensor
    const TfToken enabled;
    /// \brief "enableSemantics"
    /// 
    /// RangeSensorLidar
    const TfToken enableSemantics;
    /// \brief "firingGroups"
    /// 
    /// RangeSensorUltrasonicArray
    const TfToken firingGroups;
    /// \brief "highLod"
    /// 
    /// RangeSensorLidar
    const TfToken highLod;
    /// \brief "horizontalFov"
    /// 
    /// RangeSensorLidar, RangeSensorUltrasonicArray
    const TfToken horizontalFov;
    /// \brief "horizontalResolution"
    /// 
    /// RangeSensorLidar, RangeSensorUltrasonicArray
    const TfToken horizontalResolution;
    /// \brief "maxRange"
    /// 
    /// RangeSensorRangeSensor
    const TfToken maxRange;
    /// \brief "minRange"
    /// 
    /// RangeSensorRangeSensor
    const TfToken minRange;
    /// \brief "numBins"
    /// 
    /// RangeSensorUltrasonicArray
    const TfToken numBins;
    /// \brief "perRayIntensity"
    /// 
    /// RangeSensorUltrasonicEmitter
    const TfToken perRayIntensity;
    /// \brief "receiverModes"
    /// 
    /// RangeSensorUltrasonicFiringGroup
    const TfToken receiverModes;
    /// \brief "rotationRate"
    /// 
    /// RangeSensorLidar
    const TfToken rotationRate;
    /// \brief "samplingRate"
    /// 
    /// RangeSensorGeneric
    const TfToken samplingRate;
    /// \brief "streaming"
    /// 
    /// RangeSensorGeneric
    const TfToken streaming;
    /// \brief "useBRDF"
    /// 
    /// RangeSensorUltrasonicArray
    const TfToken useBRDF;
    /// \brief "useDistAttenuation"
    /// 
    /// RangeSensorUltrasonicArray
    const TfToken useDistAttenuation;
    /// \brief "useUSSMaterialsForBRDF"
    /// 
    /// RangeSensorUltrasonicArray
    const TfToken useUSSMaterialsForBRDF;
    /// \brief "uss:base_color"
    /// 
    /// RangeSensorUltrasonicMaterialAPI
    const TfToken ussBase_color;
    /// \brief "uss:metallic"
    /// 
    /// RangeSensorUltrasonicMaterialAPI
    const TfToken ussMetallic;
    /// \brief "uss:perceptualRoughness"
    /// 
    /// RangeSensorUltrasonicMaterialAPI
    const TfToken ussPerceptualRoughness;
    /// \brief "uss:reflectance"
    /// 
    /// RangeSensorUltrasonicMaterialAPI
    const TfToken ussReflectance;
    /// \brief "verticalFov"
    /// 
    /// RangeSensorLidar, RangeSensorUltrasonicArray
    const TfToken verticalFov;
    /// \brief "verticalResolution"
    /// 
    /// RangeSensorLidar, RangeSensorUltrasonicArray
    const TfToken verticalResolution;
    /// \brief "yawOffset"
    /// 
    /// RangeSensorLidar, RangeSensorUltrasonicEmitter
    const TfToken yawOffset;
    /// \brief "Generic"
    /// 
    /// Schema identifer and family for RangeSensorGeneric
    const TfToken Generic;
    /// \brief "Lidar"
    /// 
    /// Schema identifer and family for RangeSensorLidar
    const TfToken Lidar;
    /// \brief "RangeSensor"
    /// 
    /// Schema identifer and family for RangeSensorRangeSensor
    const TfToken RangeSensor;
    /// \brief "UltrasonicArray"
    /// 
    /// Schema identifer and family for RangeSensorUltrasonicArray
    const TfToken UltrasonicArray;
    /// \brief "UltrasonicEmitter"
    /// 
    /// Schema identifer and family for RangeSensorUltrasonicEmitter
    const TfToken UltrasonicEmitter;
    /// \brief "UltrasonicFiringGroup"
    /// 
    /// Schema identifer and family for RangeSensorUltrasonicFiringGroup
    const TfToken UltrasonicFiringGroup;
    /// \brief "UltrasonicMaterialAPI"
    /// 
    /// Schema identifer and family for RangeSensorUltrasonicMaterialAPI
    const TfToken UltrasonicMaterialAPI;
    /// A vector of all of the tokens listed above.
    const std::vector<TfToken> allTokens;
};

/// \var RangeSensorTokens
///
/// A global variable with static, efficient \link TfToken TfTokens\endlink
/// for use in all public USD API.  \sa RangeSensorTokensType
extern RANGESENSORSCHEMA_API TfStaticData<RangeSensorTokensType> RangeSensorTokens;

PXR_NAMESPACE_CLOSE_SCOPE

#endif
