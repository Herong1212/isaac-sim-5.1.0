// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnDivideDatabase.h>
#include "OgnDivideHelper.h"
#include <carb/logging/Log.h>
#include <type_traits>

namespace omni
{
namespace graph
{
namespace nodes
{


class OgnDivide
{
public:
    static bool computeVectorized(OgnDivideDatabase& db, size_t count)
    {
        auto const& a = db.inputs.a();
        auto const& b = db.inputs.b();
        auto& result = db.outputs.result();
        try
        {
            if (OGNDivideHelper::tryComputeScalars(db, a, b, result, count))
                return true;

            if (OGNDivideHelper::tryComputeTuple2(db, a, b, result, count))
                return true;

            if (OGNDivideHelper::tryComputeTuple3(db, a, b, result, count))
                return true;

            if (OGNDivideHelper::tryComputeTuple4(db, a, b, result, count))
                return true;

            if (OGNDivideHelper::tryComputeMatrices(db, a, b, result, count))
                return true;

            db.logWarning("OgnDivide: Failed to resolve input types");
        }
        catch (ogn::compute::InputError& error)
        {
            db.logWarning("OgnDivide: %s", error.what());
        }
        return false;
    }

    static void onConnectionTypeResolve(const NodeObj& node)
    {
        auto a = node.iNode->getAttributeByToken(node, inputs::a.token());
        auto result = node.iNode->getAttributeByToken(node, outputs::result.token());
        auto aType = a.iAttribute->getResolvedType(a);

        // Require inputs to be resolved before determining result's type
        if (aType.baseType != BaseDataType::eUnknown)
        {
            // In the case of A being an integral - then we force a double
            auto newType = aType;
            if (aType.baseType == BaseDataType::eUChar || aType.baseType == BaseDataType::eInt ||
                aType.baseType == BaseDataType::eUInt || aType.baseType == BaseDataType::eInt64 ||
                aType.baseType == BaseDataType::eUInt64)
            {
                newType.baseType = BaseDataType::eDouble;
            }
            result.iAttribute->setResolvedType(result, newType);
        }
        else
            result.iAttribute->setResolvedType(result, Type(BaseDataType::eUnknown));
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
