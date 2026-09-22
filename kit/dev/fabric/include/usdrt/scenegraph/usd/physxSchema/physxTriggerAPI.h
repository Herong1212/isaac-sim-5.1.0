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

/// @file physxSchema/physxTriggerAPI.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/apiSchemaBase.h"
#include "usdrt/scenegraph/usd/physxSchema/tokens.h"


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
// PHYSXTRIGGERAPI                                                             //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxTriggerAPI
///
/// PhysX trigger
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref PhysxSchemaTokens.
/// So to set an attribute to the value "rightHanded", use PhysxSchemaTokens->rightHanded
/// as the value.

class PhysxSchemaPhysxTriggerAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxTriggerAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxTriggerAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxTriggerAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxTriggerAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxTriggerAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxTriggerAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxTriggerAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxTriggerAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxTriggerAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxTriggerAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxTriggerAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxTriggerAPI>())
        {
            return PhysxSchemaPhysxTriggerAPI(prim);
        }
        return PhysxSchemaPhysxTriggerAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // ENTERSCRIPTTYPE
    // --------------------------------------------------------------------- //
    /// Enter script type. Script file tries to find a file on disc and execute. Script buffer does execute the provided
    /// script string directly.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token physxTrigger:enterScriptType = "scriptFile"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref PhysxSchemaTokens "Allowed Values" | scriptFile, scriptBuffer |

    UsdAttribute GetEnterScriptTypeAttr() const;

    /// See GetEnterScriptTypeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateEnterScriptTypeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LEAVESCRIPTTYPE
    // --------------------------------------------------------------------- //
    /// Leave script type. Script file tries to find a file on disc and execute. Script buffer does execute the provided
    /// script string directly.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token physxTrigger:leaveScriptType = "scriptFile"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref PhysxSchemaTokens "Allowed Values" | scriptFile, scriptBuffer |

    UsdAttribute GetLeaveScriptTypeAttr() const;

    /// See GetLeaveScriptTypeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLeaveScriptTypeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ONENTERSCRIPT
    // --------------------------------------------------------------------- //
    /// Enter script.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token physxTrigger:onEnterScript` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetOnEnterScriptAttr() const;

    /// See GetOnEnterScriptAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateOnEnterScriptAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ONLEAVESCRIPT
    // --------------------------------------------------------------------- //
    /// Leave script.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token physxTrigger:onLeaveScript` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetOnLeaveScriptAttr() const;

    /// See GetOnLeaveScriptAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateOnLeaveScriptAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxTriggerAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxTriggerAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxTriggerAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxTriggerAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxTriggerAPI::GetEnterScriptTypeAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxTriggerEnterScriptType));
}

inline UsdAttribute PhysxSchemaPhysxTriggerAPI::CreateEnterScriptTypeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxTriggerEnterScriptType), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxTriggerAPI::GetLeaveScriptTypeAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxTriggerLeaveScriptType));
}

inline UsdAttribute PhysxSchemaPhysxTriggerAPI::CreateLeaveScriptTypeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxTriggerLeaveScriptType), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxTriggerAPI::GetOnEnterScriptAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxTriggerOnEnterScript));
}

inline UsdAttribute PhysxSchemaPhysxTriggerAPI::CreateOnEnterScriptAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxTriggerOnEnterScript), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxTriggerAPI::GetOnLeaveScriptAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxTriggerOnLeaveScript));
}

inline UsdAttribute PhysxSchemaPhysxTriggerAPI::CreateOnLeaveScriptAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxTriggerOnLeaveScript), SdfValueTypeNames->Token,
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
