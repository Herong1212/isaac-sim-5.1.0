// Copyright (c) 2019-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Framework.h>
#include <carb/Interface.h>
#include <omni/fabric/IToken.h>

#include <functional>

// Set to empty macro when IPath::iPath static member is removed
#define FABRIC_IPATH_INIT const omni::fabric::IPath* omni::fabric::Path::iPath = nullptr;

namespace omni
{
namespace fabric
{
// PathC are integer keys that identify paths to C-ABI interfaces
struct PathC
{
    constexpr PathC() : path(0){};
    constexpr PathC(uint64_t _path) : path(_path){};
    uint64_t path;

    constexpr bool operator<(const PathC& other) const
    {
        return path < other.path;
    }
    constexpr bool operator==(const PathC& other) const
    {
        return path == other.path;
    }
    constexpr bool operator!=(const PathC& other) const
    {
        return path != other.path;
    }
};

static_assert(std::is_standard_layout<PathC>::value, "Struct must be standard layout as it is used in C-ABI interfaces");

// We don't reference count the uninitialized (or empty) path, and we use
// this fact to avoid unnecessary dll calls to addRef()/removeRef(), for
// example during std::vector resize. To do this we need to check whether a
// path is uninitialized without the dll call getEmptyPath(), so we store
// its value here in a constant.
// We run automated test "IPath::getEmptyPath() dll call can be replaced with
// constant, Path::kUninitializedPath" to ensure that this constant never
// changes.
static constexpr PathC kUninitializedPath{ (uint64_t)0 };

// C-ABI interface to pxr::SdfPath
struct IPath
{
    //! @private to avoid doxygen problems
    CARB_PLUGIN_INTERFACE("omni::fabric::IPath", 0, 2);

    // Create a path. The caller of this function owns a reference to the underlying path object
    PathC (*getHandle)(const char* name);

    // Get the text representation of the path from the handle
    const char* (*getText)(PathC handle);

    // Get the path to the parent
    PathC (*getParent)(PathC handle);

    // Construct a path to a child
    PathC (*appendChild)(PathC handle, TokenC childName);

    // Add a reference to the underlying path object
    void (*addRef)(PathC handle);

    // Remove a reference to the underlying path object
    void (*removeRef)(PathC handle);

    // The empty path object, same as omni::fabric::kUninitializedPath
    PathC (*getEmptyPath)();

    // Creates a path by appending a given relative path to this path.
    PathC (*appendPath)(PathC handle, PathC path);

    // Returns the number of path elements in this path.
    uint32_t (*getPathElementCount)(PathC handle);

    // Returns the token element in this path.
    TokenC (*getNameToken)(PathC handle);
};

// C++ wrapper for IPath
class Path
{
    static omni::fabric::IPath& sIPath();

    struct StealTag{};
    Path(PathC handle, StealTag) : mHandle(handle)
    {
    }

public:
    // DEPRECATED: keeping for binary compatibility
    // Will be removed in October 2021 - @TODO set FABRIC_IPATH_INIT to empty macro when removed!
    // Still safe to use if initialized in a given dll
    static const omni::fabric::IPath* iPath;

    Path() : mHandle(kUninitializedPath)
    {
    }

    Path(const char* path)
    {
        mHandle = sIPath().getHandle(path);
    }

    // Needs to be noexcept for std::vector::resize() to move instead of copy
    ~Path() noexcept
    {
        // We see the compiler construct and destruct many uninitialized
        // temporaries, for example when resizing std::vector.
        // We don't want to do an IPath dll call for these, so skip if handle
        // is uninitialized.
        if (mHandle != kUninitializedPath)
        {
            sIPath().removeRef(mHandle);
        }
    }

    // Copy constructor
    Path(const Path& other) : mHandle(other.mHandle)
    {
        if (mHandle != kUninitializedPath)
        {
            sIPath().addRef(mHandle);
        }
    }

    // Copy construct from integer
    Path(PathC handle) : mHandle(handle)
    {
        if (mHandle != kUninitializedPath)
        {
            sIPath().addRef(mHandle);
        }
    }

    // Move constructor
    // Needs to be noexcept for std::vector::resize() to move instead of copy
    Path(Path&& other) noexcept
    {
        // We are moving the src handle so don't need to change its refcount
        mHandle = other.mHandle;

        // Make source invalid
        other.mHandle = kUninitializedPath;
    }

    // Copy assignment
    Path& operator=(const Path& other)
    {
        if (this != &other)
        {
            if (mHandle != kUninitializedPath)
            {
                sIPath().removeRef(mHandle);
            }

            if (other.mHandle != kUninitializedPath)
            {
                sIPath().addRef(other.mHandle);
            }
        }
        mHandle = other.mHandle;

        return *this;
    }

    // Move assignment
    Path& operator=(Path&& other) noexcept
    {
        if (&other == this)
            return *this;

        // We are about to overwrite the dest handle, so decrease its refcount
        if (mHandle != kUninitializedPath)
        {
            sIPath().removeRef(mHandle);
        }
        // We are moving the src handle so don't need to change its refcount

        mHandle = other.mHandle;
        other.mHandle = kUninitializedPath;

        return *this;
    }

    const char* getText() const
    {
        return sIPath().getText(mHandle);
    }

    Path appendChild(Token const& other) const
    {
        if (mHandle != kUninitializedPath && other != kUninitializedToken)
        {
            return { sIPath().appendChild(mHandle, other.asTokenC()), StealTag{} };
        }

        return { kUninitializedPath };
    }

    Path appendPath(Path const& other) const
    {
        if (mHandle != kUninitializedPath && other != kUninitializedPath)
        {
            return { sIPath().appendPath(mHandle, other.asPathC()), StealTag{} };
        }

        return { kUninitializedPath };
    }

    Path getParent() const
    {
        if (mHandle != kUninitializedPath)
        {
            return { sIPath().getParent(mHandle), StealTag{} };
        }

        return { kUninitializedPath };
    }

    constexpr bool operator<(const Path& other) const
    {
        return mHandle < other.mHandle;
    }
    constexpr bool operator!=(const Path& other) const
    {
        return mHandle != other.mHandle;
    }
    constexpr bool operator==(const Path& other) const
    {
        return mHandle == other.mHandle;
    }

    constexpr bool operator<(const PathC& other) const
    {
        return mHandle < other;
    }
    constexpr bool operator!=(const PathC& other) const
    {
        return mHandle != other;
    }
    constexpr bool operator==(const PathC& other) const
    {
        return mHandle == other;
    }

    constexpr operator PathC() const
    {
        return mHandle;
    }

    constexpr const PathC& asPathC() const
    {
        return mHandle;
    }

private:
    PathC mHandle;
};

static_assert(std::is_standard_layout<Path>::value, "Path must be standard layout as it is used in C-ABI interfaces");

#ifndef __CUDACC__
inline omni::fabric::IPath& Path::sIPath()
{
    // Acquire carbonite interface on first use
    omni::fabric::IPath* iPath = carb::getCachedInterface<omni::fabric::IPath>();
    CARB_ASSERT(iPath);
    return *iPath;
}
#endif // __CUDACC__

} // namespace fabric
} // namespace omni
namespace std
{
template <>
class hash<omni::fabric::PathC>
{
public:
    inline size_t operator()(const omni::fabric::PathC& key) const
    {
        // lower 8 bits have no entropy, so just remove the useless bits
        return key.path >> 8;
    }
};
template <>
class hash<omni::fabric::Path>
{
public:
    inline size_t operator()(const omni::fabric::Path& key) const
    {
        return std::hash<omni::fabric::PathC>()(omni::fabric::PathC(key));
    }
};
} // namespace std
