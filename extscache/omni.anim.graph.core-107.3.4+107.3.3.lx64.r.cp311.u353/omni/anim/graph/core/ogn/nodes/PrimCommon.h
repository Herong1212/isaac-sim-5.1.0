// Copyright (c) 2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include <omni/graph/core/PreUsdInclude.h>
#include <pxr/usd/usd/common.h>
#include <omni/graph/core/PostUsdInclude.h>

#include <omni/fabric/IFabric.h>
#include <omni/fabric/FabricUSD.h>
#include <omni/graph/core/Handle.h>
#include <gsl/span>

#include <tuple>
#include <vector>

namespace omni
{
namespace anim
{
namespace graph
{
using PXR_NS::UsdTimeCode;

/// Returns the FabricId and stage for the graph of that given node, or nullptr on failure
std::tuple<omni::fabric::FabricId, PXR_NS::UsdStageRefPtr> getFabricForNode(const GraphContextObj& graphContext,
                                                                         const NodeObj& nodeObj);

/// Get the prim path from a relationship. Throws std::runtime_error on failure. If `throwOnNoPrimSpecified` is
/// false it will return the empty path instead of throwing.
PXR_NS::SdfPath getRelationshipPrimPath(const omni::graph::core::GraphContextObj& context,
                                     const omni::graph::core::NodeObj& nodeObj,
                                     PXR_NS::TfToken primInput,
                                     bool throwOnNoPrimSpecified = true);

// Helper to find the USD Attribute which is indicated by the input attribute settings
PXR_NS::UsdAttribute findSelectedVariable(omni::graph::core::GraphContextObj const& context,
                                        omni::graph::core::NodeObj const& nodeObj, bool isTargetAttr);


/// Returns the skeleton root path input pin, or the graph target if the former was not set or it was invalid
template <class Database>
const char* getSkeletonRootPath(const Database& db)
{
    const char* skelRootPathInput = db.tokenToString(db.inputs.skelRootPath());
    if (skelRootPathInput && strlen(skelRootPathInput) > 0)
    {
        return skelRootPathInput;
    }
    return db.tokenToString(db.getGraphTarget());
}

namespace state
{
constexpr bool InvalidInput = false;
constexpr bool NotPlaying = false;
} // error

} // graph
} // anim
} // omni
