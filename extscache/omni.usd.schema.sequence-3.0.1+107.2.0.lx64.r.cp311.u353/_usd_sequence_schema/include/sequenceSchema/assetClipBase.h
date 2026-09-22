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
#ifndef USDSEQUENCE_GENERATED_ASSETCLIPBASE_H
#define USDSEQUENCE_GENERATED_ASSETCLIPBASE_H

/// \file UsdSequence/assetClipBase.h

#include "pxr/pxr.h"
#include "./api.h"
#include "./clipBase.h"
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
// ASSETCLIPBASE                                                              //
// -------------------------------------------------------------------------- //

/// \class UsdSequenceAssetClipBase
///
/// Base class of asset clips. An asset clip grabs time samples from "animation" prim and applies these time samples to "assetPrim". If "assetPrim" is Skeleton and "animation" is SkelAnimation, AssetClip sets "animation" to "skel:animationSource" relationship of "assetPrim".
///
class UsdSequenceAssetClipBase : public UsdSequenceClipBase
{
public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// \sa UsdSchemaKind
    static const UsdSchemaKind schemaKind = UsdSchemaKind::AbstractTyped;

    /// Construct a UsdSequenceAssetClipBase on UsdPrim \p prim .
    /// Equivalent to UsdSequenceAssetClipBase::Get(prim.GetStage(), prim.GetPath())
    /// for a \em valid \p prim, but will not immediately throw an error for
    /// an invalid \p prim
    explicit UsdSequenceAssetClipBase(const UsdPrim& prim=UsdPrim())
        : UsdSequenceClipBase(prim)
    {
    }

    /// Construct a UsdSequenceAssetClipBase on the prim held by \p schemaObj .
    /// Should be preferred over UsdSequenceAssetClipBase(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdSequenceAssetClipBase(const UsdSchemaBase& schemaObj)
        : UsdSequenceClipBase(schemaObj)
    {
    }

    /// Destructor.
    USDSEQUENCE_API
    virtual ~UsdSequenceAssetClipBase();

    /// Return a vector of names of all pre-declared attributes for this schema
    /// class and all its ancestor classes.  Does not include attributes that
    /// may be authored by custom/extended methods of the schemas involved.
    USDSEQUENCE_API
    static const TfTokenVector &
    GetSchemaAttributeNames(bool includeInherited=true);

    /// Return a UsdSequenceAssetClipBase holding the prim adhering to this
    /// schema at \p path on \p stage.  If no prim exists at \p path on
    /// \p stage, or if the prim at that path does not adhere to this schema,
    /// return an invalid schema object.  This is shorthand for the following:
    ///
    /// \code
    /// UsdSequenceAssetClipBase(stage->GetPrimAtPath(path));
    /// \endcode
    ///
    USDSEQUENCE_API
    static UsdSequenceAssetClipBase
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
    // PLAYOFFSET 
    // --------------------------------------------------------------------- //
    /// The time of animation when the clip starts to play. It should be between playStart and playEnd.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform timecode playOffset = nan` |
    /// | C++ Type | SdfTimeCode |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->TimeCode |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    USDSEQUENCE_API
    UsdAttribute GetPlayOffsetAttr() const;

    /// See GetPlayOffsetAttr(), and also 
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
    USDSEQUENCE_API
    UsdAttribute CreatePlayOffsetAttr(VtValue const &defaultValue = VtValue(), bool writeSparsely=false) const;

public:
    // --------------------------------------------------------------------- //
    // PLAYSTART 
    // --------------------------------------------------------------------- //
    /// Start time of the range in animation that is used by clip.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform timecode playStart = nan` |
    /// | C++ Type | SdfTimeCode |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->TimeCode |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    USDSEQUENCE_API
    UsdAttribute GetPlayStartAttr() const;

    /// See GetPlayStartAttr(), and also 
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
    USDSEQUENCE_API
    UsdAttribute CreatePlayStartAttr(VtValue const &defaultValue = VtValue(), bool writeSparsely=false) const;

public:
    // --------------------------------------------------------------------- //
    // PLAYEND 
    // --------------------------------------------------------------------- //
    /// End time of the range in animation that is used by clip.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform timecode playEnd = nan` |
    /// | C++ Type | SdfTimeCode |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->TimeCode |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    USDSEQUENCE_API
    UsdAttribute GetPlayEndAttr() const;

    /// See GetPlayEndAttr(), and also 
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
    USDSEQUENCE_API
    UsdAttribute CreatePlayEndAttr(VtValue const &defaultValue = VtValue(), bool writeSparsely=false) const;

public:
    // --------------------------------------------------------------------- //
    // LOOP 
    // --------------------------------------------------------------------- //
    /// Indicates whether animation loop.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform bool loop = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    USDSEQUENCE_API
    UsdAttribute GetLoopAttr() const;

    /// See GetLoopAttr(), and also 
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
    USDSEQUENCE_API
    UsdAttribute CreateLoopAttr(VtValue const &defaultValue = VtValue(), bool writeSparsely=false) const;

public:
    // --------------------------------------------------------------------- //
    // PLAYRATE 
    // --------------------------------------------------------------------- //
    /// Indicates how fast animation is played.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform float playRate = 1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    USDSEQUENCE_API
    UsdAttribute GetPlayRateAttr() const;

    /// See GetPlayRateAttr(), and also 
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
    USDSEQUENCE_API
    UsdAttribute CreatePlayRateAttr(VtValue const &defaultValue = VtValue(), bool writeSparsely=false) const;

public:
    // --------------------------------------------------------------------- //
    // ASSETPRIM 
    // --------------------------------------------------------------------- //
    /// The prim to which the AssetClip applies animation.
    ///
    USDSEQUENCE_API
    UsdRelationship GetAssetPrimRel() const;

    /// See GetAssetPrimRel(), and also 
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    USDSEQUENCE_API
    UsdRelationship CreateAssetPrimRel() const;

public:
    // --------------------------------------------------------------------- //
    // ANIMATION 
    // --------------------------------------------------------------------- //
    /// The prim from which the AssetClip grabs time samples. If it's empty, AssetClip grabs time samples from the "assetPrim". 
    ///
    USDSEQUENCE_API
    UsdRelationship GetAnimationRel() const;

    /// See GetAnimationRel(), and also 
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    USDSEQUENCE_API
    UsdRelationship CreateAnimationRel() const;

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
