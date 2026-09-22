// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnFindStringDatabase.h>
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
size_t tryComputeAssumingString(OgnFindStringDatabase& db, size_t count)
{
    for (size_t idx = 0; idx < count; ++idx)
    {
        auto const inString = db.inputs.string(idx).template get<uchar[]>();
        auto const inSubString = db.inputs.value(idx).template get<uchar[]>();
        db.outputs.index(idx) = -1;

        if (!inString->empty() && !inSubString->empty())
        {
            std::string_view searchString(reinterpret_cast<char const*>(inString->data()), inString->size());
            std::string_view subString(reinterpret_cast<char const*>(inSubString->data()), inSubString->size());
            db.outputs.index(idx) = (int)searchString.find(subString, db.inputs.pos(idx));
        }
    }
    return count;
}

size_t tryComputeAssumingToken(OgnFindStringDatabase& db, size_t count)
{
    for (size_t idx = 0; idx < count; ++idx)
    {
        auto const inToken = db.inputs.string(idx).template get<ogn::Token>();
        auto const inSubString = db.inputs.value(idx).template get<ogn::Token>();
        db.outputs.index(idx) = -1;

        if (*inToken != omni::fabric::kUninitializedToken && *inSubString != omni::fabric::kUninitializedToken)
        {
            std::string_view searchString(db.tokenToString(*inToken));
            std::string_view subString(db.tokenToString(*inSubString));
            db.outputs.index(idx) = (int)searchString.find(subString, db.inputs.pos(idx));
        }
    }
    return count;
}
} // namespace

class OgnFindString
{
public:
    static size_t computeVectorized(OgnFindStringDatabase& db, size_t count)
    {
        try
        {
            auto& inputType = db.inputs.string().type();
            switch (inputType.baseType)
            {
            case BaseDataType::eToken:
                return tryComputeAssumingToken(db, count);
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
        auto const string = node.iNode->getAttributeByToken(node, inputs::string.token());
        auto const value = node.iNode->getAttributeByToken(node, inputs::value.token());

        std::array<AttributeObj, 2> attrs{ string, value };
        node.iNode->resolveCoupledAttributes(node, attrs.data(), attrs.size());
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
