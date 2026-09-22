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

/// @file physxSchema/physxParticleIsosurfaceAPI.h

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
// PHYSXPARTICLEISOSURFACEAPI                                                  //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxParticleIsosurfaceAPI
///
/// WARNING: This is a draft API; the design is not fixed and may change in the future.
/// Applied to a PhysxParticleSystem. Defines settings to extract an isosurface from the fluid particles in the particle
/// system. The isosurface extraction is a post-processing step that does not affect the particle dynamics.

class PhysxSchemaPhysxParticleIsosurfaceAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxParticleIsosurfaceAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxParticleIsosurfaceAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxParticleIsosurfaceAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxParticleIsosurfaceAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxParticleIsosurfaceAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxParticleIsosurfaceAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxParticleIsosurfaceAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxParticleIsosurfaceAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxParticleIsosurfaceAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxParticleIsosurfaceAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxParticleIsosurfaceAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxParticleIsosurfaceAPI>())
        {
            return PhysxSchemaPhysxParticleIsosurfaceAPI(prim);
        }
        return PhysxSchemaPhysxParticleIsosurfaceAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // ISOSURFACEENABLED
    // --------------------------------------------------------------------- //
    /// Enable or disable the creation of an isosurface.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxParticleIsosurface:isosurfaceEnabled = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetIsosurfaceEnabledAttr() const;

    /// See GetIsosurfaceEnabledAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateIsosurfaceEnabledAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MAXVERTICES
    // --------------------------------------------------------------------- //
    /// Maximum number of vertices the extracted isosurface can have.
    /// Range: [3, inf)
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform int physxParticleIsosurface:maxVertices = 1048576` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetMaxVerticesAttr() const;

    /// See GetMaxVerticesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaxVerticesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MAXTRIANGLES
    // --------------------------------------------------------------------- //
    /// Maximum number of triangles the extracted isosurface can have.
    /// Range: [1, inf)
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform int physxParticleIsosurface:maxTriangles = 2097152` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetMaxTrianglesAttr() const;

    /// See GetMaxTrianglesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaxTrianglesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MAXSUBGRIDS
    // --------------------------------------------------------------------- //
    /// Maximum number of blocks the sparse grid structure can contain.
    /// Range: [1, inf)
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform int physxParticleIsosurface:maxSubgrids = 2048` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetMaxSubgridsAttr() const;

    /// See GetMaxSubgridsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaxSubgridsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // GRIDSPACING
    // --------------------------------------------------------------------- //
    /// Cell Size of the grid used for isosurface extraction. Default value -inf results in a simulation-determined
    /// value. Range: [0, inf) Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxParticleIsosurface:gridSpacing = -inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetGridSpacingAttr() const;

    /// See GetGridSpacingAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateGridSpacingAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SURFACEDISTANCE
    // --------------------------------------------------------------------- //
    /// Distance from particle center to isosurface. Default value -inf results in a simulation-determined value.
    /// Range: [0, 2.5*gridSpacing)
    /// Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxParticleIsosurface:surfaceDistance = -inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSurfaceDistanceAttr() const;

    /// See GetSurfaceDistanceAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSurfaceDistanceAttr() const;

public:
    // --------------------------------------------------------------------- //
    // GRIDFILTERINGPASSES
    // --------------------------------------------------------------------- //
    /// Grid filtering sequence, defined as capital letters "S":Smooth, "G":Grow, "R":Reduce. Up to 32 passes.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `string physxParticleIsosurface:gridFilteringPasses = "GSRS"` |
    /// | C++ Type | std::string |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->String |

    UsdAttribute GetGridFilteringPassesAttr() const;

    /// See GetGridFilteringPassesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateGridFilteringPassesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // GRIDSMOOTHINGRADIUS
    // --------------------------------------------------------------------- //
    /// The radius used during the smoothing process on the grid. Default value -inf results in a simulation-determined
    /// value. Range: [0, inf) Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxParticleIsosurface:gridSmoothingRadius = -inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetGridSmoothingRadiusAttr() const;

    /// See GetGridSmoothingRadiusAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateGridSmoothingRadiusAttr() const;

public:
    // --------------------------------------------------------------------- //
    // NUMMESHSMOOTHINGPASSES
    // --------------------------------------------------------------------- //
    /// Number of smoothing passes applied to the generated isosurface triangle mesh.
    /// Range: [0, inf)
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int physxParticleIsosurface:numMeshSmoothingPasses = 4` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |

    UsdAttribute GetNumMeshSmoothingPassesAttr() const;

    /// See GetNumMeshSmoothingPassesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateNumMeshSmoothingPassesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // NUMMESHNORMALSMOOTHINGPASSES
    // --------------------------------------------------------------------- //
    /// Number of smoothing passes applied to the normals of the generated isosurface triangle mesh.
    /// Range: [0, inf)
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int physxParticleIsosurface:numMeshNormalSmoothingPasses = 4` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |

    UsdAttribute GetNumMeshNormalSmoothingPassesAttr() const;

    /// See GetNumMeshNormalSmoothingPassesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateNumMeshNormalSmoothingPassesAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxParticleIsosurfaceAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxParticleIsosurfaceAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxParticleIsosurfaceAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxParticleIsosurfaceAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxParticleIsosurfaceAPI::GetIsosurfaceEnabledAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxParticleIsosurfaceIsosurfaceEnabled));
}

inline UsdAttribute PhysxSchemaPhysxParticleIsosurfaceAPI::CreateIsosurfaceEnabledAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxParticleIsosurfaceIsosurfaceEnabled),
                                     SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleIsosurfaceAPI::GetMaxVerticesAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxParticleIsosurfaceMaxVertices));
}

inline UsdAttribute PhysxSchemaPhysxParticleIsosurfaceAPI::CreateMaxVerticesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxParticleIsosurfaceMaxVertices),
                                     SdfValueTypeNames->Int,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleIsosurfaceAPI::GetMaxTrianglesAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxParticleIsosurfaceMaxTriangles));
}

inline UsdAttribute PhysxSchemaPhysxParticleIsosurfaceAPI::CreateMaxTrianglesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxParticleIsosurfaceMaxTriangles),
                                     SdfValueTypeNames->Int,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleIsosurfaceAPI::GetMaxSubgridsAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxParticleIsosurfaceMaxSubgrids));
}

inline UsdAttribute PhysxSchemaPhysxParticleIsosurfaceAPI::CreateMaxSubgridsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxParticleIsosurfaceMaxSubgrids),
                                     SdfValueTypeNames->Int,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleIsosurfaceAPI::GetGridSpacingAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxParticleIsosurfaceGridSpacing));
}

inline UsdAttribute PhysxSchemaPhysxParticleIsosurfaceAPI::CreateGridSpacingAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxParticleIsosurfaceGridSpacing),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleIsosurfaceAPI::GetSurfaceDistanceAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxParticleIsosurfaceSurfaceDistance));
}

inline UsdAttribute PhysxSchemaPhysxParticleIsosurfaceAPI::CreateSurfaceDistanceAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxParticleIsosurfaceSurfaceDistance),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleIsosurfaceAPI::GetGridFilteringPassesAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxParticleIsosurfaceGridFilteringPasses));
}

inline UsdAttribute PhysxSchemaPhysxParticleIsosurfaceAPI::CreateGridFilteringPassesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxParticleIsosurfaceGridFilteringPasses),
                                     SdfValueTypeNames->String,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleIsosurfaceAPI::GetGridSmoothingRadiusAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxParticleIsosurfaceGridSmoothingRadius));
}

inline UsdAttribute PhysxSchemaPhysxParticleIsosurfaceAPI::CreateGridSmoothingRadiusAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxParticleIsosurfaceGridSmoothingRadius),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleIsosurfaceAPI::GetNumMeshSmoothingPassesAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxParticleIsosurfaceNumMeshSmoothingPasses));
}

inline UsdAttribute PhysxSchemaPhysxParticleIsosurfaceAPI::CreateNumMeshSmoothingPassesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxParticleIsosurfaceNumMeshSmoothingPasses),
                                     SdfValueTypeNames->Int,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxParticleIsosurfaceAPI::GetNumMeshNormalSmoothingPassesAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxParticleIsosurfaceNumMeshNormalSmoothingPasses));
}

inline UsdAttribute PhysxSchemaPhysxParticleIsosurfaceAPI::CreateNumMeshNormalSmoothingPassesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxParticleIsosurfaceNumMeshNormalSmoothingPasses),
                                     SdfValueTypeNames->Int,
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
