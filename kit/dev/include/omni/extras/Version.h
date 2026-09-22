// SPDX-FileCopyrightText: Copyright (c) 2019-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file
//! @brief Version utilities
#pragma once

#include "StringHelpers.h"
#include "../../carb/RString.h"

#include <string>

namespace omni
{
namespace extras
{

/**
 * Version struct, follows Semantic Versioning 2.0. https://semver.org/
 * @warning This struct is not @rstref{ABI safe <abi-compatibility>} and must not be passed through ABI boundaries. For
 *   an ABI-safe version, see \ref omni::ext::Version.
 */
struct SemanticVersion
{
    //! The major version, as defined by <a href="https://semver.org">Semantic Versioning</a>. May be negative to match
    //! any major version.
    int32_t major{ -1 };
    //! The minor version, as defined by <a href="https://semver.org">Semantic Versioning</a>. May be negative to match
    //! any minor version.
    int32_t minor{ -1 };
    //! The patch version, as defined by <a href="https://semver.org">Semantic Versioning</a>. May be negative to match
    //! any patch version.
    int32_t patch{ -1 };
    std::string prerelease; //!< A string indicating a pre-release value. May be empty
    std::string build; //!< A string indicating a build value. May be empty

    //! Constructor.
    //! \details Initializes a SemanticVersion with `-1` for all version values and empty pre-release and build values.
    SemanticVersion() = default;

    /**
     * Converts this version to a string.
     * \details If \ref major, \ref minor and \ref patch are negative, an empty string is returned. Otherwise the string
     * returned is `<major>.<minor>.<patch>[-<prerelease>][+<build>]`. The `+<build>` section is only included if
     * \p includeBuildMetadata is `true`. The `-<prerelease>` and `+<build>` sections are only included if the
     * \ref prerelease and \ref build members (respectively) are not empty.
     * @param includeBuildMetadata If `true`, the `+<build>` section is included in the returned string
     * @returns the version string. See above for detailed explanation
     */
    std::string toString(bool includeBuildMetadata = true) const
    {
        if (this->major < 0 && this->minor < 0 && this->patch < 0)
            return "";
        else
        {
            std::ostringstream ss;
            if (this->major >= 0)
                ss << this->major;
            if (this->minor >= 0)
                ss << "." << this->minor;
            if (this->patch >= 0)
                ss << "." << this->patch;
            if (!std::string(this->prerelease).empty())
                ss << "-" << this->prerelease;
            if (includeBuildMetadata && !std::string(this->build).empty())
                ss << "+" << this->build;
            return ss.str();
        }
    }

    //! Replaces major, minor or patch values with zeros if they are negative.
    void replaceNegativesWithZeros() noexcept
    {
        if (this->major < 0)
            this->major = 0;
        if (this->minor < 0)
            this->minor = 0;
        if (this->patch < 0)
            this->patch = 0;
    }

    //! Checks if the major, minor and patch values are all zeros.
    //! @returns `true` if the \ref major, \ref minor and \ref patch values are all zero; `false` otherwise
    bool isAllZeroes() const noexcept
    {
        return this->major == 0 && this->minor == 0 && this->patch == 0;
    }

    //! Returns a default-constructed SemanticVersion.
    //! @returns a default-constructed SemanticVersion
    static SemanticVersion getDefault() noexcept
    {
        return {};
    }
};

/**
 * Checks if the given SemanticVersion has negative major, minor and patch values.
 * @param v A \ref SemanticVersion to test
 * @returns `true` if @p v has negative major, minor and patch values; `false` otherwise
 */
inline bool isAnyVersion(const SemanticVersion& v)
{
    return v.major < 0 && v.minor < 0 && v.patch < 0;
}

/**
 * Semantic Version pre-release comparator according to rules at https://semver.org/#spec-item-11
 * @param x A pre-release value from a \ref SemanticVersion
 * @param y A pre-release value from a \ref SemanticVersion
 * @returns -1 if \p x should be ordered-before \p y; 0 if they are equal; 1 in all other cases
 */
inline int prereleaseCmp(const char* x, const char* y)
{
    // SemVer prerelease part comparison according to: https://semver.org/#spec-item-11

    const size_t xLen = strlen(x);
    const size_t yLen = strlen(y);

    //  both empty
    if (xLen == 0 && yLen == 0)
        return 0;

    // ("abc" < "") => -1
    if (yLen == 0)
        return -1;

    // ("" < "abc") => 1
    if (xLen == 0)
        return 1;

    const char* xPartFrom = x;
    const char* yPartFrom = y;
    while (1)
    {
        // Find next '.'. Chunks are: [xPartFrom, xPartTo] and [yPartFrom, yPartTo]
        const char* xPartTo = strchr(xPartFrom, '.');
        xPartTo = xPartTo ? xPartTo : x + xLen;
        const char* yPartTo = strchr(yPartFrom, '.');
        yPartTo = yPartTo ? yPartTo : y + yLen;
        const size_t xPartLen = (size_t)(xPartTo - xPartFrom);
        const size_t yPartLen = (size_t)(yPartTo - yPartFrom);

        // Try to convert to integer until next '.'.
        char* end;
        const long xNum = strtol(xPartFrom, &end, 10);
        const bool xIsNum = (end == xPartTo);
        const long yNum = strtol(yPartFrom, &end, 10);
        const bool yIsNum = (end == yPartTo);


        // "123" < "abc"
        if (xIsNum && !yIsNum)
            return -1;
        if (!xIsNum && yIsNum)
            return 1;

        if (xIsNum && yIsNum)
        {
            // numerical comparison
            if (xNum != yNum)
                return xNum < yNum ? -1 : 1;
        }
        else
        {
            // string comparison until next nearest '.'
            const int res = strncmp(xPartFrom, yPartFrom, carb_min(xPartLen, yPartLen));

            // if different "zzz" < "abc", return:
            if (res != 0)
                return res < 0 ? -1 : 1;

            // they are the same, but one longer? "abc" < "abcdef"
            if (xPartLen != yPartLen)
                return xPartLen < yPartLen ? -1 : 1;
        }

        // Go to the next `.` part
        xPartFrom = xPartTo + 1;
        yPartFrom = yPartTo + 1;

        // Reached the end of both? => they are equal
        if (xPartFrom == x + xLen + 1 && yPartFrom == y + yLen + 1)
            break;

        // x ended first? "abc.def" < "abc.def.xyz"
        if (xPartFrom == x + xLen + 1)
            return -1;

        // y ended first?
        if (yPartFrom == y + yLen + 1)
            return 1;
    }

    return 0;
}

//! @copydoc prereleaseCmp(const char*,const char*)
inline int prereleaseCmp(const std::string& x, const std::string& y)
{
    return prereleaseCmp(x.c_str(), y.c_str());
}

/**
 * Less-than comparator for two versions.
 * @tparam VersionT The type of the version struct, typically \ref omni::ext::Version or \ref SemanticVersion.
 * @param lhs The first version to compare
 * @param rhs The second version to compare
 * @returns -1 if \p lhs should be ordered-before \p rhs; 0 if eequal; 1 in all other cases
 * @see prereleaseCmp(const char*,const char*)
 */
template <class VersionT>
inline int versionsCmp(const VersionT& lhs, const VersionT& rhs)
{
    if (lhs.major != rhs.major)
        return lhs.major < rhs.major ? -1 : 1;

    if (lhs.minor != rhs.minor)
        return lhs.minor < rhs.minor ? -1 : 1;

    if (lhs.patch != rhs.patch)
        return lhs.patch < rhs.patch ? -1 : 1;

    return prereleaseCmp(lhs.prerelease, rhs.prerelease);
}


/**
 * Less-than operator for two semantic versions.
 * @param lhs The first \ref SemanticVersion to compare
 * @param rhs The second \ref SemanticVersion to compare
 * @returns `true` if \p lhs should be ordered-before \p rhs; `false` otherwise
 * @see prereleaseCmp(const char*,const char*), versionsCmp()
 */
inline bool operator<(const SemanticVersion& lhs, const SemanticVersion& rhs)
{
    return versionsCmp(lhs, rhs) < 0;
}

/**
 * Equality operator for two semantic versions.
 * @param lhs The first \ref SemanticVersion to compare
 * @param rhs The second \ref SemanticVersion to compare
 * @returns `true` if \p lhs and \p rhs are equal; `false` otherwise
 */
inline bool operator==(const SemanticVersion& lhs, const SemanticVersion& rhs)
{
    // Notice that "build metadata" is ignored in version comparison
    return lhs.major == rhs.major && lhs.minor == rhs.minor && lhs.patch == rhs.patch && lhs.prerelease == rhs.prerelease;
}

/**
 * Parses a given string into a semantic version.
 * @param str The string to parse into a semantic version, as described by \ref SemanticVersion::toString()
 * @param outVersion A reference that will receive the semantic version. If `false` is returned, this reference will be
 *   in an indeterminate state.
 * @returns `true` if parsing succeeded and \p outVersion has received the parsed semantic version; `false` if parsing
 *   failed and \p outVersion is in an indeterminate state and should not be used
 */
inline bool stringToVersion(const std::string& str, SemanticVersion& outVersion)
{
    outVersion = SemanticVersion::getDefault();

    // [major].[minor].[patch]-[prerelease]+[build]
    auto versionAndBuild = extras::split(str, '+');

    // Only one `+` allowed in semver
    if (versionAndBuild.size() > 2)
        return false;

    auto versionParts = extras::split(versionAndBuild[0], '-', 2);

    // parse first part: [major].[minor].[patch]
    {
        auto parts = extras::split(versionParts[0], '.');

        if (parts.empty())
            return false;

        // 1.2.3.4 is not semver
        if (parts.size() > 3)
            return false;

        if (!extras::stringToInteger(parts[0], outVersion.major))
            return false;

        if (parts.size() > 1)
        {
            if (!extras::stringToInteger(parts[1], outVersion.minor))
                return false;
        }
        if (parts.size() > 2)
        {
            if (!extras::stringToInteger(parts[2], outVersion.patch))
                return false;
        }
    }

    // parse second part: [prerelease]+[build]
    if (versionParts.size() > 1)
        outVersion.prerelease = versionParts[1];

    if (versionAndBuild.size() > 1)
        outVersion.build = versionAndBuild[1];

    return true;
}

/**
 * Parses a string to a semantic version, or a default value if parsing fails.
 * @param str The string to parse
 * @returns a \ref SemanticVersion parsed from \p str, or \ref SemanticVersion::getDefault() if parsing fails
 */
inline SemanticVersion stringToVersionOrDefault(const std::string& str)
{
    SemanticVersion v;
    if (!stringToVersion(str, v))
        v = SemanticVersion::getDefault();
    return v;
}

/**
 * Attempts to parse the Git hash from an Omniverse-specific semantic version.
 * \details An Omniverse Flow version format is `<version>+<gitbranch>.<number>.<githash>.<build_location>`. This
 *   function parses out the `<githash>` from this format.
 * @param version The \ref SemanticVersion to process
 * @param outHash A reference that receives the Git hash if `true` is returned; if `false` is returned this will be
 *   `00000000`.
 * @returns `true` if parsing succeeded; `false` otherwise
 */
inline bool gitHashFromOmniverseVersion(const extras::SemanticVersion& version, std::string& outHash)
{
    // Omniverse Flow format: "{version}+{gitbranch}.{number}.{githash}.{build_location}"
    auto parts = extras::split(version.build, '.');
    outHash = "00000000";
    if (parts.size() > 2)
    {
        outHash = parts[2];
        return true;
    }
    return false;
}

} // namespace extras
} // namespace omni
