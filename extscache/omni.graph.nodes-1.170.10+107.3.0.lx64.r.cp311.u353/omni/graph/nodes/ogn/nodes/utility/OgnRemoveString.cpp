// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnRemoveStringDatabase.h>
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
// helper to wrap a given index from legal range [-arrayLength, arrayLength) to [0:arrayLength).
// values outside of the legal range with throw
size_t tryWrapIndex(int index, size_t arraySize)
{
    int wrappedIndex = index;
    if (index < 0)
        wrappedIndex = static_cast<int>(arraySize) + index;
    if (wrappedIndex < 0 || wrappedIndex >= static_cast<int>(arraySize))
        throw ogn::compute::InputError(
            formatString("inputs:index %d is out of range for inputs:array of size %zu", wrappedIndex, arraySize));
    return static_cast<size_t>(wrappedIndex);
}

size_t tryComputeAssumingString(OgnRemoveStringDatabase& db, size_t count)
{
    for (size_t idx = 0; idx < count; ++idx)
    {
        auto const inString = db.inputs.string(idx).template get<uchar[]>();
        auto outString = db.outputs.string(idx).template get<uchar[]>();

        if (!inString->empty())
        {
            std::string baseString(inString->data(), inString->data() + inString->size());
            size_t const index = tryWrapIndex(db.inputs.index(idx), baseString.size());
            size_t const count = std::max(db.inputs.count(idx), -1);
            auto newString = baseString.erase(index, count);
            outString.resize(newString.size());
            memcpy(outString->data(), newString.data(), newString.size());
        }
        else
            outString.resize(0);
    }
    return count;
}

size_t tryComputeAssumingToken(OgnRemoveStringDatabase& db, size_t count)
{
    for (size_t idx = 0; idx < count; ++idx)
    {
        auto const inToken = db.inputs.string(idx).template get<ogn::Token>();
        auto outToken = db.outputs.string(idx).template get<ogn::Token>();

        if (*inToken != omni::fabric::kUninitializedToken)
        {
            std::string baseString = db.tokenToString(*inToken);
            size_t const index = tryWrapIndex(db.inputs.index(idx), baseString.size());
            size_t const count = std::max(db.inputs.count(idx), -1);
            *outToken = db.stringToToken(baseString.erase(index, count).c_str());
        }
        else
            *outToken = omni::fabric::kUninitializedToken;
    }
    return count;
}
} // namespace

class OgnRemoveString
{
public:
    static size_t computeVectorized(OgnRemoveStringDatabase& db, size_t count)
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
        auto const outString = node.iNode->getAttributeByToken(node, outputs::string.token());

        std::array<AttributeObj, 2> attrs{ string, outString };
        node.iNode->resolveCoupledAttributes(node, attrs.data(), attrs.size());
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
