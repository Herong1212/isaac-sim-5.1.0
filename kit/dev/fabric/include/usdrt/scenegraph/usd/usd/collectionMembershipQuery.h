// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <usdrt/scenegraph/usd/sdf/path.h>
#include <usdrt/scenegraph/base/tf/token.h>
#include <omni/fabric/core/hash_combine.h>
#include <omni/fabric/stage/StageReaderWriter.h>
#include <omni/fabric/connectivity/Connectivity.h>
#include <carb/logging/Log.h>
#include <stack>

namespace usdrt
{


/// Represents a flattened view of a collection.  For more information
/// about collections, please see UsdCollectionAPI as a way to encode and
/// retrieve a collection from scene description.  A
/// UsdCollectionMembershipQuery object can be used to answer queries about
/// membership of paths in the collection efficiently.
class UsdCollectionMembershipQuery
{
public:
    /// Holds an unordered map describing membership of paths in this collection
    /// and the associated expansionRule for how the paths are to be expanded.
    /// Valid expansionRules are UsdTokens->explicitOnly,
    /// UsdTokens->expandPrims, and UsdTokens->expandPrimsAndProperties.  For
    /// more information on the expansion rules, please see the expansionRule
    /// attribute on UsdCollectionAPI.
    /// If a collection includes another collection, the included collection's
    /// PathExpansionRuleMap is merged into this one. If a path is excluded,
    /// its expansion rule is set to UsdTokens->exclude.
    using PathExpansionRuleMap = std::unordered_map<SdfPath, TfToken>;

    /// Default Constructor, creates an empty UsdCollectionMembershipQuery
    /// object
    UsdCollectionMembershipQuery() = default;

    /// Constructor that takes a path expansion rule map.  The map is scanned
    /// for 'excludes' when the UsdCollectionMembershipQuery object is
    /// constructed.
    UsdCollectionMembershipQuery(const PathExpansionRuleMap& pathExpansionRuleMap, const SdfPathSet& includedCollections);

    /// Constructor that takes a path expansion rule map as an rvalue reference
    UsdCollectionMembershipQuery(PathExpansionRuleMap&& pathExpansionRuleMap, SdfPathSet&& includedCollections);

    /// Returns whether the given path is included in the collection from
    /// which this UsdCollectionMembershipQuery object was computed. This is the
    /// API that clients should use for determining if a given object is a
    /// member of the collection. To enumerate all the members of a collection,
    /// use \ref UsdComputeIncludedObjectsFromCollection or
    /// \ref UsdComputeIncludedPathsFromCollection.
    ///
    /// If \p expansionRule is not nullptr, it is set to the expansion-
    /// rule value that caused the path to be included in or excluded from
    /// the collection. If \p path is not included in the collection,
    /// \p expansionRule is set to UsdTokens->exclude.
    ///
    /// It is useful to specify this parameter and use this overload of
    /// IsPathIncluded(), when you're interested in traversing a subtree
    /// and want to know whether the root of the subtree is included in a
    /// collection. For evaluating membership of descendants of the root,
    /// please use the other overload of IsPathIncluded(), that takes both
    /// a path and the parent expansionRule.
    ///
    /// The python version of this method only returns the boolean result.
    /// It does not return \p expansionRule.
    bool IsPathIncluded(const SdfPath &path, TfToken *expansionRule=nullptr) const;

    /// Returns true if the collection excludes one or more paths below an
    /// included path.
    bool HasExcludes() const
    {
        return _hasExcludes;
    }

    /// Equality operator
    bool operator==(UsdCollectionMembershipQuery const& rhs) const
    {
        return _hasExcludes == rhs._hasExcludes && _pathExpansionRuleMap == rhs._pathExpansionRuleMap &&
               _includedCollections == rhs._includedCollections;
    }

    /// Inequality operator
    bool operator!=(UsdCollectionMembershipQuery const& rhs) const
    {
        return !(*this == rhs);
    }

    /// Returns a raw map of the paths included or excluded in the
    /// collection along with the expansion rules for the included
    /// paths.
    const PathExpansionRuleMap& GetAsPathExpansionRuleMap() const;

    /// Returns a set of paths for all collections that were included in the
    /// collection from which this UsdCollectionMembershipQuery object was
    /// computed. This set is recursive, so collections that were included
    /// by other collections will be part of this set. The collection from
    /// which this UsdCollectionMembershipQuery object was computed is *not*
    /// part of this set.
    const SdfPathSet& GetIncludedCollections() const
    {
        return _includedCollections;
    }

    /// Hash functor
    struct Hash
    {
        size_t operator()(UsdCollectionMembershipQuery const& query) const;
    };

    /// Hash function
    size_t GetHash() const;

private:
    PathExpansionRuleMap _pathExpansionRuleMap;

    SdfPathSet _includedCollections;

    // A cached flag indicating whether _pathExpansionRuleMap contains
    // any exclude rules.
    bool _hasExcludes = false;
};

inline UsdCollectionMembershipQuery::UsdCollectionMembershipQuery(const PathExpansionRuleMap& pathExpansionRuleMap,
                                                           const SdfPathSet& includedCollections)
    : _pathExpansionRuleMap(pathExpansionRuleMap), _includedCollections(includedCollections)
{
    for (const auto& pathAndExpansionRule : _pathExpansionRuleMap)
    {
        if (pathAndExpansionRule.second == UsdTokens->exclude)
        {
            _hasExcludes = true;
            break;
        }
    }
}

inline UsdCollectionMembershipQuery::UsdCollectionMembershipQuery(PathExpansionRuleMap&& pathExpansionRuleMap,
                                                           SdfPathSet&& includedCollections)
    : _pathExpansionRuleMap(std::move(pathExpansionRuleMap)), _includedCollections(std::move(includedCollections))
{
    for (const auto& pathAndExpansionRule : _pathExpansionRuleMap)
    {
        if (pathAndExpansionRule.second == UsdTokens->exclude)
        {
            _hasExcludes = true;
            break;
        }
    }
}

inline bool UsdCollectionMembershipQuery::IsPathIncluded(const SdfPath &path, TfToken *expansionRule) const {
    // Passing one causes a infinite loop because of how `GetParentPath` works.
    if (!path.IsAbsolutePath())
    {
        return false;
    }

    // Only prims and properties can belong to a collection.
    if (!path.IsPrimPath() && !path.IsPropertyPath())
        return false;

    // Have separate code paths for prim and property paths as we'd like this
    // method to be as fast as possible.
    if (path.IsPrimPath())
    {
        for (SdfPath p = path; p != SdfPath::EmptyPath(); p = p.GetParentPath())
        {
            const auto i = _pathExpansionRuleMap.find(p);
            if (i != _pathExpansionRuleMap.end())
            {
                if (i->second == UsdTokens->exclude)
                {
                    if (expansionRule)
                    {
                        *expansionRule = UsdTokens->exclude;
                    }
                    return false;
                }
                else if (i->second != UsdTokens->explicitOnly || p == path)
                {
                    if (expansionRule)
                    {
                        *expansionRule = i->second;
                    }
                    return true;
                }
            }
        }
    }
    else
    {
        for (SdfPath p = path; p != SdfPath::EmptyPath(); p = p.GetParentPath())
        {
            const auto i = _pathExpansionRuleMap.find(p);
            if (i != _pathExpansionRuleMap.end())
            {
                if (i->second == UsdTokens->exclude)
                {
                    if (expansionRule)
                    {
                        *expansionRule = UsdTokens->exclude;
                    }
                    return false;
                }
                else if ((i->second == UsdTokens->expandPrimsAndProperties) ||
                         (i->second == UsdTokens->explicitOnly && p == path))
                {
                    if (expansionRule)
                    {
                        *expansionRule = i->second;
                    }
                    return true;
                }
            }
        }
    }

    // Any path that's not explicitly mentioned is not included in the
    // collection.
    return false;
}

inline const UsdCollectionMembershipQuery::PathExpansionRuleMap& UsdCollectionMembershipQuery::GetAsPathExpansionRuleMap() const
{
    return _pathExpansionRuleMap;
}

inline size_t UsdCollectionMembershipQuery::GetHash() const
{
    return Hash()(*this);
}

inline size_t UsdCollectionMembershipQuery::Hash::operator()(UsdCollectionMembershipQuery const& q) const
{
    // Hashing unordered maps is costly because two maps holding the
    // same (key,value) pairs may store them in a different layout,
    // due to population history.  We must use a history-independent
    // order to compute a consistent hash value.
    //
    // If the runtime cost becomes problematic, we should consider
    // computing the hash once and storing it in the MembershipQuery,
    // as a finalization step in _ComputeMembershipQueryImpl().
    typedef std::pair<SdfPath, TfToken> _Entry;
    std::vector<_Entry> entries(q._pathExpansionRuleMap.begin(), q._pathExpansionRuleMap.end());
    std::sort(entries.begin(), entries.end());
    size_t h = 0;
    for (_Entry const& entry : entries)
    {
        h = hash_combine(h, entry.first);
        h = hash_combine(h, entry.second);
    }
    // Don't hash _hasExcludes because it is derived from
    // the contents of _pathExpansionRuleMap.
    return h;
}

inline void _ComputeIncludedImpl(const UsdCollectionMembershipQuery& query,
                                 omni::fabric::StageReaderWriterId stageId,
                                 SdfPathSet& includedPaths)
{
    omni::fabric::StageReaderWriter stage(stageId);

    const UsdCollectionMembershipQuery::PathExpansionRuleMap& pathExpRuleMap = query.GetAsPathExpansionRuleMap();
    const bool hasExcludes = query.HasExcludes();

    // A path is excluded if the path itself or any of its ancestors are
    // excluded.
    auto IsExcluded = [hasExcludes, pathExpRuleMap](const SdfPath& path) {
        // Return early if we know that there are no excludes.
        if (!hasExcludes)
        {
            return false;
        }
        for (SdfPath p = path; p != SdfPath::EmptyPath(); p = p.GetParentPath())
        {
            // Include if the nearest ancestor path with an opinion in
            // path->expansionRuleMap isn't excluded.
            auto it = pathExpRuleMap.find(p);
            if (it != pathExpRuleMap.end())
            {
                return it->second == UsdTokens->exclude;
            }
        }
        return false;
    };

    // Returns true if a property is excluded in the PathExpansionRuleMap.
    auto IsPropertyExplicitlyExcluded = [hasExcludes, pathExpRuleMap](const SdfPath& propPath) {
        if (!hasExcludes)
        {
            return false;
        }
        auto it = pathExpRuleMap.find(propPath);
        if (it != pathExpRuleMap.end())
        {
            return it->second == UsdTokens->exclude;
        }
        return false;
    };

    // Iterate through all the entries in the PathExpansionRuleMap.
    for (const auto& pathAndExpansionRule : pathExpRuleMap)
    {
        const TfToken& expansionRule = pathAndExpansionRule.second;

        // Skip excluded paths.
        if (expansionRule == UsdTokens->exclude)
        {
            continue;
        }

        const SdfPath& path = pathAndExpansionRule.first;
        const omni::fabric::PathC pathC(path);

        if (expansionRule == UsdTokens->explicitOnly)
        {
            if (path.IsPrimPath())
            {
                if (stage.primExists(pathC))
                {
                    includedPaths.insert(path);
                }
            }
            else if (path.IsPropertyPath())
            {
                if (stage.attributeExists(omni::fabric::PathC(path.GetPrimPath()), omni::fabric::TokenC(path.GetNameToken()))) {
                    includedPaths.insert(path);
                }
                else
                {
                    CARB_LOG_ERROR("No property found mathcing: %s", path.GetText());
                }
            }
        }
        else if (expansionRule == UsdTokens->expandPrims || expansionRule == UsdTokens->expandPrimsAndProperties)
        {
            if (path.IsPropertyPath())
            {
                if (stage.attributeExists(
                        omni::fabric::PathC(path.GetPrimPath()), omni::fabric::TokenC(path.GetNameToken())))
                {
                    includedPaths.insert(path);
                }
                else
                {
                    CARB_LOG_ERROR("No property found mathcing: %s", path.GetText());
                }
            }
            else if (stage.primExists(pathC))
            {
                omni::fabric::USDHierarchy usdHier(stage.getFabricId());

                std::stack<omni::fabric::Path> pathStack;
                pathStack.push(pathC);

                while (!pathStack.empty())
                {
                    const auto current = pathStack.top();
                    pathStack.pop();

                    // Skip the descendant prim and its subtree
                    // if it's excluded.
                    // If an object below the excluded object is included,
                    // it will have a separate entry in the
                    // path<->expansionRule map.
                    if (IsExcluded(current))
                    {
                        continue;
                    }

                    includedPaths.insert(current);

                    if (expansionRule == UsdTokens->expandPrimsAndProperties)
                    {
                        const auto& attrNamesAndTypes = stage.getAttributeNamesAndTypes(current);
                        for (const auto& propertyName : attrNamesAndTypes.first)
                        {
                            SdfPath propertyPath = SdfPath(current).AppendProperty(propertyName);
                            if (!IsPropertyExplicitlyExcluded(propertyPath))
                            {
                                includedPaths.insert(propertyPath);
                            }
                        }
                    }

                    const omni::fabric::Path firstChild(usdHier.getFirstChild(current));
                    omni::fabric::Path child = firstChild;
                    if (firstChild != omni::fabric::kUninitializedPath)
                    {
                        do
                        {
                            pathStack.push(child);
                            child = usdHier.getNextSibling(child);

                        } while (child != firstChild);
                    }
                }
            }
        }
    }
}

inline SdfPathSet UsdComputeIncludedPathsFromCollection(const UsdCollectionMembershipQuery& query,
                                                        omni::fabric::StageReaderWriterId stageId)
{
    SdfPathSet result;
    _ComputeIncludedImpl(query, stageId, result);
    return result;
}

inline SdfPathSet UsdComputeIncludedPathsFromCollection(const UsdCollectionMembershipQuery& query,
                                                        const UsdStageRefPtr& stage)
{
    return UsdComputeIncludedPathsFromCollection(query, stage->GetStageReaderWriterId());
}

} // namespace usdrt
