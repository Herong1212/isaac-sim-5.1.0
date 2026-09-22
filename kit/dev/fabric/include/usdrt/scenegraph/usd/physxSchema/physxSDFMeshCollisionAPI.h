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

/// @file physxSchema/physxSDFMeshCollisionAPI.h

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
// PHYSXSDFMESHCOLLISIONAPI                                                    //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxSDFMeshCollisionAPI
///
/// PhysX SDF mesh extended parameters
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref PhysxSchemaTokens.
/// So to set an attribute to the value "rightHanded", use PhysxSchemaTokens->rightHanded
/// as the value.

class PhysxSchemaPhysxSDFMeshCollisionAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxSDFMeshCollisionAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxSDFMeshCollisionAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxSDFMeshCollisionAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxSDFMeshCollisionAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxSDFMeshCollisionAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxSDFMeshCollisionAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxSDFMeshCollisionAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxSDFMeshCollisionAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxSDFMeshCollisionAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxSDFMeshCollisionAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxSDFMeshCollisionAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxSDFMeshCollisionAPI>())
        {
            return PhysxSchemaPhysxSDFMeshCollisionAPI(prim);
        }
        return PhysxSchemaPhysxSDFMeshCollisionAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // SDFRESOLUTION
    // --------------------------------------------------------------------- //
    /// The spacing of the uniformly sampled SDF is equal to the largest AABB extent of the mesh, divided by the
    /// resolution. Choose the lowest possible resolution that provides acceptable performance; very high resolution
    /// results in large memory consumption, and slower cooking and simulation performance. Range: (1, inf)
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform int physxSDFMeshCollision:sdfResolution = 256` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetSdfResolutionAttr() const;

    /// See GetSdfResolutionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSdfResolutionAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SDFSUBGRIDRESOLUTION
    // --------------------------------------------------------------------- //
    /// A positive subgrid resolution enables sparsity on signed-distance-fields (SDF) while a value of 0 leads
    /// to the usage of a dense SDF. A value in the range of 4 to 8 is a reasonable compromise between block size and
    /// the overhead introduced by block addressing. The smaller a block, the more memory is spent on the address
    /// table. The bigger a block, the less precisely the sparse SDF can adapt to the mesh's surface. In most cases
    /// sparsity reduces the memory consumption of a SDF significantly.
    /// Range: [0, inf)
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform int physxSDFMeshCollision:sdfSubgridResolution = 6` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetSdfSubgridResolutionAttr() const;

    /// See GetSdfSubgridResolutionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSdfSubgridResolutionAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SDFBITSPERSUBGRIDPIXEL
    // --------------------------------------------------------------------- //
    /// Values of 8, 16 and 32 bits per subgrid pixel are supported. Dense SDFs always use 32 bits per pixel. The
    /// less bits per pixel, the smaller the resulting SDF but also the less precise. The SDF's memory consumption
    /// scales proportionally with the number of bits per subgrid pixel.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token physxSDFMeshCollision:sdfBitsPerSubgridPixel = "BitsPerPixel16"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref PhysxSchemaTokens "Allowed Values" | BitsPerPixel8, BitsPerPixel16, BitsPerPixel32 |

    UsdAttribute GetSdfBitsPerSubgridPixelAttr() const;

    /// See GetSdfBitsPerSubgridPixelAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSdfBitsPerSubgridPixelAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SDFNARROWBANDTHICKNESS
    // --------------------------------------------------------------------- //
    /// Size of the narrow band around the mesh surface where high resolution SDF samples are available. Outside
    /// of the narrow band, only low resolution samples are stored. Representing the narrow band thickness as a fraction
    /// of the mesh's bounding box diagonal length ensures that it is scale independent. A value of 0.01 is usually
    /// large enough. The smaller the narrow band thickness, the smaller the memory consumption of the sparse SDF.
    /// Range: [0, 1]
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform float physxSDFMeshCollision:sdfNarrowBandThickness = 0.01` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetSdfNarrowBandThicknessAttr() const;

    /// See GetSdfNarrowBandThicknessAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSdfNarrowBandThicknessAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SDFMARGIN
    // --------------------------------------------------------------------- //
    /// Margin to increase the size of the SDF relative to the bounding box diagonal length of the mesh. A sdf
    /// margin value of 0.01 means the sdf boundary will be enlarged in any direction by 1% of the mesh's bounding box
    /// diagonal length. Representing the margin relative to the bounding box diagonal length ensures that it is scale
    /// independent. Margins allow for precise distance queries in a region slightly outside of the mesh's bounding box.
    /// Range: [0, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform float physxSDFMeshCollision:sdfMargin = 0.01` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetSdfMarginAttr() const;

    /// See GetSdfMarginAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSdfMarginAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SDFENABLEREMESHING
    // --------------------------------------------------------------------- //
    /// Enables optional remeshing as a preprocessing step before the SDF is computed. Remeshing can help generate
    /// valid SDF data even if the input mesh has bad properties like inconsistent winding or self-intersections. The
    /// SDF distances (and therefore the collisions) will be slightly less accurate when remeshing is enabled.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform bool physxSDFMeshCollision:sdfEnableRemeshing = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetSdfEnableRemeshingAttr() const;

    /// See GetSdfEnableRemeshingAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSdfEnableRemeshingAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SDFTRIANGLECOUNTREDUCTIONFACTOR
    // --------------------------------------------------------------------- //
    /// Factor that quantifies the percentage of the input triangles to keep. 1 means the input triangle mesh does not
    /// get modified. 0.5 would mean that the triangle count gets reduced to half the amount of the original mesh such
    /// that the collider needs to process less data. This helps to speed up collision detection at the cost of a small
    /// geometric error. Range: [0, 1] Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform float physxSDFMeshCollision:sdfTriangleCountReductionFactor = 1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetSdfTriangleCountReductionFactorAttr() const;

    /// See GetSdfTriangleCountReductionFactorAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSdfTriangleCountReductionFactorAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxSDFMeshCollisionAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxSDFMeshCollisionAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxSDFMeshCollisionAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxSDFMeshCollisionAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxSDFMeshCollisionAPI::GetSdfResolutionAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSDFMeshCollisionSdfResolution));
}

inline UsdAttribute PhysxSchemaPhysxSDFMeshCollisionAPI::CreateSdfResolutionAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSDFMeshCollisionSdfResolution),
                                     SdfValueTypeNames->Int,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSDFMeshCollisionAPI::GetSdfSubgridResolutionAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSDFMeshCollisionSdfSubgridResolution));
}

inline UsdAttribute PhysxSchemaPhysxSDFMeshCollisionAPI::CreateSdfSubgridResolutionAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSDFMeshCollisionSdfSubgridResolution),
                                     SdfValueTypeNames->Int,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSDFMeshCollisionAPI::GetSdfBitsPerSubgridPixelAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSDFMeshCollisionSdfBitsPerSubgridPixel));
}

inline UsdAttribute PhysxSchemaPhysxSDFMeshCollisionAPI::CreateSdfBitsPerSubgridPixelAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSDFMeshCollisionSdfBitsPerSubgridPixel),
                                     SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSDFMeshCollisionAPI::GetSdfNarrowBandThicknessAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSDFMeshCollisionSdfNarrowBandThickness));
}

inline UsdAttribute PhysxSchemaPhysxSDFMeshCollisionAPI::CreateSdfNarrowBandThicknessAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSDFMeshCollisionSdfNarrowBandThickness),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSDFMeshCollisionAPI::GetSdfMarginAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSDFMeshCollisionSdfMargin));
}

inline UsdAttribute PhysxSchemaPhysxSDFMeshCollisionAPI::CreateSdfMarginAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSDFMeshCollisionSdfMargin), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSDFMeshCollisionAPI::GetSdfEnableRemeshingAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSDFMeshCollisionSdfEnableRemeshing));
}

inline UsdAttribute PhysxSchemaPhysxSDFMeshCollisionAPI::CreateSdfEnableRemeshingAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSDFMeshCollisionSdfEnableRemeshing),
                                     SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxSDFMeshCollisionAPI::GetSdfTriangleCountReductionFactorAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxSDFMeshCollisionSdfTriangleCountReductionFactor));
}

inline UsdAttribute PhysxSchemaPhysxSDFMeshCollisionAPI::CreateSdfTriangleCountReductionFactorAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxSDFMeshCollisionSdfTriangleCountReductionFactor),
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
