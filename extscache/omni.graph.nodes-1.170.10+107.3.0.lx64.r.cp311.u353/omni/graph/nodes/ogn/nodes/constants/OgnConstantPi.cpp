// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnConstantPiDatabase.h>
#include <omni/math/linalg/math.h>

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnConstantPi
{
public:
    static size_t computeVectorized(OgnConstantPiDatabase& db, size_t count)
    {
        auto ptr = db.outputs.value.vectorized(count);
        auto pFactor = db.inputs.factor.vectorized(count);
        for (size_t i = 0; i < count; ++i)
            ptr[i] = pFactor[i] * M_PI;
        return count;
    }
};

REGISTER_OGN_NODE()

}
}
}
