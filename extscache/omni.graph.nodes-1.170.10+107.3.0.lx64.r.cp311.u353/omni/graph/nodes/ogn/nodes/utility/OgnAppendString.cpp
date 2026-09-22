// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnAppendStringDatabase.h>

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnAppendString
{
public:
    static bool compute(OgnAppendStringDatabase& db)
    {
        auto const& suffix = db.inputs.suffix();
        if (suffix.type().baseType == BaseDataType::eToken)
            return computeForToken(db);
        return computeForString(db);
    }

    static bool computeForString(OgnAppendStringDatabase& db)
    {
        auto const inputValue = db.inputs.value();
        auto const suffixIn = db.inputs.suffix();
        auto const suffixData = suffixIn.get<uint8_t[]>();
        auto& outValue = db.outputs.value();

        // No suffix? Just copy in to out
        if (suffixData->empty())
        {
            db.outputs.value().copyData(inputValue);
            return true;
        }

        auto const inputValueData = inputValue.get<uint8_t[]>();

        std::string outVal;
        outVal.reserve(inputValueData.size() + suffixData.size());

        outVal.append(reinterpret_cast<char const*>(inputValueData->data()), inputValueData.size());
        outVal.append(reinterpret_cast<char const*>(suffixData->data()), suffixData.size());

        auto outData = outValue.get<uint8_t[]>();
        size_t outBufferSize = outVal.size();
        outData->resize(outBufferSize);
        memcpy(outData->data(), reinterpret_cast<uint8_t const*>(outVal.data()), outBufferSize);

        return true;
    }

    static bool computeForToken(OgnAppendStringDatabase& db)
    {
        auto const& inputValue = db.inputs.value();
        auto const& suffix = db.inputs.suffix();

        std::vector<char const*> suffixes;

        if (suffix.type().arrayDepth == 0)
        {
            NameToken suffixToken = *suffix.get<OgnToken>();
            if (suffixToken != omni::fabric::kUninitializedToken)
                suffixes.push_back(db.tokenToString(suffixToken));
        }
        else
        {
            const auto suffixTokens = *suffix.get<OgnToken[]>();
            suffixes.resize(suffixTokens.size());
            std::transform(suffixTokens.begin(), suffixTokens.end(), suffixes.begin(),
                           [&db](auto t) { return db.tokenToString(t); });
        }

        // No suffix? Just copy in to out
        if (suffixes.empty())
        {
            db.outputs.value().copyData(inputValue);
            return true;
        }

        if (inputValue.type().arrayDepth > 0)
        {
            const auto inputValueArray = *inputValue.get<OgnToken[]>();
            auto outputPathArray = *db.outputs.value().get<OgnToken[]>();
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
                    db.logError("inputs:value and inputs:suffix arrays are not the same size (%zu and %zu)",
                                inputValueArray.size(), suffixes.size());
                    return false;
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
            NameToken inValue = *inputValue.get<OgnToken>();
            std::string s;
            if (inValue != omni::fabric::kUninitializedToken)
            {
                s = db.tokenToString(inValue);
            }
            s += suffixes[0];
            *db.outputs.value().get<OgnToken>() = db.stringToToken(s.c_str());
        }
        return true;
    }

    static void onConnectionTypeResolve(const NodeObj& node)
    {
        auto inputVal = node.iNode->getAttributeByToken(node, OgnAppendStringAttributes::inputs::value.m_token);
        auto outputVal = node.iNode->getAttributeByToken(node, OgnAppendStringAttributes::outputs::value.m_token);
        auto suffixVal = node.iNode->getAttributeByToken(node, OgnAppendStringAttributes::inputs::suffix.m_token);

        // in type
        auto type = inputVal.iAttribute->getResolvedType(inputVal);

        // if input is an array of token, suffix is allowed to be either a simple or an array of token(s)
        if (type.baseType == BaseDataType::eToken && type.arrayDepth != 0)
        {
            // both in and out needs to be the same
            std::array<AttributeObj, 2> attrs{ inputVal, outputVal };
            node.iNode->resolveCoupledAttributes(node, attrs.data(), attrs.size());

            // change suffix if necessary
            auto suffixType = suffixVal.iAttribute->getResolvedType(suffixVal);
            if (suffixType.baseType == BaseDataType::eUChar) // string not compatible with tokens
                suffixVal.iAttribute->setResolvedType(suffixVal, type); // LCOV_EXCL_LINE This will never happen
        }
        else
        {
            // else, the 3 needs to have the same type
            std::array<AttributeObj, 3> attrs{ inputVal, suffixVal, outputVal };
            node.iNode->resolveCoupledAttributes(node, attrs.data(), attrs.size());
        }
    }
};

REGISTER_OGN_NODE();

} // nodes
} // graph
} // omni
