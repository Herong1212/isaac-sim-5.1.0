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

/// @file usdGeom/xformCommonAPI.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/apiSchemaBase.h"
#include "usdrt/scenegraph/usd/usdGeom/tokens.h"

// clang-format off
/* Extra Includes
// USDRT NOTE: Use custom includes below instead to allow for
// implementation differences in the custom code. This section comes
// from the pxr schema.usda files which we may not have in usdrt.
//#include "usdrt/scenegraph/usd/usdGeom/xformable.h"
#include "usdrt/scenegraph/usd/usdGeom/xformOp.h" */
// clang-format on

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
// XFORMCOMMONAPI                                                              //
// -------------------------------------------------------------------------- //

/// @class UsdGeomXformCommonAPI
///
/// This class provides API for authoring and retrieving a standard set
/// of component transformations which include a scale, a rotation, a
/// scale-rotate pivot and a translation. The goal of the API is to enhance
/// component-wise interchange. It achieves this by limiting the set of allowed
/// basic ops and by specifying the order in which they are applied. In addition
/// to the basic set of ops, the 'resetXformStack' bit can also be set to
/// indicate whether the underlying xformable resets the parent transformation
/// (i.e. does not inherit it's parent's transformation).
///
/// \sa UsdGeomXformCommonAPI::GetResetXformStack()
/// \sa UsdGeomXformCommonAPI::SetResetXformStack()
///
/// The operator-bool for the class will inform you whether an existing
/// xformable is compatible with this API.
///
/// The scale-rotate pivot is represented by a pair of (translate,
/// inverse-translate) xformOps around the scale and rotate operations.
/// The rotation operation can be any of the six allowed Euler angle sets.
/// \sa UsdGeomXformOp::Type.
///
/// The xformOpOrder of an xformable that has all of the supported basic ops
/// is as follows:
/// ["xformOp:translate", "xformOp:translate:pivot", "xformOp:rotateXYZ",
/// "xformOp:scale", "!invert!xformOp:translate:pivot"].
///
/// It is worth noting that all of the ops are optional. For example, an
/// xformable may have only a translate or a rotate. It would still be
/// considered as compatible with this API. Individual SetTranslate(),
/// SetRotate(), SetScale() and SetPivot() methods are provided by this API
/// to allow such sparse authoring.

class UsdGeomXformCommonAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::NonAppliedAPI;


    /// Construct a UsdGeomXformCommonAPI on UsdPrim @p prim.
    /// Equivalent to UsdGeomXformCommonAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdGeomXformCommonAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a UsdGeomXformCommonAPI on the prim held by @p schemaObj .
    /// Should be preferred over UsdGeomXformCommonAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdGeomXformCommonAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdGeomXformCommonAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdGeomXformCommonAPI::_GetStaticTfType()
{
    const static TfToken token("UsdGeomXformCommonAPI");
    return token;
}

/* virtual */
inline const TfToken UsdGeomXformCommonAPI::_GetTfTypeToken() const
{
    const static TfToken token("UsdGeomXformCommonAPI");
    return token;
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
