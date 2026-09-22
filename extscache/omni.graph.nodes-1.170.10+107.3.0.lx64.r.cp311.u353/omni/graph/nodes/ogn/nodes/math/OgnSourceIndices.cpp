// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnSourceIndicesDatabase.h>

class OgnSourceIndices
{
public:
    static bool compute(OgnSourceIndicesDatabase& db)
    {
        auto inputValues = db.inputs.sourceStartsInTarget();
        auto sourceCount = inputValues.size();
        auto sourceIndices = db.outputs.sourceIndices();

        if (sourceCount <= 1)
        {
            sourceIndices.resize(0);
            return true;
        }
        --sourceCount;

        int32_t targetCount = inputValues[sourceCount];
        if (targetCount < 0)
        {
            sourceIndices.resize(0);
            return true;
        }

        sourceIndices.resize(targetCount);

        int32_t i = 0;
        for (size_t sourcei = 0; sourcei < sourceCount; ++sourcei)
        {
            const int32_t sourceEnd = inputValues[sourcei + 1];
            while (i < sourceEnd)
            {
                sourceIndices[i] = (int32_t)sourcei;
                ++i;
            }
        }

        return true;
    }
};

REGISTER_OGN_NODE()
