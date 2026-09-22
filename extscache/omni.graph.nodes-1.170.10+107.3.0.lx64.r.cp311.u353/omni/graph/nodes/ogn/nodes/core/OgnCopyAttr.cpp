// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include "OgnCopyAttrDatabase.h"
#include "TokenUtils.h"

#include <algorithm>
#include <cstring>
#include <string>
#include <vector>

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnCopyAttr
{
public:
    // Copies all attributes from one input prim and specified attributes from a
    // second input prim to the output prim.
    static bool compute(OgnCopyAttrDatabase& db)
    {
        const auto& fullInputBundle = db.inputs.fullData();
        auto& outputBundle = db.outputs.data();

        // Set up the output, first by copying the input 'fullData' into the output if it exists, else clearing it
        outputBundle = db.inputs.fullData();
        if (!outputBundle.isValid())
        {
            // LCOV_EXCL_START : Firewall - should never happen
            db.logError("Failed to copy entire input bundle to the output");
            return false;
            // LCOV_EXCL_STOP
        }

        // Find all of the attribute names for selection.
        std::vector<NameToken> inputAttrNames;
        std::vector<NameToken> outputAttrNames;
        if (!TokenHelper::splitNames(db.tokenToString(db.inputs.inputAttrNames()), inputAttrNames) ||
            !TokenHelper::splitNames(db.tokenToString(db.inputs.outputAttrNames()), outputAttrNames))
        {
            // LCOV_EXCL_START : Firewall - should never happen
            db.logError("Could not parse the attribute names");
            return false;
            // LCOV_EXCL_STOP
        }

        // Mismatched name sizes are dealt with going with the minimum number, and reporting this warning
        if (inputAttrNames.size() != outputAttrNames.size())
        {
            db.logWarning("Input name size %zu != output name size %zu", inputAttrNames.size(), outputAttrNames.size());
        }
        // Loop through the name list, adding attributes from the input
        size_t nameCount = std::min(inputAttrNames.size(), outputAttrNames.size());
        if (nameCount == 0)
        {
            return true;
        }

        // Figure out which bundle is to be used for renamed attributes
        const auto& partialInputBundle = db.inputs.partialData();
        const auto& renamingBundle = partialInputBundle.isValid() ? partialInputBundle : fullInputBundle;

        for (size_t name_index = 0; name_index < nameCount; ++name_index)
        {
            auto bundledAttribute = renamingBundle.attributeByName(inputAttrNames[name_index]);
            if (!bundledAttribute.isValid())
            {
                db.logWarning("Input attribute '%s' not found in bundle", db.tokenToString(inputAttrNames[name_index]));
                continue;
            }
            outputBundle.insertAttribute(bundledAttribute, outputAttrNames[name_index]);
        }
        return true;
    }
};

REGISTER_OGN_NODE()

} // nodes
} // graph
} // omni
