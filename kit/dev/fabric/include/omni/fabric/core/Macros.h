// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <cstring>
#include <functional>
#include <type_traits>

#include <carb/logging/Log.h>


namespace omni
{
namespace fabric
{

#define ARRAY_COUNT(X) ((sizeof(X) / sizeof(0 [X])) / ((size_t)(!(sizeof(X) % sizeof(0 [X])))))

#define FABRIC_ENFORCE_STANDARD_LAYOUT(X)                                                                              \
    static_assert(std::is_standard_layout<X>::value, "Struct must be standard layout as it is used in C-ABI interfaces.")

#define FABRIC_EXPECT_TRIVIALLY_COPYABLE(X)                                                                            \
    static_assert(std::is_trivially_copyable<X>::value, "Struct expected be trivially copyable.")

#define FABRIC_DEFINE_COMPARATORS(X)                                                                                   \
    inline bool operator<(const X& l, const X& r)                                                                      \
    {                                                                                                                  \
        FABRIC_EXPECT_TRIVIALLY_COPYABLE(X);                                                                           \
        return memcmp(&l, &r, sizeof(X)) < 0;                                                                          \
    }                                                                                                                  \
    inline bool operator<=(const X& l, const X& r)                                                                      \
    {                                                                                                                  \
        FABRIC_EXPECT_TRIVIALLY_COPYABLE(X);                                                                           \
        return memcmp(&l, &r, sizeof(X)) <= 0;                                                                          \
    }                                                                                                                  \
    inline bool operator==(const X& l, const X& r)                                                                     \
    {                                                                                                                  \
        FABRIC_EXPECT_TRIVIALLY_COPYABLE(X);                                                                           \
        return memcmp(&l, &r, sizeof(X)) == 0;                                                                         \
    }                                                                                                                  \
    inline bool operator>(const X& l, const X& r)                                                                      \
    {                                                                                                                  \
        FABRIC_EXPECT_TRIVIALLY_COPYABLE(X);                                                                           \
        return memcmp(&l, &r, sizeof(X)) > 0;                                                                          \
    }                                                                                                                  \
    inline bool operator>=(const X& l, const X& r)                                                                     \
    {                                                                                                                  \
        FABRIC_EXPECT_TRIVIALLY_COPYABLE(X);                                                                           \
        return memcmp(&l, &r, sizeof(X)) >= 0;                                                                         \
    }                                                                                                                  \
    inline bool operator!=(const X& l, const X& r)                                                                     \
    {                                                                                                                  \
        return !(l == r);                                                                                              \
    }


#define FABRIC_DEFINE_ID_TYPE_STD_HASH(X)                                                                              \
    namespace std                                                                                                      \
    {                                                                                                                  \
    template <>                                                                                                        \
    struct hash<X>                                                                                                     \
    {                                                                                                                  \
        std::size_t operator()(const X& key) const                                                                     \
        {                                                                                                              \
            return key.id;                                                                                             \
        }                                                                                                              \
    };                                                                                                                 \
    }

#if CARB_ASSERT_ENABLED
# define VERIFY(X, ...) (CARB_ASSERT(X, ##__VA_ARGS__))
#else
// "|| false" silences GCC's -Wunused-value
# define VERIFY(X, ...) (((X) ? true : false) || false)
#endif

#define USING_CARB_LOG_INFO (g_carbLogFn && g_carbLogLevel <= carb::logging::kLevelInfo)

#define CONCATENATE_IMPL(X, Y) X##Y
#define CONCATENATE(X, Y) CONCATENATE_IMPL(X, Y)
#define STRINGIFY_IMPL(X) #X
#define STRINGIFY(X) STRINGIFY_IMPL(X)

} // namespace fabric
} // namespace omni
