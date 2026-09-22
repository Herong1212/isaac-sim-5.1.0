// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnBuildStringDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnBuildString
{
public:
    static size_t computeVectorized(OgnBuildStringDatabase& db, size_t count)
    {
        try
        {
            for (size_t idx = 0; idx < count; idx++)
            {
                auto const& inputValue = db.inputs.a(idx);
                auto const& suffixIn = db.inputs.b(idx);
                auto& outValue = db.outputs.value(idx);

                if (inputValue.type().baseType == BaseDataType::eToken)
                    computeForToken(db, idx, inputValue, suffixIn, outValue);
                else
                    computeForString(db, idx, inputValue, suffixIn, outValue);

                auto const& dynamicInputs = db.getDynamicInputs();
                if (!dynamicInputs.empty())
                {
                    auto accumulatingValue = omni::graph::core::ogn::constructInputFromOutput(
                        db, db.outputs.value(idx), outputs::value.token());

                    for (auto const& input : dynamicInputs)
                    {
                        if (input(idx).type().baseType == BaseDataType::eToken)
                            computeForToken(db, idx, accumulatingValue, input(idx), outValue);
                        else
                            computeForString(db, idx, accumulatingValue, input(idx), outValue);
                    }
                }
            }
            return count;
        }
        // LCOV_EXCL_START
        catch (ogn::compute::InputError& error)
        {
            db.logError(error.what());
        }
        return 0;
        // LCOV_EXCL_STOP
    }

    static bool computeForString(OgnBuildStringDatabase& db,
                                 size_t idx,
                                 ogn::RuntimeAttribute<ogn::kOgnInput, ogn::kCpu> const& inputValue,
                                 ogn::RuntimeAttribute<ogn::kOgnInput, ogn::kCpu> const& suffixIn,
                                 ogn::RuntimeAttribute<ogn::kOgnOutput, ogn::kCpu>& outValue)
    {
        if (inputValue.type().baseType != BaseDataType::eUChar || suffixIn.type().baseType != BaseDataType::eUChar)
            throw ogn::compute::InputError("Mismatched base types - cannot append.");

        auto const suffixData = suffixIn.template get<uint8_t[]>();

        // No suffix? Just copy in to out
        if (suffixData->empty())
        {
            // the inputValue may be an alias for the outValue
            if (inputValue.name() != outValue.name())
                db.outputs.value(idx).copyData(inputValue);
            return true;
        }

        auto const inputValueData = inputValue.template get<uint8_t[]>();

        std::string outVal;
        outVal.reserve(inputValueData.size() + suffixData.size());

        outVal.append(reinterpret_cast<char const*>(inputValueData->data()), inputValueData.size());
        outVal.append(reinterpret_cast<char const*>(suffixData->data()), suffixData.size());

        auto outData = outValue.template get<uint8_t[]>();
        size_t outBufferSize = outVal.size();
        outData->resize(outBufferSize);
        memcpy(outData->data(), reinterpret_cast<uint8_t const*>(outVal.data()), outBufferSize);

        return true;
    }

    static bool computeForToken(OgnBuildStringDatabase& db,
                                size_t idx,
                                ogn::RuntimeAttribute<ogn::kOgnInput, ogn::kCpu> const& inputValue,
                                ogn::RuntimeAttribute<ogn::kOgnInput, ogn::kCpu> const& suffix,
                                ogn::RuntimeAttribute<ogn::kOgnOutput, ogn::kCpu>& outValue)
    {
        if (inputValue.type().baseType != BaseDataType::eToken || suffix.type().baseType != BaseDataType::eToken)
            throw ogn::compute::InputError("Mismatched base types - cannot append.");

        std::vector<char const*> suffixes;

        if (suffix.type().arrayDepth == 0)
        {
            NameToken suffixToken = *suffix.template get<OgnToken>();
            if (suffixToken != omni::fabric::kUninitializedToken)
                suffixes.push_back(db.tokenToString(suffixToken));
        }
        else
        {
            const auto suffixTokens = *suffix.template get<OgnToken[]>();
            suffixes.resize(suffixTokens.size());
            std::transform(suffixTokens.begin(), suffixTokens.end(), suffixes.begin(),
                           [&db](auto t) { return db.tokenToString(t); });
        }

        // No suffix? Just copy in to out
        if (suffixes.empty())
        {
            // the input value may be an alias for the output value
            if (inputValue.name() != outValue.name())
                db.outputs.value(idx).copyData(inputValue);
            return true;
        }

        if (inputValue.type().arrayDepth > 0)
        {
            const auto inputValueArray = *inputValue.template get<OgnToken[]>();
            auto outputPathArray = *db.outputs.value(idx).template get<OgnToken[]>();
            outputPathArray.resize(inputValueArray.size());

            if (suffixes.size() == 1)
            {
                const char* suffixStr = suffixes[0];
                std::transform(inputValueArray.begin(), inputValueArray.end(), outputPathArray.begin(),
                               [&](const auto& p)
                               {
                                   std::string s = db.tokenToString(p);
                                   s += suffixStr;
                                   return db.stringToToken(s.c_str());
                               });
            }
            else
            {
                if (inputValueArray.size() != suffixes.size())
                {
                    throw ogn::compute::InputError(
                        formatString("inputs:value and inputs:suffix arrays are not the same size (%zu and %zu)",
                                     inputValueArray.size(), suffixes.size())
                            .c_str());
                }
                for (size_t i = 0; i < inputValueArray.size(); ++i)
                {
                    std::string s = db.tokenToString(inputValueArray[i]);
                    s += suffixes[i];
                    outputPathArray[i] = db.stringToToken(s.c_str());
                }
            }
            return true;
        }
        else
        {
            auto inValue = *inputValue.template get<OgnToken>();
            std::string s;
            if (inValue != omni::fabric::kUninitializedToken)
            {
                s = db.tokenToString(inValue);
            }
            s += suffixes[0];
            *db.outputs.value(idx).template get<OgnToken>() = db.stringToToken(s.c_str());
        }
        return true;
    }

    // FIXME: This should be improved if this node is versioned, as it is very confusing and can lead to bad
    // resolutions. It is left functioning as is to keep backwards compatibility.
    static void onConnectionTypeResolve(const NodeObj& node)
    {
        auto inputVal = node.iNode->getAttributeByToken(node, inputs::a.m_token);
        auto outputVal = node.iNode->getAttributeByToken(node, outputs::value.m_token);

        auto totalCount = node.iNode->getAttributeCount(node);
        std::vector<AttributeObj> allAttributes(totalCount);
        node.iNode->getAttributes(node, allAttributes.data(), totalCount);

        std::vector<AttributeObj> unresolvedAttrs;
        unresolvedAttrs.reserve(totalCount);
        unresolvedAttrs.push_back(inputVal);

        // Gather unresolved input attributes
        for (auto const& attr : allAttributes)
        {
            auto resolvedType = attr.iAttribute->getResolvedType(attr);
            if (attr.iAttribute->getPortType(attr) == AttributePortType::kAttributePortType_Input &&
                resolvedType.baseType == BaseDataType::eUnknown && attr.attributeHandle != inputVal.attributeHandle)
            {
                unresolvedAttrs.push_back(attr);
            }
        }

        // Include output attribute
        unresolvedAttrs.push_back(outputVal);

        auto type = inputVal.iAttribute->getResolvedType(inputVal);
        // if input is an array of token, suffixes are allowed to be either a simple or an array of token(s)
        if (type.baseType == BaseDataType::eToken && type.arrayDepth == 1)
        {
            if (unresolvedAttrs.size() == 2) // Only in and out are present
            {
                node.iNode->resolveCoupledAttributes(node, unresolvedAttrs.data(), unresolvedAttrs.size());
            }
        }
        else if (type.baseType != BaseDataType::eUnknown)
        {
            node.iNode->resolveCoupledAttributes(node, unresolvedAttrs.data(), unresolvedAttrs.size());
        }
    }
};

REGISTER_OGN_NODE();

} // nodes
} // graph
} // omni
