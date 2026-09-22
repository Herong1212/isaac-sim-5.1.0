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
#ifndef RANGESENSORSCHEMA_GENERATED_ULTRASONICARRAY_H
#define RANGESENSORSCHEMA_GENERATED_ULTRASONICARRAY_H

/// \file rangeSensorSchema/ultrasonicArray.h

#include "pxr/pxr.h"
#include ".//api.h"
#include ".//rangeSensor.h"
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
// ULTRASONICARRAY                                                            //
// -------------------------------------------------------------------------- //

/// \class RangeSensorUltrasonicArray
///
///
class RangeSensorUltrasonicArray : public RangeSensorRangeSensor
{
public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// \sa UsdSchemaKind
    static const UsdSchemaKind schemaKind = UsdSchemaKind::ConcreteTyped;

    /// Construct a RangeSensorUltrasonicArray on UsdPrim \p prim .
    /// Equivalent to RangeSensorUltrasonicArray::Get(prim.GetStage(), prim.GetPath())
    /// for a \em valid \p prim, but will not immediately throw an error for
    /// an invalid \p prim
    explicit RangeSensorUltrasonicArray(const UsdPrim& prim=UsdPrim())
        : RangeSensorRangeSensor(prim)
    {
    }

    /// Construct a RangeSensorUltrasonicArray on the prim held by \p schemaObj .
    /// Should be preferred over RangeSensorUltrasonicArray(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit RangeSensorUltrasonicArray(const UsdSchemaBase& schemaObj)
        : RangeSensorRangeSensor(schemaObj)
    {
    }

    /// Destructor.
    RANGESENSORSCHEMA_API
    virtual ~RangeSensorUltrasonicArray();

    /// Return a vector of names of all pre-declared attributes for this schema
    /// class and all its ancestor classes.  Does not include attributes that
    /// may be authored by custom/extended methods of the schemas involved.
    RANGESENSORSCHEMA_API
    static const TfTokenVector &
    GetSchemaAttributeNames(bool includeInherited=true);

    /// Return a RangeSensorUltrasonicArray holding the prim adhering to this
    /// schema at \p path on \p stage.  If no prim exists at \p path on
    /// \p stage, or if the prim at that path does not adhere to this schema,
    /// return an invalid schema object.  This is shorthand for the following:
    ///
    /// \code
    /// RangeSensorUltrasonicArray(stage->GetPrimAtPath(path));
    /// \endcode
    ///
    RANGESENSORSCHEMA_API
    static RangeSensorUltrasonicArray
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
    RANGESENSORSCHEMA_API
    static RangeSensorUltrasonicArray
    Define(const UsdStagePtr &stage, const SdfPath &path);

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
    // NUMBINS 
    // --------------------------------------------------------------------- //
    /// Number of bins that emitters in this array outputs
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int numBins = 224` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |
    RANGESENSORSCHEMA_API
    UsdAttribute GetNumBinsAttr() const;

    /// See GetNumBinsAttr(), and also 
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
    RANGESENSORSCHEMA_API
    UsdAttribute CreateNumBinsAttr(VtValue const &defaultValue = VtValue(), bool writeSparsely=false) const;

public:
    // --------------------------------------------------------------------- //
    // USEBRDF 
    // --------------------------------------------------------------------- //
    /// Use angle of emitter/receiver relative to normal to compute intensity response
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool useBRDF = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |
    RANGESENSORSCHEMA_API
    UsdAttribute GetUseBRDFAttr() const;

    /// See GetUseBRDFAttr(), and also 
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
    RANGESENSORSCHEMA_API
    UsdAttribute CreateUseBRDFAttr(VtValue const &defaultValue = VtValue(), bool writeSparsely=false) const;

public:
    // --------------------------------------------------------------------- //
    // USEUSSMATERIALSFORBRDF 
    // --------------------------------------------------------------------- //
    /// Use Ultrasonic materials for BRDF calculation
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool useUSSMaterialsForBRDF = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |
    RANGESENSORSCHEMA_API
    UsdAttribute GetUseUSSMaterialsForBRDFAttr() const;

    /// See GetUseUSSMaterialsForBRDFAttr(), and also 
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
    RANGESENSORSCHEMA_API
    UsdAttribute CreateUseUSSMaterialsForBRDFAttr(VtValue const &defaultValue = VtValue(), bool writeSparsely=false) const;

public:
    // --------------------------------------------------------------------- //
    // USEDISTATTENUATION 
    // --------------------------------------------------------------------- //
    /// Use simplified Beer-Lambert model, negative exponential attenuation
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool useDistAttenuation = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |
    RANGESENSORSCHEMA_API
    UsdAttribute GetUseDistAttenuationAttr() const;

    /// See GetUseDistAttenuationAttr(), and also 
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
    RANGESENSORSCHEMA_API
    UsdAttribute CreateUseDistAttenuationAttr(VtValue const &defaultValue = VtValue(), bool writeSparsely=false) const;

public:
    // --------------------------------------------------------------------- //
    // ATTENUATIONALPHA 
    // --------------------------------------------------------------------- //
    /// Single attenuation parameter for simplified Beer-Lambert model
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float attenuationAlpha = 0.6` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |
    RANGESENSORSCHEMA_API
    UsdAttribute GetAttenuationAlphaAttr() const;

    /// See GetAttenuationAlphaAttr(), and also 
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
    RANGESENSORSCHEMA_API
    UsdAttribute CreateAttenuationAlphaAttr(VtValue const &defaultValue = VtValue(), bool writeSparsely=false) const;

public:
    // --------------------------------------------------------------------- //
    // HORIZONTALFOV 
    // --------------------------------------------------------------------- //
    /// Horizontal Field of View in degrees
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float horizontalFov = 60` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |
    RANGESENSORSCHEMA_API
    UsdAttribute GetHorizontalFovAttr() const;

    /// See GetHorizontalFovAttr(), and also 
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
    RANGESENSORSCHEMA_API
    UsdAttribute CreateHorizontalFovAttr(VtValue const &defaultValue = VtValue(), bool writeSparsely=false) const;

public:
    // --------------------------------------------------------------------- //
    // VERTICALFOV 
    // --------------------------------------------------------------------- //
    /// Vertical Field of View in degrees
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float verticalFov = 30` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |
    RANGESENSORSCHEMA_API
    UsdAttribute GetVerticalFovAttr() const;

    /// See GetVerticalFovAttr(), and also 
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
    RANGESENSORSCHEMA_API
    UsdAttribute CreateVerticalFovAttr(VtValue const &defaultValue = VtValue(), bool writeSparsely=false) const;

public:
    // --------------------------------------------------------------------- //
    // HORIZONTALRESOLUTION 
    // --------------------------------------------------------------------- //
    /// Degrees in between rays for horizontal axis
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float horizontalResolution = 0.4` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |
    RANGESENSORSCHEMA_API
    UsdAttribute GetHorizontalResolutionAttr() const;

    /// See GetHorizontalResolutionAttr(), and also 
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
    RANGESENSORSCHEMA_API
    UsdAttribute CreateHorizontalResolutionAttr(VtValue const &defaultValue = VtValue(), bool writeSparsely=false) const;

public:
    // --------------------------------------------------------------------- //
    // VERTICALRESOLUTION 
    // --------------------------------------------------------------------- //
    /// Degrees in between rays for vertical axis
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float verticalResolution = 4` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |
    RANGESENSORSCHEMA_API
    UsdAttribute GetVerticalResolutionAttr() const;

    /// See GetVerticalResolutionAttr(), and also 
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
    RANGESENSORSCHEMA_API
    UsdAttribute CreateVerticalResolutionAttr(VtValue const &defaultValue = VtValue(), bool writeSparsely=false) const;

public:
    // --------------------------------------------------------------------- //
    // EMITTERPRIMS 
    // --------------------------------------------------------------------- //
    /// List of emitter/receiver prims that are part of the array, zero indexed
    ///
    RANGESENSORSCHEMA_API
    UsdRelationship GetEmitterPrimsRel() const;

    /// See GetEmitterPrimsRel(), and also 
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    RANGESENSORSCHEMA_API
    UsdRelationship CreateEmitterPrimsRel() const;

public:
    // --------------------------------------------------------------------- //
    // FIRINGGROUPS 
    // --------------------------------------------------------------------- //
    /// List of UltrasonicFiringGroups, used to define the firing pattern for the array,
    ///
    RANGESENSORSCHEMA_API
    UsdRelationship GetFiringGroupsRel() const;

    /// See GetFiringGroupsRel(), and also 
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    RANGESENSORSCHEMA_API
    UsdRelationship CreateFiringGroupsRel() const;

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
