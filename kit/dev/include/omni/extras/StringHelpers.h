// SPDX-FileCopyrightText: Copyright (c) 2018-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file
//! @brief String manipulation helper utilities
#pragma once

#include "../../carb/Types.h"

#include <algorithm>
#include <sstream>
#include <string>
#include <vector>
#include <cctype>
#include <limits>

namespace omni
{
namespace extras
{

#pragma push_macro("max")
#undef max

/**
 * Splits a string based on a delimiter.
 * @param s The string to split
 * @param d The delimiter character
 * @param count The maximum number of sections to split \p s into
 * @returns a `std::vector` of strings that have been split from \p s at delimiter \p d. The delimiter is not included
 *   in the strings. Adjacent delimiters do not produce empty strings in the returned vector. Up to \p count entries
 *   will be in the returned vector. e.g. `"a.b..c.dee."` would produce `{ "a", "b", "c", "dee" }` assuming that \p d is
 *   `.` and \p count is >= 4.
 */
inline std::vector<std::string> split(const std::string& s, char d, size_t count = std::numeric_limits<size_t>::max())
{
    std::vector<std::string> res;
    std::stringstream ss(s);
    size_t i = 0;
    while (ss.good() && i < count)
    {
        std::string tmp;
        if (i == count - 1)
        {
            std::getline(ss, tmp, (char)0);
        }
        else
        {
            std::getline(ss, tmp, d);
        }

        if (!tmp.empty())
        {
            res.push_back(tmp);
        }
        i++;
    }
    return res;
}

#pragma pop_macro("max")

/**
 * Checks a string to see if it ends with a given suffix.
 * @param str The string to check
 * @param ending The possible ending to check for
 * @returns `true` if \p str ends with \p ending; `false` otherwise
 */
inline bool endsWith(const std::string& str, const std::string& ending)
{
    if (ending.size() > str.size())
    {
        return false;
    }
    return std::equal(ending.rbegin(), ending.rend(), str.rbegin());
}

/**
 * Checks a string to see if it begins with a given prefix.
 * @param str The string to check
 * @param prefix The possible prefix to check for
 * @returns `true` if \p str starts with \p prefix; `false` otherwise
 */
inline bool startsWith(const std::string& str, const std::string& prefix)
{
    return (str.length() >= prefix.length() && str.compare(0, prefix.size(), prefix) == 0);
}

/**
 * Transforms a string to lowercase in-place.
 * @warning This performs an ASCII lowercase only; current locale and UTF-8 encoding is ignored.
 * @param str The string to transform in-place. When the function returns the string has been changed to ASCII
 *   lowercase.
 */
inline void toLower(std::string& str)
{
    std::transform(str.begin(), str.end(), str.begin(), [](char c) { return (char)std::tolower(c); });
}

/**
 * Converts a given string to a 32-bit signed integer value.
 * @warning This function will truncate values and may lose information even though `true` is returned. It's use is not
 *   recommended.
 * @param str The string to convert. May be a decimal, hexadecimal (`0x` prefix) or octal (`0` prefix) number. A
 *   floating point value may also be given including with exponential notation, though floating point values will be
 *   casted to an integer and may lose precision.
 * @param[out] outResult The reference that receives the integer result
 * @returns `true` if `strtoll` or `strtod` parse \p str in its entirety; `false` otherwise. **NOTE** a return value of
 *   `true` does not mean that information or precision is not lost!
 */
inline bool stringToInteger(const std::string& str, int32_t& outResult)
{
    char* numericEnd;

    int32_t val = (int32_t)strtoll(str.c_str(), &numericEnd, 0);
    if (*numericEnd == '\0')
    {
        outResult = val;
        return true;
    }

    double fVal = strtod(str.c_str(), &numericEnd);
    if (*numericEnd == '\0')
    {
        outResult = static_cast<int32_t>(fVal);
        return true;
    }

    return false;
}

//! Default delimiters for \ref stringToInt2.
constexpr char kInt2Delimiters[] = ",x";

/**
 * Converts a string value to an Int2 representation, that is, a two-component vector.
 * \details This function attempts to convert values such as `0,-1` or `99x84` into a \ref carb::Int2. The delimiters
 *   given by \p delims are tried in order, passed along with \p str to \ref split(). If two components are found,
 *   both components must successfully parse with \ref stringToInteger() in order to consider the result valid.
 * @warning See the warnings at \ref stringToInteger() about potential data loss.
 * @param str The string to convert
 * @param[out] outResult Reference that receives the \ref carb::Int2 result from parsing. Only valid if `true` is
 *   returned.
 * @param delims Delimiters to separate the vector components
 * @returns `true` if parsing was successful; `false` otherwise
 */
inline bool stringToInt2(const std::string& str, carb::Int2& outResult, const char* delims = kInt2Delimiters)
{
    // try splitting by different delimiters

    for (int delimIndex = 0; delims[delimIndex] != 0; delimIndex++)
    {
        auto delim = delims[delimIndex];
        auto pathAndOther = split(str, delim);

        if (pathAndOther.size() == 2)
        {
            int32_t x, y;

            if (extras::stringToInteger(pathAndOther[0], x) && extras::stringToInteger(pathAndOther[1], y))
            {
                outResult = { x, y };
                return true;
            }
        }
    }

    return false;
}

//! \defgroup stringtrim String Trimming Utilities
//! @{

//! Default whitespace characters for string trimming functions
constexpr char kTrimCharsDefault[] = " \t\n\r\f\v";

/**
 * Performs an in-place right-trim on a given string.
 * \details This will trim the characters in \p t from the right side of \p s. e.g. given \p s = `"  asdf  "` with the
 *   default \p t value, \p s would be modified to contain `"  asdf"`. This is effectively
 *   `s.erase(s.find_last_not_of(t) + 1)`.
 * @param s The string to trim in-place
 * @param t A string containing the list of characters to trim (such as \ref kTrimCharsDefault)
 * @returns \p s for convenience
 * @see ltrim(), trim(), trimCopy()
 */
inline std::string& rtrim(std::string& s, const char* t = kTrimCharsDefault)
{
    s.erase(s.find_last_not_of(t) + 1);
    return s;
}

/**
 * Performs an in-place left-trim on a given string.
 * \details This will trim the characters in \p t from the left side of \p s. e.g. given \p s = `"  asdf  "` with the
 *   default \p t value, \p s would be modified to contain `"asdf  "`. This is effectively
 *   `s.erase(0, s.find_first_not_of(t))`.
 * @param s The string to trim in-place
 * @param t A string containing the list of characters to trim (such as \ref kTrimCharsDefault)
 * @returns \p s for convenience
 * @see rtrim(), trim(), trimCopy()
 */
inline std::string& ltrim(std::string& s, const char* t = kTrimCharsDefault)
{
    s.erase(0, s.find_first_not_of(t));
    return s;
}

/**
 * Performs an in-place trim (from both sides) on a given string.
 * \details This will trim the characters in \p t from both sides of \p s. e.g. given \p s = `"  asdf  "` with the
 *   default \p t value, \p s would be modified to contain `"asdf"`. This is effectively
 *   `ltrim(rtrim(s, t), t)`.
 * @param s The string to trim in-place
 * @param t A string containing the list of characters to trim (such as \ref kTrimCharsDefault)
 * @returns \p s for convenience
 * @see ltrim(), rtrim(), trimCopy()
 */
inline std::string& trim(std::string& s, const char* t = kTrimCharsDefault)
{
    return ltrim(rtrim(s, t), t);
}

/**
 * Performs a trim (from both sides) on a given string, returning a copy.
 * \details This will trim the characters in \p t from both sides of \p s. e.g. given \p s = `"  asdf  "` with the
 *   default \p t value, `"asdf"` would be returned. This is effectively `std::string copy(s); return trim(copy);`.
 * @param s The string to trim
 * @param t A string containing the list of characters to trim (such as \ref kTrimCharsDefault)
 * @returns The trimmed string
 * @see ltrim(), rtrim(), trim()
 */
inline std::string trimCopy(std::string s, const char* t = kTrimCharsDefault)
{
    trim(s, t);
    return s;
}

//! @}

/**
 * Replaces all instances of a substring within a given string with a replacement value.
 * \details This function calls `std::string::replace()` in a loop so that all instances are replaced.
 * \note The replacement is not recursive, so \p replaceWith may contain the substring \p subStr without causing endless
 *   recursion. Whenever a replacement occurs, the search for \p subStr resumes after the inserted \p replaceWith.
 * @param str The string to modify in-place
 * @param subStr The substring to find within \p str
 * @param replaceWith The substring that all instances of \p subStr are replaced with
 */
inline void replaceAll(std::string& str, const std::string& subStr, const std::string& replaceWith)
{
    size_t pos = str.find(subStr);
    while (pos != std::string::npos)
    {
        str.replace(pos, subStr.size(), replaceWith);
        pos = str.find(subStr, pos + replaceWith.size());
    }
}

/**
 * Checks two strings for equality in an ASCII case-insensitive manner.
 * \warning This function checks for ASCII case-insensitivity only. UTF-8 encoding and locale are ignored.
 * @param str1 The first string to compare
 * @param str2 The second string to compare
 * @returns `true` if the strings are equal when ASCII case is ignored; `false` otherwise
 */
inline bool stringCompareCaseInsensitive(const std::string& str1, const std::string& str2)
{
    return ((str1.size() == str2.size()) && std::equal(str1.begin(), str1.end(), str2.begin(), [](char a, char b) {
                return std::tolower(a) == std::tolower(b);
            }));
}

/**
 * Checks if two given file paths are equal with case sensitivity based on the platform.
 * \warning For Windows, this function checks for ASCII case-insensitivity only. UTF-8 encoding and locale are ignored.
 *   Therefore, this function does not work properly with Windows paths that may contain non-ASCII characters and its
 *   use should be avoided.
 * \note This is intended for file paths only. URLs are case sensitive.
 * @param strLeft The first path to compare
 * @param strRight The second path to compare
 * @returns `true` if \p strLeft and \p strRight are equal paths with the caveats presented above; `false` otherwise
 */
inline bool isPathEqual(const std::string& strLeft, const std::string& strRight)
{
#if CARB_PLATFORM_WINDOWS
    if (strLeft.size() != strRight.size())
    {
        return false;
    }

    return stringCompareCaseInsensitive(strLeft, strRight);
#else
    return (strLeft == strRight);
#endif
}

} // namespace extras
} // namespace omni
