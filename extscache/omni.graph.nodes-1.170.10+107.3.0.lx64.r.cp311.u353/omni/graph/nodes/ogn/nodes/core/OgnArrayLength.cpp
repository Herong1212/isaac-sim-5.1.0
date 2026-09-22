// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include "OgnArrayLengthDatabase.h"

namespace omni
{
namespace graph
{
namespace core
{

class OgnArrayLength
{
public:
    // Outputs the length of a specified array attribute in an input prim,
    // or 1 if the attribute is not an array attribute.
    static bool compute(OgnArrayLengthDatabase& db)
    {
        auto bundledAttribute = db.inputs.data().attributeByName(db.inputs.attrName());
        db.outputs.length() = bundledAttribute.isValid() ? bundledAttribute.size() : 0;

        return true;
    }
};

REGISTER_OGN_NODE()

}
}
}
