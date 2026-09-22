// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
// TODO USD COPYRIGHT AS WELL?
#pragma once

/// @file usdGeom/motionAPI.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/apiSchemaBase.h"
#include "usdrt/scenegraph/usd/usdGeom/tokens.h"


// ===================================================================== //
// Feel free to add custom includes between BEGIN and END CUSTOM INCLUDES
// below this line. It will be preserved by the code generator.
// We are using this instead of the `extraIncludes` in the pxr schema.usda
// files to allow for implementation differences in the custom code.
// ===================================================================== //
// --(BEGIN CUSTOM INCLUDES)--
// --(END CUSTOM INCLUDES)--

#include <omni/core/IObject.h>
#include <usdrt/scenegraph/base/tf/token.h>
#include <usdrt/scenegraph/base/vt/array.h>
#include <usdrt/scenegraph/interface/IRtAttribute.h>
#include <usdrt/scenegraph/interface/IRtPrim.h>
#include <usdrt/scenegraph/interface/IRtPrimRange.h>
#include <usdrt/scenegraph/interface/IRtRelationship.h>
#include <usdrt/scenegraph/interface/IRtStage.h>
#include <usdrt/scenegraph/usd/sdf/path.h>
#include <usdrt/scenegraph/usd/sdf/types.h>
#include <usdrt/scenegraph/usd/sdf/valueTypeName.h>
#include <usdrt/scenegraph/usd/usd/attribute.h>
#include <usdrt/scenegraph/usd/usd/common.h>
#include <usdrt/scenegraph/usd/usd/prim.h>
#include <usdrt/scenegraph/usd/usd/timeCode.h>

namespace usdrt
{

// -------------------------------------------------------------------------- //
// MOTIONAPI                                                                   //
// -------------------------------------------------------------------------- //

/// @class UsdGeomMotionAPI
///
/// UsdGeomMotionAPI encodes data that can live on any prim that
/// may affect computations involving:
/// - computed motion for motion blur
/// - sampling for motion blur
///
/// The \ref GetMotionBlurScaleAttr() "motion:blurScale" attribute allows
/// artists to scale the __amount__ of motion blur to be rendered for parts
/// of the scene without changing the recorded animation.  See
/// \ref UsdGeomMotionAPI_blurScale for use and implementation details.
///
///

class UsdGeomMotionAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a UsdGeomMotionAPI on UsdPrim @p prim.
    /// Equivalent to UsdGeomMotionAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdGeomMotionAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a UsdGeomMotionAPI on the prim held by @p schemaObj .
    /// Should be preferred over UsdGeomMotionAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdGeomMotionAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdGeomMotionAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "MotionAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid UsdGeomMotionAPI object is returned upon success.
    /// An invalid (or empty) UsdGeomMotionAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static UsdGeomMotionAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<UsdGeomMotionAPI>())
        {
            return UsdGeomMotionAPI(prim);
        }
        return UsdGeomMotionAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // MOTIONBLURSCALE
    // --------------------------------------------------------------------- //
    /// BlurScale is an __inherited__ float attribute that stipulates
    /// the rendered motion blur (as typically specified via UsdGeomCamera's
    /// _shutter:open_ and _shutter:close_ properties) should be scaled for
    /// __all objects__ at and beneath the prim in namespace on which the
    /// _motion:blurScale_ value is specified.
    ///
    /// Without changing any other data in the scene, _blurScale_ allows artists to
    /// "dial in" the amount of blur on a per-object basis.  A _blurScale_
    /// value of zero removes all blur, a value of 0.5 reduces blur by half,
    /// and a value of 2.0 doubles the blur.  The legal range for _blurScale_
    /// is [0, inf), although very high values may result in extremely expensive
    /// renders, and may exceed the capabilities of some renderers.
    ///
    /// Although renderers are free to implement this feature however they see
    /// fit, see \ref UsdGeomMotionAPI_blurScale for our guidance on implementing
    /// the feature universally and efficiently.
    ///
    /// \sa ComputeMotionBlurScale()
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float motion:blurScale = 1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMotionBlurScaleAttr() const;

    /// See GetMotionBlurScaleAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMotionBlurScaleAttr() const;

public:
    // --------------------------------------------------------------------- //
    // VELOCITYSCALE
    // --------------------------------------------------------------------- //
    /// \deprecated
    ///
    /// VelocityScale is an **inherited** float attribute that
    /// velocity-based schemas (e.g. PointBased, PointInstancer) can consume
    /// to compute interpolated positions and orientations by applying
    /// velocity and angularVelocity, which is required for interpolating
    /// between samples when topology is varying over time.  Although these
    /// quantities are generally physically computed by a simulator, sometimes
    /// we require more or less motion-blur to achieve the desired look.
    /// VelocityScale allows artists to dial-in, as a post-sim correction,
    /// a scale factor to be applied to the velocity prior to computing
    /// interpolated positions from it.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float motion:velocityScale = 1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetVelocityScaleAttr() const;

    /// See GetVelocityScaleAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateVelocityScaleAttr() const;

public:
    // --------------------------------------------------------------------- //
    // NONLINEARSAMPLECOUNT
    // --------------------------------------------------------------------- //
    /// Determines the number of position or transformation samples
    /// created when motion is described by attributes contributing non-linear
    /// terms.
    ///
    /// To give an example, imagine an application (such as a
    /// renderer) consuming 'points' and the USD document also
    /// contains 'accelerations' for the same prim. Unless the
    /// application can consume these 'accelerations' itself, an
    /// intermediate layer has to compute samples within the sampling
    /// interval for the point positions based on the value of
    /// 'points', 'velocities' and 'accelerations'. The number of these
    /// samples is given by 'nonlinearSampleCount'. The samples are
    /// equally spaced within the sampling interval.
    ///
    /// Another example involves the PointInstancer where
    /// 'nonlinearSampleCount' is relevant when 'angularVelocities'
    /// or 'accelerations' are authored.
    ///
    /// 'nonlinearSampleCount' is an **inherited** attribute, also
    /// see ComputeNonlinearSampleCount()
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int motion:nonlinearSampleCount = 3` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |

    UsdAttribute GetNonlinearSampleCountAttr() const;

    /// See GetNonlinearSampleCountAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateNonlinearSampleCountAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdGeomMotionAPI::_GetStaticTfType()
{
    const static TfToken token("UsdGeomMotionAPI");
    return token;
}

/* virtual */
inline const TfToken UsdGeomMotionAPI::_GetTfTypeToken() const
{
    const static TfToken token("UsdGeomMotionAPI");
    return token;
}


inline UsdAttribute UsdGeomMotionAPI::GetMotionBlurScaleAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->motionBlurScale));
}

inline UsdAttribute UsdGeomMotionAPI::CreateMotionBlurScaleAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->motionBlurScale), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomMotionAPI::GetVelocityScaleAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->motionVelocityScale));
}

inline UsdAttribute UsdGeomMotionAPI::CreateVelocityScaleAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->motionVelocityScale), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomMotionAPI::GetNonlinearSampleCountAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->motionNonlinearSampleCount));
}

inline UsdAttribute UsdGeomMotionAPI::CreateNonlinearSampleCountAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->motionNonlinearSampleCount), SdfValueTypeNames->Int,
                                     /* custom = */ false);
}


} // namespace usdrt
// ===================================================================== //
// Feel free to add custom code below this line. It will be preserved by
// the code generator.
//
// Just remember to wrap code in the appropriate delimiters:
// 'namespace usdrt {', '}'.
// ===================================================================== //
// --(BEGIN CUSTOM CODE)--
