// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnBreakVector4Database.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
// clang-format on

namespace omni
{
namespace graph
{
namespace nodes
{

namespace
{
template <typename T>
bool tryComputeAssumingType(OgnBreakVector4Database& db, size_t count)
{
    switch (db.inputs.tuple().type().arrayDepth)
    {
    case 0:
    {
        const auto vector = db.inputs.tuple().template get<T[4]>();
        auto x = db.outputs.x().template get<T>();
        auto y = db.outputs.y().template get<T>();
        auto z = db.outputs.z().template get<T>();
        auto w = db.outputs.w().template get<T>();
        if (vector && x && y && z && w)
        {
            const auto pVector = vector.vectorized(count);
            const auto px = x.vectorized(count);
            const auto py = y.vectorized(count);
            const auto pz = z.vectorized(count);
            const auto pw = w.vectorized(count);
            if (!pVector.empty() && !px.empty() && !py.empty() && !pz.empty() && !pw.empty())
            {
                for (size_t idx = 0; idx < count; idx++)
                {
                    px[idx] = pVector[idx][0];
                    py[idx] = pVector[idx][1];
                    pz[idx] = pVector[idx][2];
                    pw[idx] = pVector[idx][3];
                }
            }
        }
        return count;
    }
    case 1:
        for (size_t idx = 0; idx < count; idx++)
        {
            const auto vector = db.inputs.tuple(idx).template get<T[][4]>();
            auto x = db.outputs.x(idx).template get<T[]>();
            auto y = db.outputs.y(idx).template get<T[]>();
            auto z = db.outputs.z(idx).template get<T[]>();
            auto w = db.outputs.w(idx).template get<T[]>();
            if (vector && x && y && z && w)
            {
                x->resize(vector->size());
                y->resize(vector->size());
                z->resize(vector->size());
                w->resize(vector->size());
                for (size_t i = 0; i < vector->size(); i++)
                {
                    (*x)[i] = (*vector)[i][0];
                    (*y)[i] = (*vector)[i][1];
                    (*z)[i] = (*vector)[i][2];
                    (*w)[i] = (*vector)[i][3];
                }
            }
        }
        return count;
    // LCOV_EXCL_START
    default:
        throw ogn::compute::InputError("Failed to resolve input types");
        // LCOV_EXCL_STOP
    }
}
} // namespace

// Node to break a 4-vector into it's component scalers
class OgnBreakVector4
{
public:
    static size_t computeVectorized(OgnBreakVector4Database& db, size_t count)
    {
        try
        {
            const auto& inputType = db.inputs.tuple().type();
            switch (inputType.baseType)
            {
            case BaseDataType::eDouble:
                return tryComputeAssumingType<double>(db, count);
            case BaseDataType::eFloat:
                return tryComputeAssumingType<float>(db, count);
            case BaseDataType::eHalf:
                return tryComputeAssumingType<pxr::GfHalf>(db, count);
            case BaseDataType::eInt:
                return tryComputeAssumingType<int>(db, count);
            // LCOV_EXCL_START
            default:
                throw ogn::compute::InputError("Failed to resolve input types");
                // LCOV_EXCL_STOP
            }
        }
        // LCOV_EXCL_START
        catch (ogn::compute::InputError& error)
        {
            db.logError(error.what());
        }
        return 0;
        // LCOV_EXCL_STOP
    }

    static void onConnectionTypeResolve(const NodeObj& nodeObj)
    {
        auto vector = nodeObj.iNode->getAttributeByToken(nodeObj, inputs::tuple.token());
        auto x = nodeObj.iNode->getAttributeByToken(nodeObj, outputs::x.token());
        auto y = nodeObj.iNode->getAttributeByToken(nodeObj, outputs::y.token());
        auto z = nodeObj.iNode->getAttributeByToken(nodeObj, outputs::z.token());
        auto w = nodeObj.iNode->getAttributeByToken(nodeObj, outputs::w.token());

        auto vectorType = vector.iAttribute->getResolvedType(vector);

        // Require inputs to be resolved before determining outputs' type
        if (vectorType.baseType != BaseDataType::eUnknown)
        {
            std::array<AttributeObj, 5> attrs{ vector, x, y, z, w };
            std::array<uint8_t, 5> tuples{ 4, 1, 1, 1, 1 };
            std::array<uint8_t, 5> arrays{ vectorType.arrayDepth, vectorType.arrayDepth, vectorType.arrayDepth,
                                           vectorType.arrayDepth, vectorType.arrayDepth };
            std::array<AttributeRole, 5> roles{ vectorType.role, AttributeRole::eNone, AttributeRole::eNone,
                                                AttributeRole::eNone, AttributeRole::eNone };
            nodeObj.iNode->resolvePartiallyCoupledAttributes(
                nodeObj, attrs.data(), tuples.data(), arrays.data(), roles.data(), attrs.size());
        }
    }
};

REGISTER_OGN_NODE();

}
}
}
