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

/// @file physxSchema/physxCameraAPI.h

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
// PHYSXCAMERAAPI                                                              //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxCameraAPI
///
/// PhysX camera.

class PhysxSchemaPhysxCameraAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxCameraAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxCameraAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxCameraAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxCameraAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxCameraAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxCameraAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxCameraAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxCameraAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxCameraAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxCameraAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxCameraAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxCameraAPI>())
        {
            return PhysxSchemaPhysxCameraAPI(prim);
        }
        return PhysxSchemaPhysxCameraAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // ALWAYSUPDATEENABLED
    // --------------------------------------------------------------------- //
    /// When enabled, always update this camera whether it is the active camera or not. This prevents cameras from
    /// slewing into position when switching to a new active camera. When disabled, only the active camera is updated,
    /// saving time.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool alwaysUpdateEnabled = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetAlwaysUpdateEnabledAttr() const;

    /// See GetAlwaysUpdateEnabledAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateAlwaysUpdateEnabledAttr() const;

public:
    // --------------------------------------------------------------------- //
    // PHYSXCAMERASUBJECT
    // --------------------------------------------------------------------- //
    /// Reference to the subject this camera is to track.
    ///
    UsdRelationship GetPhysxCameraSubjectRel() const;

    /// See GetPhysxCameraSubjectRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreatePhysxCameraSubjectRel() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxCameraAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxCameraAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxCameraAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxCameraAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxCameraAPI::GetAlwaysUpdateEnabledAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->alwaysUpdateEnabled));
}

inline UsdAttribute PhysxSchemaPhysxCameraAPI::CreateAlwaysUpdateEnabledAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->alwaysUpdateEnabled), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}


inline UsdRelationship PhysxSchemaPhysxCameraAPI::GetPhysxCameraSubjectRel() const
{
    return GetPrim().GetRelationship(PhysxSchemaTokens->physxCameraSubject);
}

inline UsdRelationship PhysxSchemaPhysxCameraAPI::CreatePhysxCameraSubjectRel() const
{
    return GetPrim().CreateRelationship(PhysxSchemaTokens->physxCameraSubject,
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
