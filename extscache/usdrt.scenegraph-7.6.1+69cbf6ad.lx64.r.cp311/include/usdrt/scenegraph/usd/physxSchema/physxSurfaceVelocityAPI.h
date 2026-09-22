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

/// @file physxSchema/physxSurfaceVelocityAPI.h

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
// PHYSXSURFACEVELOCITYAPI                                                     //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxSurfaceVelocityAPI
///
/// PhysxSurfaceVelocityAPI enables surface velocity simulation
/// that injects velocity to the solver through internal contact modify
/// callback. Surface velocity can be used typically for conveyer belt
/// simulation. It must be applied to a prim with UsdPhysicsRigidBodyAPI.
///

class PhysxSchemaPhysxSurfaceVelocityAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxSurfaceVelocityAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxSurfaceVelocityAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxSurfaceVelocityAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxSurfaceVelocityAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxSurfaceVelocityAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxSurfaceVelocityAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxSurfaceVelocityAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxSurfaceVelocityAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxSurfaceVelocityAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxSurfaceVelocityAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxSurfaceVelocityAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxSurfaceVelocityAPI>())
        {
            return PhysxSchemaPhysxSurfaceVelocityAPI(prim);
        }
        return PhysxSchemaPhysxSurfaceVelocityAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // SURFACEVELOCITYENABLED
    // --------------------------------------------------------------------- //
    /// Whether surface velocity is enabled or not.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxSurfaceVelocity:surfaceVelocityEnabled = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetSurfaceVelocityEnabledAttr() const;

    /// See GetSurfaceVelocityEnabledAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSurfaceVelocityEnabledAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SURFACEVELOCITYLOCALSPACE
    // --------------------------------------------------------------------- //
    /// Whether surface velocity is defined in body local space or in world space.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxSurfaceVelocity:surfaceVelocityLocalSpace = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetSurfaceVelocityLocalSpaceAttr() const;

    /// See GetSurfaceVelocityLocalSpaceAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSurfaceVelocityLocalSpaceAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SURFACEVELOCITY
    // --------------------------------------------------------------------- //
    /// Surface linear velocity applied through contact modify callback.
    /// Units: distance/second.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `vector3f physxSurfaceVelocity:surfaceVelocity = (0, 0, 0)` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Vector3f |

    UsdAttribute GetSurfaceVelocityAttr() const;

    /// See GetSurfaceVelocityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSurfaceVelocityAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SURFACEANGULARVELOCITY
    // --------------------------------------------------------------------- //
    /// Surface angular velocity applied through contact modify callback.
    /// Units: degrees/second.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `vector3f physxSurfaceVelocity:surfaceAngularVelocity = (0, 0, 0)` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Vector3f |

    UsdAttribute GetSurfaceAngularVelocityAttr() const;

    /// See GetSurfaceAngularVelocityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSurfaceAngularVelocityAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxSurfaceVelocityAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxSurfaceVelocityAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxSurfaceVelocityAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxSurfaceVelocityAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxSurfaceVelocityAPI::GetSurfaceVelocityEnabledAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSurfaceVelocitySurfaceVelocityEnabled));
}

inline UsdAttribute PhysxSchemaPhysxSurfaceVelocityAPI::CreateSurfaceVelocityEnabledAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSurfaceVelocitySurfaceVelocityEnabled),
                                     SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSurfaceVelocityAPI::GetSurfaceVelocityLocalSpaceAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSurfaceVelocitySurfaceVelocityLocalSpace));
}

inline UsdAttribute PhysxSchemaPhysxSurfaceVelocityAPI::CreateSurfaceVelocityLocalSpaceAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSurfaceVelocitySurfaceVelocityLocalSpace),
                                     SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSurfaceVelocityAPI::GetSurfaceVelocityAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSurfaceVelocitySurfaceVelocity));
}

inline UsdAttribute PhysxSchemaPhysxSurfaceVelocityAPI::CreateSurfaceVelocityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSurfaceVelocitySurfaceVelocity),
                                     SdfValueTypeNames->Vector3f,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSurfaceVelocityAPI::GetSurfaceAngularVelocityAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSurfaceVelocitySurfaceAngularVelocity));
}

inline UsdAttribute PhysxSchemaPhysxSurfaceVelocityAPI::CreateSurfaceAngularVelocityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSurfaceVelocitySurfaceAngularVelocity),
                                     SdfValueTypeNames->Vector3f,
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
