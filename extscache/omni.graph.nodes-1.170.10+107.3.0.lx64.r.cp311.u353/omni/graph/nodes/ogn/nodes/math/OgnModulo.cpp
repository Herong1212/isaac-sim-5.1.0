// SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnModuloDatabase.h>
#include <cmath>
#include <algorithm>
#include <array>

template <typename T, typename AttrInType, typename AttrOutType>
void modulo(AttrInType& a, AttrInType& b, AttrOutType& result, size_t count)
{
    auto aValAttr = a.template get<T>();
    auto bValAttr = b.template get<T>();
    auto resAttr = result.template get<T>();
    auto aVal = aValAttr.vectorized(count);
    auto bVal = bValAttr.vectorized(count);
    auto res = resAttr.vectorized(count);

    for (size_t i = 0; i < count; ++i)
        res[i] = bVal[i] == 0 ? 0 : aVal[i] % bVal[i];
}

class OgnModulo
{
public:
    static size_t computeVectorized(OgnModuloDatabase& db, size_t count)
    {
        const auto& a = db.inputs.a();
        const auto& b = db.inputs.b();
        auto& result = db.outputs.result();

        if (!a.resolved())
            return true;

        switch (a.type().baseType)
        {
        case BaseDataType::eInt:
            modulo<int>(a, b, result, count);
            break;
        case BaseDataType::eUInt:
            modulo<uint32_t>(a, b, result, count);
            break;
        case BaseDataType::eInt64:
            modulo<int64_t>(a, b, result, count);
            break;
        case BaseDataType::eUInt64:
            modulo<uint64_t>(a, b, result, count);
            break;
        default:
            break;
        }

        return true;
    }

    static void onConnectionTypeResolve(const NodeObj& node)
    {
        // Resolve fully-coupled types for the 3 attributes
        std::array<AttributeObj, 3> attrs{ node.iNode->getAttribute(node, OgnModuloAttributes::inputs::a.m_name),
                                           node.iNode->getAttribute(node, OgnModuloAttributes::inputs::b.m_name),
                                           node.iNode->getAttribute(node, OgnModuloAttributes::outputs::result.m_name) };
        node.iNode->resolveCoupledAttributes(node, attrs.data(), attrs.size());
    }
};

REGISTER_OGN_NODE()
