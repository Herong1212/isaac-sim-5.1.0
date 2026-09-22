// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnPartialSumDatabase.h>
#include <numeric>

class OgnPartialSum
{
public:
    static bool compute(OgnPartialSumDatabase& db)
    {
        auto inputs = db.inputs.array();
        auto outputs = db.outputs.partialSum();
        outputs.resize(inputs.size() + 1);
        outputs[0] = 0;
        std::partial_sum(inputs.begin(), inputs.end(), outputs.begin() + 1);
        return true;
    }
};

REGISTER_OGN_NODE()
