// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#pragma once

#include <omni/graph/core/Handle.h>

#include <vector>
#include <unordered_map>
#include <unordered_set>

namespace omni
{
namespace graph
{
namespace nodes
{

//
// Manager of attribute names, keeps in track if attribute is renamed
//
class AttributeNameMap
{
public:
    using NameToken = omni::graph::core::NameToken;

    AttributeNameMap() = delete;

    AttributeNameMap(const AttributeNameMap&) = delete;
    AttributeNameMap(AttributeNameMap&&) = delete;

    AttributeNameMap& operator=(const AttributeNameMap&) = delete;
    AttributeNameMap& operator=(AttributeNameMap&&) = delete;

    // Initialize rename map and specified attributes
    AttributeNameMap(bool importAttributes,
                     bool renameAttributes,
                     const NameToken inputAttrNames,
                     const NameToken outputAttrNames,
                     const NameToken specifiedAttrNames);

    AttributeNameMap(bool renameAttributes,
                     const NameToken inputAttrNames,
                     const NameToken outputAttrNames,
                     const NameToken specifiedAttrNames);

    // Get name with automatic lookup if attribute is renamed
    NameToken getName(NameToken name) const noexcept;

    bool isSpecifiedName(NameToken name) const noexcept;
    bool isNotSpecifiedName(NameToken name) const noexcept;

    static std::vector<NameToken> splitNames(const char* namesString)
    {
        std::vector<NameToken> names;
        splitNames(namesString, names);
        return names;
    }

    static std::vector<NameToken> splitNames(NameToken namesString)
    {
        std::vector<NameToken> names;
        splitNames(namesString, names);
        return names;
    }

private:
    template <typename C>
    static bool splitNames(const char* namesString, C& names);

    template <typename C>
    static bool splitNames(NameToken namesString, C& names);

    static void append(std::vector<NameToken>& container, NameToken&& value)
    {
        container.push_back(std::forward<NameToken>(value));
    }

    static void append(std::unordered_set<NameToken>& container, NameToken&& value)
    {
        container.insert(std::forward<NameToken>(value));
    }

    bool m_useRename{ false };
    std::unordered_map<NameToken, NameToken> m_rename;

    bool m_useSpecified{ false };
    std::unordered_set<NameToken> m_specified;
};

inline AttributeNameMap::AttributeNameMap(bool importAttributes,
                                          bool renameAttributes,
                                          const NameToken inputAttrNames,
                                          const NameToken outputAttrNames,
                                          const NameToken specifiedAttrNames)
{
    if (!importAttributes)
    {
        return;
    }

    omni::fabric::IToken* iToken = carb::getCachedInterface<omni::fabric::IToken>();
    if (!iToken)
    {
        CARB_LOG_ERROR_ONCE("Failed to initialize node type - no token interface");
        return;
    }

    // Create input -> output rename map
    if (renameAttributes)
    {
        m_useRename = true;

        const std::vector<NameToken> iAttrNames = splitNames(inputAttrNames);
        const std::vector<NameToken> oAttrNames = splitNames(outputAttrNames);

        // If an attribute doesn't have a counterpart in the other array, just pass it through without being renamed.
        const size_t size = std::min(iAttrNames.size(), oAttrNames.size());
        for (size_t i = 0; i < size; ++i)
        {
            m_rename.emplace(iAttrNames[i], oAttrNames[i]);
        }
    }

    // Create specified lookup
    const char* specifiedAttrNamesText = iToken->getText(specifiedAttrNames);
    if (specifiedAttrNamesText != nullptr && specifiedAttrNamesText[0] != 0)
    {
        m_useSpecified = true;
        splitNames(specifiedAttrNamesText, m_specified);
    }
}

inline AttributeNameMap::AttributeNameMap(bool renameAttributes,
                                          const NameToken inputAttrNames,
                                          const NameToken outputAttrNames,
                                          const NameToken specifiedAttrNames)
    : AttributeNameMap{ true, renameAttributes, inputAttrNames, outputAttrNames, specifiedAttrNames }
{
}

inline AttributeNameMap::NameToken AttributeNameMap::getName(NameToken name) const noexcept
{
    // if renaming is disabled return input name
    if (!m_useRename)
    {
        return name;
    }

    // if renaming is enabled, find attribute in the lookup map
    auto iter = m_rename.find(name);
    if (iter != m_rename.end())
    {
        return iter->second;
    }
    return name;
}

inline bool AttributeNameMap::isSpecifiedName(NameToken name) const noexcept
{
    return m_useSpecified && m_specified.count(name) != 0;
}

inline bool AttributeNameMap::isNotSpecifiedName(NameToken name) const noexcept
{
    return m_useSpecified && m_specified.count(name) == 0;
}

template <typename C>
bool AttributeNameMap::splitNames(const char* namesString, C& names)
{
    omni::fabric::IToken* iToken = carb::getCachedInterface<omni::fabric::IToken>();
    if (!iToken)
    {
        CARB_LOG_ERROR("Failed to split token strings - no token interface");
        return false;
    }

    constexpr size_t invalidIndex = ~size_t(0);
    const std::size_t length = std::strlen(namesString);

    size_t previousBegin = invalidIndex;
    for (size_t i = 0; i < length; ++i)
    {
        const char c = namesString[i];
        // Attribute names can be separated with spaces, tabs, commas, or semicolons.
        if (c == ' ' || c == '\t' || c == ',' || c == ';')
        {
            if (previousBegin != invalidIndex)
            {
                // End of previous attribute name
                std::string fullName(namesString + previousBegin, i - previousBegin);
                append(names, iToken->getHandle(fullName.c_str()));
                previousBegin = invalidIndex;
            }
        }
        else if (previousBegin == invalidIndex)
        {
            // Beginning of new attribute name
            previousBegin = i;
        }
    }
    if (previousBegin != invalidIndex)
    {
        // End of previous attribute name
        std::string fullName(namesString + previousBegin, length - previousBegin);
        append(names, iToken->getHandle(fullName.c_str()));
    }
    return true;
}

template <typename C>
bool AttributeNameMap::splitNames(NameToken namesToken, C& names)
{
    omni::fabric::IToken* iToken = carb::getCachedInterface<omni::fabric::IToken>();
    if (!iToken)
    {
        CARB_LOG_ERROR("Failed to split token strings - no token interface");
        return false;
    }

    const char* namesString = iToken->getText(namesToken);
    return splitNames(namesString, names);
}

} // namespace io
} // namespace graph
} // namespace omni
