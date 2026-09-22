// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include "OgnRenameAttrDatabase.h"
#include "TokenUtils.h"

#include <algorithm>
#include <string>
#include <unordered_map>
#include <vector>

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnRenameAttr
{
public:
    // Changes the names of attributes from an input prim for the corresponding output prim.
    // Attributes not renamed will be copied from the input prim to the output prim without changing the name.
    static bool compute(OgnRenameAttrDatabase& db)
    {
        const auto& inputBundle = db.inputs.data();
        auto& outputBundle = db.outputs.data();

        // Find all of the attribute names for selection.
        std::vector<NameToken> inputAttrNames;
        std::vector<NameToken> outputAttrNames;
        TokenHelper::splitNames(db.tokenToString(db.inputs.inputAttrNames()), inputAttrNames);
        TokenHelper::splitNames(db.tokenToString(db.inputs.outputAttrNames()), outputAttrNames);

        size_t nameCount = std::min(inputAttrNames.size(), outputAttrNames.size());
        if (nameCount == 0)
        {
            // No renaming, so we can just copy the input data into the output.
            outputBundle = inputBundle;
            return true;
        }

        // Mismatched name sizes are dealt with going with the minimum number, and reporting this warning
        if (inputAttrNames.size() != outputAttrNames.size())
        {
            db.logWarning("Input name size %zu != output name size %zu", inputAttrNames.size(), outputAttrNames.size());
            // Reduce the size of the name arrays to make them easier to look up later
            inputAttrNames.resize(nameCount);
            outputAttrNames.resize(nameCount);
        }

        // Zip them together so that iterators can be used to find matches
        std::unordered_map<NameToken, NameToken> attrNameMap;
        std::transform(inputAttrNames.begin(), inputAttrNames.end(), outputAttrNames.begin(),
                       std::inserter(attrNameMap, attrNameMap.end()),
                       [](NameToken a, NameToken b) { return std::make_pair(a, b); });

        // Start from an empty output prim.
        outputBundle.clear();

        // Loop through the attributes on the input bundle, adding them to the output and renaming if they appear
        // on the list.
        for (const auto& input : inputBundle)
        {
            CARB_ASSERT(input.isValid());
            auto newName = input.name();

            // If the attribute's name is in the renaming list then rename it
            auto itNameFound = attrNameMap.find(input.name());
            if (itNameFound != attrNameMap.end())
            {
                newName = itNameFound->second;
            }
            outputBundle.insertAttribute(input, newName);
        }
        return true;
    }
};

REGISTER_OGN_NODE()

} // nodes
} // graph
} // omni
