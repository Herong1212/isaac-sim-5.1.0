// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnBundleToUSDADatabase.h>

#include <omni/graph/core/BundlePrims.h>
#include <omni/math/linalg/half.h>

#include <algorithm>
#include <numeric>

using omni::graph::core::BundleAttributeInfo;
using omni::graph::core::ConstBundlePrim;
using omni::graph::core::ConstBundlePrims;
using omni::math::linalg::half;

static const char* const s_indentText = "    ";
static const size_t s_indentLength = 4;
static const char* const s_defSpaceText = "def ";
static const size_t s_defSpaceLength = 4;
static const char* const s_interpolationEquals = "interpolation = \"";
static const size_t s_interpolationEqualsLength = 17;

static void parsePath(const bool outputAncestors,
                      const char*& pathText,
                      std::vector<std::pair<size_t, size_t>>& pathComponents,
                      const char*& nameText,
                      size_t& nameTextLength)
{
    if (pathText == nullptr || pathText[0] == 0)
    {
        return;
    }

    // Skip the first leading slash, if there is one.
    if (pathText[0] == '/')
    {
        ++pathText;

        // If only "/", don't treat prim as having a name.
        if (pathText[0] == 0)
        {
            return;
        }
    }
    nameText = pathText;

    // Separate the path into its parts.
    const char* nextSlash = strchr(nameText, '/');
    while (nextSlash != nullptr)
    {
        // Ignore trailing slash.
        if (nextSlash[1] == 0)
        {
            nameTextLength = nextSlash - nameText;
            break;
        }
        if (outputAncestors)
        {
            pathComponents.emplace_back(nameText - pathText, nextSlash - pathText);
        }
        nameText = nextSlash + 1;
        nextSlash = strchr(nameText, '/');
    }
    if (nextSlash == nullptr)
    {
        nameTextLength = strlen(nameText);
    }
}

static void parsePath(const GraphContextObj& context,
                      const ConstBundleHandle& bundle,
                      const NameToken primPathToken,
                      const bool outputAncestors,
                      const char*& pathText,
                      std::vector<std::pair<size_t, size_t>>& pathComponents,
                      const char*& nameText,
                      size_t& nameTextLength)
{
    const auto* const iToken = context.iToken;
    const auto* const iBundle = context.iBundle;
    const auto* const iAttributeData = context.iAttributeData;

    // Get the path.
    ConstAttributeDataHandle primPathAttr;
    iBundle->getAttributesByNameR(&primPathAttr, context, bundle, &primPathToken, 1);
    if (!primPathAttr.isValid())
    {
        return;
    }
    Type type = iAttributeData->getType(context, primPathAttr);
    if (type != Type(BaseDataType::eToken, 1, 0, AttributeRole::eNone))
    {
        return;
    }

    NameToken pathToken = *getDataR<NameToken>(context, primPathAttr);
    pathText = iToken->getText(pathToken);
    parsePath(outputAncestors, pathText, pathComponents, nameText, nameTextLength);
}

static const char* getPrimType(const GraphContextObj& context,
                               const ConstBundleHandle& bundle,
                               const NameToken primTypeToken)
{
    const auto* const iToken = context.iToken;
    const auto* const iBundle = context.iBundle;
    const auto* const iAttributeData = context.iAttributeData;

    // Get the type.
    ConstAttributeDataHandle primTypeAttr;
    iBundle->getAttributesByNameR(&primTypeAttr, context, bundle, &primTypeToken, 1);
    if (!primTypeAttr.isValid())
    {
        return nullptr;
    }
    Type type = iAttributeData->getType(context, primTypeAttr);
    if (type != Type(BaseDataType::eToken, 1, 0, AttributeRole::eNone))
    {
        return nullptr;
    }

    NameToken typeToken = *getDataR<NameToken>(context, primTypeAttr);
    const char* typeText = iToken->getText(typeToken);
    if (typeText == nullptr || typeText[0] == 0)
    {
        return nullptr;
    }
    return typeText;
}

static void pushText(std::vector<char>& outputText, const char* begin, const char* end)
{
    // TODO: reserve in advance, but without risking n^2 time if n small reserve calls.
    for (; begin != end; ++begin)
    {
        outputText.push_back(*begin);
    }
}

static void outputPrimHeader(const char* primPathText,
                             const std::vector<std::pair<size_t, size_t>>& pathComponents,
                             const char* primTypeText,
                             const char* primNameText,
                             const size_t nameTextLength,
                             std::vector<char>& outputText)
{
    for (size_t level = 0, levelCount = pathComponents.size(); level < levelCount; ++level)
    {
        // Indents
        for (size_t indent = 0; indent < level; ++indent)
        {
            pushText(outputText, s_indentText, s_indentText + s_indentLength);
        }

        // def
        pushText(outputText, s_defSpaceText, s_defSpaceText + s_defSpaceLength);

        // NOTE: Don't know type of ancestor prims.

        // "name"
        outputText.push_back('\"');
        const char* const begin = primPathText + pathComponents[level].first;
        const char* const end = primPathText + pathComponents[level].second;
        pushText(outputText, begin, end);
        outputText.push_back('\"');
        outputText.push_back('\n');

        // Indents and open brace
        for (size_t indent = 0; indent < level; ++indent)
        {
            pushText(outputText, s_indentText, s_indentText + s_indentLength);
        }
        outputText.push_back('{');
        outputText.push_back('\n');
    }

    const size_t level = pathComponents.size();

    // Indents
    for (size_t indent = 0; indent < level; ++indent)
    {
        pushText(outputText, s_indentText, s_indentText + s_indentLength);
    }

    // def
    pushText(outputText, s_defSpaceText, s_defSpaceText + s_defSpaceLength);

    // PrimType, if supplied
    if (primTypeText != nullptr)
    {
        const char* const primTypeEnd = primTypeText + strlen(primTypeText);
        pushText(outputText, primTypeText, primTypeEnd);
        outputText.push_back(' ');
    }

    // "name", if supplied
    if (primNameText != nullptr)
    {
        outputText.push_back('\"');
        const char* const primNameEnd = primNameText + nameTextLength;
        pushText(outputText, primNameText, primNameEnd);
        outputText.push_back('\"');
    }
    outputText.push_back('\n');

    // Indents and open brace
    for (size_t indent = 0; indent < level; ++indent)
    {
        pushText(outputText, s_indentText, s_indentText + s_indentLength);
    }
    outputText.push_back('{');
    outputText.push_back('\n');
}

static void outputPrimFooter(size_t levelCount, std::vector<char>& outputText)
{
    // All but the last level
    for (size_t level = levelCount - 1; level > 0; --level)
    {
        // Indents
        for (size_t indent = 0; indent < level; ++indent)
        {
            pushText(outputText, s_indentText, s_indentText + s_indentLength);
        }
        outputText.push_back('}');
        outputText.push_back('\n');
    }
    // Last level
    outputText.push_back('}');
    outputText.push_back('\n');
}

static void outputSingleFloat(half i, std::vector<char>& outputText)
{
    float f = float(i);
    char buffer[128];
#ifdef _WIN32
    sprintf_s(buffer, "%.8e", f);
#else
    snprintf(buffer, 128, "%.8e", f);
#endif
    for (size_t i = 0; i < 128 && buffer[i] != 0; ++i)
    {
        outputText.push_back(buffer[i]);
    }
}

static void outputSingleFloat(float f, std::vector<char>& outputText)
{
    char buffer[128];
#ifdef _WIN32
    sprintf_s(buffer, "%.8e", f);
#else
    snprintf(buffer, 128, "%.8e", f);
#endif
    for (size_t i = 0; i < 128 && buffer[i] != 0; ++i)
    {
        outputText.push_back(buffer[i]);
    }
}

static void outputSingleFloat(double f, std::vector<char>& outputText)
{
    char buffer[128];
#ifdef _WIN32
    sprintf_s(buffer, "%.17e", f);
#else
    snprintf(buffer, 128, "%.17e", f);
#endif
    for (size_t i = 0; i < 128 && buffer[i] != 0; ++i)
    {
        outputText.push_back(buffer[i]);
    }
}

static void outputSingleInt(int64_t i, std::vector<char>& outputText)
{
    char buffer[128];
#ifdef _WIN32
    sprintf_s(buffer, "%lld", (long long)i);
#else
    snprintf(buffer, 128, "%lld", (long long)i);
#endif
    for (size_t i = 0; i < 128 && buffer[i] != 0; ++i)
    {
        outputText.push_back(buffer[i]);
    }
}

static void outputSingleInt(uint64_t i, std::vector<char>& outputText)
{
    char buffer[128];
#ifdef _WIN32
    sprintf_s(buffer, "%llu", (unsigned long long)i);
#else
    snprintf(buffer, 128, "%llu", (unsigned long long)i);
#endif
    for (size_t i = 0; i < 128 && buffer[i] != 0; ++i)
    {
        outputText.push_back(buffer[i]);
    }
}

static void outputSingleInt(uint8_t i, std::vector<char>& outputText)
{
    outputSingleInt(uint64_t(i), outputText);
}

static void outputSingleInt(int32_t i, std::vector<char>& outputText)
{
    outputSingleInt(int64_t(i), outputText);
}

static void outputSingleInt(uint32_t i, std::vector<char>& outputText)
{
    outputSingleInt(uint64_t(i), outputText);
}

static void outputSingleInt(bool i, std::vector<char>& outputText)
{
    // bool values are "0" or "1" in usda text.
    outputSingleInt(i ? uint64_t(1) : uint64_t(0), outputText);
}

static void outputSingleToken(const IToken* iToken, NameToken t, std::vector<char>& outputText)
{
    outputText.push_back('\"');
    const char* text = iToken->getText(t);
    const char* end = text + strlen(text);
    pushText(outputText, text, end);
    outputText.push_back('\"');
}

static void outputSinglePath(const omni::fabric::IPath* iPath, omni::fabric::PathC p, std::vector<char>& outputText)
{
    outputText.push_back('<');
    const char* text = iPath->getText(p);
    const char* end = text + strlen(text);
    pushText(outputText, text, end);
    outputText.push_back('>');
}

template <typename T>
static void outputSingleFloatTuple(const T* data, size_t n, std::vector<char>& outputText, bool isQuaternion)
{
    outputText.push_back('(');
    outputSingleFloat(data[isQuaternion ? 3 : 0], outputText);
    for (size_t component = 1; component < n; ++component)
    {
        outputText.push_back(',');
        outputText.push_back(' ');
        outputSingleFloat(data[component - (isQuaternion ? 1 : 0)], outputText);
    }
    outputText.push_back(')');
}

template <typename T>
static void outputSingleMatrix(const T* data, size_t n, std::vector<char>& outputText)
{
    outputText.push_back('(');
    outputText.push_back(' ');
    outputSingleFloatTuple(data, n, outputText, false);
    data += n;
    for (size_t i = 1; i < n; ++i)
    {
        outputText.push_back(',');
        outputText.push_back(' ');
        outputSingleFloatTuple(data, n, outputText, false);
        data += n;
    }
    outputText.push_back(' ');
    outputText.push_back(')');
}

template <typename T>
static void outputFloatArray(const GraphContextObj& context,
                             const BundleAttributeInfo& attr,
                             const Type type,
                             size_t elementCount,
                             bool isArray,
                             std::vector<char>& outputText)
{
    const T* data = attr.getData<T>();

    if (type.componentCount == 1)
    {
        outputSingleFloat(data[0], outputText);
        for (size_t i = 1; i < elementCount; ++i)
        {
            outputText.push_back(',');
            outputText.push_back(' ');
            outputSingleFloat(data[i], outputText);
        }
    }
    else if ((type.role == AttributeRole::eTransform || type.role == AttributeRole::eFrame ||
              type.role == AttributeRole::eMatrix) &&
             (type.componentCount == 4 || type.componentCount == 9 || type.componentCount == 16))
    {
        // Matrix
        // This formula doesn't generalize, but:
        // ((4 - 4) / 5) + 2 --> 2
        // ((9 - 4) / 5) + 2 --> 3
        // ((16 - 4)/ 5) + 2 --> 4
        // which is what we need for the matrix size here.
        size_t n = ((type.componentCount - 4) / 5) + 2;
        outputSingleMatrix(data, n, outputText);
        data += type.componentCount;
        for (size_t i = 1; i < elementCount; ++i)
        {
            outputText.push_back(',');
            outputText.push_back(' ');
            outputSingleMatrix(data, n, outputText);
            data += type.componentCount;
        }
    }
    else if (type.componentCount > 1)
    {
        // Quaternion values in usda files list the real part first, but in memory,
        // the real part comes last, so they need to be reordered for output.
        bool isQuaternion = (type.componentCount == 4 && type.role == AttributeRole::eQuaternion);

        outputSingleFloatTuple(data, type.componentCount, outputText, isQuaternion);
        data += type.componentCount;
        for (size_t i = 1; i < elementCount; ++i)
        {
            outputText.push_back(',');
            outputText.push_back(' ');
            outputSingleFloatTuple(data, type.componentCount, outputText, isQuaternion);
            data += type.componentCount;
        }
    }
}

template <typename T>
static void outputIntArray(const GraphContextObj& context,
                           const BundleAttributeInfo& attr,
                           const Type type,
                           size_t elementCount,
                           bool isArray,
                           std::vector<char>& outputText)
{
    const T* data = attr.getData<T>();

    if (type.componentCount == 1)
    {
        outputSingleInt(data[0], outputText);
        for (size_t i = 1; i < elementCount; ++i)
        {
            outputText.push_back(',');
            outputText.push_back(' ');
            outputSingleInt(data[i], outputText);
        }
    }
    else if (type.componentCount > 1)
    {
        outputText.push_back('(');
        outputSingleInt(*data, outputText);
        ++data;
        for (size_t component = 1; component < type.componentCount; ++component, ++data)
        {
            outputText.push_back(',');
            outputText.push_back(' ');
            outputSingleInt(*data, outputText);
        }
        outputText.push_back(')');
        for (size_t i = 1; i < elementCount; ++i)
        {
            outputText.push_back(',');
            outputText.push_back(' ');
            outputText.push_back('(');
            outputSingleInt(*data, outputText);
            ++data;
            for (size_t component = 1; component < type.componentCount; ++component, ++data)
            {
                outputText.push_back(',');
                outputText.push_back(' ');
                outputSingleInt(*data, outputText);
            }
            outputText.push_back(')');
        }
    }
}

static void outputTokenArray(const GraphContextObj& context,
                             const BundleAttributeInfo& attr,
                             const Type type,
                             size_t elementCount,
                             bool isArray,
                             std::vector<char>& outputText)
{
    const auto* iToken = context.iToken;
    const NameToken* data = (const NameToken*)attr.getData<Token>();

    if (type.componentCount == 1)
    {
        outputSingleToken(iToken, data[0], outputText);
        for (size_t i = 1; i < elementCount; ++i)
        {
            outputText.push_back(',');
            outputText.push_back(' ');
            outputSingleToken(iToken, data[i], outputText);
        }
    }
    else if (type.componentCount > 1)
    {
        outputText.push_back('(');
        outputSingleToken(iToken, *data, outputText);
        ++data;
        for (size_t component = 1; component < type.componentCount; ++component, ++data)
        {
            outputText.push_back(',');
            outputText.push_back(' ');
            outputSingleToken(iToken, *data, outputText);
        }
        outputText.push_back(')');
        for (size_t i = 1; i < elementCount; ++i)
        {
            outputText.push_back(',');
            outputText.push_back(' ');
            outputText.push_back('(');
            outputSingleToken(iToken, *data, outputText);
            ++data;
            for (size_t component = 1; component < type.componentCount; ++component, ++data)
            {
                outputText.push_back(',');
                outputText.push_back(' ');
                outputSingleToken(iToken, *data, outputText);
            }
            outputText.push_back(')');
        }
    }
}

static void outputRelationshipArray(const GraphContextObj& context,
                                    const BundleAttributeInfo& attr,
                                    const Type type,
                                    size_t elementCount,
                                    bool isArray,
                                    std::vector<char>& outputText)
{
    const auto* iPath = context.iPath;
    const omni::fabric::PathC* data;
    if (isArray)
    {
        data = *getDataR<const omni::fabric::PathC*>(context, attr.handle());
    }
    else
    {
        data = getDataR<omni::fabric::PathC>(context, attr.handle());
    }
    if (type.componentCount == 1)
    {
        outputSinglePath(iPath, data[0], outputText);
        for (size_t i = 1; i < elementCount; ++i)
        {
            outputText.push_back(',');
            outputText.push_back(' ');
            outputSinglePath(iPath, data[i], outputText);
        }
    }
    else if (type.componentCount > 1)
    {
        outputText.push_back('(');
        outputSinglePath(iPath, *data, outputText);
        ++data;
        for (size_t component = 1; component < type.componentCount; ++component, ++data)
        {
            outputText.push_back(',');
            outputText.push_back(' ');
            outputSinglePath(iPath, *data, outputText);
        }
        outputText.push_back(')');
        for (size_t i = 1; i < elementCount; ++i)
        {
            outputText.push_back(',');
            outputText.push_back(' ');
            outputText.push_back('(');
            outputSinglePath(iPath, *data, outputText);
            ++data;
            for (size_t component = 1; component < type.componentCount; ++component, ++data)
            {
                outputText.push_back(',');
                outputText.push_back(' ');
                outputSinglePath(iPath, *data, outputText);
            }
            outputText.push_back(')');
        }
    }
}

static void outputAttributeArray(const GraphContextObj& context,
                                 const BundleAttributeInfo& attr,
                                 const Type type,
                                 size_t elementCount,
                                 bool isArray,
                                 std::vector<char>& outputText)
{
    if (elementCount == 0)
    {
        return;
    }

    switch (type.baseType)
    {
    case BaseDataType::eHalf:
        outputFloatArray<half>(context, attr, type, elementCount, isArray, outputText);
        break;
    case BaseDataType::eFloat:
        outputFloatArray<float>(context, attr, type, elementCount, isArray, outputText);
        break;
    case BaseDataType::eDouble:
        outputFloatArray<double>(context, attr, type, elementCount, isArray, outputText);
        break;
    case BaseDataType::eBool:
        outputIntArray<bool>(context, attr, type, elementCount, isArray, outputText);
        break;
    case BaseDataType::eUChar:
        outputIntArray<uint8_t>(context, attr, type, elementCount, isArray, outputText);
        break;
    case BaseDataType::eInt:
        outputIntArray<int32_t>(context, attr, type, elementCount, isArray, outputText);
        break;
    case BaseDataType::eInt64:
        outputIntArray<int64_t>(context, attr, type, elementCount, isArray, outputText);
        break;
    case BaseDataType::eUInt:
        outputIntArray<uint32_t>(context, attr, type, elementCount, isArray, outputText);
        break;
    case BaseDataType::eUInt64:
        outputIntArray<uint64_t>(context, attr, type, elementCount, isArray, outputText);
        break;
    case BaseDataType::eToken:
        outputTokenArray(context, attr, type, elementCount, isArray, outputText);
        break;
    case BaseDataType::eRelationship:
        outputRelationshipArray(context, attr, type, elementCount, isArray, outputText);
        break;
    default:
        CARB_LOG_ERROR("OgnBundleToUSDA outputting attribute value of unsupported type");
        break;
    }
}

static void outputAllAttributes(const GraphContextObj& context,
                                ConstBundlePrim& prim,
                                const size_t indentCount,
                                std::vector<char>& outputText,
                                const bool usePrimvarMetadata,
                                const bool outputValues)
{
    const auto* const iToken = context.iToken;

    // Get all of the attributes.
    size_t attrCount = prim.attrCount();
    std::vector<const BundleAttributeInfo*> attrs;
    attrs.reserve(attrCount);
    std::vector<std::pair<NameToken, std::string>> names;
    names.reserve(attrCount);
    for (const auto& attr : prim)
    {
        attrs.push_back(&attr);
        NameToken nameToken = attr.name();
        const char* nameText = iToken->getText(nameToken);
        names.emplace_back(nameToken, std::string(nameText));
    }

    // Sort the attributes alphabetically.
    std::vector<size_t> indices;
    indices.resize(attrCount);
    std::iota(indices.begin(), indices.end(), 0);
    std::sort(indices.begin(), indices.end(), [&names](size_t a, size_t b) { return names[a].second < names[b].second; });

    for (size_t attri = 0; attri < attrCount; ++attri)
    {
        const size_t index = indices[attri];
        const BundleAttributeInfo& attr = *attrs[index];

// Skip primPath or primType, if intended for the prim header
// FIXME: Re-add this as needed.
#if 0
        if ((db.inputs.usePrimPath() && nameToken == primPathToken) ||
            (db.inputs.usePrimType() && nameToken == primTypeToken))
        {
            continue;
        }
#endif

        const char* nameText = names[index].second.c_str();
        const size_t nameLength = names[index].second.size();
        const char* nameEnd = nameText + nameLength;

        // Check if this is a primvar, and may have metadata, like interpolation.
        const char* interpolationText = nullptr;
        if (usePrimvarMetadata && attr.interpolation() != omni::fabric::kUninitializedToken)
        {
            interpolationText = iToken->getText(attr.interpolation());
        }

        // Indents
        for (size_t indent = 0; indent < indentCount; ++indent)
        {
            pushText(outputText, s_indentText, s_indentText + s_indentLength);
        }

        // Type name
        const NameToken typeNameToken = context.iAttributeData->getTypeName(context, attr.handle());
        const char* typeNameText = iToken->getText(typeNameToken);
        const char* typeNameEnd = typeNameText + strlen(typeNameText);
        pushText(outputText, typeNameText, typeNameEnd);
        outputText.push_back(' ');

        // Attribute name
        pushText(outputText, nameText, nameEnd);

        // Attribute values
        if (outputValues)
        {
            outputText.push_back(' ');
            outputText.push_back('=');
            outputText.push_back(' ');

            const Type type = attr.type();
            bool isArray = (type.arrayDepth == 1);
            size_t elementCount = 1;
            if (isArray)
            {
                elementCount = attr.size();
                outputText.push_back('[');
            }

            outputAttributeArray(context, attr, type, elementCount, isArray, outputText);

            if (isArray)
            {
                outputText.push_back(']');
            }
        }

        // Primvar metadata
        if (interpolationText != nullptr)
        {
            outputText.push_back(' ');
            outputText.push_back('(');
            outputText.push_back('\n');
            // Indents
            for (size_t indent = 0; indent < indentCount + 1; ++indent)
            {
                pushText(outputText, s_indentText, s_indentText + s_indentLength);
            }
            pushText(outputText, s_interpolationEquals, s_interpolationEquals + s_interpolationEqualsLength);
            pushText(outputText, interpolationText, interpolationText + strlen(interpolationText));
            outputText.push_back('\"');
            outputText.push_back('\n');
            // Indents
            for (size_t indent = 0; indent < indentCount; ++indent)
            {
                pushText(outputText, s_indentText, s_indentText + s_indentLength);
            }
            outputText.push_back(')');
        }

        outputText.push_back('\n');
    }
}

class OgnBundleToUSDA
{
public:
    static bool compute(OgnBundleToUSDADatabase& db)
    {
        auto& context = db.abi_context();

        const auto* const iToken = context.iToken;

        const NameToken primPathToken = iToken->getHandle("primPath");
        const NameToken primTypeToken = iToken->getHandle("primType");

        ConstBundleHandle bundle = db.inputs.bundle().abi_bundleHandle();

        std::vector<char> outputText;

        ConstBundlePrims bundlePrims(context, bundle);
        if (bundlePrims.getPrimCount() != 0)
        {
            // FIXME: Sort out sharing common ancestors of prims if outputAncestors is true.

            for (auto& prim : bundlePrims)
            {
                const char* primPathText = nullptr;
                std::vector<std::pair<size_t, size_t>> pathComponents;
                const char* primNameText = nullptr;
                size_t nameTextLength = 0;
                if (db.inputs.usePrimPath())
                {
                    primPathText = iToken->getText(prim.path());
                    parsePath(db.inputs.outputAncestors(), primPathText, pathComponents, primNameText, nameTextLength);
                }

                const char* primTypeText = nullptr;
                if (db.inputs.usePrimType())
                    primTypeText = iToken->getText(prim.type());

                bool hasPrimHeader = (primNameText != nullptr || primTypeText != nullptr);
                size_t indentCount = hasPrimHeader ? (1 + pathComponents.size()) : 0;
                if (hasPrimHeader)
                {
                    outputPrimHeader(
                        primPathText, pathComponents, primTypeText, primNameText, nameTextLength, outputText);
                }

                outputAllAttributes(
                    context, prim, indentCount, outputText, db.inputs.usePrimvarMetadata(), db.inputs.outputValues());

                if (hasPrimHeader)
                {
                    outputPrimFooter(indentCount, outputText);
                }
            }


            // Add the terminating zero.
            outputText.push_back(0);

            db.outputs.text() = iToken->getHandle(outputText.data());

            return true;
        }

        const char* primPathText = nullptr;
        std::vector<std::pair<size_t, size_t>> pathComponents;
        const char* primNameText = nullptr;
        size_t nameTextLength = 0;
        if (db.inputs.usePrimPath())
        {
            parsePath(context, bundle, primPathToken, db.inputs.outputAncestors(), primPathText, pathComponents,
                      primNameText, nameTextLength);
        }

        const char* primTypeText = nullptr;
        if (db.inputs.usePrimType())
        {
            primTypeText = getPrimType(context, bundle, primTypeToken);
        }

        bool hasPrimHeader = (primNameText != nullptr || primTypeText != nullptr);
        size_t indentCount = hasPrimHeader ? (1 + pathComponents.size()) : 0;
        if (hasPrimHeader)
        {
            outputPrimHeader(primPathText, pathComponents, primTypeText, primNameText, nameTextLength, outputText);
        }

        outputAllAttributes(context, bundlePrims.getCommonAttrs(), indentCount, outputText,
                            db.inputs.usePrimvarMetadata(), db.inputs.outputValues());

        if (hasPrimHeader)
        {
            outputPrimFooter(indentCount, outputText);
        }

        // Add the terminating zero.
        outputText.push_back(0);

        db.outputs.text() = iToken->getHandle(outputText.data());

        return true;
    }
};

REGISTER_OGN_NODE()
