// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnReplaceStringDatabase.h>
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
size_t tryComputeAssumingString(OgnReplaceStringDatabase& db, size_t count)
{
    for (size_t idx = 0; idx < count; ++idx)
    {
        const auto base = db.inputs.string(idx).template get<uchar[]>();
        const auto replace = db.inputs.replace(idx).template get<uchar[]>();
        const auto value = db.inputs.value(idx).template get<uchar[]>();
        auto outString = db.outputs.string(idx).template get<uchar[]>();

        if (!base->empty())
        {
            std::string baseString(base->data(), base->data() + base->size());
            if (!replace->empty())
            {
                std::string_view replString(reinterpret_cast<char const*>(replace->data()), replace->size());
                std::string_view newString(reinterpret_cast<char const*>(value->data()), value->size());
                if (db.inputs.replaceAll(idx))
                {
                    size_t index = 0;
                    while ((index = baseString.find(replString, index)) != std::string::npos)
                    {
                        baseString.replace(index, replString.size(), newString);
                        index += newString.size();
                    }
                }
                else
                {
                    baseString.replace(baseString.find(replString), replString.size(), newString);
                }
            }
            outString.resize(baseString.size());
            memcpy(outString->data(), baseString.data(), baseString.size());
        }
        else
            outString.resize(0);
    }
    return count;
}

size_t tryComputeAssumingToken(OgnReplaceStringDatabase& db, size_t count)
{
    for (size_t idx = 0; idx < count; ++idx)
    {
        const auto inToken = db.inputs.string(idx).template get<ogn::Token>();
        const auto replace = db.inputs.replace(idx).template get<ogn::Token>();
        const auto value = db.inputs.value(idx).template get<ogn::Token>();
        auto outToken = db.outputs.string(idx).template get<ogn::Token>();

        if (*inToken != omni::fabric::kUninitializedToken)
        {
            std::string baseString = db.tokenToString(*inToken);
            if (*replace != omni::fabric::kUninitializedToken)
            {
                std::string_view replString(db.tokenToString(*replace));
                std::string_view newString(db.tokenToString(*value));
                if (db.inputs.replaceAll(idx))
                {
                    size_t index = 0;
                    while ((index = baseString.find(replString, index)) != std::string::npos)
                    {
                        baseString.replace(index, replString.size(), newString);
                        index += newString.size();
                    }
                }
                else
                {
                    baseString.replace(baseString.find(replString), replString.size(), newString);
                }
            }
            *outToken = db.stringToToken(baseString.c_str());
        }
        else
            *outToken = omni::fabric::kUninitializedToken;
    }
    return count;
}
} // namespace

class OgnReplaceString
{
public:
    static size_t computeVectorized(OgnReplaceStringDatabase& db, size_t count)
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
        auto const replace = node.iNode->getAttributeByToken(node, inputs::replace.token());
        auto const value = node.iNode->getAttributeByToken(node, inputs::value.token());
        auto const outString = node.iNode->getAttributeByToken(node, outputs::string.token());

        std::array<AttributeObj, 4> attrs{ string, replace, value, outString };
        node.iNode->resolveCoupledAttributes(node, attrs.data(), attrs.size());
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
