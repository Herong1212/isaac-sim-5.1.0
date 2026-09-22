// SPDX-FileCopyrightText: Copyright (c) 2019-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnNotDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
// clang-format on

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnNot
{
public:
    static bool computeVectorized(OgnNotDatabase& db, size_t count)
    {
        auto functor = [](bool const& valueIn, bool& valueOut) { valueOut = static_cast<bool>(!valueIn); };
        return ogn::compute::tryComputeWithArrayBroadcasting<bool, bool>(
                   db.inputs.valueIn(), db.outputs.valueOut(), functor, count) ?
                   count :
                   0;
    }

    static void onConnectionTypeResolve(const NodeObj& node)
    {
        auto valueIn = node.iNode->getAttributeByToken(node, inputs::valueIn.token());
        auto valueOut = node.iNode->getAttributeByToken(node, outputs::valueOut.token());

        auto valueInType = valueIn.iAttribute->getResolvedType(valueIn);

        // Require inputs to be resolved before determining result type
        if (valueInType.baseType != BaseDataType::eUnknown)
        {
            std::array<AttributeObj, 2> attrs{ valueIn, valueOut };
            node.iNode->resolveCoupledAttributes(node, attrs.data(), attrs.size());
        }
    }
};

REGISTER_OGN_NODE()

}
}
}
