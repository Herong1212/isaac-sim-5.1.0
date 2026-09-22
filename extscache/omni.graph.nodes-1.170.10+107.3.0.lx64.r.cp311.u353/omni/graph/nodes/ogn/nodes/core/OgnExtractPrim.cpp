// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

// clang-format off
#include "UsdPCH.h"
// clang-format on

#include "OgnExtractPrimDatabase.h"
#include "ReadPrimCommon.h"

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnExtractPrim
{
public:
    // Copies attributes from an input bundle to attributes directly on the node
    static bool compute(OgnExtractPrimDatabase& db)
    {
        auto& contextObj = db.abi_context();
        auto const& inputPrims = db.inputs.prims();

        // The computation should only be performed when input bundle or prim or prim path changes.
        // At this moment, unfortunately, there is no way to find out if incoming bundle has changed.
        // That means we have to recompute all the time.
        // Extracting bundles is a O(n) operation in worse case. If the number of children in the input bundle
        // is substantial, then we can get significant performance slow down.
        // When Dirty IDs interface is in place, this function should be updated to recompute only
        // when input bundle, or prim path is out of date.
        // Suggestion: an internal cache - a map of path to child bundle handle could be sufficient.
        ConstBundleHandle extractedHandle{ ConstBundleHandle::invalidValue() };
        if (db.inputs.prim().size() == 0)
        {
            // extract child bundle using input prim path
            std::string const pathStr{ db.inputs.primPath() };
            if (PXR_NS::SdfPath::IsValidPathString(pathStr))
            {
                auto primPath = omni::fabric::asInt(PXR_NS::TfToken(pathStr.data()));
                extractedHandle = extractPrimByPath(contextObj, inputPrims, primPath);
            }
        }
        else
        {
            if (db.inputs.prim().size() > 1)
                db.logWarning("Only one prim target is supported, the rest will be ignored");
            extractedHandle = extractPrimByPath(contextObj, inputPrims, db.pathToToken(db.inputs.prim()[0]));
        }

        // update outputs
        BundleType extractedBundle(contextObj, extractedHandle);
        db.outputs.primBundle() = extractedBundle;
        return extractedBundle.isValid();
    }
};

REGISTER_OGN_NODE()

} // nodes
} // graph
} // omni
