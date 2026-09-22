// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include "OgnRemoveAttrDatabase.h"
#include "TokenUtils.h"
#include "PrimCommon.h"

#include <algorithm>
#include <unordered_set>

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnRemoveAttr
{
public:
    // Copies all attributes from an input prim to the output prim, except for any specified to be removed.
    static bool compute(OgnRemoveAttrDatabase& db)
    {
        auto& inputBundle = db.inputs.data();
        auto& outputBundle = db.outputs.data();

        outputBundle = inputBundle;

        // Use pattern matching to find the attribute names.
        std::vector<NameToken> attributes(outputBundle.attributeCount());
        outputBundle.abi_bundleInterface()->getAttributeNames(attributes.data(), attributes.size());

        std::vector<NameToken> remove;
        remove.reserve(outputBundle.attributeCount());

        std::string const& attrNamesToRemove = toTfToken(db.inputs.attrNamesToRemove()).GetString();
        PatternMatcher attrNameMatcher{ attrNamesToRemove };

        // allow removing primitive internal attributes
        if (!db.inputs.allowRemovePrimInternal())
            attrNameMatcher.addExcludeTokens(getPrimAdditionalAttrs().names);

        for (auto attribute : attributes)
        {
            if (attrNameMatcher && attrNameMatcher.matches(attribute))
            {
                remove.push_back(attribute);
            }
        }

        if (!remove.empty())
        {
            outputBundle.removeAttributes(remove.size(), remove.data());
        }

        return true;
    }
};

REGISTER_OGN_NODE()

} // nodes
} // graph
} // omni
