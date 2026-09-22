// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "OgnGetPrimsDatabase.h"
#include "PrimCommon.h"

namespace omni
{
namespace graph
{
namespace nodes
{
class OgnGetPrims
{
public:
    static bool compute(OgnGetPrimsDatabase& db)
    {
        IBundle2* outputBundle = db.outputs.bundle().abi_bundleInterface();
        outputBundle->clearContents(true);

        IConstBundle2* inputBundle = db.inputs.bundle().abi_bundleInterface();
        size_t const childBundleCount = inputBundle->getChildBundleCount();

        // nothing to do
        if (childBundleCount == 0)
        {
            return true;
        }

        std::vector<ConstBundleHandle> childBundleHandles(childBundleCount);
        inputBundle->getConstChildBundles(childBundleHandles.data(), childBundleHandles.size());

        std::vector<ConstBundleHandle> bundles;
        bundles.reserve(childBundleCount);

        GraphContextObj const& context = db.abi_context();

        if (db.inputs.prims().size() != 0)
        {
            // We want to have same order of `prims` input in the output.
            // Unfortunately, the order of child bundles is not preserved, OM-

            // Construct children lookup map
            std::unordered_map<fabric::TokenC, ConstBundleHandle> pathToChildMap;
            for (ConstBundleHandle const& childBundleHandle : childBundleHandles)
            {
                ConstAttributeDataHandle const attr =
                    getAttributeR(context, childBundleHandle, PrimAdditionalAttrs::kSourcePrimPathToken);
                if (fabric::Token const* data = getDataR<fabric::Token>(context, attr))
                {
                    pathToChildMap.emplace(data->asTokenC(), childBundleHandle);
                }
            }

            // Search for inputTargets
            auto const& inputPrims = db.inputs.prims();
            for (auto const& inputTarget : inputPrims)
            {
                auto const asToken = fabric::asInt(fabric::toSdfPath(inputTarget).GetToken());
                if (auto it = pathToChildMap.find(asToken); it != pathToChildMap.end())
                {
                    bundles.push_back(it->second);
                }
            }
        }
        else
        {
            // By default all primitives matching the path/type patterns are added to the output bundle;
            // when the "inverse" option is on, all mismatching primitives will be added instead.
            bool const inverse = db.inputs.inverse();

            // Use wildcard pattern matching for prim type.
            std::string const typePattern(db.inputs.typePattern());
            PatternMatcher const typeMatcher(typePattern);

            // Use wildcard pattern matching for prim path.
            std::string const pathPattern(db.inputs.pathPattern());
            PatternMatcher const pathMatcher(pathPattern);

            auto matchesPattern =
                [&context](ConstBundleHandle& bundle, NameToken attrName, PatternMatcher const& patternMatcher)
            {
                ConstAttributeDataHandle attr = getAttributeR(context, bundle, attrName);
                return attr.isValid() && patternMatcher.matches(*getDataR<NameToken>(context, attr));
            };

            for (ConstBundleHandle& childBundleHandle : childBundleHandles)
            {
                bool const matched =
                    matchesPattern(childBundleHandle, PrimAdditionalAttrs::kSourcePrimTypeToken, typeMatcher) &&
                    matchesPattern(childBundleHandle, PrimAdditionalAttrs::kSourcePrimPathToken, pathMatcher);
                if (matched != inverse)
                {
                    bundles.push_back(childBundleHandle);
                }
            }
        }

        if (!bundles.empty())
        {
            outputBundle->copyChildBundles(bundles.data(), bundles.size());
        }

        return true;
    }
};

REGISTER_OGN_NODE()

} // nodes
} // graph
} // omni
