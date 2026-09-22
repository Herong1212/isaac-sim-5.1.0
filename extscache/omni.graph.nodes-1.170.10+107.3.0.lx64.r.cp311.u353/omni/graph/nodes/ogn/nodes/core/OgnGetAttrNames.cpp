// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include "OgnGetAttrNamesDatabase.h"
#include <algorithm>

namespace omni
{
namespace graph
{
namespace core
{

class OgnGetAttrNames
{
public:
    // Retrieves the names of all of the attributes contained in the input prim, optionally sorted.
    static bool compute(OgnGetAttrNamesDatabase& db)
    {
        auto& inputBundle = db.inputs.data();
        auto attributesInBundle = inputBundle.attributeCount();
        auto& arrayNames = db.outputs.output();
        arrayNames.resize(attributesInBundle);

        // Empty bundles yield empty output arrays, which is okay
        if (attributesInBundle == 0)
        {
            return true;
        }

        // Get all of the bundle member names into the output (as-is for now).
        std::transform(inputBundle.begin(), inputBundle.end(), arrayNames.begin(),
                       [](const ogn::RuntimeAttribute<ogn::kOgnInput, ogn::kCpu>& attribute) -> NameToken
                       { return attribute.name(); });

        // If sorting was requested do that now
        if (db.inputs.sort())
        {
            auto sortByNameString = [&db](const NameToken& a, const NameToken& b) -> bool
            {
                const char* aString = db.tokenToString(a);
                const char* bString = db.tokenToString(b);
                return strcmp(aString, bString) < 0;
            };
            std::sort(arrayNames.data(), arrayNames.data() + attributesInBundle, sortByNameString);
        }
        return true;
    }
};

REGISTER_OGN_NODE()

}
}
}
