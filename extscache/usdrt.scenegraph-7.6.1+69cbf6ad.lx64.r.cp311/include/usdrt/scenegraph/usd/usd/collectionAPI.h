// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
// TODO USD COPYRIGHT AS WELL?
#pragma once

/// @file usd/collectionAPI.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/apiSchemaBase.h"
#include "usdrt/scenegraph/usd/usd/tokens.h"

// clang-format off
/* Extra Includes
// USDRT NOTE: Use custom includes below instead to allow for
// implementation differences in the custom code. This section comes
// from the pxr schema.usda files which we may not have in usdrt.
//#include "usdrt/scenegraph/usd/usd/collectionMembershipQuery.h"
#include "usdrt/scenegraph/usd/usd/primFlags.h"
#include "usdrt/scenegraph/usd/usd/tokens.h"*/
// clang-format on

// ===================================================================== //
// Feel free to add custom includes between BEGIN and END CUSTOM INCLUDES
// below this line. It will be preserved by the code generator.
// We are using this instead of the `extraIncludes` in the pxr schema.usda
// files to allow for implementation differences in the custom code.
// ===================================================================== //
// --(BEGIN CUSTOM INCLUDES)--
// --(END CUSTOM INCLUDES)--

#include <omni/core/IObject.h>
#include <usdrt/scenegraph/base/tf/token.h>
#include <usdrt/scenegraph/base/vt/array.h>
#include <usdrt/scenegraph/interface/IRtAttribute.h>
#include <usdrt/scenegraph/interface/IRtPrim.h>
#include <usdrt/scenegraph/interface/IRtPrimRange.h>
#include <usdrt/scenegraph/interface/IRtRelationship.h>
#include <usdrt/scenegraph/interface/IRtCollection.h>
#include <usdrt/scenegraph/interface/IRtStage.h>
#include <usdrt/scenegraph/usd/sdf/path.h>
#include <usdrt/scenegraph/usd/sdf/types.h>
#include <usdrt/scenegraph/usd/sdf/valueTypeName.h>
#include <usdrt/scenegraph/usd/usd/attribute.h>
#include <usdrt/scenegraph/usd/usd/common.h>
#include <usdrt/scenegraph/usd/usd/prim.h>
#include <usdrt/scenegraph/usd/usd/timeCode.h>
#include <usdrt/scenegraph/usd/usd/collectionMembershipQuery.h>
#include <carb/logging/Log.h>
#include <omni/fabric/stage/StageReaderWriter.h>

namespace usdrt
{

// -------------------------------------------------------------------------- //
// COLLECTIONAPI                                                               //
// -------------------------------------------------------------------------- //

/// @class UsdCollectionAPI
///
/// This is a general purpose API schema, used to describe a
/// collection of heterogeneous objects within the scene. "Objects" here may be
/// prims or properties belonging to prims or other collections. It's an add-on
/// schema that can be applied many times to a prim with different collection
/// names.
///
/// A collection allows an enumeration of a set of paths to include and a
/// set of paths to exclude.  Whether the descendants of an included
/// path are members of a collection are decided by its expansion rule
/// (see below).  If the collection excludes paths that are not descendents
/// of included paths, the collection implicitly includes the root path
/// &lt;/&gt;.  If such a collection also includes paths that are not
/// descendants of the excluded paths, it is considered invalid, since
/// the intention is ambiguous.
///
/// All the properties authored by the schema are namespaced under
/// "collection:". The given name of the collection provides additional
/// namespacing for the various per-collection properties, which include the
/// following:
///
/// <ul><li><b>uniform token collection:<i>collectionName</i>:expansionRule</b> -
/// specified how the paths that are included in the collection must be expanded
/// to determine its members. Possible values include:
/// <ul>
/// <li><b>explicitOnly</b> - only paths in the includes rel targets and not
/// in the excludes rel targets belong to the collection.
/// </li>
/// <li><b>expandPrims</b> - all the prims at or below the includes rel-
/// targets (and not under the excludes rel-targets) belong to the
/// collection.  Any property paths included in the collection would, of
/// course, also be honored. This is the default behavior as it satisfies
/// most use cases.
/// </li>
/// <li><b>expandPrimsAndProperties</b> - like expandPrims, but also
/// includes all properties on all matched prims.  We're still not quite
/// sure what the use cases are for this, but you can use it to capture a
/// whole lot of UsdObjects very concisely.
/// </li>
/// </ul>
/// </li>
/// <li><b>bool collection:<i>collectionName</i>:includeRoot</b> - boolean
/// attribute indicating whether the pseudo-root path &lt;/&gt; should
/// be counted as one of the included target paths.  The fallback is false.
/// This separate attribute is required because relationships cannot
/// directly target the root.
/// <li><b>rel collection:<i>collectionName</i>:includes</b> - specifies a list
/// of targets that are included in the collection. This can target prims or
/// properties directly. A collection can insert the rules of another
/// collection by making its <i>includes</i> relationship target the
/// <b>collection:{collectionName}</b> property on the owning prim of the
/// collection to be included.
/// Such a property may not (and typically does not) exist on the UsdStage, but
/// it is the path that is used to refer to the collection.
/// It is important to note that including another collection does not
/// guarantee the contents of that collection will be in the final collection;
/// instead, the rules are merged.  This means, for example, an exclude
/// entry may exclude a portion of the included collection.
/// When a collection includes one or more collections, the order in which
/// targets are added to the includes relationship may become significant, if
/// there are conflicting opinions about the same path. Targets that are added
/// later are considered to be stronger than earlier targets for the same path.
/// </li>
/// <li><b>rel collection:<i>collectionName</i>:excludes</b> - specifies a list
/// of targets that are excluded below the <b>included</b> paths in this
/// collection. This can target prims or properties directly, but <b>cannot
/// target another collection</b>. This is to keep the membership determining
/// logic simple, efficient and easier to reason about. Finally, it is invalid
/// for a collection to exclude paths that are not included in it. The presence
/// of such "orphaned" excluded paths will not affect the set of paths included
/// in the collection, but may affect the performance of querying membership of
/// a path in the collection (see UsdCollectionAPI::MembershipQuery::IsPathIncluded)
/// or of enumerating the objects belonging to the collection (see
/// UsdCollectionAPI::GetIncludedObjects).
/// </li></ul>
///
/// <b>Implicit inclusion</b>
///
/// In some scenarios it is useful to express a collection that includes
/// everything except certain paths.  To support this, a collection
/// that has an exclude that is not a descendent of any include
/// will include the root path &lt;/&gt;.
///
/// <b>Creating collections in C++</b>
///
/// \snippet examples.cpp ApplyCollections
///
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdTokens.
/// So to set an attribute to the value "rightHanded", use UsdTokens->rightHanded
/// as the value.

class UsdCollectionAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::MultipleApplyAPI;

    /// Construct a UsdCollectionAPI on UsdPrim @p prim with
    /// name @p name . Equivalent to
    /// UsdCollectionAPI::Get(
    ///    prim.GetStage(),
    ///    prim.GetPath().AppendProperty(
    ///        "collection:name"));
    ///
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdCollectionAPI(const UsdPrim& prim = UsdPrim(), const TfToken& name = TfToken())
        : UsdAPISchemaBase(prim, /*instanceName*/ name)
    {
    }

    /// Construct a UsdCollectionAPI on the prim held by @p schemaObj with
    /// name @p name .  Should be preferred over
    /// UsdCollectionAPI(schemaObj.GetPrim(), name), as it preserves
    /// SchemaBase state.
    explicit UsdCollectionAPI(const UsdSchemaBase& schemaObj, const TfToken& name)
        : UsdAPISchemaBase(schemaObj, /*instanceName*/ name)
    {
    }

    /// Destructor.
    virtual ~UsdCollectionAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();

    /// Returns the name of this multiple-apply schema instance
    TfToken GetName() const
    {
        return _GetInstanceName();
    }

    /// Applies this <b>multiple-apply</b> API schema to the given @p prim
    /// along with the given instance name, @p name.
    ///
    /// This information is stored by adding "CollectionAPI:<i>name</i>"
    /// to the token-valued, listOp metadata \em apiSchemas on the prim.
    /// For example, if @p name is 'instance1', the token
    /// 'CollectionAPI:instance1' is added to 'apiSchemas'.
    ///
    /// @return A valid UsdCollectionAPI object is returned upon success.
    /// An invalid (or empty) UsdCollectionAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for
    /// conditions resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static UsdCollectionAPI Apply(const UsdPrim& prim, const TfToken& name)
    {
        if (prim.ApplyAPI<UsdCollectionAPI>(name))
        {
            return UsdCollectionAPI(prim, name);
        }
        return UsdCollectionAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // EXPANSIONRULE
    // --------------------------------------------------------------------- //
    /// Specifies how the paths that are included in
    /// the collection must be expanded to determine its members.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token expansionRule = "expandPrims"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref UsdTokens "Allowed Values" | explicitOnly, expandPrims, expandPrimsAndProperties |

    UsdAttribute GetExpansionRuleAttr() const;

    /// See GetExpansionRuleAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateExpansionRuleAttr() const;

public:
    // --------------------------------------------------------------------- //
    // INCLUDEROOT
    // --------------------------------------------------------------------- //
    /// Boolean attribute indicating whether the pseudo-root
    /// path &lt;/&gt; should be counted as one of the included target
    /// paths.  The fallback is false.  This separate attribute is
    /// required because relationships cannot directly target the root.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform bool includeRoot` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetIncludeRootAttr() const;

    /// See GetIncludeRootAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateIncludeRootAttr() const;

public:
    // --------------------------------------------------------------------- //
    // INCLUDES
    // --------------------------------------------------------------------- //
    /// Specifies a list of targets that are included in the collection.
    /// This can target prims or properties directly. A collection can insert
    /// the rules of another collection by making its <i>includes</i>
    /// relationship target the <b>collection:{collectionName}</b> property on
    /// the owning prim of the collection to be included
    ///
    UsdRelationship GetIncludesRel() const;

    /// See GetIncludesRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateIncludesRel() const;

public:
    // --------------------------------------------------------------------- //
    // EXCLUDES
    // --------------------------------------------------------------------- //
    /// Specifies a list of targets that are excluded below
    /// the included paths in this collection. This can target prims or
    /// properties directly, but cannot target another collection. This is to
    /// keep the membership determining logic simple, efficient and easier to
    /// reason about. Finally, it is invalid for a collection to exclude
    /// paths that are not included in it. The presence of such "orphaned"
    /// excluded paths will not affect the set of paths included in the
    /// collection, but may affect the performance of querying membership of
    /// a path in the collection (see
    /// UsdCollectionAPI::MembershipQuery::IsPathIncluded)
    /// or of enumerating the objects belonging to the collection (see
    /// UsdCollectionAPI::GetIncludedObjects).
    ///
    UsdRelationship GetExcludesRel() const;

    /// See GetExcludesRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateExcludesRel() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--

    /// Convenient alias for UsdCollectionMembershipQuery object
    using MembershipQuery = UsdCollectionMembershipQuery;

    /// Returns the canonical path that represents this collection. 
    /// This points to a property named "collection:{collectionName}" on the 
    /// prim defining the collection (which won't really exist as a property 
    /// on the UsdStage, but will be used to refer to the collection).
    /// This is the path to be used to "include" this collection in another
    /// collection.
    SdfPath GetCollectionPath() const;

    /// Computes and returns a UsdCollectionMembershipQuery object which can
    /// be used to query inclusion or exclusion of paths in the collection.
    UsdCollectionMembershipQuery ComputeMembershipQuery() const;

    /// Populates the UsdCollectionMembershipQuery object with data from this
    /// collection, so it can be used to query inclusion or exclusion of paths.
    void ComputeMembershipQuery(UsdCollectionMembershipQuery* query) const;

    /// Checks if the given path \p path is of an API schema of type
    /// CollectionAPI. If so, it stores the instance name of
    /// the schema in \p name and returns true. Otherwise, it returns false.
    static bool IsCollectionAPIPath(const SdfPath& path, TfToken* name);

    /// Returns the name of the property, given the name of collection and
    /// base name of the attribute. Eg, if collection name is 'lightLink' and 
    /// baseName is 'includes', this returns 'collection:lightLink:includes'.
    static TfToken GetCollectionPropertyName(const TfToken& name, bool prefixedName = false,
                                             const TfToken& baseName = TfToken());

    /// Computes and returns a UsdCollectionMembershipQuery object which can
    /// be used to query inclusion or exclusion of paths in the collection.
    static UsdCollectionMembershipQuery ComputeMembershipQuery(omni::fabric::StageReaderWriterId stageId,
                                                        const SdfPath& collectionPath);

    /// Populates the UsdCollectionMembershipQuery object with data from this
    /// collection, so it can be used to query inclusion or exclusion of paths.
    static void ComputeMembershipQuery(omni::fabric::StageReaderWriterId stageId,
                                       const SdfPath& collectionPath, UsdCollectionMembershipQuery* query);

    /// Returns all the paths in the collection represented by the UsdCollectionMembershipQuery object.
    static SdfPathSet ComputeIncludedPaths(
        const UsdCollectionMembershipQuery &query,
        omni::fabric::StageReaderWriterId stageId);

    /// Convenience API for adding or removing prims and properties to (or 
    /// from) a collection..
    ///
    /// Includes or adds the given path, \p pathToInclude in the collection. 
    /// 
    /// This does nothing if the path is already included in the collection. 
    /// 
    /// This does not modify the expansion-rule of the collection. Hence, if the 
    /// expansionRule is <i>expandPrims</i> or <i>expandPrimsAndProperties</i>, 
    /// then the descendants of \p pathToInclude will be also included in the 
    /// collection unless explicitly excluded.
    bool IncludePath(const SdfPath &pathToInclude) const;

    /// Excludes or removes the given path, \p pathToExclude from the collection.
    /// 
    /// If the collection is empty, the collection becomes one that
    /// includes all paths except the givne path.  Otherwise, this does
    /// nothing if the path is not included in the collection. 
    ///
    /// This does not modify the expansion-rule of the collection. Hence, if the 
    /// expansionRule is <i>expandPrims</i> or <i>expandPrimsAndProperties</i>, 
    /// then the descendants of \p pathToExclude will also be excluded from the 
    /// collection, unless explicitly included.
    bool ExcludePath(const SdfPath &pathToExclude) const; 

private:

    // Helper method for computing the UsdCollectionMembershipQuery object for
    // a collection.
    // This makes recursive calls if the collection includes other collections.
    // \p chainedCollectionPaths is used to pass in the set of all seen and
    // included collections in the dependency chain and is used to detect
    // circular dependencies.
    // If \p foundCircularDependency is not nullptr, it is set to true if a
    // circular dependency is detected amongst the included collections.
    // If it is nullptr, a warning is issued when a circular dependency is
    // detected.
    static void _ComputeMembershipQueryImpl(omni::fabric::StageReaderWriterId stageId,
                                            const SdfPath& collectionPath,
                                            UsdCollectionMembershipQuery* query,
                                            const SdfPathSet& chainedCollectionPaths,
                                            bool* foundCircularDependency = nullptr);
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdCollectionAPI::_GetStaticTfType()
{
    const static TfToken token("UsdCollectionAPI");
    return token;
}

/* virtual */
inline const TfToken UsdCollectionAPI::_GetTfTypeToken() const
{
    const static TfToken token("UsdCollectionAPI");
    return token;
}


/// @private
/// Returns the property name prefixed with the correct namespace prefix, which
/// is composed of the the API's propertyNamespacePrefix metadata and the
/// instance name of the API.
inline TfToken _GetNamespacedPropertyNameCollectionAPI(const TfToken instanceName, const TfToken propName)
{
    std::vector<TfToken> identifiers = { TfToken("collection"), instanceName, propName };
    // join (TODO this was SdfPath::JoinIdentifier(identifiers))
    std::string namespaceDelimeter = ":";
    std::string namespacedName = "";
    for (auto& token : identifiers)
    {
        namespacedName += token.GetString();
        if (!(token == *(identifiers.end() - 1)))
        {
            namespacedName += namespaceDelimeter;
        }
    }

    return TfToken(namespacedName);
}

inline UsdAttribute UsdCollectionAPI::GetExpansionRuleAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNameCollectionAPI(GetName(), UsdTokens->expansionRule));
}

inline UsdAttribute UsdCollectionAPI::CreateExpansionRuleAttr() const
{
    return GetPrim().CreateAttribute(_GetNamespacedPropertyNameCollectionAPI(GetName(), UsdTokens->expansionRule),
                                     SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdCollectionAPI::GetIncludeRootAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNameCollectionAPI(GetName(), UsdTokens->includeRoot));
}

inline UsdAttribute UsdCollectionAPI::CreateIncludeRootAttr() const
{
    return GetPrim().CreateAttribute(_GetNamespacedPropertyNameCollectionAPI(GetName(), UsdTokens->includeRoot),
                                     SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}


inline UsdRelationship UsdCollectionAPI::GetIncludesRel() const
{
    return GetPrim().GetRelationship(_GetNamespacedPropertyNameCollectionAPI(GetName(), UsdTokens->includes));
}

inline UsdRelationship UsdCollectionAPI::CreateIncludesRel() const
{
    return GetPrim().CreateRelationship(_GetNamespacedPropertyNameCollectionAPI(GetName(), UsdTokens->includes),
                                        /* custom = */ false);
}
inline UsdRelationship UsdCollectionAPI::GetExcludesRel() const
{
    return GetPrim().GetRelationship(_GetNamespacedPropertyNameCollectionAPI(GetName(), UsdTokens->excludes));
}

inline UsdRelationship UsdCollectionAPI::CreateExcludesRel() const
{
    return GetPrim().CreateRelationship(_GetNamespacedPropertyNameCollectionAPI(GetName(), UsdTokens->excludes),
                                        /* custom = */ false);
}
} // namespace usdrt
// ===================================================================== //
// Feel free to add custom code below this line. It will be preserved by
// the code generator.
//
// Just remember to wrap code in the appropriate delimiters:
// 'namespace usdrt {', '}'.
// ===================================================================== //
// --(BEGIN CUSTOM CODE)--

namespace usdrt {

inline SdfPath UsdCollectionAPI::GetCollectionPath() const {
    return GetPath().AppendProperty(UsdCollectionAPI::GetCollectionPropertyName(GetName()));
}

inline UsdCollectionMembershipQuery UsdCollectionAPI::ComputeMembershipQuery() const
{
    UsdCollectionMembershipQuery query;
    ComputeMembershipQuery(&query);
    return query;
}

inline void UsdCollectionAPI::ComputeMembershipQuery(UsdCollectionMembershipQuery* query) const
{
    return UsdCollectionAPI::ComputeMembershipQuery(GetPrim().GetStage()->GetStageReaderWriterId(), GetCollectionPath(), query);
}

inline bool UsdCollectionAPI::IsCollectionAPIPath(const SdfPath& path, TfToken* name)
{
    auto iCollection = omni::core::createType<usdrt::IRtCollection>();
    if (!iCollection)
    {
        return false;
    }

    if (!path.IsPropertyPath())
    {
        return false;
    }

    const SdfPath primPath = path.GetPrimPath();
    const TfToken property = path.GetNameToken();

    omni::fabric::TokenC nameC;
    const auto result =
        iCollection->isCollectionAPIPath(omni::fabric::PathC(path), omni::fabric::TokenC(property), &nameC);
    *name = omni::fabric::Token(nameC);

    return result;
}

inline TfToken UsdCollectionAPI::GetCollectionPropertyName(const TfToken& name, bool prefixedName, const TfToken& baseName)
{
    return TfToken((prefixedName ? "" : UsdTokens->collection.GetString() + ":") + name.GetString() +
                   (baseName.IsEmpty() ? "" : (":" + baseName.GetString())));
}

inline UsdCollectionMembershipQuery UsdCollectionAPI::ComputeMembershipQuery(
    omni::fabric::StageReaderWriterId stageId,
    const SdfPath& collectionPath) {
    UsdCollectionMembershipQuery query;
    ComputeMembershipQuery(stageId, collectionPath, &query);
    return query;
}

inline void UsdCollectionAPI::ComputeMembershipQuery(omni::fabric::StageReaderWriterId stageId,
                                                     const SdfPath& collectionPath,
                                                     UsdCollectionMembershipQuery* query) {
    if (!query)
    {
        CARB_LOG_ERROR("Invalid query pointer.");
        return;
    }

    SdfPathSet chainedCollectionPaths{ collectionPath };
    _ComputeMembershipQueryImpl(stageId, collectionPath, query, chainedCollectionPaths);
}

inline void UsdCollectionAPI::_ComputeMembershipQueryImpl(
                                 omni::fabric::StageReaderWriterId stageId,
                                 const SdfPath& collectionPath,
                                 UsdCollectionMembershipQuery* query,
                                 const SdfPathSet& chainedCollectionPaths,
                                 bool* foundCircularDependency) {

    if (!query)
    {
        return;
    }

    const omni::fabric::Path primPath(collectionPath.GetPrimPath());

    using PathExpansionRuleMap = UsdCollectionMembershipQuery::PathExpansionRuleMap;

    // Get the map from the query
    PathExpansionRuleMap map = query->GetAsPathExpansionRuleMap();
    SdfPathSet collections = query->GetIncludedCollections();

    omni::fabric::StageReaderWriter stage(stageId);

    // Get this collection's expansionRule.
    TfToken expRule = UsdTokens->expandPrims;
    const auto& expRuleAttrName =
        UsdCollectionAPI::GetCollectionPropertyName(collectionPath.GetNameToken(), true, UsdTokens->expansionRule);
    auto expRuleF = stage.getAttributeRd<omni::fabric::TokenC>(primPath, omni::fabric::TokenC(expRuleAttrName));
    if (expRuleF)
    {
        expRule = omni::fabric::Token(*expRuleF);
    }

    // Get this collection's includes.
    const auto includesAttrName =
        UsdCollectionAPI::GetCollectionPropertyName(collectionPath.GetNameToken(), true, UsdTokens->includes);
    const auto includesF =
        stage.getArrayAttributeRd<omni::fabric::PathC>(primPath, omni::fabric::TokenC(includesAttrName));
    SdfPathVector includes(includesF.begin(), includesF.end());

    // Get this collection's excludes.
    const auto excludesAttrName =
        UsdCollectionAPI::GetCollectionPropertyName(collectionPath.GetNameToken(), true, UsdTokens->excludes);
    const auto excludesF =
        stage.getArrayAttributeRd<omni::fabric::PathC>(primPath, omni::fabric::TokenC(excludesAttrName));
    SdfPathVector excludes(excludesF.begin(), excludesF.end());

    // Consult includeRoot and include </> if requested.
    // (The separate attribute is necessary since </> cannot be a
    // target path in a relationship.)
    const auto includeRootAttrName =
        UsdCollectionAPI::GetCollectionPropertyName(collectionPath.GetNameToken(), true, UsdTokens->includeRoot);
    const auto includeRootF = stage.getAttributeRd<bool>(primPath, omni::fabric::TokenC(includeRootAttrName));
    if (includeRootF && *includeRootF)
    {
        includes.push_back(SdfPath::AbsoluteRootPath());
    }

    for (const SdfPath& includedPath : includes)
    {
        TfToken collectionName;
        // Check if the included path is a collection. If it is, then
        // handle it specially.
        if (IsCollectionAPIPath(includedPath, &collectionName))
        {
            if (chainedCollectionPaths.count(includedPath) > 0)
            {
                if (foundCircularDependency)
                {
                    *foundCircularDependency = true;
                }
                else
                {
                    // Issue a warning message if the clients of this method
                    // don't care about knowing if there's a circular
                    // dependency.
                    std::string includedCollectionsStr;
                    for (const SdfPath& collPath : chainedCollectionPaths)
                    {
                        includedCollectionsStr.append(collPath.GetString());
                        includedCollectionsStr.append(", ");
                    }
                    
                    CARB_LOG_WARN(
                        "Found circular dependency involving the following "
                        "collections: [%s]",
                        includedCollectionsStr.c_str());
                }
                // Continuing here avoids infinite recursion.
                continue;
            }

            SdfPath includedPrimPath = includedPath.GetPrimPath();

            // The included collection must belong to a valid prim.
            // XXX: Should we check validity? We should skip circular
            // dependency check if we do validate.
            if (!stage.primExists(omni::fabric::PathC(includedPrimPath)))
            {
                CARB_LOG_WARN("Could not get prim at path <%s>, therefore cannot "
                              "include its collection '%s' in collection '%s'.",
                    includedPrimPath.GetText(), collectionName.GetText(), collectionPath.GetName().c_str());
                continue;
            }

            // Recursively compute the included collection's membership map with
            // an updated set of seen/included collection paths.
            //
            // Create a copy so we can add this collection to the list
            // before calling ComputeMembershipQuery.
            SdfPathSet seenCollectionPaths = chainedCollectionPaths;
            seenCollectionPaths.insert(includedPath);
            UsdCollectionMembershipQuery includedQuery;
            _ComputeMembershipQueryImpl(
                stageId, includedPrimPath, &includedQuery, seenCollectionPaths, foundCircularDependency);

            const PathExpansionRuleMap& includedMap = includedQuery.GetAsPathExpansionRuleMap();

            // Merge path expansion rule maps
            // We can't just do an insert here as we need to overwrite existing
            // entries with new values of expansion rule from other map
            for (const auto& pathAndExpansionRule : includedMap)
            {
                map[pathAndExpansionRule.first] = pathAndExpansionRule.second;
            }

            // Merge included collections
            collections.insert(includedPath);

            const SdfPathSet& includedCollections = includedQuery.GetIncludedCollections();
            collections.insert(includedCollections.begin(), includedCollections.end());
        }
        else
        {
            // Append included path
            map[includedPath] = expRule;
        }
    }

    // Process the excludes after the includes.
    for (const auto& p : excludes)
    {
        // Append excluded path
        map[p] = UsdTokens->exclude;
    }

    *query = UsdCollectionMembershipQuery(std::move(map), std::move(collections));
}

inline SdfPathSet UsdCollectionAPI::ComputeIncludedPaths(
        const UsdCollectionMembershipQuery& query,
        omni::fabric::StageReaderWriterId stageId) {
    return UsdComputeIncludedPathsFromCollection(query, stageId);
}

inline bool UsdCollectionAPI::IncludePath(const SdfPath& pathToInclude) const {
    // If the prim is already included in the collection, do nothing.
    UsdCollectionMembershipQuery query = ComputeMembershipQuery();
    if (query.IsPathIncluded(pathToInclude))
    {
        return true;
    }

    if (pathToInclude == SdfPath::AbsoluteRootPath())
    {
        auto includeRootAttr = CreateIncludeRootAttr();
        includeRootAttr.Set(true);
        return true;
    }

    // Check if the prim is directly excluded from the collection.
    SdfPathVector excludes;
    if (UsdRelationship excludesRel = GetExcludesRel())
    {
        excludesRel.GetTargets(&excludes);

        if (std::find(excludes.begin(), excludes.end(), pathToInclude) != excludes.end())
        {
            excludesRel.RemoveTarget(pathToInclude);
            // Update the query object we have by updating the map and
            // reconstructing the query
            UsdCollectionMembershipQuery::PathExpansionRuleMap map = query.GetAsPathExpansionRuleMap();
            auto it = map.find(pathToInclude);
            if (it != map.end())
            {
                map.erase(it);
                query = UsdCollectionMembershipQuery(std::move(map), query.GetIncludedCollections());
            }
        }
    }

    // Now that we've removed the explicit excludes if there was one,
    // we can add the prim if it's not already included in the collection.
    if (!query.IsPathIncluded(pathToInclude))
    {
        return CreateIncludesRel().AddTarget(pathToInclude);
    }

    return true;
}

inline bool UsdCollectionAPI::ExcludePath(const SdfPath& pathToExclude) const
{
    // If the path is already excluded from a non-empty collection
    // (or simply not included at all), do nothing.
    UsdCollectionMembershipQuery query = ComputeMembershipQuery();
    if (!query.GetAsPathExpansionRuleMap().empty() && !query.IsPathIncluded(pathToExclude))
    {
        return true;
    }

    if (pathToExclude == SdfPath::AbsoluteRootPath())
    {
        auto includeRootAttr = CreateIncludeRootAttr();
        includeRootAttr.Set(false);
        return true;
    }

    // Check if the path is directly included in the collection.
    SdfPathVector includes;
    if (UsdRelationship includesRel = GetIncludesRel())
    {
        includesRel.GetTargets(&includes);

        if (std::find(includes.begin(), includes.end(), pathToExclude) != includes.end())
        {
            includesRel.RemoveTarget(pathToExclude);
            // Update the query object we have, instead of having to
            // recompute it.
            UsdCollectionMembershipQuery::PathExpansionRuleMap map = query.GetAsPathExpansionRuleMap();
            auto it = map.find(pathToExclude);
            if (it != map.end())
            {
                map.erase(it);
                query = UsdCollectionMembershipQuery(std::move(map), query.GetIncludedCollections());
            }
        }
    }

    // Now that we've removed the explicit include if there was one,
    // we can add an explicit exclude, if required.
    if (query.GetAsPathExpansionRuleMap().empty() || query.IsPathIncluded(pathToExclude))
    {
        return CreateExcludesRel().AddTarget(pathToExclude);
    }

    return true;
}

} // namespace usdrt

