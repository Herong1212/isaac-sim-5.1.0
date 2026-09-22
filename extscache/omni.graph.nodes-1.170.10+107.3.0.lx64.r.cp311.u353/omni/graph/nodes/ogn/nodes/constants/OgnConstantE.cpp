// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnConstantEDatabase.h>
#include <omni/math/linalg/math.h>

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnConstantE
{
public:
    static size_t computeVectorized(OgnConstantEDatabase& db, size_t count)
    {
        auto value = db.outputs.value.vectorized(count);
        auto exp = db.inputs.exponent.vectorized(count);
        for (size_t i = 0; i < count; ++i)
            value[i] = std::pow(M_E, exp[i]);
        return count;
    }
};

REGISTER_OGN_NODE()

}
}
}
