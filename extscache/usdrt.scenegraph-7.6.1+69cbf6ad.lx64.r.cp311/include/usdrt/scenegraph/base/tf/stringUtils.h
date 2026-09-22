// Copyright (c) 2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

//! @file
//!
//! @brief TODO

#include <cstring>
#include <string>

namespace usdrt
{

inline bool Tf_StringStartsWithImpl(char const* s, size_t slen, char const* prefix, size_t prelen)
{
    return slen >= prelen && strncmp(s, prefix, prelen) == 0;
}

// NOTE: OMPE-19870: Unused TfStringStartsWith(const std::string& s, const char*
//        prefix) overload removed due buffer-overflow danger in unchecked
//        strlen

/// \overload
inline bool TfStringStartsWith(const std::string& s, const std::string& prefix)
{
    return Tf_StringStartsWithImpl(s.c_str(), s.length(), prefix.c_str(), prefix.length());
}

inline bool Tf_StringEndsWithImpl(char const *s, size_t slen, char const *suffix, size_t suflen)
{
    return slen >= suflen && strcmp(s + (slen - suflen), suffix) == 0;
}

inline bool TfStringEndsWith(const std::string& s, const std::string& suffix)
{
    return Tf_StringEndsWithImpl(s.c_str(), s.length(), suffix.c_str(), suffix.length());
}

} // namespace usdrt
