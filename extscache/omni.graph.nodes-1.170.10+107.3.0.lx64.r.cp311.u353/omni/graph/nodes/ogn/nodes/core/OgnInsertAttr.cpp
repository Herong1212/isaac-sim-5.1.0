// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include "OgnInsertAttrDatabase.h"

namespace omni
{
namespace graph
{
namespace core
{

class OgnInsertAttr
{
public:
    // Copies all attributes from an input prim to the output prim, as well as copying an additional
    // "attrToInsert" attribute from the node itself with a specified name.
    static bool compute(OgnInsertAttrDatabase& db)
    {
        const auto& outputAttrNameToken = db.inputs.outputAttrName();
        const auto& inputBundle = db.inputs.data();
        auto& outputBundle = db.outputs.data();

        // Start by copying the input prim into the output prim.
        outputBundle = inputBundle;
        if (!outputBundle.isValid())
        {
            // LCOV_EXCL_START : Firewall - should never happen
            db.logWarning("Failed to copy input bundle to the output");
            return false;
            // LCOV_EXCL_STOP
        }

        const auto& inputToInsert = db.inputs.attrToInsert();
        if (!inputToInsert.isValid())
        {
            // LCOV_EXCL_START : Firewall - should never happen
            db.logWarning("Input attribute to insert is not valid");
            return false;
            // LCOV_EXCL_STOP
        }
        outputBundle.insertAttribute(inputToInsert, outputAttrNameToken);
        return true;
    }
};

REGISTER_OGN_NODE()

}
}
}
