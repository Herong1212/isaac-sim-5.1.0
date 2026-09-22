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

/// @file physxSchema/physxArticulationAPI.h

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
// PHYSXARTICULATIONAPI                                                        //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxArticulationAPI
///
/// PhysX articulation extended parameters

class PhysxSchemaPhysxArticulationAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxArticulationAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxArticulationAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxArticulationAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxArticulationAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxArticulationAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxArticulationAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxArticulationAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxArticulationAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxArticulationAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxArticulationAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxArticulationAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxArticulationAPI>())
        {
            return PhysxSchemaPhysxArticulationAPI(prim);
        }
        return PhysxSchemaPhysxArticulationAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // ARTICULATIONENABLED
    // --------------------------------------------------------------------- //
    /// Boolean defining whether articulation is enabled or disabled.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxArticulation:articulationEnabled = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetArticulationEnabledAttr() const;

    /// See GetArticulationEnabledAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateArticulationEnabledAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SOLVERPOSITIONITERATIONCOUNT
    // --------------------------------------------------------------------- //
    /// Solver position iteration counts for the body. Allowed range [1, 255].
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int physxArticulation:solverPositionIterationCount = 32` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |

    UsdAttribute GetSolverPositionIterationCountAttr() const;

    /// See GetSolverPositionIterationCountAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSolverPositionIterationCountAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SOLVERVELOCITYITERATIONCOUNT
    // --------------------------------------------------------------------- //
    /// Solver velocity iteration counts for the body. Allowed range [0, 255].
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int physxArticulation:solverVelocityIterationCount = 1` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |

    UsdAttribute GetSolverVelocityIterationCountAttr() const;

    /// See GetSolverVelocityIterationCountAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSolverVelocityIterationCountAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SLEEPTHRESHOLD
    // --------------------------------------------------------------------- //
    /// Mass-normalized kinetic energy threshold below which the articulation may go to sleep.
    /// Range: [0, inf)
    /// Default: 0.00005 * tolerancesSpeed * tolerancesSpeed
    /// Units: distance * distance / seconds / seconds
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxArticulation:sleepThreshold = 0.00005` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSleepThresholdAttr() const;

    /// See GetSleepThresholdAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSleepThresholdAttr() const;

public:
    // --------------------------------------------------------------------- //
    // STABILIZATIONTHRESHOLD
    // --------------------------------------------------------------------- //
    /// The mass-normalized kinetic energy threshold below which the articulation may participate in stabilization.
    /// Range: [0, inf)
    /// Default: 0.00001 * tolerancesSpeed * tolerancesSpeed
    /// Units: distance * distance / seconds / seconds
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxArticulation:stabilizationThreshold = 0.00001` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetStabilizationThresholdAttr() const;

    /// See GetStabilizationThresholdAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateStabilizationThresholdAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ENABLEDSELFCOLLISIONS
    // --------------------------------------------------------------------- //
    /// Boolean defining whether self collisions should be enabled or disabled.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxArticulation:enabledSelfCollisions = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetEnabledSelfCollisionsAttr() const;

    /// See GetEnabledSelfCollisionsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateEnabledSelfCollisionsAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxArticulationAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxArticulationAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxArticulationAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxArticulationAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxArticulationAPI::GetArticulationEnabledAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxArticulationArticulationEnabled));
}

inline UsdAttribute PhysxSchemaPhysxArticulationAPI::CreateArticulationEnabledAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxArticulationArticulationEnabled),
                                     SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxArticulationAPI::GetSolverPositionIterationCountAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxArticulationSolverPositionIterationCount));
}

inline UsdAttribute PhysxSchemaPhysxArticulationAPI::CreateSolverPositionIterationCountAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxArticulationSolverPositionIterationCount),
                                     SdfValueTypeNames->Int,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxArticulationAPI::GetSolverVelocityIterationCountAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxArticulationSolverVelocityIterationCount));
}

inline UsdAttribute PhysxSchemaPhysxArticulationAPI::CreateSolverVelocityIterationCountAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxArticulationSolverVelocityIterationCount),
                                     SdfValueTypeNames->Int,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxArticulationAPI::GetSleepThresholdAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxArticulationSleepThreshold));
}

inline UsdAttribute PhysxSchemaPhysxArticulationAPI::CreateSleepThresholdAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxArticulationSleepThreshold),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxArticulationAPI::GetStabilizationThresholdAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxArticulationStabilizationThreshold));
}

inline UsdAttribute PhysxSchemaPhysxArticulationAPI::CreateStabilizationThresholdAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxArticulationStabilizationThreshold),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxArticulationAPI::GetEnabledSelfCollisionsAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxArticulationEnabledSelfCollisions));
}

inline UsdAttribute PhysxSchemaPhysxArticulationAPI::CreateEnabledSelfCollisionsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxArticulationEnabledSelfCollisions),
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
