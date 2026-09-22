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

/// @file physxSchema/physxParticleAPI.h

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
// PHYSXPARTICLEAPI                                                            //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxParticleAPI
///
/// WARNING: This is a draft API; the design is not fixed and may change in the future.
/// Do not apply. Provides parameters shared among particle objects.

class PhysxSchemaPhysxParticleAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxParticleAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxParticleAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxParticleAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxParticleAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxParticleAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxParticleAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxParticleAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxParticleAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxParticleAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxParticleAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxParticleAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxParticleAPI>())
        {
            return PhysxSchemaPhysxParticleAPI(prim);
        }
        return PhysxSchemaPhysxParticleAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // PARTICLEENABLED
    // --------------------------------------------------------------------- //
    /// Enable or disable the particle object.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxParticle:particleEnabled = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetParticleEnabledAttr() const;

    /// See GetParticleEnabledAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateParticleEnabledAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SELFCOLLISION
    // --------------------------------------------------------------------- //
    /// Enables self-collision of the particles or of the particle object.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxParticle:selfCollision = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetSelfCollisionAttr() const;

    /// See GetSelfCollisionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSelfCollisionAttr() const;

public:
    // --------------------------------------------------------------------- //
    // PARTICLEGROUP
    // --------------------------------------------------------------------- //
    /// Group Id of the particles. Particles / objects in different groups in the same system collide with each other.
    /// Within the same group in the same system, the collision behavior is controlled by the selfCollision parameter.
    /// Range: [0, 2^20)
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int physxParticle:particleGroup = 0` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |

    UsdAttribute GetParticleGroupAttr() const;

    /// See GetParticleGroupAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateParticleGroupAttr() const;

public:
    // --------------------------------------------------------------------- //
    // PARTICLESYSTEM
    // --------------------------------------------------------------------- //
    /// Single particle system that the particle-based object belongs to.
    ///
    UsdRelationship GetParticleSystemRel() const;

    /// See GetParticleSystemRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateParticleSystemRel() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxParticleAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxParticleAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxParticleAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxParticleAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxParticleAPI::GetParticleEnabledAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxParticleParticleEnabled));
}

inline UsdAttribute PhysxSchemaPhysxParticleAPI::CreateParticleEnabledAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxParticleParticleEnabled), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleAPI::GetSelfCollisionAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxParticleSelfCollision));
}

inline UsdAttribute PhysxSchemaPhysxParticleAPI::CreateSelfCollisionAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxParticleSelfCollision), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleAPI::GetParticleGroupAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxParticleParticleGroup));
}

inline UsdAttribute PhysxSchemaPhysxParticleAPI::CreateParticleGroupAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxParticleParticleGroup), SdfValueTypeNames->Int,
                                     /* custom = */ false);
}


inline UsdRelationship PhysxSchemaPhysxParticleAPI::GetParticleSystemRel() const
{
    return GetPrim().GetRelationship(PhysxSchemaTokens->physxParticleParticleSystem);
}

inline UsdRelationship PhysxSchemaPhysxParticleAPI::CreateParticleSystemRel() const
{
    return GetPrim().CreateRelationship(PhysxSchemaTokens->physxParticleParticleSystem,
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
