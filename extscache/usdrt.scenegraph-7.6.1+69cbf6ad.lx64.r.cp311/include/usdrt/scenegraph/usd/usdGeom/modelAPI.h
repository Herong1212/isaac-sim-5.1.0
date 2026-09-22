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

/// @file usdGeom/modelAPI.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/apiSchemaBase.h"
#include "usdrt/scenegraph/usd/usdGeom/tokens.h"

// clang-format off
/* Extra Includes
// USDRT NOTE: Use custom includes below instead to allow for
// implementation differences in the custom code. This section comes
// from the pxr schema.usda files which we may not have in usdrt.
//#include "usdrt/scenegraph/usd/usdGeom/bboxCache.h"
#include "usdrt/scenegraph/usd/usdGeom/constraintTarget.h"
#include "usdrt/scenegraph/usd/usdGeom/imageable.h" */
// clang-format on

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
// GEOMMODELAPI                                                                //
// -------------------------------------------------------------------------- //

/// @class UsdGeomModelAPI
///
/// UsdGeomModelAPI extends the generic UsdModelAPI schema with
/// geometry specific concepts such as cached extents for the entire model,
/// constraint targets, and geometry-inspired extensions to the payload
/// lofting process.
///
/// As described in GetExtentsHint() below, it is useful to cache extents
/// at the model level.  UsdGeomModelAPI provides schema for computing and
/// storing these cached extents, which can be consumed by UsdGeomBBoxCache to
/// provide fast access to precomputed extents that will be used as the model's
/// bounds ( see UsdGeomBBoxCache::UsdGeomBBoxCache() ).
///
/// \section UsdGeomModelAPI_drawMode Draw Modes
///
/// Draw modes provide optional alternate imaging behavior for USD subtrees with
/// kind model. \em model:drawMode (which is inheritable) and
/// \em model:applyDrawMode (which is not) are resolved into a decision to stop
/// traversing the scene graph at a certain point, and replace a USD subtree
/// with proxy geometry.
///
/// The value of \em model:drawMode determines the type of proxy geometry:
/// - \em origin - Draw the model-space basis vectors of the replaced prim.
/// - \em bounds - Draw the model-space bounding box of the replaced prim.
/// - \em cards - Draw textured quads as a placeholder for the replaced prim.
/// - \em default - An explicit opinion to draw the USD subtree as normal.
/// - \em inherited - Defer to the parent opinion.
///
/// \em model:drawMode falls back to _inherited_ so that a whole scene,
/// a large group, or all prototypes of a model hierarchy PointInstancer can
/// be assigned a draw mode with a single attribute edit.  If no draw mode is
/// explicitly set in a hierarchy, the resolved value is _default_.
///
/// \em model:applyDrawMode is meant to be written when an asset is authored,
/// and provides flexibility for different asset types. For example,
/// a character assembly (composed of character, clothes, etc) might have
/// \em model:applyDrawMode set at the top of the subtree so the whole group
/// can be drawn as a single card object. An effects subtree might have
/// \em model:applyDrawMode set at a lower level so each particle
/// group draws individually.
///
/// Models of kind component are treated as if \em model:applyDrawMode
/// were true.  This means a prim is drawn with proxy geometry when: the
/// prim has kind component, and/or \em model:applyDrawMode is set; and
/// the prim's resolved value for \em model:drawMode is not _default_.
///
/// \section UsdGeomModelAPI_cardGeometry Cards Geometry
///
/// The specific geometry used in cards mode is controlled by the
/// \em model:cardGeometry attribute:
/// - \em cross - Generate a quad normal to each basis direction and negative.
/// Locate each quad so that it bisects the model extents.
/// - \em box   - Generate a quad normal to each basis direction and negative.
/// Locate each quad on a face of the model extents, facing out.
/// - \em fromTexture - Generate a quad for each supplied texture from
/// attributes stored in that texture's metadata.
///
/// For \em cross and \em box mode, the extents are calculated for purposes
/// \em default, \em proxy, and \em render, at their earliest authored time.
/// If the model has no textures, all six card faces are rendered using
/// \em model:drawModeColor. If one or more textures are present, only axes
/// with one or more textures assigned are drawn.  For each axis, if both
/// textures (positive and negative) are specified, they'll be used on the
/// corresponding card faces; if only one texture is specified, it will be
/// mapped to the opposite card face after being flipped on the texture's
/// s-axis. Any card faces with invalid asset paths will be drawn with
/// \em model:drawModeColor.
///
/// Both \em model:cardGeometry and \em model:drawModeColor should be
/// authored on the prim where the draw mode takes effect, since these
/// attributes are not inherited.
///
/// For \em fromTexture mode, only card faces with valid textures assigned
/// are drawn. The geometry is generated by pulling the \em worldtoscreen
/// attribute out of texture metadata.  This is expected to be a 4x4 matrix
/// mapping the model-space position of the card quad to the clip-space quad
/// with corners (-1,-1,0) and (1,1,0).  The card vertices are generated by
/// transforming the clip-space corners by the inverse of \em worldtoscreen.
/// Textures are mapped so that (s) and (t) map to (+x) and (+y) in clip space.
/// If the metadata cannot be read in the right format, or the matrix can't
/// be inverted, the card face is not drawn.
///
/// All card faces are drawn and textured as single-sided.
///
/// \todo CreatePayload()
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdGeomTokens.
/// So to set an attribute to the value "rightHanded", use UsdGeomTokens->rightHanded
/// as the value.

class UsdGeomModelAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a UsdGeomModelAPI on UsdPrim @p prim.
    /// Equivalent to UsdGeomModelAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdGeomModelAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a UsdGeomModelAPI on the prim held by @p schemaObj .
    /// Should be preferred over UsdGeomModelAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdGeomModelAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdGeomModelAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "GeomModelAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid UsdGeomModelAPI object is returned upon success.
    /// An invalid (or empty) UsdGeomModelAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static UsdGeomModelAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<UsdGeomModelAPI>())
        {
            return UsdGeomModelAPI(prim);
        }
        return UsdGeomModelAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // MODELDRAWMODE
    // --------------------------------------------------------------------- //
    /// Alternate imaging mode; applied to this prim or child prims
    /// where \em model:applyDrawMode is true, or where the prim
    /// has kind \em component. See \ref UsdGeomModelAPI_drawMode
    /// for mode descriptions.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token model:drawMode = "inherited"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref UsdGeomTokens "Allowed Values" | origin, bounds, cards, default, inherited |

    UsdAttribute GetModelDrawModeAttr() const;

    /// See GetModelDrawModeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateModelDrawModeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MODELAPPLYDRAWMODE
    // --------------------------------------------------------------------- //
    /// If true, and the resolved value of \em model:drawMode is
    /// non-default, apply an alternate imaging mode to this prim. See
    /// \ref UsdGeomModelAPI_drawMode.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform bool model:applyDrawMode = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetModelApplyDrawModeAttr() const;

    /// See GetModelApplyDrawModeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateModelApplyDrawModeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MODELDRAWMODECOLOR
    // --------------------------------------------------------------------- //
    /// The base color of imaging prims inserted for alternate
    /// imaging modes. For \em origin and \em bounds modes, this
    /// controls line color; for \em cards mode, this controls the
    /// fallback quad color.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform float3 model:drawModeColor = (0.18, 0.18, 0.18)` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float3 |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetModelDrawModeColorAttr() const;

    /// See GetModelDrawModeColorAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateModelDrawModeColorAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MODELCARDGEOMETRY
    // --------------------------------------------------------------------- //
    /// The geometry to generate for imaging prims inserted for \em
    /// cards imaging mode. See \ref UsdGeomModelAPI_cardGeometry for
    /// geometry descriptions.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token model:cardGeometry = "cross"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref UsdGeomTokens "Allowed Values" | cross, box, fromTexture |

    UsdAttribute GetModelCardGeometryAttr() const;

    /// See GetModelCardGeometryAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateModelCardGeometryAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MODELCARDTEXTUREXPOS
    // --------------------------------------------------------------------- //
    /// In \em cards imaging mode, the texture applied to the X+ quad.
    /// The texture axes (s,t) are mapped to model-space axes (-y, -z).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `asset model:cardTextureXPos` |
    /// | C++ Type | SdfAssetPath |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Asset |

    UsdAttribute GetModelCardTextureXPosAttr() const;

    /// See GetModelCardTextureXPosAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateModelCardTextureXPosAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MODELCARDTEXTUREYPOS
    // --------------------------------------------------------------------- //
    /// In \em cards imaging mode, the texture applied to the Y+ quad.
    /// The texture axes (s,t) are mapped to model-space axes (x, -z).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `asset model:cardTextureYPos` |
    /// | C++ Type | SdfAssetPath |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Asset |

    UsdAttribute GetModelCardTextureYPosAttr() const;

    /// See GetModelCardTextureYPosAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateModelCardTextureYPosAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MODELCARDTEXTUREZPOS
    // --------------------------------------------------------------------- //
    /// In \em cards imaging mode, the texture applied to the Z+ quad.
    /// The texture axes (s,t) are mapped to model-space axes (x, -y).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `asset model:cardTextureZPos` |
    /// | C++ Type | SdfAssetPath |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Asset |

    UsdAttribute GetModelCardTextureZPosAttr() const;

    /// See GetModelCardTextureZPosAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateModelCardTextureZPosAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MODELCARDTEXTUREXNEG
    // --------------------------------------------------------------------- //
    /// In \em cards imaging mode, the texture applied to the X- quad.
    /// The texture axes (s,t) are mapped to model-space axes (y, -z).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `asset model:cardTextureXNeg` |
    /// | C++ Type | SdfAssetPath |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Asset |

    UsdAttribute GetModelCardTextureXNegAttr() const;

    /// See GetModelCardTextureXNegAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateModelCardTextureXNegAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MODELCARDTEXTUREYNEG
    // --------------------------------------------------------------------- //
    /// In \em cards imaging mode, the texture applied to the Y- quad.
    /// The texture axes (s,t) are mapped to model-space axes (-x, -z).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `asset model:cardTextureYNeg` |
    /// | C++ Type | SdfAssetPath |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Asset |

    UsdAttribute GetModelCardTextureYNegAttr() const;

    /// See GetModelCardTextureYNegAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateModelCardTextureYNegAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MODELCARDTEXTUREZNEG
    // --------------------------------------------------------------------- //
    /// In \em cards imaging mode, the texture applied to the Z- quad.
    /// The texture axes (s,t) are mapped to model-space axes (-x, -y).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `asset model:cardTextureZNeg` |
    /// | C++ Type | SdfAssetPath |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Asset |

    UsdAttribute GetModelCardTextureZNegAttr() const;

    /// See GetModelCardTextureZNegAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateModelCardTextureZNegAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdGeomModelAPI::_GetStaticTfType()
{
    const static TfToken token("UsdGeomModelAPI");
    return token;
}

/* virtual */
inline const TfToken UsdGeomModelAPI::_GetTfTypeToken() const
{
    const static TfToken token("UsdGeomModelAPI");
    return token;
}


inline UsdAttribute UsdGeomModelAPI::GetModelDrawModeAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->modelDrawMode));
}

inline UsdAttribute UsdGeomModelAPI::CreateModelDrawModeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->modelDrawMode), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomModelAPI::GetModelApplyDrawModeAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->modelApplyDrawMode));
}

inline UsdAttribute UsdGeomModelAPI::CreateModelApplyDrawModeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->modelApplyDrawMode), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomModelAPI::GetModelDrawModeColorAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->modelDrawModeColor));
}

inline UsdAttribute UsdGeomModelAPI::CreateModelDrawModeColorAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->modelDrawModeColor), SdfValueTypeNames->Float3,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomModelAPI::GetModelCardGeometryAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->modelCardGeometry));
}

inline UsdAttribute UsdGeomModelAPI::CreateModelCardGeometryAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->modelCardGeometry), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomModelAPI::GetModelCardTextureXPosAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->modelCardTextureXPos));
}

inline UsdAttribute UsdGeomModelAPI::CreateModelCardTextureXPosAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->modelCardTextureXPos), SdfValueTypeNames->Asset,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomModelAPI::GetModelCardTextureYPosAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->modelCardTextureYPos));
}

inline UsdAttribute UsdGeomModelAPI::CreateModelCardTextureYPosAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->modelCardTextureYPos), SdfValueTypeNames->Asset,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomModelAPI::GetModelCardTextureZPosAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->modelCardTextureZPos));
}

inline UsdAttribute UsdGeomModelAPI::CreateModelCardTextureZPosAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->modelCardTextureZPos), SdfValueTypeNames->Asset,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomModelAPI::GetModelCardTextureXNegAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->modelCardTextureXNeg));
}

inline UsdAttribute UsdGeomModelAPI::CreateModelCardTextureXNegAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->modelCardTextureXNeg), SdfValueTypeNames->Asset,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomModelAPI::GetModelCardTextureYNegAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->modelCardTextureYNeg));
}

inline UsdAttribute UsdGeomModelAPI::CreateModelCardTextureYNegAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->modelCardTextureYNeg), SdfValueTypeNames->Asset,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomModelAPI::GetModelCardTextureZNegAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->modelCardTextureZNeg));
}

inline UsdAttribute UsdGeomModelAPI::CreateModelCardTextureZNegAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->modelCardTextureZNeg), SdfValueTypeNames->Asset,
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
