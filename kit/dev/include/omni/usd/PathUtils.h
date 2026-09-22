// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Framework.h>
#include <carb/extras/Path.h>

#include <random>
#include <string>

#if CARB_PLATFORM_WINDOWS
#    define strncasecmp(x, y, z) _strnicmp(x, y, z)
#endif

namespace omni
{
namespace usd
{

constexpr char kWritableUsdFileExts[] = "usd|usda|usdc|live";

class PathUtils
{
public:
    /**
     * Checks if path is omniverse path (prefixed with omni:).
     *
     * @param path Path string.
     * @return true if it's omniverse path.
     */

    static bool isOmniPath(const std::string& path)
    {
        return path.length() > 10 && strncasecmp(path.c_str(), "omniverse:", 10) == 0;
    }

    /**
     * Appends a random number to path. This is used to construct unique path.
     *
     * @param path Path string.
     * @return unique path string.
     */
    static std::string appendRandomNumberToFilename(const std::string& path)
    {
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_int_distribution<uint64_t> dis(0, std::numeric_limits<uint64_t>::max());

        carb::extras::Path carbPath(path);
        return carbPath.getParent() / carbPath.getStem() + std::to_string(dis(gen)) + carbPath.getExtension();
    }
};
}
}
