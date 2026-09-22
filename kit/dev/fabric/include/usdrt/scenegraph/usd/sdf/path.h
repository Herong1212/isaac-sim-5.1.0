// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

//! @file sdf/path.h

#include <omni/core/Omni.h>
#include <omni/fabric/IFabric.h>
#include <omni/fabric/IPath.h>
#include <omni/fabric/IToken.h>
#include <usdrt/scenegraph/base/tf/stringUtils.h>
#include <usdrt/scenegraph/base/tf/token.h>
#include <usdrt/scenegraph/interface/IRtPath107.h>

#include <set>
#include <string>

namespace usdrt
{

class SdfPath;
class SdfPathAncestorsRange;

//! A vector of SdfPaths.
using SdfPathVector = std::vector<SdfPath>;
//! A set of SdfPaths.
using SdfPathSet = std::set<SdfPath>;

//! @class SdfPath
//!
//! A path value used to locate objects in the scenegraph.
//!
//! Uses omni::fabric::Path for the prim path, and TfToken for
//! the property part.
//!
//! @note USDRT paths support is limited to absolute paths.
 class SdfPath
{
public:
    //! @name Constructors
    //! @{

    //! Constructs the default, empty path.
    SdfPath() = default;
    //! Default copy constructor
    SdfPath(const SdfPath&) = default;
    //! Create a new path from fabric data.
    //! @param path The fabric path.
    //! @param prop The property part of the new path. Default empty TfToken.
    SdfPath(const omni::fabric::Path& path, const TfToken prop = TfToken());
    //! Create a new path with a copy of the given fabric data.
    //! @param path The fabric path.
    //! @param prop The property part of the new path. Default empty TfToken.
    SdfPath(omni::fabric::Path&& path, TfToken&& prop = TfToken()) noexcept;
    //! Create a new path from the given fabric data.
    //! @param pathC The fabric PathC - integer key that identifies paths in fabric.
    //! @param prop The property part of the new path. Default empty TfToken.
    SdfPath(const omni::fabric::PathC pathC, const TfToken prop = TfToken());
    //! Create a new path from the given string.
    //! @param path String representation of the new path.
    //! @note This does not currently check if the path string is valid.
    //! It only searches for the property delimiter to construct the
    //! fabric path and token.
    SdfPath(const std::string& path);
    //! Create a new path from the given c-string.
    //! @param path c-string representation of the new path.
    //! @note This does not currently check if the path string is valid.
    //! It only searches for the property delimiter to construct the
    //! fabric path and token
    SdfPath(const char* path);
    //! Create a new path from the given omni::fabric::Connection
    //! @param conn omni::fabric::Connection representation of the path.
    SdfPath(const omni::fabric::Connection& conn);
    //! Create a new path from the given fabric data.
    //! @param pathC The fabric PathC - integer key that identifies paths in fabric.
    //! @param propC The fabric TokenC representation of thie property - integer key that identifies tokens in fabric.
    SdfPath(const omni::fabric::PathC pathC, const omni::fabric::TokenC propC);
    //! Create a new path from the omni interface object.
    //! @param rtPath the omni interface object
    SdfPath(omni::core::ObjectPtr<usdrt::IRtPath> rtPath);
    //! Destructor
    ~SdfPath();
    //! @}

    // Static Methods

    //! The empty path value, equivalent to SdfPath().
    static const SdfPath EmptyPath();
    //! The absolute path representing the top of the
    //! namespace hierarchy.
    static const SdfPath AbsoluteRootPath();
    //! Check if the given string represents a legal path identifier.
    //! @note This calls underlying USD SdfPath. No performance improvements over USD.
    //! @param name string representation of the path
    //! @returns Return `true` if @p name is a valid path identifier
    static bool IsValidIdentifier(const std::string& name);
    //! Check if the given string represents a legal namespaced path identifier.
    //! @note This calls underlying USD SdfPath. No performance improvements over USD.
    //! @param name string representation of the path
    //! @returns Return `true` if `IsValidIdentifier` does.
    static bool IsValidNamespacedIdentifier(const std::string& name);
    //! Check if the given string represents a valid path.
    //! @note This calls underlying USD SdfPath. No performance improvements over USD.
    //! @param pathString string representation of the path
    //! @param[out] errMsg Error message set if the path is not valid.  Default 0.
    //! @returns Return `true` if @p pathString is a valid path string.
    //! Otherwise return false an  if \p errMsg is not NULL,
    //! set the pointed-to string to the parse error.
    static bool IsValidPathString(const std::string& pathString, std::string* errMsg = 0);
    //! Joins @p lhs and @p rhs into a single identifier using the namesapce delimeter.
    //! @returns @p lhs if @p rhs is empty, and vice verse.
    static std::string JoinIdentifier(const TfToken& lhs, const TfToken& rhs);
    //! Joins @p lhs and @p rhs into a single identifier using the namesapce delimeter.
    //! @returns @p lhs if @p rhs is empty, and vice verse.
    static std::string JoinIdentifier(const std::string& lhs, const std::string& rhs);

    /// Tokenizes \p name by the namespace delimiter.
    /// Returns the empty vector if \p name is not a valid namespaced
    /// identifier.
    static std::vector<std::string> TokenizeIdentifier(const std::string& name);

    /// Join \p names into a single identifier using the namespace delimiter.
    /// Any empty strings present in \p names are ignored when joining.
    static std::string JoinIdentifier(const TfTokenVector& names);

    /// Returns (\p name, \c true) where \p name is stripped of the prefix
    /// specified by \p matchNamespace if \p name indeed starts with
    /// \p matchNamespace. Returns (\p name, \c false) otherwise, with \p name
    /// unmodified.
    ///
    /// This function deals with both the case where \p matchNamespace contains
    /// the trailing namespace delimiter ':' or not.
    ///
    static std::pair<std::string, bool> StripPrefixNamespace(const std::string& name, const std::string& matchNamespace);

    /// Returns (\p name, \c true) where \p name is stripped of the suffix
    /// specified by \p matchNamespace if \p name indeed ends with
    /// \p matchNamespace. Returns (\p name, \c false) otherwise, with \p name
    /// unmodified.
    ///
    /// This function deals with both the case where \p matchNamespace contains
    /// the leading namespace delimiter ':' or not.
    ///
    static std::pair<std::string, bool> StripSuffixNamespace(const std::string& name, const std::string& matchNamespace);

    // Querying paths

    //! Returns the string representation of this path as a TfToken.
    TfToken GetToken() const;
    //! Returns the string representation of this path as a std::string.
    std::string GetString() const;
    //! Returns the string representation of this path as a c string.
    const char* GetText() const;
    //! Returns true if this is the empty path (SdfPath::EmptyPath()).
    bool IsEmpty() const;
    //! Returns the name of the prim, property or relational
    //! attribute identified by the path.
    std::string GetName() const;
    //! Returns the name of the prim, property or relational
    //! attribute identified by the path, as a token.
    const TfToken& GetNameToken() const;
    //! Create a new SdfPath by stripping all attributes, targets, and
    //! properties from the leaf prim in this path.
    //! @returns A new SdfPath that is just the prim.
    SdfPath GetPrimPath() const;
    //! Get hash value for this path.
    size_t GetHash() const;

    //! Get the prefix paths of this path.
    //! @returns Return an SdfPathVector containing the prefix paths
    //! of this path, ordered shortest to longest.
    //! @note This calls underlying USD SdfPath. No performance improvements over USD.
    SdfPathVector GetPrefixes() const;
    //! Get the prefix paths of this path.
    //! @param[out] prefixes An SdfPathVector containing the prefix paths
    //! of this path, ordered shortest to longest.
    //! @note This calls underlying USD SdfPath. No performance improvements over USD.
    void GetPrefixes(SdfPathVector* prefixes) const;
    //! Get a range for iterating over the ancestors of this path.
    //!
    //! The range provides iteration over the prefixes of a path, ordered
    //! from longest to shortest (the opposite of the order of the prefixes
    //! returned by GetPrefixes).
    //! @returns Return the SdfPathAncestorRange for iteration.
    SdfPathAncestorsRange GetAncestorsRange() const;

    //! Returns the number of path elements in this path.
    size_t GetPathElementCount() const;
    //! Returns whether the path is absolute.
    bool IsAbsolutePath() const;
    //! Return true if this path is the AbsoluteRootPath().
    bool IsAbsoluteRootPath() const;
    //! Returns whether the path identifies a prim.
    bool IsPrimPath() const;
    //! Returns whether the path identifies a prim or the absolute root.
    bool IsAbsoluteRootOrPrimPath() const;
    //! Returns whether the path identifies a root prim.
    //!
    //! The path must be absolute and have a single element
    //! (for example <c>/foo</c>).
    bool IsRootPrimPath() const;
    //! Returns whether the path identifies a property.
    //!
    //! A relational attribute is considered to be a property, so this
    //! method will return true for relational attributes as well
    //! as properties of prims.
    bool IsPropertyPath() const;
    //! Returns whether the path identifies a prim's property.
    //!
    //! A relational attribute is not a prim property.
    bool IsPrimPropertyPath() const;
    //! Returns whether the path identifies a namespaced property.
    //!
    //! A namespaced property has colon embedded in its name.
    bool IsNamespacedPropertyPath() const;
    //! Return true if this path contains any property elements
    //! (relationships or attributes), false otherwise.
    bool ContainsPropertyElements() const;

    //! Replace the final component of this path with @p newName.
    //! @param newName The token to replace this path's name.
    //! @returns Return a copy of this path with its final component changed to
    //! @a newName. If this path is not a prim or property path, it is invalid. Return empty path.
    SdfPath ReplaceName(TfToken const& newName) const;
    //! Check if this path has @p prefix as a prefix.
    //! @param prefix Given prefix to check
    //! @returns Return true if both this path and \a prefix are not the empty
    /// path and this path has \a prefix as a prefix.  Return false otherwise.
    //! @note This calls underlying USD SdfPath. No performance improvements over USD.
    bool HasPrefix(const SdfPath& prefix) const;
    //! Get the path that identifies this path's namespace parent.
    //!
    //! If this path is a property path, assume no target paths and trim the property part.
    //! Otherwise, use fabric get the parent path.
    //! @return Return a new path that identifies this path's parent.
    SdfPath GetParentPath() const;
    //! Creates a path by stripping all properties and relational
    //! attributes from this path, leaving the path to the containing prim.
    //!
    //! If the path is already a prim or absolute root path, the same
    //! path is returned.
    SdfPath GetAbsoluteRootOrPrimPath() const;
    //! Creates a path by appending a given relative path to this path.
    //!
    //! This path and @p newSuffix must meet the following to be valid:
    //! - If the newSuffix is a prim path, then this path must be a prim path
    //! or a root path.
    //!
    //! - If the newSuffix is a prim property path, then this path must be
    //! a prim path.
    //!
    //! - Neither path can be empty.
    //!
    //! @param newSuffix The relative path to append.
    //! @return Return a new path that appends @p newSuffix to this path.
    //! If this path or @p newSuffix are invalid, return the empty path.
    SdfPath AppendPath(const SdfPath& newSuffix) const;
    //! Creates a path by appending an element for \p childName
    //! to this path.
    //!
    //! This path must be a prim path or the AbsoluteRootPath.
    //! @param childName the child prim name to append.
    //! @return Returns a new path with @p childName appended.
    SdfPath AppendChild(TfToken const& childName) const;
    //! Creates a path by appending an element for \p propName
    //! to this path.
    //!
    //! This path must be a prim path.
    //! @param propName The prop name to append.
    //! @returns Return a new path with @p propName appended.
    SdfPath AppendProperty(TfToken const& propName) const;

    //! Replace all occurences of the prefix path @p oldPrefix with @p newPrefix.
    //!
    //! @param oldPrefix Prefix to replace.
    //! @param newPrefix The new path prefix.
    //! @param fixTargetPaths This is not supported in fabric.
    //! @returns Returns a path with all occurrences of the prefix path
    //! @p oldPrefix replaced with the prefix path @p newPrefix.
    //!
    //! @note This calls underlying USD SdfPath. No performance improvements over USD.
    SdfPath ReplacePrefix(const SdfPath& oldPrefix, const SdfPath& newPrefix, bool fixTargetPaths = true) const;

    //! Get a path with maximal length that is a prefix path of
    /// both this path and @p path.
    /// @param path Path to query.
    /// @returns Return a new path that is the longest common prefix of this path and @p path.
    //! @note This calls underlying USD SdfPath. No performance improvements over USD.
    SdfPath GetCommonPrefix(const SdfPath& path) const;
    //! Find and remove the longest common suffix from two paths.
    //! @param otherPath Other path to query.
    //! @param stopAtRootPrim If this flag is \c true then neither returned path will be
    /// the root path. Default false.
    //! @returns Return a pair of new paths. This path and @p otherPath
    //! respectively, with the longest common suffix removed
    //! @note This calls underlying USD SdfPath. No performance improvements over USD.
    std::pair<SdfPath, SdfPath> RemoveCommonSuffix(const SdfPath& otherPath, bool stopAtRootPrim = false) const;

    // Operators
    //! Cast this path to omni::fabric::PathC
    explicit operator omni::fabric::PathC() const;
    //! Cast this path to omni::fabric::Path
    explicit operator omni::fabric::Path() && noexcept;
    //! Cast this path to omni::fabric::Connection
    operator omni::fabric::Connection() const;
    //! Equality operator
    bool operator==(const SdfPath& rhs) const;
    //! Inequality operator
    bool operator!=(const SdfPath& rhs) const;
    //! Comparison operator
    bool operator<(const SdfPath& rhs) const;

private:
    omni::fabric::Path m_path;
    TfToken m_property;
    mutable TfToken m_pathToken;
    mutable TfToken m_nameToken;
};

//! @class SdfPathAncestorsRange
//!
//! Range representing a path and ancestors, and providing methods for
//! iterating over them.
class SdfPathAncestorsRange
{
public:
    //! Constructor
    SdfPathAncestorsRange(const SdfPath& path) : m_path(path)
    {
    }

    //! Get the current path part in the iteration
    const SdfPath& GetPath() const
    {
        return m_path;
    }

    //! Iterator
    struct iterator
    {
        using iterator_category = std::forward_iterator_tag;
        using value_type = SdfPath;
        using difference_type = std::ptrdiff_t;
        using reference = const SdfPath&;
        using pointer = const SdfPath*;

        //! Construct an iterator from @p path
        iterator(const SdfPath& path) : m_path(path)
        {
        }

        //! Default constructor
        iterator() = default;

        //! Iterator increment
        iterator& operator++();

        //! Dereference operator
        const SdfPath& operator*() const
        {
            return m_path;
        }

        //! Accessor operator
        const SdfPath* operator->() const
        {
            return &m_path;
        }

        //! Equality operator
        bool operator==(const iterator& o) const
        {
            return m_path == o.m_path;
        }

        //! Inequality operator
        bool operator!=(const iterator& o) const
        {
            return m_path != o.m_path;
        }

    private:
        SdfPath m_path;
    };

    iterator begin() const
    {
        return iterator(m_path);
    }

    iterator end() const
    {
        return iterator();
    }

private:
    SdfPath m_path;
};

// Constructors

inline SdfPath::SdfPath(const omni::fabric::Path& path, const TfToken prop) : m_path(path), m_property(prop)
{
}

inline SdfPath::SdfPath(omni::fabric::Path&& path, TfToken&& prop) noexcept
    : m_path(std::move(path)), m_property(std::move(prop))
{
}

inline SdfPath::SdfPath(const omni::fabric::PathC pathC, const TfToken prop) : m_path(pathC), m_property(prop)
{
}

inline SdfPath::SdfPath(const omni::fabric::PathC pathC, const omni::fabric::TokenC propC)
    : m_path(pathC), m_property(propC)
{
}

inline SdfPath::SdfPath(omni::core::ObjectPtr<usdrt::IRtPath> rtPath) : m_path(), m_property()
{
    if (rtPath)
    {
        m_path = rtPath->getPrimPart();
        m_property = TfToken(rtPath->getPropPart());
    }
}

inline SdfPath::SdfPath(const std::string& path)
{
    if (!path.empty())
    {

        size_t index = path.rfind('.');
        if (index != std::string::npos)
        {
            m_path = omni::fabric::Path(path.substr(0, index).c_str());
            m_property = TfToken(path.substr(index + 1, path.size() - 1));
        }
        else
        {
            m_path = omni::fabric::Path(path.c_str());
            m_property = TfToken();
        }
    }
}

inline SdfPath::SdfPath(const char* path) : SdfPath(std::string(path))
{
}

inline SdfPath::SdfPath(const omni::fabric::Connection& conn)
{
    m_path = omni::fabric::Path(conn.path);
    m_property = TfToken(conn.attrName);
}

inline SdfPath::~SdfPath()
{
    omni::fabric::IPath* iPath = carb::getCachedInterface<omni::fabric::IPath>();
    if (iPath == nullptr)
    {
        // FIXME Python bindings helper - if omni.fabric.plugin is unloaded
        // before all Sdf.Path python objects are garbage collected, this
        // leads to COE. So work around this by doing a sneaky reset before
        // destructing m_path.
        *reinterpret_cast<omni::fabric::PathC*>(&m_path) = omni::fabric::kUninitializedPath;
    }
}

inline SdfPath::operator omni::fabric::PathC() const
{
    // ignore m_property when casting to PathC
    return omni::fabric::PathC(m_path);
}

inline SdfPath::operator omni::fabric::Path() && noexcept
{
    return std::move(m_path);
}

inline SdfPath::operator omni::fabric::Connection() const
{
    omni::fabric::Connection conn = omni::fabric::Connection();
    conn.path = omni::fabric::PathC(m_path);
    conn.attrName = omni::fabric::TokenC(m_property);
    return conn;
}

// Static Methods

inline const SdfPath SdfPath::EmptyPath()
{
    omni::fabric::IPath* iPath = carb::getCachedInterface<omni::fabric::IPath>();
    return iPath->getEmptyPath();
}

inline const SdfPath SdfPath::AbsoluteRootPath()
{
    return SdfPath("/");
}

// Querying
inline TfToken SdfPath::GetToken() const
{
    // compute path token if its not set yet
    if (m_pathToken.IsEmpty())
    {
        std::string result(m_path.getText());
        if (!m_property.IsEmpty())
        {
            result += std::string(".") + m_property.GetString();
        }
        m_pathToken = TfToken(result);
    }

    return m_pathToken;
}

inline std::string SdfPath::GetString() const
{

    return GetToken().GetString();
}

inline const char* SdfPath::GetText() const
{
    return GetToken().GetText();
}

inline std::string SdfPath::GetName() const
{
    return GetNameToken().GetString();
}

inline const TfToken& SdfPath::GetNameToken() const
{
    omni::core::ObjectPtr<usdrt::IRtPath> path =
        omni::core::createType<usdrt::IRtPath>()->create(omni::fabric::PathC(m_path), omni::fabric::TokenC(m_property));
    m_nameToken = omni::fabric::Token(path->getNameToken());
    return m_nameToken;
}

inline SdfPath SdfPath::ReplaceName(TfToken const& newName) const
{
    if (IsPrimPath())
        return GetParentPath().AppendChild(newName);
    else if (IsPrimPropertyPath())
        return GetPrimPath().AppendProperty(newName);

    // TODO warn error - not a supported path type
    return SdfPath();
}

inline SdfPath SdfPath::GetPrimPath() const
{
    return SdfPath(m_path);
}

inline size_t SdfPath::GetPathElementCount() const
{
    omni::fabric::IPath* iPath = carb::getCachedInterface<omni::fabric::IPath>();
    if (iPath)
    {
        return static_cast<size_t>(iPath->getPathElementCount(m_path));
    }

    return 0;
}

inline bool SdfPath::IsAbsolutePath() const
{
    omni::core::ObjectPtr<usdrt::IRtPath> path =
        omni::core::createType<usdrt::IRtPath>()->create(omni::fabric::PathC(m_path), omni::fabric::TokenC(m_property));

    return path->isAbsolutePath();
}

inline bool SdfPath::IsAbsoluteRootPath() const
{
    return !IsEmpty() && m_property.IsEmpty() && !GetPathElementCount();
}

inline bool SdfPath::IsPrimPath() const
{
    // Assume a path a path without a prop part is a prim path.
    // We aren't identifying Target, Mapper, or Relational path nodes like USD does.
    return m_property.IsEmpty() && GetPathElementCount();
}

inline bool SdfPath::IsAbsoluteRootOrPrimPath() const
{
    return m_property.IsEmpty() && !IsEmpty();
}

inline bool SdfPath::IsRootPrimPath() const
{
    return m_property.IsEmpty() && IsAbsolutePath() && (GetPathElementCount() == 1);
}

inline bool SdfPath::IsPropertyPath() const
{
    return !m_property.IsEmpty() && !IsEmpty();
}

inline bool SdfPath::IsPrimPropertyPath() const
{
    return IsPropertyPath();
}

inline bool SdfPath::IsNamespacedPropertyPath() const
{
    // TODO sdfpathtokens
    bool hasNamespace = m_property.GetString().find(":") != std::string::npos;
    return IsPropertyPath() && hasNamespace;
}

inline bool SdfPath::ContainsPropertyElements() const
{
    return m_property != TfToken();
}

inline bool SdfPath::HasPrefix(const SdfPath& prefix) const
{
    omni::core::ObjectPtr<usdrt::IRtPath> path =
        omni::core::createType<usdrt::IRtPath>()->create(omni::fabric::PathC(m_path), omni::fabric::TokenC(m_property));
    return path->hasPrefix(omni::fabric::PathC(prefix), prefix.IsPropertyPath() ?
                                                            omni::fabric::TokenC(prefix.GetNameToken()) :
                                                            omni::fabric::kUninitializedToken);
}

inline SdfPath SdfPath::GetParentPath() const
{
    omni::fabric::IPath* iPath = carb::getCachedInterface<omni::fabric::IPath>();
    if (iPath)
    {
        if (!m_property.IsEmpty())
        {
            // if we have a prop part, trim that
            // assuming no target paths
            return SdfPath(m_path);
        }
        else
        {
        }
        return SdfPath(iPath->getParent(m_path));
    }
    return SdfPath();
}

inline SdfPath SdfPath::GetAbsoluteRootOrPrimPath() const
{

    return IsAbsoluteRootPath() ? *this : GetPrimPath();
}

inline SdfPath SdfPath::AppendPath(const SdfPath& newSuffix) const
{
    if (IsEmpty() || newSuffix == EmptyPath())
    {
        // TODO warn error - Cannot append to invalid path
        return EmptyPath();
    }

    if (newSuffix.IsAbsolutePath())
    {
        // TODO warn - Cannot append absolute path to another path
        return EmptyPath();
    }

    if (!m_property.IsEmpty())
    {
        // TODO warn - cannot append a path to a property path
        return EmptyPath();
    }

    if (newSuffix.IsPropertyPath() && IsAbsoluteRootPath())
    {
        // TODO warn - Cannot append a property path to the absolute root path
        return EmptyPath();
    }

    omni::fabric::IPath* iPath = carb::getCachedInterface<omni::fabric::IPath>();
    if (iPath)
    {
        return SdfPath(iPath->appendPath(m_path.asPathC(), newSuffix.m_path.asPathC()), newSuffix.m_property);
    }

    return EmptyPath();
}

inline SdfPath SdfPath::AppendChild(TfToken const& childName) const
{
    if (!m_property.IsEmpty())
    {
        // TODO warn
        return EmptyPath();
    }

    omni::fabric::IPath* iPath = carb::getCachedInterface<omni::fabric::IPath>();
    if (iPath)
    {
        return SdfPath(iPath->appendChild(m_path.asPathC(), omni::fabric::TokenC(childName)));
    }
    return EmptyPath();
}

inline SdfPath SdfPath::AppendProperty(TfToken const& propName) const
{
    if (!m_property.IsEmpty() || !IsPrimPath())
    {
        // TODO warn - Can only append a property to a prim path
        return EmptyPath();
    }

    return SdfPath(m_path, propName);
}

inline SdfPath SdfPath::ReplacePrefix(const SdfPath& oldPrefix, const SdfPath& newPrefix, bool fixTargetPaths) const
{
    omni::core::ObjectPtr<usdrt::IRtPath> path =
        omni::core::createType<usdrt::IRtPath>()->create(omni::fabric::PathC(m_path), omni::fabric::TokenC(m_property));


    omni::core::ObjectPtr<usdrt::IRtPath> newPath = path->replacePrefix(
        omni::fabric::PathC(oldPrefix),
        oldPrefix.IsPropertyPath() ? omni::fabric::TokenC(oldPrefix.GetNameToken()) : omni::fabric::kUninitializedToken,
        omni::fabric::PathC(newPrefix),
        newPrefix.IsPropertyPath() ? omni::fabric::TokenC(newPrefix.GetNameToken()) : omni::fabric::kUninitializedToken);
    return SdfPath(omni::fabric::Path(newPath->getPrimPart()), omni::fabric::Token(newPath->getPropPart()));
}

inline SdfPath SdfPath::GetCommonPrefix(const SdfPath& path) const
{
    if (IsAbsoluteRootPath() || path.IsAbsoluteRootPath())
    {
        return AbsoluteRootPath();
    }
    if (IsEmpty() || path.IsEmpty())
    {
        return EmptyPath();
    }

    omni::core::ObjectPtr<usdrt::IRtPath> thisPath =
        omni::core::createType<usdrt::IRtPath>()->create(omni::fabric::PathC(m_path), omni::fabric::TokenC(m_property));


    omni::core::ObjectPtr<usdrt::IRtPath> newPath = thisPath->getCommonPrefix(
        omni::fabric::PathC(path),
        path.IsPropertyPath() ? omni::fabric::TokenC(path.GetNameToken()) : omni::fabric::kUninitializedToken);

    return SdfPath(omni::fabric::Path(newPath->getPrimPart()), omni::fabric::Token(newPath->getPropPart()));
}

inline std::pair<SdfPath, SdfPath> SdfPath::RemoveCommonSuffix(const SdfPath& otherPath, bool stopAtRootPrim) const
{
    omni::core::ObjectPtr<usdrt::IRtPath> thisPath =
        omni::core::createType<usdrt::IRtPath>()->create(omni::fabric::PathC(m_path), omni::fabric::TokenC(m_property));

    omni::core::ObjectPtr<IRtPath> result1 = omni::core::createType<usdrt::IRtPath>();

    omni::core::ObjectPtr<IRtPath> result2 = omni::core::createType<usdrt::IRtPath>();


    thisPath->removeCommonSuffix(
        omni::fabric::PathC(otherPath),
        otherPath.IsPropertyPath() ? omni::fabric::TokenC(otherPath.GetNameToken()) : omni::fabric::kUninitializedToken,
        result1, result2, stopAtRootPrim);
    return std::make_pair(SdfPath(result1), SdfPath(result2));
}

inline bool SdfPath::IsValidIdentifier(const std::string& name)
{
    omni::core::ObjectPtr<usdrt::IRtPath> thisPath = omni::core::createType<usdrt::IRtPath>();

    return thisPath->isValidIdentifier(name.c_str());
}

inline bool SdfPath::IsValidNamespacedIdentifier(const std::string& name)
{
    omni::core::ObjectPtr<usdrt::IRtPath> thisPath = omni::core::createType<usdrt::IRtPath>();

    return thisPath->isValidNamespacedIdentifier(name.c_str());
}

inline bool SdfPath::IsValidPathString(const std::string& pathString, std::string* errMsg)
{
    omni::core::ObjectPtr<usdrt::IRtPath> thisPath = omni::core::createType<usdrt::IRtPath>();

    char errBuffer[1024];
    bool result = thisPath->isValidPathString(pathString.c_str(), errBuffer);
    if (errMsg)
    {
        *errMsg = errBuffer;
    }
    return result;
}

/* static */
inline std::string SdfPath::JoinIdentifier(const TfToken& lhs, const TfToken& rhs)
{
    return JoinIdentifier(lhs.GetString(), rhs.GetString());
}

/* static */
inline std::string SdfPath::JoinIdentifier(const std::string& lhs, const std::string& rhs)
{
    if (lhs.empty())
    {
        return rhs;
    }
    else if (rhs.empty())
    {
        return lhs;
    }
    else
    {
        return lhs + ":" + rhs;
    }
}

inline std::vector<std::string> SdfPath::TokenizeIdentifier(const std::string& name)
{
    std::vector<std::string> result;

    // This code currently assumes the namespace delimiter is one character.
    const char namespaceDelimiter = ':';

    auto first = name.cbegin();
    auto last = name.cend();

    auto invalidCharacter([](char c) { return !(isalnum(c) || c == '_'); });

    // Not empty and first character is alpha or '_'.
    if (first == last || invalidCharacter(*first))
        return result;
    // Last character is not the namespace delimiter.
    if (*(last - 1) == namespaceDelimiter)
        return result;

    // Count delimiters and reserve space in result.
    result.reserve(1 + std::count(first, last, namespaceDelimiter));

    std::string::const_iterator anchor = first;
    for (++first; first != last; ++first)
    {
        // Allow a namespace delimiter.
        if (*first == namespaceDelimiter)
        {
            // Record token.
            result.push_back(std::string(anchor, first));

            // Skip delimiter.  We know we will not go beyond the end of
            // the string because we checked before the loop that the
            // last character was not the delimiter.
            anchor = ++first;

            // First character.
            if (invalidCharacter(*first))
            {
                return {};
            }
        }
        else
        {
            // Next character
            if (invalidCharacter(*first))
            {
                return {};
            }
        }
    }

    // Record the last token.
    result.push_back(std::string(anchor, first));

    return result;
}

inline std::string SdfPath::JoinIdentifier(const TfTokenVector& names)
{
    // This implementation done by converting the tokens to std::string first in USD, we are trying to avoid that.
    auto tokenJoin = [](TfTokenVector::const_iterator begin, TfTokenVector::const_iterator end,
                        const char* separator) -> std::string {
        if (begin == end)
        {
            return {};
        }

        auto distance = std::distance(begin, end);
        if (distance == 1)
        {
            return begin->GetString();
        }

        std::string retVal;

        size_t sum = 0;
        auto i = begin;
        for (i = begin; i != end; ++i)
        {
            sum += i->size();
        }
        retVal.reserve(sum + strlen(separator) * (distance - 1));

        i = begin;
        retVal.append(i->GetString());
        while (++i != end)
        {
            retVal.append(separator);
            retVal.append(i->GetString());
        }

        return retVal;
    };

    // Remove empty tokens.
    if (std::any_of(names.begin(), names.end(), [](const auto& s) { return s.IsEmpty(); }))
    {
        // Create a new vector with just the non-empty names.
        TfTokenVector nonEmptyNames;
        nonEmptyNames.reserve(names.size());
        std::copy_if(
            names.begin(), names.end(), std::back_inserter(nonEmptyNames), [](const auto& s) { return !s.IsEmpty(); });
        return tokenJoin(nonEmptyNames.begin(), nonEmptyNames.end(), ":");
    }

    return tokenJoin(names.begin(), names.end(), ":");
}

inline std::pair<std::string, bool> SdfPath::StripPrefixNamespace(const std::string& name,
                                                                  const std::string& matchNamespace)
{
    constexpr char namespaceDelimiter = ':';

    if (matchNamespace.empty())
    {
        return std::make_pair(name, false);
    }

    if (TfStringStartsWith(name, matchNamespace))
    {

        size_t matchNamespaceLen = matchNamespace.size();

        // Now check to make sure the next character is the namespace delimiter
        if (matchNamespace[matchNamespaceLen - 1] == namespaceDelimiter)
        {

            // The matched namespace already contained the end delimiter,
            // nothing more to do.
            return std::make_pair(name.substr(matchNamespaceLen), true);
        }
        else
        {

            // The matched namespace needs an extra delimiter ':' so check for
            // it now.
            if (name[matchNamespaceLen] == namespaceDelimiter)
            {
                return std::make_pair(name.substr(matchNamespaceLen + 1), true);
            }
        }
    }

    return std::make_pair(name, false);
}

inline std::pair<std::string, bool> SdfPath::StripSuffixNamespace(const std::string& name, 
                                                                  const std::string& matchNamespace)
{
    constexpr char namespaceDelimiter = ':';

    if (matchNamespace.empty())
    {
        return std::make_pair(name, false);
    }

    if (TfStringEndsWith(name, matchNamespace))
    {

        const size_t matchNamespaceLen = matchNamespace.size();

        // Now check to make sure the first character is the namespace delimiter
        if (matchNamespace[0] == namespaceDelimiter)
        {

            // The matched namespace already contained the leading delimiter,
            // nothing more to do.
            return std::make_pair(name.substr(0, name.size() - matchNamespaceLen), true);
        }
        else
        {

            // The matched namespace needs an extra delimiter ':' so check for
            // it now.
            if (name[name.size() - matchNamespaceLen - 1] == namespaceDelimiter)
            {
                return std::make_pair(name.substr(0, name.size() - matchNamespaceLen - 1), true);
            }
        }
    }

    return std::make_pair(name, false);
}

// Operators

inline bool SdfPath::operator==(const SdfPath& rhs) const
{
    return m_path == rhs.m_path && m_property == rhs.m_property;
}

inline bool SdfPath::operator!=(const SdfPath& rhs) const
{
    return m_path != rhs.m_path || m_property != rhs.m_property;
}

inline bool SdfPath::operator<(const SdfPath& rhs) const
{
    omni::core::ObjectPtr<IRtPath107> path = omni::core::cast<IRtPath107>(
        omni::core::createType<IRtPath>()->create(omni::fabric::PathC(m_path), omni::fabric::TokenC(m_property)).get());

    return path->lessThanOperator(omni::fabric::PathC(rhs), omni::fabric::TokenC(rhs.m_property));
}

inline bool SdfPath::IsEmpty() const
{
    return m_path == omni::fabric::Path();
}

inline SdfPathVector SdfPath::GetPrefixes() const
{
    SdfPathVector result;
    GetPrefixes(&result);
    return result;
}

inline void SdfPath::GetPrefixes(SdfPathVector* prefixes) const
{
    omni::core::ObjectPtr<usdrt::IRtPath> thisPath =
        omni::core::createType<usdrt::IRtPath>()->create(omni::fabric::PathC(m_path), omni::fabric::TokenC(m_property));

    std::vector<omni::core::ObjectPtr<usdrt::IRtPath>> prefixList = thisPath->getPrefixes();

    prefixes->reserve(prefixList.size());
    for (const auto& prefixPtr : prefixList)
    {
        prefixes->push_back(SdfPath(prefixPtr));
    }
}

inline SdfPathAncestorsRange SdfPath::GetAncestorsRange() const
{
    return SdfPathAncestorsRange(*this);
}

inline SdfPathAncestorsRange::iterator& SdfPathAncestorsRange::iterator::operator++()
{
    omni::core::ObjectPtr<usdrt::IRtPath> thisPath = omni::core::createType<usdrt::IRtPath>()->create(
        omni::fabric::PathC(m_path.GetPrimPath()),
        m_path.IsPropertyPath() ? omni::fabric::TokenC(m_path.GetNameToken()) : omni::fabric::kUninitializedToken);

    omni::core::ObjectPtr<usdrt::IRtPath> incPath = thisPath->ancestorsRangeIteratorIncrement();
    m_path = SdfPath(incPath->getPrimPart(), incPath->getPropPart());

    return *this;
}

} // namespace usdrt

//! Hash function for SdfPath
//!
//! Hashes omni::fabric::PathC and omni::fabric::TokenC representations of
//! this path, and uses a method from boost hash combine to get the hash value.
//! @returns Return the hash value for this path.
namespace std
{
template <>
class hash<usdrt::SdfPath>
{
public:
    inline size_t operator()(const usdrt::SdfPath& key) const
    {
        std::hash<omni::fabric::PathC> pathHasher;
        size_t pathHash = pathHasher(omni::fabric::PathC(key.GetPrimPath()));

        std::hash<omni::fabric::TokenC> propHasher;
        size_t propHash;
        if (key.IsPropertyPath())
        {
            propHash = propHasher(omni::fabric::TokenC(key.GetNameToken()));
        }
        else
        {
            propHash = propHasher(omni::fabric::kUninitializedToken);
        }

        // from boost hash combine
        size_t seed = pathHash;
        seed ^= propHash + 0x9e3779b9 + (seed << 6) + (seed >> 2);
        return seed;
    }
};
} // namespace std

namespace usdrt
{

inline size_t SdfPath::GetHash() const
{
    return std::hash<usdrt::SdfPath>{}(*this);
}

} // namespace usdrt
