// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnInsertStringDatabase.h>
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
// helper to clamp a given index to [0:arrayLength]
size_t tryWrapIndex(int index, size_t arraySize)
{
    if (index < 0)
        index = 0;
    if (index > static_cast<int>(arraySize))
        index = static_cast<int>(arraySize);
    return static_cast<size_t>(index);
}

size_t tryComputeAssumingString(OgnInsertStringDatabase& db, size_t count)
{
    for (size_t idx = 0; idx < count; ++idx)
    {
        auto const inString = db.inputs.string(idx).template get<uchar[]>();
        auto const inValue = db.inputs.value(idx).template get<uchar[]>();
        auto outString = db.outputs.string(idx).template get<uchar[]>();

        if (!inString->empty())
        {
            std::string baseString(inString->data(), inString->data() + inString->size());
            if (!inValue->empty())
            {
                std::string_view subString(reinterpret_cast<char const*>(inValue->data()), inValue->size());
                size_t const index = tryWrapIndex(db.inputs.index(idx), baseString.size());
                baseString.insert(index, subString);
            }
            outString.resize(baseString.size());
            memcpy(outString->data(), baseString.data(), baseString.size());
        }
        else
        {
            if (!inValue->empty())
            {
                outString.resize(inValue.size());
                memcpy(outString->data(), inValue->data(), inValue.size());
            }
            else
                outString.resize(0);
        }
    }
    return count;
}

size_t tryComputeAssumingToken(OgnInsertStringDatabase& db, size_t count)
{
    for (size_t idx = 0; idx < count; ++idx)
    {
        auto const inToken = db.inputs.string(idx).template get<ogn::Token>();
        auto const inValue = db.inputs.value(idx).template get<ogn::Token>();
        auto outToken = db.outputs.string(idx).template get<ogn::Token>();

        if (*inToken != omni::fabric::kUninitializedToken)
        {
            std::string baseString = db.tokenToString(*inToken);
            if (*inValue != omni::fabric::kUninitializedToken)
            {
                std::string_view subString(db.tokenToString(*inValue));
                size_t const index = tryWrapIndex(db.inputs.index(idx), baseString.size());
                baseString.insert(index, subString);
            }
            *outToken = db.stringToToken(baseString.c_str());
        }
        else
        {
            if (*inValue != omni::fabric::kUninitializedToken)
                *outToken = *inValue;
            else
                *outToken = omni::fabric::kUninitializedToken;
        }
    }
    return count;
}
} // namespace

class OgnInsertString
{
public:
    static size_t computeVectorized(OgnInsertStringDatabase& db, size_t count)
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
        auto const outString = node.iNode->getAttributeByToken(node, outputs::string.token());

        std::array<AttributeObj, 3> attrs{ string, value, outString };
        node.iNode->resolveCoupledAttributes(node, attrs.data(), attrs.size());
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
