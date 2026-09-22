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

/// @file physxSchema/physxVehicleNonlinearCommandResponseAPI.h

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
// PHYSXVEHICLENONLINEARCOMMANDRESPONSEAPI                                     //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxVehicleNonlinearCommandResponseAPI
///
/// Describes a system of graphs to define nonlinear responses to PhysxVehicleControllerAPI
/// command values like accelerator, brake0, brake1 and steer. The normalized response will be
/// a function of the command value and the longitudinal vehicle speed. The response will be
/// computed by interpolating between the points of the graph and then interpolating those
/// results again between the closest graphs. One example usage of nonlinear command response
/// is a brake pedal that has an almost flat response when tipped slightly but a very strong
/// response from a certain point on. Another example is the steering wheel showing a strong
/// response for a large input at low speed but only a weak response at high speed.
///
/// This multipleApply schema can be used to control the response to steering (use instance name
/// TfToken "steer") and braking (use instance name TfTokens "brakes0" or "brakes1"). It can
/// also control the response to the accelerator but only in combination with the basic drive (use
/// instance name TfToken "drive"). Furthermore, this API has to be applied to the appropriate
/// prims to take effect: "steer" has to be applied to a prim that has PhysxVehicleSteeringAPI or
/// PhysxVehicleAckermannSteeringAPI applied. "brakes0"/"brakes1" have to be applied to a prim that
/// has PhysxVehicleBrakesAPI:brakes0/brakes1 applied. "drive" has to be applied to a prim that
/// has PhysxVehicleDriveBasicAPI applied.

class PhysxSchemaPhysxVehicleNonlinearCommandResponseAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::MultipleApplyAPI;

    /// Construct a PhysxSchemaPhysxVehicleNonlinearCommandResponseAPI on UsdPrim @p prim with
    /// name @p name . Equivalent to
    /// PhysxSchemaPhysxVehicleNonlinearCommandResponseAPI::Get(
    ///    prim.GetStage(),
    ///    prim.GetPath().AppendProperty(
    ///        "physxVehicleNCR:name"));
    ///
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxVehicleNonlinearCommandResponseAPI(const UsdPrim& prim = UsdPrim(),
                                                                const TfToken& name = TfToken())
        : UsdAPISchemaBase(prim, /*instanceName*/ name)
    {
    }

    /// Construct a PhysxSchemaPhysxVehicleNonlinearCommandResponseAPI on the prim held by @p schemaObj with
    /// name @p name .  Should be preferred over
    /// PhysxSchemaPhysxVehicleNonlinearCommandResponseAPI(schemaObj.GetPrim(), name), as it preserves
    /// SchemaBase state.
    explicit PhysxSchemaPhysxVehicleNonlinearCommandResponseAPI(const UsdSchemaBase& schemaObj, const TfToken& name)
        : UsdAPISchemaBase(schemaObj, /*instanceName*/ name)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxVehicleNonlinearCommandResponseAPI()
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
    /// This information is stored by adding "PhysxVehicleNonlinearCommandResponseAPI:<i>name</i>"
    /// to the token-valued, listOp metadata \em apiSchemas on the prim.
    /// For example, if @p name is 'instance1', the token
    /// 'PhysxVehicleNonlinearCommandResponseAPI:instance1' is added to 'apiSchemas'.
    ///
    /// @return A valid PhysxSchemaPhysxVehicleNonlinearCommandResponseAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxVehicleNonlinearCommandResponseAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for
    /// conditions resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxVehicleNonlinearCommandResponseAPI Apply(const UsdPrim& prim, const TfToken& name)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxVehicleNonlinearCommandResponseAPI>(name))
        {
            return PhysxSchemaPhysxVehicleNonlinearCommandResponseAPI(prim, name);
        }
        return PhysxSchemaPhysxVehicleNonlinearCommandResponseAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // COMMANDVALUES
    // --------------------------------------------------------------------- //
    /// The command values to define response graphs for. Each listed command value
    /// (in range [0, 1], steer commands are treated symmetrically) has to point to a graph
    /// in speedResponses. The command values refer to steer, brake0 etc. The values
    /// have to be strictly increasing. The number of entries has to match the number of
    /// entries in speedResponsesPerCommandValue and is limited to 8. Every command value
    /// needs at least one entry in speedResponses.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float[] commandValues` |
    /// | C++ Type | VtArray<float> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->FloatArray |

    UsdAttribute GetCommandValuesAttr() const;

    /// See GetCommandValuesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCommandValuesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SPEEDRESPONSESPERCOMMANDVALUE
    // --------------------------------------------------------------------- //
    /// List of indices pointing to the start of a response graph for a certain command
    /// value. The index values have to be strictly increasing. The graph for command
    /// value commandValues[i] starts at entry speedResponses[speedResponsesPerCommandValue[i]]
    /// and stops at entry speedResponses[speedResponsesPerCommandValue[i+1] - 1]. The
    /// number of entries has to match the number of entries in commandValues and has the
    /// same maximum limit.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int[] speedResponsesPerCommandValue` |
    /// | C++ Type | VtArray<int> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->IntArray |

    UsdAttribute GetSpeedResponsesPerCommandValueAttr() const;

    /// See GetSpeedResponsesPerCommandValueAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSpeedResponsesPerCommandValueAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SPEEDRESPONSES
    // --------------------------------------------------------------------- //
    /// List of pairs that define points in graphs of longitudinal speed vs. normalized
    /// response. The first value of the pair is the longitudinal speed, the second value
    /// is the expected response (in range [0, 1]). The longitudinal speed values within
    /// a graph have to be strictly increasing. The maximum allowed number of entries is 64.
    /// See speedResponsesPerCommandValue for how the different graphs are accessed.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float2[] speedResponses` |
    /// | C++ Type | VtArray<GfVec2f> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float2Array |

    UsdAttribute GetSpeedResponsesAttr() const;

    /// See GetSpeedResponsesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSpeedResponsesAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxVehicleNonlinearCommandResponseAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxVehicleNonlinearCommandResponseAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxVehicleNonlinearCommandResponseAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxVehicleNonlinearCommandResponseAPI");
    return token;
}


/// @private
/// Returns the property name prefixed with the correct namespace prefix, which
/// is composed of the the API's propertyNamespacePrefix metadata and the
/// instance name of the API.
inline TfToken _GetNamespacedPropertyNamePhysxVehicleNonlinearCommandResponseAPI(const TfToken instanceName,
                                                                                 const TfToken propName)
{
    std::vector<TfToken> identifiers = { TfToken("physxVehicleNCR"), instanceName, propName };
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

inline UsdAttribute PhysxSchemaPhysxVehicleNonlinearCommandResponseAPI::GetCommandValuesAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysxVehicleNonlinearCommandResponseAPI(GetName(), PhysxSchemaTokens->commandValues));
}

inline UsdAttribute PhysxSchemaPhysxVehicleNonlinearCommandResponseAPI::CreateCommandValuesAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxVehicleNonlinearCommandResponseAPI(GetName(), PhysxSchemaTokens->commandValues),
        SdfValueTypeNames->FloatArray,
        /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleNonlinearCommandResponseAPI::GetSpeedResponsesPerCommandValueAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysxVehicleNonlinearCommandResponseAPI(
        GetName(), PhysxSchemaTokens->speedResponsesPerCommandValue));
}

inline UsdAttribute PhysxSchemaPhysxVehicleNonlinearCommandResponseAPI::CreateSpeedResponsesPerCommandValueAttr() const
{
    return GetPrim().CreateAttribute(_GetNamespacedPropertyNamePhysxVehicleNonlinearCommandResponseAPI(
                                         GetName(), PhysxSchemaTokens->speedResponsesPerCommandValue),
                                     SdfValueTypeNames->IntArray,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleNonlinearCommandResponseAPI::GetSpeedResponsesAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysxVehicleNonlinearCommandResponseAPI(
        GetName(), PhysxSchemaTokens->speedResponses));
}

inline UsdAttribute PhysxSchemaPhysxVehicleNonlinearCommandResponseAPI::CreateSpeedResponsesAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxVehicleNonlinearCommandResponseAPI(GetName(), PhysxSchemaTokens->speedResponses),
        SdfValueTypeNames->Float2Array,
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
