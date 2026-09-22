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
#ifndef USDSEQUENCE_GENERATED_CLIPBASE_H
#define USDSEQUENCE_GENERATED_CLIPBASE_H

/// \file UsdSequence/clipBase.h

#include "pxr/pxr.h"
#include "./api.h"
#include "pxr/usd/usdGeom/imageable.h"
#include "pxr/usd/usd/prim.h"
#include "pxr/usd/usd/stage.h"
#include "./tokens.h"

#include "pxr/base/vt/value.h"

#include "pxr/base/gf/vec3d.h"
#include "pxr/base/gf/vec3f.h"
#include "pxr/base/gf/matrix4d.h"

#include "pxr/base/tf/token.h"
#include "pxr/base/tf/type.h"

PXR_NAMESPACE_OPEN_SCOPE

class SdfAssetPath;

// -------------------------------------------------------------------------- //
// CLIPBASE                                                                   //
// -------------------------------------------------------------------------- //

/// \class UsdSequenceClipBase
///
/// Base class of other clip types in sequence. Clip is the most important thing of sequence. A clip does certain things at a given time and stops at another given time. These things are playing animations, switching cameras, etc.
///
class UsdSequenceClipBase : public UsdGeomImageable
{
public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// \sa UsdSchemaKind
    static const UsdSchemaKind schemaKind = UsdSchemaKind::AbstractTyped;

    /// Construct a UsdSequenceClipBase on UsdPrim \p prim .
    /// Equivalent to UsdSequenceClipBase::Get(prim.GetStage(), prim.GetPath())
    /// for a \em valid \p prim, but will not immediately throw an error for
    /// an invalid \p prim
    explicit UsdSequenceClipBase(const UsdPrim& prim=UsdPrim())
        : UsdGeomImageable(prim)
    {
    }

    /// Construct a UsdSequenceClipBase on the prim held by \p schemaObj .
    /// Should be preferred over UsdSequenceClipBase(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdSequenceClipBase(const UsdSchemaBase& schemaObj)
        : UsdGeomImageable(schemaObj)
    {
    }

    /// Destructor.
    USDSEQUENCE_API
    virtual ~UsdSequenceClipBase();

    /// Return a vector of names of all pre-declared attributes for this schema
    /// class and all its ancestor classes.  Does not include attributes that
    /// may be authored by custom/extended methods of the schemas involved.
    USDSEQUENCE_API
    static const TfTokenVector &
    GetSchemaAttributeNames(bool includeInherited=true);

    /// Return a UsdSequenceClipBase holding the prim adhering to this
    /// schema at \p path on \p stage.  If no prim exists at \p path on
    /// \p stage, or if the prim at that path does not adhere to this schema,
    /// return an invalid schema object.  This is shorthand for the following:
    ///
    /// \code
    /// UsdSequenceClipBase(stage->GetPrimAtPath(path));
    /// \endcode
    ///
    USDSEQUENCE_API
    static UsdSequenceClipBase
    Get(const UsdStagePtr &stage, const SdfPath &path);


protected:
    /// Returns the kind of schema this class belongs to.
    ///
    /// \sa UsdSchemaKind
    USDSEQUENCE_API
    UsdSchemaKind _GetSchemaKind() const override;

private:
    // needs to invoke _GetStaticTfType.
    friend class UsdSchemaRegistry;
    USDSEQUENCE_API
    static const TfType &_GetStaticTfType();

    static bool _IsTypedSchema();

    // override SchemaBase virtuals.
    USDSEQUENCE_API
    const TfType &_GetTfType() const override;

public:
    // --------------------------------------------------------------------- //
    // STARTTIME 
    // --------------------------------------------------------------------- //
    /// Time when the clip start.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform timecode startTime = 0` |
    /// | C++ Type | SdfTimeCode |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->TimeCode |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    USDSEQUENCE_API
    UsdAttribute GetStartTimeAttr() const;

    /// See GetStartTimeAttr(), and also 
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
    USDSEQUENCE_API
    UsdAttribute CreateStartTimeAttr(VtValue const &defaultValue = VtValue(), bool writeSparsely=false) const;

public:
    // --------------------------------------------------------------------- //
    // ENDTIME 
    // --------------------------------------------------------------------- //
    /// Time when the clip stops.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform timecode endTime = 0` |
    /// | C++ Type | SdfTimeCode |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->TimeCode |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    USDSEQUENCE_API
    UsdAttribute GetEndTimeAttr() const;

    /// See GetEndTimeAttr(), and also 
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
    USDSEQUENCE_API
    UsdAttribute CreateEndTimeAttr(VtValue const &defaultValue = VtValue(), bool writeSparsely=false) const;

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
