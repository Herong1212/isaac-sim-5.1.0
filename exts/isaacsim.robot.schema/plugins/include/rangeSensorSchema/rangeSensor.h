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
#ifndef RANGESENSORSCHEMA_GENERATED_RANGESENSOR_H
#define RANGESENSORSCHEMA_GENERATED_RANGESENSOR_H

/// \file rangeSensorSchema/rangeSensor.h

#include "pxr/pxr.h"
#include ".//api.h"
#include "pxr/usd/usdGeom/xformable.h"
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
// RANGESENSOR                                                                //
// -------------------------------------------------------------------------- //

/// \class RangeSensorRangeSensor
///
///
class RangeSensorRangeSensor : public UsdGeomXformable
{
public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// \sa UsdSchemaKind
    static const UsdSchemaKind schemaKind = UsdSchemaKind::AbstractTyped;

    /// Construct a RangeSensorRangeSensor on UsdPrim \p prim .
    /// Equivalent to RangeSensorRangeSensor::Get(prim.GetStage(), prim.GetPath())
    /// for a \em valid \p prim, but will not immediately throw an error for
    /// an invalid \p prim
    explicit RangeSensorRangeSensor(const UsdPrim& prim=UsdPrim())
        : UsdGeomXformable(prim)
    {
    }

    /// Construct a RangeSensorRangeSensor on the prim held by \p schemaObj .
    /// Should be preferred over RangeSensorRangeSensor(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit RangeSensorRangeSensor(const UsdSchemaBase& schemaObj)
        : UsdGeomXformable(schemaObj)
    {
    }

    /// Destructor.
    RANGESENSORSCHEMA_API
    virtual ~RangeSensorRangeSensor();

    /// Return a vector of names of all pre-declared attributes for this schema
    /// class and all its ancestor classes.  Does not include attributes that
    /// may be authored by custom/extended methods of the schemas involved.
    RANGESENSORSCHEMA_API
    static const TfTokenVector &
    GetSchemaAttributeNames(bool includeInherited=true);

    /// Return a RangeSensorRangeSensor holding the prim adhering to this
    /// schema at \p path on \p stage.  If no prim exists at \p path on
    /// \p stage, or if the prim at that path does not adhere to this schema,
    /// return an invalid schema object.  This is shorthand for the following:
    ///
    /// \code
    /// RangeSensorRangeSensor(stage->GetPrimAtPath(path));
    /// \endcode
    ///
    RANGESENSORSCHEMA_API
    static RangeSensorRangeSensor
    Get(const UsdStagePtr &stage, const SdfPath &path);


protected:
    /// Returns the kind of schema this class belongs to.
    ///
    /// \sa UsdSchemaKind
    RANGESENSORSCHEMA_API
    UsdSchemaKind _GetSchemaKind() const override;

private:
    // needs to invoke _GetStaticTfType.
    friend class UsdSchemaRegistry;
    RANGESENSORSCHEMA_API
    static const TfType &_GetStaticTfType();

    static bool _IsTypedSchema();

    // override SchemaBase virtuals.
    RANGESENSORSCHEMA_API
    const TfType &_GetTfType() const override;

public:
    // --------------------------------------------------------------------- //
    // ENABLED 
    // --------------------------------------------------------------------- //
    /// Flag used to enable or disable this sensor
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool enabled = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |
    RANGESENSORSCHEMA_API
    UsdAttribute GetEnabledAttr() const;

    /// See GetEnabledAttr(), and also 
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
    RANGESENSORSCHEMA_API
    UsdAttribute CreateEnabledAttr(VtValue const &defaultValue = VtValue(), bool writeSparsely=false) const;

public:
    // --------------------------------------------------------------------- //
    // DRAWPOINTS 
    // --------------------------------------------------------------------- //
    /// Set to true to draw debug points on sensor hit locations
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool drawPoints = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |
    RANGESENSORSCHEMA_API
    UsdAttribute GetDrawPointsAttr() const;

    /// See GetDrawPointsAttr(), and also 
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
    RANGESENSORSCHEMA_API
    UsdAttribute CreateDrawPointsAttr(VtValue const &defaultValue = VtValue(), bool writeSparsely=false) const;

public:
    // --------------------------------------------------------------------- //
    // DRAWLINES 
    // --------------------------------------------------------------------- //
    /// Set to true to draw debug lines representing sensor ray casts
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool drawLines = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |
    RANGESENSORSCHEMA_API
    UsdAttribute GetDrawLinesAttr() const;

    /// See GetDrawLinesAttr(), and also 
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
    RANGESENSORSCHEMA_API
    UsdAttribute CreateDrawLinesAttr(VtValue const &defaultValue = VtValue(), bool writeSparsely=false) const;

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
    RANGESENSORSCHEMA_API
    UsdAttribute GetMinRangeAttr() const;

    /// See GetMinRangeAttr(), and also 
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
    RANGESENSORSCHEMA_API
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
    RANGESENSORSCHEMA_API
    UsdAttribute GetMaxRangeAttr() const;

    /// See GetMaxRangeAttr(), and also 
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
    RANGESENSORSCHEMA_API
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
