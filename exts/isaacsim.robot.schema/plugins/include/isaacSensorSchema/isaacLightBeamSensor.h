//
// Copyright 2016 Pixar
//
// Licensed under the Apache License, Version 2.0 (the "Apache License")
// with the following modification; you may not use this file except in
// compliance with the Apache License and the following modification to it:
// Section 6. Trademarks. is deleted and replaced with:
//
// 6. Trademarks. This License does not grant permission to use the trade
//    names, trademarks, service marks, or product names of the Licensor
//    and its affiliates, except as required to comply with Section 4(c) of
//    the License and to reproduce the content of the NOTICE file.
//
// You may obtain a copy of the Apache License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the Apache License with the above modification is
// distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, either express or implied. See the Apache License for the specific
// language governing permissions and limitations under the Apache License.
//
#ifndef ISAACSENSORSCHEMA_GENERATED_ISAACLIGHTBEAMSENSOR_H
#define ISAACSENSORSCHEMA_GENERATED_ISAACLIGHTBEAMSENSOR_H

/// \file isaacSensorSchema/isaacLightBeamSensor.h

#include "pxr/pxr.h"
#include ".//api.h"
#include ".//isaacBaseSensor.h"
#include "pxr/usd/usd/prim.h"
#include "pxr/usd/usd/stage.h"
#include ".//tokens.h"

#include "pxr/base/vt/value.h"

#include "pxr/base/gf/vec3d.h"
#include "pxr/base/gf/vec3f.h"
#include "pxr/base/gf/matrix4d.h"

#include "pxr/base/tf/token.h"
#include "pxr/base/tf/type.h"

PXR_NAMESPACE_OPEN_SCOPE

class SdfAssetPath;

// -------------------------------------------------------------------------- //
// ISAACLIGHTBEAMSENSOR                                                       //
// -------------------------------------------------------------------------- //

/// \class IsaacSensorIsaacLightBeamSensor
///
///
class IsaacSensorIsaacLightBeamSensor : public IsaacSensorIsaacBaseSensor
{
public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// \sa UsdSchemaKind
    static const UsdSchemaKind schemaKind = UsdSchemaKind::ConcreteTyped;

    /// Construct a IsaacSensorIsaacLightBeamSensor on UsdPrim \p prim .
    /// Equivalent to IsaacSensorIsaacLightBeamSensor::Get(prim.GetStage(), prim.GetPath())
    /// for a \em valid \p prim, but will not immediately throw an error for
    /// an invalid \p prim
    explicit IsaacSensorIsaacLightBeamSensor(const UsdPrim& prim=UsdPrim())
        : IsaacSensorIsaacBaseSensor(prim)
    {
    }

    /// Construct a IsaacSensorIsaacLightBeamSensor on the prim held by \p schemaObj .
    /// Should be preferred over IsaacSensorIsaacLightBeamSensor(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit IsaacSensorIsaacLightBeamSensor(const UsdSchemaBase& schemaObj)
        : IsaacSensorIsaacBaseSensor(schemaObj)
    {
    }

    /// Destructor.
    ISAACSENSORSCHEMA_API
    virtual ~IsaacSensorIsaacLightBeamSensor();

    /// Return a vector of names of all pre-declared attributes for this schema
    /// class and all its ancestor classes.  Does not include attributes that
    /// may be authored by custom/extended methods of the schemas involved.
    ISAACSENSORSCHEMA_API
    static const TfTokenVector &
    GetSchemaAttributeNames(bool includeInherited=true);

    /// Return a IsaacSensorIsaacLightBeamSensor holding the prim adhering to this
    /// schema at \p path on \p stage.  If no prim exists at \p path on
    /// \p stage, or if the prim at that path does not adhere to this schema,
    /// return an invalid schema object.  This is shorthand for the following:
    ///
    /// \code
    /// IsaacSensorIsaacLightBeamSensor(stage->GetPrimAtPath(path));
    /// \endcode
    ///
    ISAACSENSORSCHEMA_API
    static IsaacSensorIsaacLightBeamSensor
    Get(const UsdStagePtr &stage, const SdfPath &path);

    /// Attempt to ensure a \a UsdPrim adhering to this schema at \p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    ///
    /// If a prim adhering to this schema at \p path is already defined on this
    /// stage, return that prim.  Otherwise author an \a SdfPrimSpec with
    /// \a specifier == \a SdfSpecifierDef and this schema's prim type name for
    /// the prim at \p path at the current EditTarget.  Author \a SdfPrimSpec s
    /// with \p specifier == \a SdfSpecifierDef and empty typeName at the
    /// current EditTarget for any nonexistent, or existing but not \a Defined
    /// ancestors.
    ///
    /// The given \a path must be an absolute prim path that does not contain
    /// any variant selections.
    ///
    /// If it is impossible to author any of the necessary PrimSpecs, (for
    /// example, in case \a path cannot map to the current UsdEditTarget's
    /// namespace) issue an error and return an invalid \a UsdPrim.
    ///
    /// Note that this method may return a defined prim whose typeName does not
    /// specify this schema class, in case a stronger typeName opinion overrides
    /// the opinion at the current EditTarget.
    ///
    ISAACSENSORSCHEMA_API
    static IsaacSensorIsaacLightBeamSensor
    Define(const UsdStagePtr &stage, const SdfPath &path);

protected:
    /// Returns the kind of schema this class belongs to.
    ///
    /// \sa UsdSchemaKind
    ISAACSENSORSCHEMA_API
    UsdSchemaKind _GetSchemaKind() const override;

private:
    // needs to invoke _GetStaticTfType.
    friend class UsdSchemaRegistry;
    ISAACSENSORSCHEMA_API
    static const TfType &_GetStaticTfType();

    static bool _IsTypedSchema();

    // override SchemaBase virtuals.
    ISAACSENSORSCHEMA_API
    const TfType &_GetTfType() const override;

public:
    // --------------------------------------------------------------------- //
    // NUMRAYS 
    // --------------------------------------------------------------------- //
    /// Number of rays for the light curtain, default 1
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int numRays = 1` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |
    ISAACSENSORSCHEMA_API
    UsdAttribute GetNumRaysAttr() const;

    /// See GetNumRaysAttr(), and also 
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
    ISAACSENSORSCHEMA_API
    UsdAttribute CreateNumRaysAttr(VtValue const &defaultValue = VtValue(), bool writeSparsely=false) const;

public:
    // --------------------------------------------------------------------- //
    // CURTAINLENGTH 
    // --------------------------------------------------------------------- //
    /// Total length of the light curtain
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float curtainLength = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |
    ISAACSENSORSCHEMA_API
    UsdAttribute GetCurtainLengthAttr() const;

    /// See GetCurtainLengthAttr(), and also 
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
    ISAACSENSORSCHEMA_API
    UsdAttribute CreateCurtainLengthAttr(VtValue const &defaultValue = VtValue(), bool writeSparsely=false) const;

public:
    // --------------------------------------------------------------------- //
    // FORWARDAXIS 
    // --------------------------------------------------------------------- //
    /// Direction to shoot the light beam in [AxisX, AxisY, AxisZ]
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float3 forwardAxis = (1, 0, 0)` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float3 |
    ISAACSENSORSCHEMA_API
    UsdAttribute GetForwardAxisAttr() const;

    /// See GetForwardAxisAttr(), and also 
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
    ISAACSENSORSCHEMA_API
    UsdAttribute CreateForwardAxisAttr(VtValue const &defaultValue = VtValue(), bool writeSparsely=false) const;

public:
    // --------------------------------------------------------------------- //
    // CURTAINAXIS 
    // --------------------------------------------------------------------- //
    /// Direction to expand the light curtain in [AxisX, AxisY, AxisZ]
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float3 curtainAxis = (0, 0, 1)` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float3 |
    ISAACSENSORSCHEMA_API
    UsdAttribute GetCurtainAxisAttr() const;

    /// See GetCurtainAxisAttr(), and also 
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
    ISAACSENSORSCHEMA_API
    UsdAttribute CreateCurtainAxisAttr(VtValue const &defaultValue = VtValue(), bool writeSparsely=false) const;

public:
    // --------------------------------------------------------------------- //
    // MINRANGE 
    // --------------------------------------------------------------------- //
    /// Minimum range for sensor to detect a hit
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float minRange = 0.4` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |
    ISAACSENSORSCHEMA_API
    UsdAttribute GetMinRangeAttr() const;

    /// See GetMinRangeAttr(), and also 
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
    ISAACSENSORSCHEMA_API
    UsdAttribute CreateMinRangeAttr(VtValue const &defaultValue = VtValue(), bool writeSparsely=false) const;

public:
    // --------------------------------------------------------------------- //
    // MAXRANGE 
    // --------------------------------------------------------------------- //
    /// Maximum range for sensor to detect a hit
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float maxRange = 100` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |
    ISAACSENSORSCHEMA_API
    UsdAttribute GetMaxRangeAttr() const;

    /// See GetMaxRangeAttr(), and also 
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
    ISAACSENSORSCHEMA_API
    UsdAttribute CreateMaxRangeAttr(VtValue const &defaultValue = VtValue(), bool writeSparsely=false) const;

public:
    // ===================================================================== //
    // Feel free to add custom code below this line, it will be preserved by 
    // the code generator. 
    //
    // Just remember to: 
    //  - Close the class declaration with }; 
    //  - Close the namespace with PXR_NAMESPACE_CLOSE_SCOPE
    //  - Close the include guard with #endif
    // ===================================================================== //
    // --(BEGIN CUSTOM CODE)--
};

PXR_NAMESPACE_CLOSE_SCOPE

#endif
