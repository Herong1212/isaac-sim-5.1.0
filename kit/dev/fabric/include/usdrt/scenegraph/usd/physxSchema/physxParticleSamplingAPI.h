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

/// @file physxSchema/physxParticleSamplingAPI.h

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
// PHYSXPARTICLESAMPLINGAPI                                                    //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxParticleSamplingAPI
///
/// WARNING: This is a draft API; the design is not fixed and may change in the future.
/// Applied to a UsdGeomMesh which is Poisson-sampled to generate particles in the particles relationship.

class PhysxSchemaPhysxParticleSamplingAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxParticleSamplingAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxParticleSamplingAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxParticleSamplingAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxParticleSamplingAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxParticleSamplingAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxParticleSamplingAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxParticleSamplingAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxParticleSamplingAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxParticleSamplingAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxParticleSamplingAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxParticleSamplingAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxParticleSamplingAPI>())
        {
            return PhysxSchemaPhysxParticleSamplingAPI(prim);
        }
        return PhysxSchemaPhysxParticleSamplingAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // SAMPLINGDISTANCE
    // --------------------------------------------------------------------- //
    /// The distance between the sampled positions. In general, choose a value larger than the corresponding particle
    /// rest offset. Default value zero means that a suitable value is auto-determined. Range: [0, inf) Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxParticleSampling:samplingDistance = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSamplingDistanceAttr() const;

    /// See GetSamplingDistanceAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSamplingDistanceAttr() const;

public:
    // --------------------------------------------------------------------- //
    // VOLUME
    // --------------------------------------------------------------------- //
    /// Whether to sample points inside the mesh or not.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxParticleSampling:volume = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetVolumeAttr() const;

    /// See GetVolumeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateVolumeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MAXSAMPLES
    // --------------------------------------------------------------------- //
    /// Approximate upper bound on the number of samples. Zero means unbounded.
    /// Range: [0, inf)
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int physxParticleSampling:maxSamples = 50000` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |

    UsdAttribute GetMaxSamplesAttr() const;

    /// See GetMaxSamplesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaxSamplesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // PARTICLES
    // --------------------------------------------------------------------- //
    /// Relationship to the particle set sampled from the mesh.
    ///
    UsdRelationship GetParticlesRel() const;

    /// See GetParticlesRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateParticlesRel() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxParticleSamplingAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxParticleSamplingAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxParticleSamplingAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxParticleSamplingAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxParticleSamplingAPI::GetSamplingDistanceAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxParticleSamplingSamplingDistance));
}

inline UsdAttribute PhysxSchemaPhysxParticleSamplingAPI::CreateSamplingDistanceAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxParticleSamplingSamplingDistance),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleSamplingAPI::GetVolumeAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxParticleSamplingVolume));
}

inline UsdAttribute PhysxSchemaPhysxParticleSamplingAPI::CreateVolumeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxParticleSamplingVolume), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleSamplingAPI::GetMaxSamplesAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxParticleSamplingMaxSamples));
}

inline UsdAttribute PhysxSchemaPhysxParticleSamplingAPI::CreateMaxSamplesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxParticleSamplingMaxSamples), SdfValueTypeNames->Int,
                                     /* custom = */ false);
}


inline UsdRelationship PhysxSchemaPhysxParticleSamplingAPI::GetParticlesRel() const
{
    return GetPrim().GetRelationship(PhysxSchemaTokens->physxParticleSamplingParticles);
}

inline UsdRelationship PhysxSchemaPhysxParticleSamplingAPI::CreateParticlesRel() const
{
    return GetPrim().CreateRelationship(PhysxSchemaTokens->physxParticleSamplingParticles,
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
