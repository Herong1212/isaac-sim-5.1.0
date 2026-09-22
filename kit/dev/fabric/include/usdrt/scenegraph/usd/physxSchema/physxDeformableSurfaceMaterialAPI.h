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

/// @file physxSchema/physxDeformableSurfaceMaterialAPI.h

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
// PHYSXDEFORMABLESURFACEMATERIALAPI                                           //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxDeformableSurfaceMaterialAPI
///
/// WARNING: This is a draft API; the design is not fixed and may change in the future.
/// Applied to USD Material. Defines material properties for deformable surfaces.

class PhysxSchemaPhysxDeformableSurfaceMaterialAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxDeformableSurfaceMaterialAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxDeformableSurfaceMaterialAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxDeformableSurfaceMaterialAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxDeformableSurfaceMaterialAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxDeformableSurfaceMaterialAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxDeformableSurfaceMaterialAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxDeformableSurfaceMaterialAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxDeformableSurfaceMaterialAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxDeformableSurfaceMaterialAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxDeformableSurfaceMaterialAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxDeformableSurfaceMaterialAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxDeformableSurfaceMaterialAPI>())
        {
            return PhysxSchemaPhysxDeformableSurfaceMaterialAPI(prim);
        }
        return PhysxSchemaPhysxDeformableSurfaceMaterialAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // DENSITY
    // --------------------------------------------------------------------- //
    /// Material density. If set to 0.0, the simulation determines a default value.
    /// The mass of deformable surface is computed by density * area * thickness.
    /// A density or mass set with a PhysicsMassAPI overrides the material density.
    /// Range: [0, inf)
    /// Units: mass / distance / distance / distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDeformableSurfaceMaterial:density = 0` |
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
    // DYNAMICFRICTION
    // --------------------------------------------------------------------- //
    /// Dynamic friction coefficient.
    /// Range: [0, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDeformableSurfaceMaterial:dynamicFriction = 0.25` |
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
    /// Used to determine in-plane and bending stiffness.
    /// If set to a negative value, the simulation determines a default value.
    /// Range: [0, inf)
    /// Units: force / area = mass/distance/seconds/seconds
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDeformableSurfaceMaterial:youngsModulus = -inf` |
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
    /// Used to determine in-plane and bending stiffness.
    /// Range: [0, 0.5]
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDeformableSurfaceMaterial:poissonsRatio = 0` |
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
    // THICKNESS
    // --------------------------------------------------------------------- //
    /// Virtual thickness of cloth mesh. Used to determine in-plane and bending stiffness, and mass from density.
    /// If set to 0.0, the simulation determines a default value.
    /// Range: [0.0, inf)
    /// Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxDeformableSurfaceMaterial:thickness = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetThicknessAttr() const;

    /// See GetThicknessAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateThicknessAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxDeformableSurfaceMaterialAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxDeformableSurfaceMaterialAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxDeformableSurfaceMaterialAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxDeformableSurfaceMaterialAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxDeformableSurfaceMaterialAPI::GetDensityAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableSurfaceMaterialDensity));
}

inline UsdAttribute PhysxSchemaPhysxDeformableSurfaceMaterialAPI::CreateDensityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableSurfaceMaterialDensity),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDeformableSurfaceMaterialAPI::GetDynamicFrictionAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableSurfaceMaterialDynamicFriction));
}

inline UsdAttribute PhysxSchemaPhysxDeformableSurfaceMaterialAPI::CreateDynamicFrictionAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableSurfaceMaterialDynamicFriction),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDeformableSurfaceMaterialAPI::GetYoungsModulusAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableSurfaceMaterialYoungsModulus));
}

inline UsdAttribute PhysxSchemaPhysxDeformableSurfaceMaterialAPI::CreateYoungsModulusAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableSurfaceMaterialYoungsModulus),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDeformableSurfaceMaterialAPI::GetPoissonsRatioAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableSurfaceMaterialPoissonsRatio));
}

inline UsdAttribute PhysxSchemaPhysxDeformableSurfaceMaterialAPI::CreatePoissonsRatioAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableSurfaceMaterialPoissonsRatio),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDeformableSurfaceMaterialAPI::GetThicknessAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableSurfaceMaterialThickness));
}

inline UsdAttribute PhysxSchemaPhysxDeformableSurfaceMaterialAPI::CreateThicknessAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableSurfaceMaterialThickness),
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
