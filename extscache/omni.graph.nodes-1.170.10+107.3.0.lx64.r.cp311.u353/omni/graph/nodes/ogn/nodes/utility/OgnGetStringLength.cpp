// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnGetStringLengthDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <string>
// clang-format on

namespace omni
{
namespace graph
{
namespace nodes
{

// unnamed namespace to avoid multiple declaration when linking
namespace
{
size_t tryComputeAssumingString(OgnGetStringLengthDatabase& db, size_t count)
{
    for (size_t idx = 0; idx < count; ++idx)
    {
        auto length = db.outputs.length(idx).template get<int>();
        *length = int(db.inputs.string(idx).size());
    }
    return count;
}

size_t tryComputeAssumingToken(OgnGetStringLengthDatabase& db, size_t count)
{
    for (size_t idx = 0; idx < count; ++idx)
    {
        auto const string = db.inputs.string(idx).template get<ogn::Token>();
        auto length = db.outputs.length(idx).template get<int>();
        *length = int(strlen(db.tokenToString(*string)));
    }
    return count;
}

size_t tryComputeAssumingTokenArray(OgnGetStringLengthDatabase& db, size_t count)
{
    for (size_t idx = 0; idx < count; ++idx)
    {
        auto const string = db.inputs.string(idx).template get<ogn::Token[]>();
        auto length = db.outputs.length(idx).template get<int[]>();
        length.resize(string.size());
        for (size_t i = 0; i < string.size(); i++)
            (*length)[i] = int(strlen(db.tokenToString((*string)[i])));
    }
    return count;
}
} // namespace

class OgnGetStringLength
{
public:
    static size_t computeVectorized(OgnGetStringLengthDatabase& db, size_t count)
    {
        try
        {
            const auto& inputType = db.inputs.string().type();
            switch (inputType.baseType)
            {
            case BaseDataType::eToken:
                switch (inputType.arrayDepth)
                {
                case 0:
                    return tryComputeAssumingToken(db, count);
                case 1:
                    return tryComputeAssumingTokenArray(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eUChar:
                return tryComputeAssumingString(db, count);
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

    static void onConnectionTypeResolve(const NodeObj& node)
    {
        auto string = node.iNode->getAttributeByToken(node, inputs::string.token());
        auto length = node.iNode->getAttributeByToken(node, outputs::length.token());

        auto stringType = string.iAttribute->getResolvedType(string);

        if (stringType.baseType != BaseDataType::eUnknown)
        {
            uint8_t outArrayDepth = (stringType.role == AttributeRole::eText) ? 0 : stringType.arrayDepth;
            Type resultType(BaseDataType::eInt, 1, outArrayDepth);
            length.iAttribute->setResolvedType(length, resultType);
        }

        else
            length.iAttribute->setResolvedType(length, Type(BaseDataType::eUnknown));
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
