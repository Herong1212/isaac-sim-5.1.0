// SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file
//! @brief Wildcard utilities for omni.kit.app
#pragma once

#include <regex>
#include <string>
#include <unordered_set>

namespace omni
{
namespace kit
{

/**
 * Defines the wildcard class.
 *
 * @warning This class uses `std::regex` which can be performance intensive. Consider using the functions in
 *   \ref omni::str instead.
 */
class Wildcard
{
public:
    /**
     * Sets the wildcard string.
     *
     * After this is set, call \ref isMatching() to determine if a string matches the wildcard pattern.
     *
     * @param pattern The wildcard pattern string to set.
     */
    void setPatternString(const char* pattern)
    {
        // Special regex character
        static const std::unordered_set<char> kSpecialCharacters = { '.', '^', '$', '|', '(', ')', '[',
                                                                     ']', '{', '}', '*', '+', '?', '\\' };

        std::string expression = "^.*";

        size_t len = strlen(pattern);
        char prev_char = ' ';
        for (size_t i = 0; i < len; i++)
        {
            const char character = pattern[i];
            switch (character)
            {
                case '?':
                    expression += '.';
                    break;
                case ' ':
                    expression += ' ';
                    break;
                case '*':
                    if (i == 0 || prev_char != '*')
                    {
                        // make sure we don't have continuous * which will make std::regex_search super heavy, leading
                        // to crash
                        expression += ".*";
                    }
                    break;
                default:
                    if (kSpecialCharacters.find(character) != kSpecialCharacters.end())
                    {
                        // Escape special regex characters
                        expression += '\\';
                    }
                    expression += character;
            }
            prev_char = character;
        }

        expression += ".*$";
        m_expression = expression;
        buildRegex();
    }

    /**
     * Tests a string against the wildcard to see if they match.
     *
     * @param str The string to be tested.
     * @retval true the string matches the wildcard
     * @retval false the string does not match the wildcard
     */
    bool isMatching(const char* str) const
    {
        return std::regex_search(str, m_wildcardRegex);
    }

    /**
     * Sets if the wildcard should be case sensitive.
     *
     * The default is false (case insensitive).
     *
     * @param sensitive `true` if the wildcard should be case sensitive; `false` to be case insensitive
     */
    void setCaseSensitive(bool sensitive)
    {
        if (m_caseSensitive != sensitive)
        {
            m_caseSensitive = sensitive;
            buildRegex();
        }
    }

private:
    void buildRegex()
    {
        if (m_expression.length())
        {
            auto flags = std::regex_constants::optimize;
            if (!m_caseSensitive)
            {
                flags |= std::regex_constants::icase;
            }
            m_wildcardRegex = std::regex(m_expression, flags);
        }
    }

    std::string m_expression;
    std::regex m_wildcardRegex;
    bool m_caseSensitive = false;
};

} // namespace kit
} // namespace omni
