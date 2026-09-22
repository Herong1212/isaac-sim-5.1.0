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

/// @file physxSchema/physxParticleSmoothingAPI.h

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
// PHYSXPARTICLESMOOTHINGAPI                                                   //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxParticleSmoothingAPI
///
/// WARNING: This is a draft API; the design is not fixed and may change in the future.
/// Applied to a PhysxParticleSystem. Controls smoothing of simulated particle positions in a post-processing step.
/// The smoothing post-processing only affects the rendering output including isosurface generation, and not the
/// particle dynamics. Affects point based primitives with PhysxParticleSetAPI, which are defined as fluid.

class PhysxSchemaPhysxParticleSmoothingAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxParticleSmoothingAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxParticleSmoothingAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxParticleSmoothingAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxParticleSmoothingAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxParticleSmoothingAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxParticleSmoothingAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxParticleSmoothingAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxParticleSmoothingAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxParticleSmoothingAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxParticleSmoothingAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxParticleSmoothingAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxParticleSmoothingAPI>())
        {
            return PhysxSchemaPhysxParticleSmoothingAPI(prim);
        }
        return PhysxSchemaPhysxParticleSmoothingAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // PARTICLESMOOTHINGENABLED
    // --------------------------------------------------------------------- //
    /// Enable or disable smoothingStrength of particle positions.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxParticleSmoothing:particleSmoothingEnabled = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetParticleSmoothingEnabledAttr() const;

    /// See GetParticleSmoothingEnabledAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateParticleSmoothingEnabledAttr() const;

public:
    // --------------------------------------------------------------------- //
    // STRENGTH
    // --------------------------------------------------------------------- //
    /// Smoothing coefficient for particle positions.
    /// Range: [0, 1]
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxParticleSmoothing:strength = 0.8` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetStrengthAttr() const;

    /// See GetStrengthAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateStrengthAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxParticleSmoothingAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxParticleSmoothingAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxParticleSmoothingAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxParticleSmoothingAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxParticleSmoothingAPI::GetParticleSmoothingEnabledAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxParticleSmoothingParticleSmoothingEnabled));
}

inline UsdAttribute PhysxSchemaPhysxParticleSmoothingAPI::CreateParticleSmoothingEnabledAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxParticleSmoothingParticleSmoothingEnabled),
                                     SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleSmoothingAPI::GetStrengthAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxParticleSmoothingStrength));
}

inline UsdAttribute PhysxSchemaPhysxParticleSmoothingAPI::CreateStrengthAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxParticleSmoothingStrength), SdfValueTypeNames->Float,
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
