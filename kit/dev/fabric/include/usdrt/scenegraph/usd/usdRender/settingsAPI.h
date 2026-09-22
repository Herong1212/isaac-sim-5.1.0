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

/// \file usdRender/settingsAPI.h

#include "usdrt/scenegraph/usd/usd/apiSchemaBase.h"

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
// RENDERSETTINGSAPI                                                           //
// -------------------------------------------------------------------------- //


/// \class UsdRenderSettingsAPI
///
/// UsdRenderSettingsAPI is a base class for API schemas
/// to encode renderer-specific settings.
///

class UsdRenderSettingsAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// \sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a UsdRenderSettingsAPI on UsdPrim \p prim .
    /// Equivalent to UsdRenderSettingsAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a \em valid \p prim, but will not immediately throw an error for
    /// an invalid \p prim
    explicit UsdRenderSettingsAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a UsdRenderSettingsAPI on the prim held by \p schemaObj .
    /// Should be preferred over UsdRenderSettingsAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdRenderSettingsAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdRenderSettingsAPI()
    {
    }

    static const TfToken _GetStaticTfType();
};

inline const TfToken UsdRenderSettingsAPI::_GetStaticTfType()
{
    return TfToken("UsdRenderSettingsAPI");
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
