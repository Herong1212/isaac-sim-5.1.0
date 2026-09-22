// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include "OgnAttrTypeDatabase.h"

namespace omni
{
namespace graph
{
namespace core
{

class OgnAttrType
{
public:
    // Queries information about the type of a specified attribute in an input prim
    static bool compute(OgnAttrTypeDatabase& db)
    {
        auto bundledAttribute = db.inputs.data().attributeByName(db.inputs.attrName());
        if (!bundledAttribute.isValid())
        {
            db.outputs.baseType() = -1;
            db.outputs.componentCount() = -1;
            db.outputs.arrayDepth() = -1;
            db.outputs.role() = -1;
            db.outputs.fullType() = -1;
        }
        else
        {
            auto& attributeType = bundledAttribute.type();
            db.outputs.baseType() = int(attributeType.baseType);
            db.outputs.componentCount() = attributeType.componentCount;
            db.outputs.arrayDepth() = attributeType.arrayDepth;
            db.outputs.role() = int(attributeType.role);
            db.outputs.fullType() = int(omni::fabric::TypeC(attributeType).type);
        }
        return true;
    }
};

REGISTER_OGN_NODE()

}
}
}
