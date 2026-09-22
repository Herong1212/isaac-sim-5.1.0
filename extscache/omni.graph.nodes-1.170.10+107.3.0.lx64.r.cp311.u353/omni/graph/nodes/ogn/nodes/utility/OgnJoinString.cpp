// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnJoinStringDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include "CoverageUtils.h"


namespace omni
{
namespace graph
{
namespace nodes
{

class OgnJoinString
{
public:
    static size_t computeVectorized(OgnJoinStringDatabase& db, size_t count)
    {
        auto tokenInterface = carb::getCachedInterface<omni::fabric::IToken>();
        FIREWALL_RET_ERROR(db, !tokenInterface, 0, "Failed to initialize token interface"); // LCOV_EXCL_LINE

        try
        {
            for (size_t idx = 0; idx < count; ++idx)
            {
                const auto& input = db.inputs.elements(idx);
                const auto& delimiter = db.inputs.delimiter(idx);

                std::string outString;
                if (!input.empty())
                {
                    for (size_t i = 0; i < input.size(); i++)
                    {
                        if (input[i] != omni::fabric::kUninitializedToken)
                        {
                            if (i > 0 && !delimiter.empty())
                                outString += delimiter;
                            outString += tokenInterface->getText(input[i]);
                        }
                    }
                }

                db.outputs.string(idx) = outString;
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
