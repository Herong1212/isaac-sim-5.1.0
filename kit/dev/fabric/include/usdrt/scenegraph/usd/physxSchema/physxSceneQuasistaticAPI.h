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

/// @file physxSchema/physxSceneQuasistaticAPI.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/apiSchemaBase.h"
#include "usdrt/scenegraph/usd/physxSchema/tokens.h"

// clang-format off
/* Extra Includes
// USDRT NOTE: Use custom includes below instead to allow for
// implementation differences in the custom code. This section comes
// from the pxr schema.usda files which we may not have in usdrt.
//#include "usdrt/scenegraph/usd/ usd/collectionAPI.h" */
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
// PHYSXSCENEQUASISTATICAPI                                                    //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxSceneQuasistaticAPI
///
/// PhysxSceneQuasistaticAPI defines quasistatic mode for simulation.
/// The API must be applied to a UsdPhysics.PhysicsScene prim.
///
///
/// In this mode actors are simulated/moved by the physics engine by obeying
/// external forces and constraints as usual, but they do not accumulate momentum.
/// So that e.g. falling due to gravity is with constant speed, and motion stops
/// as soon as external forces cease to apply. There is no conservation of momentum.
///
///
/// By default all actors belonging to the scene have this behavior unless the collection
/// does have the includes defined, then the collection definition does have a precendence.
///

class PhysxSchemaPhysxSceneQuasistaticAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxSceneQuasistaticAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxSceneQuasistaticAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxSceneQuasistaticAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxSceneQuasistaticAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxSceneQuasistaticAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxSceneQuasistaticAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxSceneQuasistaticAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxSceneQuasistaticAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxSceneQuasistaticAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxSceneQuasistaticAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxSceneQuasistaticAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxSceneQuasistaticAPI>())
        {
            return PhysxSchemaPhysxSceneQuasistaticAPI(prim);
        }
        return PhysxSchemaPhysxSceneQuasistaticAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // ENABLEQUASISTATIC
    // --------------------------------------------------------------------- //
    /// Whether the actors should behave quasistatic or not.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxSceneQuasistatic:enableQuasistatic = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetEnableQuasistaticAttr() const;

    /// See GetEnableQuasistaticAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateEnableQuasistaticAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxSceneQuasistaticAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxSceneQuasistaticAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxSceneQuasistaticAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxSceneQuasistaticAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxSceneQuasistaticAPI::GetEnableQuasistaticAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSceneQuasistaticEnableQuasistatic));
}

inline UsdAttribute PhysxSchemaPhysxSceneQuasistaticAPI::CreateEnableQuasistaticAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSceneQuasistaticEnableQuasistatic),
                                     SdfValueTypeNames->Bool,
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
