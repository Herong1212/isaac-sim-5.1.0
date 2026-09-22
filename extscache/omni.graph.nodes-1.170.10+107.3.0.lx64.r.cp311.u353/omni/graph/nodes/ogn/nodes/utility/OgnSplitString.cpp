// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnSplitStringDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include "CoverageUtils.h"


namespace omni
{
namespace graph
{
namespace nodes
{

class OgnSplitString
{
public:
    static size_t computeVectorized(OgnSplitStringDatabase& db, size_t count)
    {
        auto tokenInterface = carb::getCachedInterface<omni::fabric::IToken>();
        FIREWALL_RET_ERROR(db, !tokenInterface, 0, "Failed to initialize token interface"); // LCOV_EXCL_LINE

        try
        {
            for (size_t idx = 0; idx < count; ++idx)
            {
                const auto& inString = db.inputs.string(idx);
                const auto& inDelimiter = db.inputs.delimiter(idx);
                auto& output = db.outputs.elements(idx);

                if (!inString.empty() && !inDelimiter.empty())
                {
                    size_t pos_start = 0;
                    size_t pos_end = 0;
                    std::vector<OgnToken> outElements;
                    std::string_view splitString(inString.data(), inString.size());
                    std::string_view delimiter(inDelimiter.data(), inDelimiter.size());
                    while ((pos_end = splitString.find(delimiter, pos_start)) != std::string::npos)
                    {
                        auto element = std::string(splitString.substr(pos_start, pos_end - pos_start));
                        pos_start = pos_end + delimiter.length();
                        outElements.push_back(tokenInterface->getHandle(element.c_str()));
                    }
                    outElements.push_back(tokenInterface->getHandle(std::string(splitString.substr(pos_start)).c_str()));

                    if (!outElements.empty())
                    {
                        output.resize(outElements.size());
                        memcpy(output.data(), outElements.data(), sizeof(OgnToken) * outElements.size());
                    }
                }
                else
                    output.resize(0);
            }
            return count;
        }
        // LCOV_EXCL_START
        catch (ogn::compute::InputError& error)
        {
            db.logError(error.what());
        }
        return 0;
        // LCOV_EXCL_STOP
    }
};


REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
