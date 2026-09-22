// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include "OgnExtractAttrDatabase.h"

namespace omni
{
namespace graph
{
namespace core
{

class OgnExtractAttr
{
public:
    // Copies a single attribute from an input prim to an output attribute directly on the node,
    // if it exists in the input prim and matches the type of the output attribute.
    static bool compute(OgnExtractAttrDatabase& db)
    {
        const auto& inputToken = db.inputs.attrName();
        auto extractedBundledAttribute = db.inputs.data().attributeByName(inputToken);
        if (!extractedBundledAttribute.isValid())
        {
            db.logWarning("No attribute matching '%s' was found in the input bundle", db.tokenToString(inputToken));
            return false;
        }
        const Type& inputType = extractedBundledAttribute.type();
        auto& outputAttribute = db.outputs.output();
        // This compute is not creating the attribute data, that should have been done externally.
        // The attribute type should match the one extracted though, otherwise connections can go astray.
        if (!outputAttribute.resolved())
        {
            // Not resolved, so we have to resolve it now. This node is unusual in that the resolved output type
            // depends on run-time state of the bundle.
            AttributeObj out = db.abi_node().iNode->getAttributeByToken(db.abi_node(), outputs::output.m_token);
            out.iAttribute->setResolvedType(out, inputType);
            outputAttribute.reset(
                db.abi_context(), out.iAttribute->getAttributeDataHandle(out, db.getInstanceIndex()), out);
        }
        else
        {
            Type outType = outputAttribute.type();
            if (!inputType.compatibleRawData(outType))
            {
                db.logWarning("Attribute '%s' of type %s in the input bundle is not compatible with type %s",
                              db.tokenToString(inputToken), getOgnTypeName(inputType).c_str(),
                              getOgnTypeName(outType).c_str());
                return false;
            }
        }
        outputAttribute.copyData(extractedBundledAttribute);
        return true;
    }
};

REGISTER_OGN_NODE()

}
}
}
