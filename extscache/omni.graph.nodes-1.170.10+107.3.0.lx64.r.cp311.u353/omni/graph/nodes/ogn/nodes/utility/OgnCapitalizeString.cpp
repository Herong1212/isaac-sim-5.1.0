// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnCapitalizeStringDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <algorithm>
#include <string>
// clang-format on

namespace omni
{
namespace graph
{
namespace nodes
{
void stringOperation(OgnCapitalizeStringDatabase& db, NameToken operation, std::string& str)
{
    if (str.size() == 0)
        return;

    // Find the desired comparison
    if (operation == db.tokens.upper)
        std::transform(str.begin(), str.end(), str.begin(), [](auto c) { return std::toupper(c); });
    // Lower: this is lower
    else if (operation == db.tokens.lower)
        std::transform(str.begin(), str.end(), str.begin(), [](auto c) { return std::tolower(c); });
    // Capitalize: This is capitalized
    else if (operation == db.tokens.capitalize)
    {
        std::transform(str.begin(), str.end(), str.begin(), [](auto c) { return std::tolower(c); });
        str[0] = std::toupper(str[0]);
    }
    // Title Case: This Is A Title
    else if (operation == db.tokens.title)
    {
        // Capitalize string
        std::transform(str.begin(), str.end(), str.begin(), [](auto c) { return std::tolower(c); });
        str[0] = std::toupper(str[0]);

        // Capitalize character after " "
        size_t pos_start = 0;
        size_t pos_end = 0;
        while ((pos_end = str.find(" ", pos_start)) != std::string::npos)
        {
            pos_start = pos_end + 1;
            if (pos_start != std::string::npos)
                str[pos_start] = std::toupper(str[pos_start]);
        }
    }
    else
    {
        throw ogn::compute::InputError("Failed to resolve token " + std::string(db.tokenToString(operation)) +
                                       ", expected one of (UpperCase, LowerCase, Capitalize, Title)");
    }
}

// unnamed namespace to avoid multiple declaration when linking
namespace
{
size_t tryComputeAssumingString(OgnCapitalizeStringDatabase& db, size_t count)
{
    for (size_t idx = 0; idx < count; ++idx)
    {
        auto const in = db.inputs.string(idx).template get<uchar[]>();
        auto out = db.outputs.string(idx).template get<uchar[]>();

        if (!in->empty())
        {
            std::string str(in->data(), in->data() + in->size());
            stringOperation(db, db.inputs.operation(idx), str);
            out.resize(str.size());
            memcpy(out->data(), str.data(), str.size());
        }
        else
            out.resize(0);
    }
    return count;
}

size_t tryComputeAssumingToken(OgnCapitalizeStringDatabase& db, size_t count)
{
    for (size_t idx = 0; idx < count; ++idx)
    {
        auto const in = db.inputs.string(idx).template get<ogn::Token>();
        auto out = db.outputs.string(idx).template get<ogn::Token>();

        if (*in != omni::fabric::kUninitializedToken)
        {
            std::string str = db.tokenToString(*in);
            stringOperation(db, db.inputs.operation(idx), str);
            *out = db.stringToToken(str.c_str());
        }
        else
            *out = omni::fabric::kUninitializedToken;
    }
    return count;
}

size_t tryComputeAssumingTokenArray(OgnCapitalizeStringDatabase& db, size_t count)
{
    for (size_t idx = 0; idx < count; ++idx)
    {
        auto const in = db.inputs.string(idx).template get<ogn::Token[]>();
        auto out = db.outputs.string(idx).template get<ogn::Token[]>();

        if (!in->empty())
        {
            out.resize(in.size());
            for (size_t i = 0; i < in.size(); i++)
            {
                std::string str = db.tokenToString((*in)[i]);
                stringOperation(db, db.inputs.operation(idx), str);
                (*out)[i] = db.stringToToken(str.c_str());
            }
        }
        else
            out.resize(0);
    }
    return count;
}
} // namespace

class OgnCapitalizeString
{
public:
    static size_t computeVectorized(OgnCapitalizeStringDatabase& db, size_t count)
    {
        try
        {
            auto& inputType = db.inputs.string().type();
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
        auto const in = node.iNode->getAttributeByToken(node, inputs::string.token());
        auto const out = node.iNode->getAttributeByToken(node, outputs::string.token());

        std::array<AttributeObj, 2> attrs{ in, out };
        node.iNode->resolveCoupledAttributes(node, attrs.data(), attrs.size());
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
