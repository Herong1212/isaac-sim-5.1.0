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

/// @file physxSchema/physxDiffuseParticlesAPI.h

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
// PHYSXDIFFUSEPARTICLESAPI                                                    //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxDiffuseParticlesAPI
///
/// WARNING: This is a draft API; the design is not fixed and may change in the future.
/// Applied to a UsdGeomPoints or UsdGeomPointInstancer primitive with PhysxParticleSetAPI.
/// Defines settings that the particle simulation uses to spawn diffuse particles.
/// The diffuse particles are a render-only effect and do not affect the particle dynamics.

class PhysxSchemaPhysxDiffuseParticlesAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxDiffuseParticlesAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxDiffuseParticlesAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxDiffuseParticlesAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxDiffuseParticlesAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxDiffuseParticlesAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxDiffuseParticlesAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxDiffuseParticlesAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxDiffuseParticlesAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxDiffuseParticlesAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxDiffuseParticlesAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxDiffuseParticlesAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxDiffuseParticlesAPI>())
        {
            return PhysxSchemaPhysxDiffuseParticlesAPI(prim);
        }
        return PhysxSchemaPhysxDiffuseParticlesAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // DIFFUSEPARTICLESENABLED
    // --------------------------------------------------------------------- //
    /// Enable or disable the creation of diffuse particles.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxDiffuseParticles:diffuseParticlesEnabled = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetDiffuseParticlesEnabledAttr() const;

    /// See GetDiffuseParticlesEnabledAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDiffuseParticlesEnabledAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MAXDIFFUSEPARTICLEMULTIPLIER
    // --------------------------------------------------------------------- //
    /// Maximum number of diffuse particles that can be present in the simulation relative to the number
    /// of non-diffuse particles.
    /// Range: [0.0, inf)
    /// Default value -inf means default is picked by the simulation.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform float physxDiffuseParticles:maxDiffuseParticleMultiplier = -inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetMaxDiffuseParticleMultiplierAttr() const;

    /// See GetMaxDiffuseParticleMultiplierAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaxDiffuseParticleMultiplierAttr() const;

public:
    // --------------------------------------------------------------------- //
    // THRESHOLD
    // --------------------------------------------------------------------- //
    /// Kinetic energy threshold a particle must reach to spawn a diffuse particle.
    /// Range: [0, inf)
    /// Units: energy = mass * distance * distance / seconds / seconds
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDiffuseParticles:threshold = 0.01` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetThresholdAttr() const;

    /// See GetThresholdAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateThresholdAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LIFETIME
    // --------------------------------------------------------------------- //
    /// Lifetime of a spawned particle before it is removed again.
    /// Range: [0, inf)
    /// Units: seconds
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDiffuseParticles:lifetime = 5` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetLifetimeAttr() const;

    /// See GetLifetimeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLifetimeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // AIRDRAG
    // --------------------------------------------------------------------- //
    /// Air drag force factor for spray particles.
    /// Range: [0, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDiffuseParticles:airDrag = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetAirDragAttr() const;

    /// See GetAirDragAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateAirDragAttr() const;

public:
    // --------------------------------------------------------------------- //
    // BUBBLEDRAG
    // --------------------------------------------------------------------- //
    /// Fluid drag force factor for bubble particles.
    /// Range: [0, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDiffuseParticles:bubbleDrag = 0.5` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetBubbleDragAttr() const;

    /// See GetBubbleDragAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateBubbleDragAttr() const;

public:
    // --------------------------------------------------------------------- //
    // BUOYANCY
    // --------------------------------------------------------------------- //
    /// Buoyancy force factor for bubble particles.
    /// Range: [0, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDiffuseParticles:buoyancy = 0.8` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetBuoyancyAttr() const;

    /// See GetBuoyancyAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateBuoyancyAttr() const;

public:
    // --------------------------------------------------------------------- //
    // KINETICENERGYWEIGHT
    // --------------------------------------------------------------------- //
    /// Contribution from kinetic energy when deciding diffuse particle creation.
    /// Range: [0, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDiffuseParticles:kineticEnergyWeight = 0.01` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetKineticEnergyWeightAttr() const;

    /// See GetKineticEnergyWeightAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateKineticEnergyWeightAttr() const;

public:
    // --------------------------------------------------------------------- //
    // PRESSUREWEIGHT
    // --------------------------------------------------------------------- //
    /// Contribution from pressure when deciding diffuse particle creation.
    /// Range: [0, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDiffuseParticles:pressureWeight = 1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetPressureWeightAttr() const;

    /// See GetPressureWeightAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreatePressureWeightAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DIVERGENCEWEIGHT
    // --------------------------------------------------------------------- //
    /// Contribution from divergence when deciding diffuse particle creation.
    /// Range: [0, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDiffuseParticles:divergenceWeight = 5` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetDivergenceWeightAttr() const;

    /// See GetDivergenceWeightAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDivergenceWeightAttr() const;

public:
    // --------------------------------------------------------------------- //
    // COLLISIONDECAY
    // --------------------------------------------------------------------- //
    /// Decay factor of diffuse particles' lifetime after they collide with shapes. 0 == lifetime remains unchanged, 1
    /// == particle disappears immediately. Range: [0, 1] Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDiffuseParticles:collisionDecay = 0.5` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetCollisionDecayAttr() const;

    /// See GetCollisionDecayAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCollisionDecayAttr() const;

public:
    // --------------------------------------------------------------------- //
    // USEACCURATEVELOCITY
    // --------------------------------------------------------------------- //
    /// Enables accurate particle velocity estimation.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxDiffuseParticles:useAccurateVelocity = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetUseAccurateVelocityAttr() const;

    /// See GetUseAccurateVelocityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateUseAccurateVelocityAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxDiffuseParticlesAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxDiffuseParticlesAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxDiffuseParticlesAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxDiffuseParticlesAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxDiffuseParticlesAPI::GetDiffuseParticlesEnabledAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDiffuseParticlesDiffuseParticlesEnabled));
}

inline UsdAttribute PhysxSchemaPhysxDiffuseParticlesAPI::CreateDiffuseParticlesEnabledAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDiffuseParticlesDiffuseParticlesEnabled),
                                     SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDiffuseParticlesAPI::GetMaxDiffuseParticleMultiplierAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDiffuseParticlesMaxDiffuseParticleMultiplier));
}

inline UsdAttribute PhysxSchemaPhysxDiffuseParticlesAPI::CreateMaxDiffuseParticleMultiplierAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDiffuseParticlesMaxDiffuseParticleMultiplier),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDiffuseParticlesAPI::GetThresholdAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDiffuseParticlesThreshold));
}

inline UsdAttribute PhysxSchemaPhysxDiffuseParticlesAPI::CreateThresholdAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDiffuseParticlesThreshold), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDiffuseParticlesAPI::GetLifetimeAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDiffuseParticlesLifetime));
}

inline UsdAttribute PhysxSchemaPhysxDiffuseParticlesAPI::CreateLifetimeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDiffuseParticlesLifetime), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDiffuseParticlesAPI::GetAirDragAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDiffuseParticlesAirDrag));
}

inline UsdAttribute PhysxSchemaPhysxDiffuseParticlesAPI::CreateAirDragAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDiffuseParticlesAirDrag), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDiffuseParticlesAPI::GetBubbleDragAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDiffuseParticlesBubbleDrag));
}

inline UsdAttribute PhysxSchemaPhysxDiffuseParticlesAPI::CreateBubbleDragAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDiffuseParticlesBubbleDrag),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDiffuseParticlesAPI::GetBuoyancyAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDiffuseParticlesBuoyancy));
}

inline UsdAttribute PhysxSchemaPhysxDiffuseParticlesAPI::CreateBuoyancyAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDiffuseParticlesBuoyancy), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDiffuseParticlesAPI::GetKineticEnergyWeightAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDiffuseParticlesKineticEnergyWeight));
}

inline UsdAttribute PhysxSchemaPhysxDiffuseParticlesAPI::CreateKineticEnergyWeightAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDiffuseParticlesKineticEnergyWeight),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDiffuseParticlesAPI::GetPressureWeightAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDiffuseParticlesPressureWeight));
}

inline UsdAttribute PhysxSchemaPhysxDiffuseParticlesAPI::CreatePressureWeightAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDiffuseParticlesPressureWeight),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDiffuseParticlesAPI::GetDivergenceWeightAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDiffuseParticlesDivergenceWeight));
}

inline UsdAttribute PhysxSchemaPhysxDiffuseParticlesAPI::CreateDivergenceWeightAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDiffuseParticlesDivergenceWeight),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDiffuseParticlesAPI::GetCollisionDecayAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDiffuseParticlesCollisionDecay));
}

inline UsdAttribute PhysxSchemaPhysxDiffuseParticlesAPI::CreateCollisionDecayAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDiffuseParticlesCollisionDecay),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDiffuseParticlesAPI::GetUseAccurateVelocityAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDiffuseParticlesUseAccurateVelocity));
}

inline UsdAttribute PhysxSchemaPhysxDiffuseParticlesAPI::CreateUseAccurateVelocityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDiffuseParticlesUseAccurateVelocity),
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
