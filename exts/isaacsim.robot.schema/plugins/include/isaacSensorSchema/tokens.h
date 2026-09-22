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
#ifndef ISAACSENSOR_TOKENS_H
#define ISAACSENSOR_TOKENS_H

/// \file isaacSensorSchema/tokens.h

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


/// \class IsaacSensorTokensType
///
/// \link IsaacSensorTokens \endlink provides static, efficient
/// \link TfToken TfTokens\endlink for use in all public USD API.
///
/// These tokens are auto-generated from the module's schema, representing
/// property names, for when you need to fetch an attribute or relationship
/// directly by name, e.g. UsdPrim::GetAttribute(), in the most efficient
/// manner, and allow the compiler to verify that you spelled the name
/// correctly.
///
/// IsaacSensorTokens also contains all of the \em allowedTokens values
/// declared for schema builtin attributes of 'token' scene description type.
/// Use IsaacSensorTokens like so:
///
/// \code
///     gprim.GetMyTokenValuedAttr().Set(IsaacSensorTokens->angularVelocityFilterWidth);
/// \endcode
struct IsaacSensorTokensType {
    ISAACSENSORSCHEMA_API IsaacSensorTokensType();
    /// \brief "angularVelocityFilterWidth"
    /// 
    /// IsaacSensorIsaacImuSensor
    const TfToken angularVelocityFilterWidth;
    /// \brief "color"
    /// 
    /// IsaacSensorIsaacContactSensor
    const TfToken color;
    /// \brief "curtainAxis"
    /// 
    /// IsaacSensorIsaacLightBeamSensor
    const TfToken curtainAxis;
    /// \brief "curtainLength"
    /// 
    /// IsaacSensorIsaacLightBeamSensor
    const TfToken curtainLength;
    /// \brief "enabled"
    /// 
    /// IsaacSensorIsaacBaseSensor
    const TfToken enabled;
    /// \brief "forwardAxis"
    /// 
    /// IsaacSensorIsaacLightBeamSensor
    const TfToken forwardAxis;
    /// \brief "linearAccelerationFilterWidth"
    /// 
    /// IsaacSensorIsaacImuSensor
    const TfToken linearAccelerationFilterWidth;
    /// \brief "maxRange"
    /// 
    /// IsaacSensorIsaacLightBeamSensor
    const TfToken maxRange;
    /// \brief "minRange"
    /// 
    /// IsaacSensorIsaacLightBeamSensor
    const TfToken minRange;
    /// \brief "numRays"
    /// 
    /// IsaacSensorIsaacLightBeamSensor
    const TfToken numRays;
    /// \brief "orientationFilterWidth"
    /// 
    /// IsaacSensorIsaacImuSensor
    const TfToken orientationFilterWidth;
    /// \brief "radius"
    /// 
    /// IsaacSensorIsaacContactSensor
    const TfToken radius;
    /// \brief "sensorPeriod"
    /// 
    /// IsaacSensorIsaacContactSensor, IsaacSensorIsaacImuSensor
    const TfToken sensorPeriod;
    /// \brief "threshold"
    /// 
    /// IsaacSensorIsaacContactSensor
    const TfToken threshold;
    /// \brief "IsaacBaseSensor"
    /// 
    /// Schema identifer and family for IsaacSensorIsaacBaseSensor
    const TfToken IsaacBaseSensor;
    /// \brief "IsaacContactSensor"
    /// 
    /// Schema identifer and family for IsaacSensorIsaacContactSensor
    const TfToken IsaacContactSensor;
    /// \brief "IsaacImuSensor"
    /// 
    /// Schema identifer and family for IsaacSensorIsaacImuSensor
    const TfToken IsaacImuSensor;
    /// \brief "IsaacLightBeamSensor"
    /// 
    /// Schema identifer and family for IsaacSensorIsaacLightBeamSensor
    const TfToken IsaacLightBeamSensor;
    /// \brief "IsaacRtxLidarSensorAPI"
    /// 
    /// Schema identifer and family for IsaacSensorIsaacRtxLidarSensorAPI
    const TfToken IsaacRtxLidarSensorAPI;
    /// \brief "IsaacRtxRadarSensorAPI"
    /// 
    /// Schema identifer and family for IsaacSensorIsaacRtxRadarSensorAPI
    const TfToken IsaacRtxRadarSensorAPI;
    /// A vector of all of the tokens listed above.
    const std::vector<TfToken> allTokens;
};

/// \var IsaacSensorTokens
///
/// A global variable with static, efficient \link TfToken TfTokens\endlink
/// for use in all public USD API.  \sa IsaacSensorTokensType
extern ISAACSENSORSCHEMA_API TfStaticData<IsaacSensorTokensType> IsaacSensorTokens;

PXR_NAMESPACE_CLOSE_SCOPE

#endif
