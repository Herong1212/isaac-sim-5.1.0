//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
// TODO USD COPYRIGHT AS WELL?
#pragma once

//! @file
//!
//! @brief TODO

// GENERATED FILE DO NOT EDIT

/// \file usdLux/lightPortal.h

#include "usdrt/scenegraph/usd/usdGeom/xformable.h"

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
// LIGHTPORTAL                                                                 //
// -------------------------------------------------------------------------- //


/// \class UsdLuxLightPortal
///
/// A rectangular portal in the local XY plane that guides sampling
/// of a dome light.  Transmits light in the -Z direction.
/// The rectangle is 1 unit in length.
///

class UsdLuxLightPortal : public UsdGeomXformable
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// \sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdLuxLightPortal on UsdPrim \p prim .
    /// Equivalent to UsdLuxLightPortal::Get(prim.GetStage(), prim.GetPath())
    /// for a \em valid \p prim, but will not immediately throw an error for
    /// an invalid \p prim
    explicit UsdLuxLightPortal(const UsdPrim& prim = UsdPrim()) : UsdGeomXformable(prim)
    {
    }

    /// Construct a UsdLuxLightPortal on the prim held by \p schemaObj .
    /// Should be preferred over UsdLuxLightPortal(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdLuxLightPortal(const UsdSchemaBase& schemaObj) : UsdGeomXformable(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdLuxLightPortal()
    {
    }

    static const TfToken _GetStaticTfType();
};

inline const TfToken UsdLuxLightPortal::_GetStaticTfType()
{
    return TfToken("UsdLuxLightPortal");
}


}

// ===================================================================== //
// Feel free to add custom code below this line. It will be preserved by
// the code generator.
//
// Just remember to wrap code in the appropriate delimiters:
// 'namespace usdrt {', '}'.
// ===================================================================== //
// --(BEGIN CUSTOM CODE)--
