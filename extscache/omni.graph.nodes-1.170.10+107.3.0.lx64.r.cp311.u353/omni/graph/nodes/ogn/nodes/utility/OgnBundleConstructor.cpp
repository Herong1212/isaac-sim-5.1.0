// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include "OgnBundleConstructorDatabase.h"

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnBundleConstructor
{
public:
    static bool compute(OgnBundleConstructorDatabase& db)
    {
        IBundle2* outputBundle = db.outputs.bundle().abi_bundleInterface();
        outputBundle->clearContents(true);

        // Copy all dynamic inputs to the output bundle.
        auto& node = db.abi_node();
        auto totalCount = node.iNode->getAttributeCount(node);
        std::vector<AttributeObj> allAttributes(totalCount);
        node.iNode->getAttributes(node, allAttributes.data(), totalCount);

        std::vector<ConstAttributeDataHandle> handlesToCopy;
        std::vector<NameToken> namesToCopy;

        for (AttributeObj const& attr : allAttributes)
        {
            if (!attr.isValid())
            {
                // LCOV_EXCL_START : Firewall - should never happen
                db.logWarning("Input attribute to insert is not valid");
                return false;
                // LCOV_EXCL_STOP
            }

            if (!attr.iAttribute->isDynamic(attr))
                continue;

            if (!attr.iAttribute->getPortType(attr) == AttributePortType::kAttributePortType_Input)
                continue;

            std::string attrName = attr.iAttribute->getName(attr);

            if (attr.iAttribute->getExtendedType(attr) != kExtendedAttributeType_Regular)
            {
                db.logWarning("Cannot add extended attribute types like '%s' to a bundle", attrName.c_str());
                continue;
            }

            if (attr.iAttribute->getResolvedType(attr).baseType == BaseDataType::eRelationship)
            {
                db.logWarning("Cannot add bundle attribute types like '%s' to a bundle", attrName.c_str());
                continue;
            }

            // The bundled name does not need the port namespace
            size_t prefixPos = attrName.find("inputs:");
            if (prefixPos == 0)
            {
                attrName = attrName.substr(prefixPos + 7);
            }
            namesToCopy.push_back(db.abi_context().iToken->getHandle(attrName.c_str()));
            handlesToCopy.push_back(attr.iAttribute->getConstAttributeDataHandle(attr, kAccordingToContextIndex));
        }
        if (!namesToCopy.empty())
            outputBundle->copyAttributes(handlesToCopy.data(), namesToCopy.size(), true, namesToCopy.data());
        return true;
    }
};

REGISTER_OGN_NODE()

}
}
}
