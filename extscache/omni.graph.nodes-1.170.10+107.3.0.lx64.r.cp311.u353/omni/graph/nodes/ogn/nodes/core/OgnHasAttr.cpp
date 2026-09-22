// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include "OgnHasAttrDatabase.h"

namespace omni
{
namespace graph
{
namespace core
{

class OgnHasAttr
{
public:
    // Checks whether an input prim contains the specified attribute
    static bool compute(OgnHasAttrDatabase& db)
    {
        db.outputs.output() = db.inputs.data().attributeByName(db.inputs.attrName()).isValid();
        return true;
    }
};

REGISTER_OGN_NODE()

}
}
}
