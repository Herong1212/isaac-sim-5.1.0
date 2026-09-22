// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "ResolveBooleanOpAttributes.h"
#include <omni/graph/core/iComputeGraph.h>

#include <algorithm>
#include <array>

namespace omni
{
namespace graph
{
namespace nodes
{

void resolveBooleanOpAttributes(const core::NodeObj& node,
                                const core::NameToken aToken,
                                const core::NameToken bToken,
                                const core::NameToken resultToken)
{
    auto a = node.iNode->getAttributeByToken(node, aToken);
    auto b = node.iNode->getAttributeByToken(node, bToken);
    auto result = node.iNode->getAttributeByToken(node, resultToken);

    auto aType = a.iAttribute->getResolvedType(a);
    auto bType = b.iAttribute->getResolvedType(b);

    // Require inputs to be resolved before determining result type
    if (aType.baseType != BaseDataType::eUnknown && bType.baseType != BaseDataType::eUnknown)
    {
        std::array<AttributeObj, 3> attrs{ a, b, result };
        std::array<uint8_t, 3> arrayDepths{ aType.arrayDepth, bType.arrayDepth,
                                            // Allow for a mix of singular and array inputs. If any input is an array,
                                            // the output must be an array
                                            std::max(aType.arrayDepth, bType.arrayDepth) };
        std::array<AttributeRole, 3> rolesBuf{ aType.role, bType.role,
                                               // Copy the attribute role from the resolved type to the output type
                                               AttributeRole::eUnknown };
        node.iNode->resolvePartiallyCoupledAttributes(node, attrs.data(), nullptr, // tupleCounts default to scalar
                                                      arrayDepths.data(), rolesBuf.data(), attrs.size());
    }
}

void resolveBooleanOpDynamicAttributes(const core::NodeObj& node, const core::NameToken resultToken)
{
    auto totalCount = node.iNode->getAttributeCount(node);
    std::vector<AttributeObj> allAttributes(totalCount);
    node.iNode->getAttributes(node, allAttributes.data(), totalCount);

    std::vector<AttributeObj> attributes;
    std::vector<uint8_t> arrayDepths;
    std::vector<AttributeRole> roles;

    attributes.reserve(totalCount - 2);
    arrayDepths.reserve(totalCount - 2);
    roles.reserve(totalCount - 2);

    uint8_t maxArrayDepth = 0;
    uint8_t maxComponentCount = 0;

    auto result = node.iNode->getAttributeByToken(node, resultToken);

    for (auto const& attr : allAttributes)
    {
        if (attr.iAttribute->getPortType(attr) == AttributePortType::kAttributePortType_Input)
        {
            auto resolvedType = attr.iAttribute->getResolvedType(attr);

            // all inputs must be connected and resolved to complete the output port type resolution
            if (resolvedType.baseType == BaseDataType::eUnknown)
            {
                result.iAttribute->setResolvedType(result, Type(BaseDataType::eUnknown));
                return;
            }

            arrayDepths.push_back(resolvedType.arrayDepth);
            roles.push_back(resolvedType.role);
            maxComponentCount = std::max(maxComponentCount, resolvedType.componentCount);
            maxArrayDepth = std::max(maxArrayDepth, resolvedType.arrayDepth);

            attributes.push_back(attr);
        }
    }

    attributes.push_back(result);
    // Allow for a mix of singular and array inputs. If any input is an array, the output must be an array
    arrayDepths.push_back(maxArrayDepth);
    // Copy the attribute role from the resolved type to the output type
    roles.push_back(AttributeRole::eUnknown);

    node.iNode->resolvePartiallyCoupledAttributes(node, attributes.data(), nullptr, // tupleCounts default to scalar
                                                  arrayDepths.data(), roles.data(), attributes.size());
}
}
}
}
