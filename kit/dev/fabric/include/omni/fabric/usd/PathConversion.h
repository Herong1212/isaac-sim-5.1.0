// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/logging/Log.h>

#include <omni/fabric/FabricTypes.h>
#include <omni/fabric/IdTypes.h>
#include <omni/fabric/IPath.h>
#include <omni/fabric/IToken.h>
#include <omni/fabric/Type.h>
#include <omni/fabric/core/AttrNameAndType.h>

#include <omni/fabric/usd/interface/UsdIncludes.h>

#include <set>
#include <vector>

namespace omni
{
namespace fabric
{

//
// pxr::SdfPath <-> PathC interop
//

// asInt() is the same as SdfPath::_AsInt()
// Fabric relies on asInt(a)==asInt(b) <=> a is same path as b,
// which is how SdfPath::operator== is currently defined.
// If USD changes sizeof(pxr::SdfPath), we will need to change PathC to make it
// the same size.

static_assert(sizeof(pxr::SdfPath) == sizeof(PathC), "Change PathC to make the same size as pxr::SdfPath");

inline PathC asInt(const pxr::SdfPath& sdfPath)
{
    // DO NOT STEAL THIS LOGIC IT IS SUBJECT TO CHANGE
    PathC pathC;
    const void* sdfPathPtr = &sdfPath; // -Wclass-memaccess on gcc11.4.0
    std::memcpy(&pathC, sdfPathPtr, sizeof(pxr::SdfPath));
    return pathC;
}

inline const pxr::SdfPath& toSdfPath(const PathC& pathC)
{
    // DO NOT STEAL THIS LOGIC IT IS SUBJECT TO CHANGE
    return reinterpret_cast<const pxr::SdfPath&>(pathC);
}

inline const pxr::SdfPath& toSdfPath(const Path& path)
{
    return toSdfPath(path.asPathC());
}

// The rvalue reference form is deleted. Please pass an lvalue reference instead to
// avoid potential issues with temporary objects.
const pxr::SdfPath& toSdfPath(PathC&& pathC) = delete;
const pxr::SdfPath& toSdfPath(Path&& path) = delete;

CARB_DEPRECATED("Please use asInt(const pxr::SdfPath& sdfPath) as we won't handle null pointers")
inline const PathC* asInt(const pxr::SdfPath* path)
{
    // DO NOT STEAL THIS LOGIC IT IS SUBJECT TO CHANGE
    return reinterpret_cast<const PathC*>(path);
}

CARB_DEPRECATED("Please use toSdfPath")
inline const pxr::SdfPath& intToPath(const PathC& path)
{
    return toSdfPath(path);
}

//
// pxr::TfToken <-> TokenC interop
//  We outright copy TfToken without changing it's references
//  This is fast and simple, but means TfToken lifetime MUST exceed fabric's copies to still be meaningful
//

static_assert(sizeof(pxr::TfToken) == sizeof(TokenC), "Change TokenC to make the same size as pxr::TfToken");

inline TokenC asInt(const pxr::TfToken& tfToken)
{
    // DO NOT STEAL THIS LOGIC IT IS SUBJECT TO CHANGE
    TokenC tokenC;
    const void* tfTokenPtr = &tfToken; // -Wclass-memaccess on gcc11.4.0
    std::memcpy(&tokenC, tfTokenPtr, sizeof(pxr::TfToken));
    return tokenC;
}

inline const pxr::TfToken& toTfToken(const TokenC& tokenC)
{
    // DO NOT STEAL THIS LOGIC IT IS SUBJECT TO CHANGE
    return reinterpret_cast<const pxr::TfToken&>(tokenC);
}

inline const pxr::TfToken& toTfToken(const Token& token)
{
    return toTfToken(token.asTokenC());
}

// The rvalue reference form is deleted. Please pass an lvalue reference instead to
// avoid potential issues with temporary objects.
const pxr::TfToken& toTfToken(TokenC&& tokenC) = delete;
const pxr::TfToken& toTfToken(Token&& token) = delete;

CARB_DEPRECATED("Please use asInt(const pxr::TfToken& tfToken) as we won't handle null pointers")
inline const TokenC* asInt(const pxr::TfToken* token)
{
    // DO NOT STEAL THIS LOGIC IT IS SUBJECT TO CHANGE
    return reinterpret_cast<const TokenC*>(token);
}

CARB_DEPRECATED("Please use toTfToken")
inline const pxr::TfToken& intToToken(const TokenC& token)
{
    return toTfToken(token);
}

//
// omni::fabric::IPath <-> PathC interop
//

static_assert(sizeof(pxr::SdfPath) == sizeof(Path), "Change Path to make the same size as pxr::SdfPath");

CARB_DEPRECATED("Please use toSdfPath(path.asPathC())")
inline const pxr::SdfPath* toSdfPath(const Path* path)
{
    // DO NOT STEAL THIS LOGIC IT IS SUBJECT TO CHANGE
    return reinterpret_cast<const pxr::SdfPath*>(path);
}

//
// omni::fabric::AttrName
//

inline std::string toString(const AttrName& attrName)
{
    return toTfToken(attrName.name).GetString() + toString(attrName.suffix);
}

} // namespace fabric
} // namespace omni
