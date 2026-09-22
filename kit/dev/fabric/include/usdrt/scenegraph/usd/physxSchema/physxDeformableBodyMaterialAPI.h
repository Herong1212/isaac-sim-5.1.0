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

/// @file physxSchema/physxDeformableBodyMaterialAPI.h

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
// PHYSXDEFORMABLEBODYMATERIALAPI                                              //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxDeformableBodyMaterialAPI
///
/// Applied to USD Material. Defines material properties for deformable bodies.

class PhysxSchemaPhysxDeformableBodyMaterialAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxDeformableBodyMaterialAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxDeformableBodyMaterialAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxDeformableBodyMaterialAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxDeformableBodyMaterialAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxDeformableBodyMaterialAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxDeformableBodyMaterialAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxDeformableBodyMaterialAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxDeformableBodyMaterialAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxDeformableBodyMaterialAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxDeformableBodyMaterialAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxDeformableBodyMaterialAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxDeformableBodyMaterialAPI>())
        {
            return PhysxSchemaPhysxDeformableBodyMaterialAPI(prim);
        }
        return PhysxSchemaPhysxDeformableBodyMaterialAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // DENSITY
    // --------------------------------------------------------------------- //
    /// Material density. If set to 0.0, the simulation determines a default density. A density or mass set with a
    /// PhysicsMassAPI overrides the material density. Range: [0, inf) Units: mass / distance / distance / distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDeformableBodyMaterial:density = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetDensityAttr() const;

    /// See GetDensityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDensityAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ELASTICITYDAMPING
    // --------------------------------------------------------------------- //
    /// Material damping parameter. Use values much smaller than one for good results.
    /// Range: [0, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDeformableBodyMaterial:elasticityDamping = 0.005` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetElasticityDampingAttr() const;

    /// See GetElasticityDampingAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateElasticityDampingAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DYNAMICFRICTION
    // --------------------------------------------------------------------- //
    /// Dynamic friction coefficient.
    /// Range: [0, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDeformableBodyMaterial:dynamicFriction = 0.25` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetDynamicFrictionAttr() const;

    /// See GetDynamicFrictionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDynamicFrictionAttr() const;

public:
    // --------------------------------------------------------------------- //
    // YOUNGSMODULUS
    // --------------------------------------------------------------------- //
    /// Young's modulus, i.e. the tensile stiffness of the material.
    /// Range: [0, inf)
    /// Units: force / area = mass/distance/seconds/seconds
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDeformableBodyMaterial:youngsModulus = 50000000` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetYoungsModulusAttr() const;

    /// See GetYoungsModulusAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateYoungsModulusAttr() const;

public:
    // --------------------------------------------------------------------- //
    // POISSONSRATIO
    // --------------------------------------------------------------------- //
    /// Poissons's ratio which defines the material's volume preservation under stress.
    /// Range: [0, 0.5]
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDeformableBodyMaterial:poissonsRatio = 0.45` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetPoissonsRatioAttr() const;

    /// See GetPoissonsRatioAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreatePoissonsRatioAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DAMPINGSCALE
    // --------------------------------------------------------------------- //
    /// Experimental parameter. Try a high damping together with a scale of zero for a water-bed like effect.
    /// Range: [0, 1]
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDeformableBodyMaterial:dampingScale = 1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetDampingScaleAttr() const;

    /// See GetDampingScaleAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDampingScaleAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxDeformableBodyMaterialAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxDeformableBodyMaterialAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxDeformableBodyMaterialAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxDeformableBodyMaterialAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxDeformableBodyMaterialAPI::GetDensityAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableBodyMaterialDensity));
}

inline UsdAttribute PhysxSchemaPhysxDeformableBodyMaterialAPI::CreateDensityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableBodyMaterialDensity),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDeformableBodyMaterialAPI::GetElasticityDampingAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableBodyMaterialElasticityDamping));
}

inline UsdAttribute PhysxSchemaPhysxDeformableBodyMaterialAPI::CreateElasticityDampingAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableBodyMaterialElasticityDamping),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDeformableBodyMaterialAPI::GetDynamicFrictionAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableBodyMaterialDynamicFriction));
}

inline UsdAttribute PhysxSchemaPhysxDeformableBodyMaterialAPI::CreateDynamicFrictionAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableBodyMaterialDynamicFriction),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDeformableBodyMaterialAPI::GetYoungsModulusAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableBodyMaterialYoungsModulus));
}

inline UsdAttribute PhysxSchemaPhysxDeformableBodyMaterialAPI::CreateYoungsModulusAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableBodyMaterialYoungsModulus),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDeformableBodyMaterialAPI::GetPoissonsRatioAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableBodyMaterialPoissonsRatio));
}

inline UsdAttribute PhysxSchemaPhysxDeformableBodyMaterialAPI::CreatePoissonsRatioAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableBodyMaterialPoissonsRatio),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDeformableBodyMaterialAPI::GetDampingScaleAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableBodyMaterialDampingScale));
}

inline UsdAttribute PhysxSchemaPhysxDeformableBodyMaterialAPI::CreateDampingScaleAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableBodyMaterialDampingScale),
                                     SdfValueTypeNames->Float,
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
