// Copyright (c) 2023-2024, NVIDIA CORPORATION. All rights reserved.
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
//! @brief USDRT implementation of SdfAssetPath - represents "asset" type attributes

#include <omni/fabric/IToken.h>
#include <usdrt/scenegraph/interface/IRtAssetPath.h>

#include <string>

namespace usdrt
{

//! SdfAssetPath represent a path to an asset (file or URI) in
//! both un-resolved and resolved form. 'asset' type attribute
//! will Get and Set a value of this type
//!
class SdfAssetPath
{
public:
    //! Construct an empty asset path
    SdfAssetPath();

    //! Construct an asset path with an empty resolved path
    //!
    //! @param path The unresolved asset path
    SdfAssetPath(const std::string& path);

    //! Construct an asset path unresolved and resolved paths
    //!
    //! @param path The unresolved asset path
    //! @param resolvedPath The resolved asset path
    SdfAssetPath(const std::string& path, const std::string& resolvedPath);

    //! Return the unresolved asset path as a string
    //!
    //! @returns unresolved asset path
    std::string GetAssetPath() const;

    //! Return the resolved asset path as a string
    //!
    //! @returns resolved asset path
    std::string GetResolvedPath() const;

    // RT only

    //! Construct an asset from an IRtAssetPath smart pointer
    //!
    //! @param assetPath The IRtAssetPath
    SdfAssetPath(omni::core::ObjectPtr<usdrt::IRtAssetPath> assetPath);

    //! Create an SdfAssetPath from an omni::fabric::AssetPath pointer
    //! (as a void* to avoid including FabricUSD.h which includes USD)
    //!
    //! @param fabricAssetPath Pointer to an omni::fabric::AssetPath as a void*
    //!
    //! @returns A new SdfAssetPath object
    static SdfAssetPath CreateFromFabric(const void* fabricAssetPath);

    //! Return the unresolved asset path as a TokenC
    //!
    //! @returns unresolved asset path
    omni::fabric::TokenC _GetAssetPathC() const;

    //! Return the resolved asset path as a TokenC
    //!
    //! @returns resolved asset path
    omni::fabric::TokenC _GetResolvedPathC() const;

    bool operator==(const SdfAssetPath& rhs) const;
    bool operator!=(const SdfAssetPath& rhs) const;
    bool operator<(const SdfAssetPath& rhs) const;

private:
    omni::core::ObjectPtr<usdrt::IRtAssetPath> m_assetPath;
};

inline SdfAssetPath::SdfAssetPath()
{
    m_assetPath = omni::core::createType<usdrt::IRtAssetPath>();
}

inline SdfAssetPath::SdfAssetPath(const std::string& path)
{
    m_assetPath = omni::core::createType<usdrt::IRtAssetPath>()->create(path.c_str());
}

inline SdfAssetPath::SdfAssetPath(const std::string& path, const std::string& resolvedPath)
{
    m_assetPath = omni::core::createType<usdrt::IRtAssetPath>()->createWithResolved(path.c_str(), resolvedPath.c_str());
}

inline SdfAssetPath::SdfAssetPath(omni::core::ObjectPtr<usdrt::IRtAssetPath> assetPath) : m_assetPath(assetPath)
{
}

inline SdfAssetPath SdfAssetPath::CreateFromFabric(const void* fabricAssetPath)
{
    return SdfAssetPath(omni::core::createType<usdrt::IRtAssetPath>()->createFromFabric(fabricAssetPath));
}

inline std::string SdfAssetPath::GetAssetPath() const
{
    return std::string(m_assetPath->getAssetPath());
}

inline std::string SdfAssetPath::GetResolvedPath() const
{
    return std::string(m_assetPath->getResolvedPath());
}

inline bool SdfAssetPath::operator==(const SdfAssetPath& rhs) const
{
    return GetAssetPath() == rhs.GetAssetPath() && GetResolvedPath() == rhs.GetResolvedPath();
}

inline bool SdfAssetPath::operator!=(const SdfAssetPath& rhs) const
{
    return GetAssetPath() != rhs.GetAssetPath() || GetResolvedPath() != rhs.GetResolvedPath();
}

inline bool SdfAssetPath::operator<(const SdfAssetPath& rhs) const
{
    if (GetAssetPath() == rhs.GetAssetPath())
    {
        if (GetResolvedPath() < rhs.GetResolvedPath())
        {
            return true;
        }
    }

    return GetAssetPath() < rhs.GetAssetPath();
}

inline omni::fabric::TokenC SdfAssetPath::_GetAssetPathC() const
{
    return m_assetPath->getAssetPathC();
}

inline omni::fabric::TokenC SdfAssetPath::_GetResolvedPathC() const
{
    return m_assetPath->getResolvedPathC();
}

} // namespace usdrt
