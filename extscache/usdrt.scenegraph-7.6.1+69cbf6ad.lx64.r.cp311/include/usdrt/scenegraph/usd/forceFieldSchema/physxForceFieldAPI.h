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

/// @file forceFieldSchema/physxForceFieldAPI.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/apiSchemaBase.h"
#include "usdrt/scenegraph/usd/forceFieldSchema/tokens.h"


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
// PHYSXFORCEFIELDAPI                                                          //
// -------------------------------------------------------------------------- //

/// @class ForceFieldSchemaPhysxForceFieldAPI
///
/// Force field base class that simply specifies the position and enables or disables the ForceField.

class ForceFieldSchemaPhysxForceFieldAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::MultipleApplyAPI;

    /// Construct a ForceFieldSchemaPhysxForceFieldAPI on UsdPrim @p prim with
    /// name @p name . Equivalent to
    /// ForceFieldSchemaPhysxForceFieldAPI::Get(
    ///    prim.GetStage(),
    ///    prim.GetPath().AppendProperty(
    ///        "physxForceField:name"));
    ///
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit ForceFieldSchemaPhysxForceFieldAPI(const UsdPrim& prim = UsdPrim(), const TfToken& name = TfToken())
        : UsdAPISchemaBase(prim, /*instanceName*/ name)
    {
    }

    /// Construct a ForceFieldSchemaPhysxForceFieldAPI on the prim held by @p schemaObj with
    /// name @p name .  Should be preferred over
    /// ForceFieldSchemaPhysxForceFieldAPI(schemaObj.GetPrim(), name), as it preserves
    /// SchemaBase state.
    explicit ForceFieldSchemaPhysxForceFieldAPI(const UsdSchemaBase& schemaObj, const TfToken& name)
        : UsdAPISchemaBase(schemaObj, /*instanceName*/ name)
    {
    }

    /// Destructor.
    virtual ~ForceFieldSchemaPhysxForceFieldAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();

    /// Returns the name of this multiple-apply schema instance
    TfToken GetName() const
    {
        return _GetInstanceName();
    }

    /// Applies this <b>multiple-apply</b> API schema to the given @p prim
    /// along with the given instance name, @p name.
    ///
    /// This information is stored by adding "PhysxForceFieldAPI:<i>name</i>"
    /// to the token-valued, listOp metadata \em apiSchemas on the prim.
    /// For example, if @p name is 'instance1', the token
    /// 'PhysxForceFieldAPI:instance1' is added to 'apiSchemas'.
    ///
    /// @return A valid ForceFieldSchemaPhysxForceFieldAPI object is returned upon success.
    /// An invalid (or empty) ForceFieldSchemaPhysxForceFieldAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for
    /// conditions resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static ForceFieldSchemaPhysxForceFieldAPI Apply(const UsdPrim& prim, const TfToken& name)
    {
        if (prim.ApplyAPI<ForceFieldSchemaPhysxForceFieldAPI>(name))
        {
            return ForceFieldSchemaPhysxForceFieldAPI(prim, name);
        }
        return ForceFieldSchemaPhysxForceFieldAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // ENABLED
    // --------------------------------------------------------------------- //
    /// Enable or disable this ForceField. Overrides all other settings.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxForceField:enabled = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetEnabledAttr() const;

    /// See GetEnabledAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateEnabledAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SURFACESAMPLEDENSITY
    // --------------------------------------------------------------------- //
    /// Number of rays to cast per square unit of surface area.
    /// When Surface Sampling is disabled, by setting this value to 0.0,
    /// (or when it is enabled and a rigid body has no geometry to sample)
    /// all forces act through the Center of Mass of the Rigid Body and
    /// no rotational torques will be applied. Any positive value will
    /// enable Surface Sampling. Ray casts are performed against the
    /// Collision Object of the Rigid Body in order to apply forces on
    /// the surface along the direction of the surface normal. This will
    /// apply torques to the Rigid Body that will induce rotation. Higher
    /// densities will cast more rays over the surface and spread the same
    /// force over the surface area. More ray casts will generate more accurate
    /// forces and torques, but will take additional compute time.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxForceField:surfaceSampleDensity = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSurfaceSampleDensityAttr() const;

    /// See GetSurfaceSampleDensityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSurfaceSampleDensityAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SURFACEAREASCALEENABLED
    // --------------------------------------------------------------------- //
    /// Enable or disable scaling forces by the surface area that faces
    /// in the direction of the applied force. If a rigid body has no
    /// geometry to sample, the surface area scaling is also disabled
    /// for that rigid body. The surface area measurement is an
    /// approximation based on the collision object bounding box.
    /// Certain forces, like wind and drag increase as the exposed surface
    /// area increases, but this may not always be desirable.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxForceField:surfaceAreaScaleEnabled = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetSurfaceAreaScaleEnabledAttr() const;

    /// See GetSurfaceAreaScaleEnabledAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSurfaceAreaScaleEnabledAttr() const;

public:
    // --------------------------------------------------------------------- //
    // POSITION
    // --------------------------------------------------------------------- //
    /// The location of the force field. Set to (0, 0, 0) to obtain the position
    /// from the prim and continuously update it if it is animated.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float3 physxForceField:position = (0, 0, 0)` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float3 |

    UsdAttribute GetPositionAttr() const;

    /// See GetPositionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreatePositionAttr() const;

public:
    // --------------------------------------------------------------------- //
    // RANGE
    // --------------------------------------------------------------------- //
    /// Forces are not applied when the distance to the force field is outside
    /// of this (minimum, maximum) range. Each force field can have a different
    /// definition of distance, e.g. for a spherical fore field, the distance is
    /// to the center, for a plane, the distance is to the closest point on the
    /// surface, for a line, it is to the closest point on the line. The minimum
    /// or maximum range is ignored if the value is negative.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float2 physxForceField:range = (-1, -1)` |
    /// | C++ Type | GfVec2f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float2 |

    UsdAttribute GetRangeAttr() const;

    /// See GetRangeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateRangeAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken ForceFieldSchemaPhysxForceFieldAPI::_GetStaticTfType()
{
    const static TfToken token("ForceFieldSchemaPhysxForceFieldAPI");
    return token;
}

/* virtual */
inline const TfToken ForceFieldSchemaPhysxForceFieldAPI::_GetTfTypeToken() const
{
    const static TfToken token("ForceFieldSchemaPhysxForceFieldAPI");
    return token;
}


/// @private
/// Returns the property name prefixed with the correct namespace prefix, which
/// is composed of the the API's propertyNamespacePrefix metadata and the
/// instance name of the API.
inline TfToken _GetNamespacedPropertyNamePhysxForceFieldAPI(const TfToken instanceName, const TfToken propName)
{
    std::vector<TfToken> identifiers = { TfToken("physxForceField"), instanceName, propName };
    // join (TODO this was SdfPath::JoinIdentifier(identifiers))
    std::string namespaceDelimeter = ":";
    std::string namespacedName = "";
    for (auto& token : identifiers)
    {
        namespacedName += token.GetString();
        if (!(token == *(identifiers.end() - 1)))
        {
            namespacedName += namespaceDelimeter;
        }
    }

    return TfToken(namespacedName);
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldAPI::GetEnabledAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysxForceFieldAPI(GetName(), ForceFieldSchemaTokens->physxForceFieldEnabled));
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldAPI::CreateEnabledAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxForceFieldAPI(GetName(), ForceFieldSchemaTokens->physxForceFieldEnabled),
        SdfValueTypeNames->Bool,
        /* custom = */ false);
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldAPI::GetSurfaceSampleDensityAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysxForceFieldAPI(
        GetName(), ForceFieldSchemaTokens->physxForceFieldSurfaceSampleDensity));
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldAPI::CreateSurfaceSampleDensityAttr() const
{
    return GetPrim().CreateAttribute(_GetNamespacedPropertyNamePhysxForceFieldAPI(
                                         GetName(), ForceFieldSchemaTokens->physxForceFieldSurfaceSampleDensity),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldAPI::GetSurfaceAreaScaleEnabledAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysxForceFieldAPI(
        GetName(), ForceFieldSchemaTokens->physxForceFieldSurfaceAreaScaleEnabled));
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldAPI::CreateSurfaceAreaScaleEnabledAttr() const
{
    return GetPrim().CreateAttribute(_GetNamespacedPropertyNamePhysxForceFieldAPI(
                                         GetName(), ForceFieldSchemaTokens->physxForceFieldSurfaceAreaScaleEnabled),
                                     SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldAPI::GetPositionAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysxForceFieldAPI(GetName(), ForceFieldSchemaTokens->physxForceFieldPosition));
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldAPI::CreatePositionAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxForceFieldAPI(GetName(), ForceFieldSchemaTokens->physxForceFieldPosition),
        SdfValueTypeNames->Float3,
        /* custom = */ false);
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldAPI::GetRangeAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysxForceFieldAPI(GetName(), ForceFieldSchemaTokens->physxForceFieldRange));
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldAPI::CreateRangeAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxForceFieldAPI(GetName(), ForceFieldSchemaTokens->physxForceFieldRange),
        SdfValueTypeNames->Float2,
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
