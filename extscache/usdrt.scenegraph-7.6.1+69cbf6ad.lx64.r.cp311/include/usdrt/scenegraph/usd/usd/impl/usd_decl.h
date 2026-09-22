// Copyright (c) 2021-2025, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

//! @file usd/impl/usd_decl.h
//!
//! @brief Implements UsdStage, UsdPrim, UsdAttribute, UsdRelationship,
//! UsdPrimRange, UsdSchemaBase, UsdTyped, UsdSchemaRegistry

#include <omni/core/IObject.h>
#include <omni/fabric/batch/View.h>
#include <usdrt/scenegraph/base/gf/range3d.h>
#include <usdrt/scenegraph/base/tf/token.h>
#include <usdrt/scenegraph/base/vt/array.h>
#include <usdrt/scenegraph/interface/IRtAttribute105.h>
#include <usdrt/scenegraph/interface/IRtPrim107.h>
#include <usdrt/scenegraph/interface/IRtPrimRange.h>
#include <usdrt/scenegraph/interface/IRtRelationship.h>
#include <usdrt/scenegraph/interface/IRtStage107.h>
#include <usdrt/scenegraph/usd/rt/defines.h>
#include <usdrt/scenegraph/usd/sdf/path.h>
#include <usdrt/scenegraph/usd/sdf/types.h>
#include <usdrt/scenegraph/usd/sdf/valueTypeName.h>
#include <usdrt/scenegraph/usd/usd/common.h>
#include <usdrt/scenegraph/usd/usd/schemaRegistry.h>
#include <usdrt/scenegraph/usd/usd/timeCode.h>

#include <iterator>
#include <memory>
#include <optional>

namespace usdrt
{

class UsdStage;
class UsdPrim;
class UsdAttribute;
class UsdRelationship;
class UsdPrimRange;
class UsdSchemaBase;
class UsdAPISchemaBase;
class UsdTyped;
class UsdSchemaRegistry;
class RtPrimSelection;

using UsdStageId = uint64_t;

typedef std::shared_ptr<UsdStage> UsdStageRefPtr;

//! @class UsdStage
//!
//! @brief The outermost container for the scene description.
//!
//! Contains a fabric stage, and offers most familiar Usd methods,
//! and some additional methods to query fabric and export to USD.
class UsdStage
{
public:
    //! @enum InitialLoadSet
    //! Specifies the initial set of prims to load when opening a UsdStage.
    enum InitialLoadSet
    {
        LoadAll, //!< Load all loadable prims
        LoadNone //!< Load no loadable prims
    };

    // FIXME - pybind requires void here?
    ~UsdStage(void);

    // ------------------
    // Stage management
    // ------------------

    //! Creates a new stage with root layer @p identifier.
    //! @param identifier Root layer name for the new stage.
    //! @param load The initial set of prims to load on the staged. Default is `LoadAll`.
    //! @return Return the reference pointer to the new stage.
    static UsdStageRefPtr CreateNew(const std::string& identifier, InitialLoadSet load = LoadAll);

    //! Open a stage rooted at @p filePath.
    //! @param filePath Path to the stage to open.
    //! @param load The initial set of prims to load on the stage. Default is `LoadAll`.
    //! @return Return the reference pointer to the opened stage.
    static UsdStageRefPtr Open(const std::string& filePath, InitialLoadSet load = LoadAll);

    //! Creates a new stage only in memory with  root layer @p identifier.
    //! Note: This also creates an underlying usd stage.
    //! To create a stage in Fabric only, see @p CreateOnlyInFabric
    //! @param identifier Root layer name for the new stage.
    //! @param load The initial set of prims to load on the stage. Default is `LoadAll`.
    //! @return Return the reference pointer to the new stage.
    static UsdStageRefPtr CreateInMemory(const std::string& identifier, InitialLoadSet load = LoadAll);

    //! Creates a new stage only in fabric.
    //! @return Return the reference pointer to the new stage.
    static UsdStageRefPtr CreateOnlyInFabric();

    //! Attempt to find a matching existing fabric stage with Usd stage id @p stageId.
    //! @param stageId The `UsdStageId` to look for in the UsdUtils global stage cache.
    //! @param stageReaderWriterId The fabric stage id associated with this usdrt stage.
    //! @return Return the reference pointer to the attached stage.
    static UsdStageRefPtr Attach(omni::fabric::UsdStageId stageId,
                                 omni::fabric::StageReaderWriterId stageReaderWriterId = { 0 });

    //! Attempt to find a matching existing fabric stage with fabric id @p fabricId.
    //! @param fabricId The `FabricId` to look for.
    //! @return Return the reference pointer to the attached stage.
    static UsdStageRefPtr Attach(const omni::fabric::FabricId fabricId);

    // ------------------
    // Prim access
    // ------------------

    //! Get the UsdPrim on this stage at the specified @p path
    //! and optionally prefetch the data in fabric from USD.
    //! @param path The prim path to find.
    //! @param prefetchFromUsd Is prefetching from USD necessary.
    //! @return Return the UsdPrim at the given path, or an
    //! invalid prim if not found.
    UsdPrim GetPrimAtPath(const SdfPath& path, bool prefetchFromUsd = true) const;

    //! Get the root UsdPrim on this stage whose name is the
    //! root layer's defaultPrim metadata's value and optionally
    //! prefetch in fabric from USD.
    //! @param prefetchFromUsd Is prefetching from USD necessary.
    //! @note For a Fabric only stage, this will always return the absolute root path.
    //! @return Return the root UsdPrim.
    UsdPrim GetDefaultPrim(bool prefetchFromUsd = true) const;

    //! Gets or Creates a prim on this stage. If the prim already exists
    //! on the Usd stage, prefetch to fabric and return it. If the prim
    //! already exists in fabric, return it. Otherwise a
    //! new prim is created on the fabric stage.
    //!
    //! @note Current implementation does not yet automatically create
    //! any schema attributes defined by the prim type.
    //!
    //! @param path The path to the prim.
    //! @param typeName type of prim to create. Default is empty token.
    //! @return Return the prim at the given path.
    UsdPrim DefinePrim(const SdfPath& path, const TfToken& typeName = TfToken());

    //! Get the psuedo root "/" and prefetch in fabric.
    //! @return Return the pseudo root defined by Usd.
    UsdPrim GetPseudoRoot() const;

    //! Remove prim at @p path from the fabric stage only.
    //! @param path The path to the prim to remove.
    //! @return `true` if the prim has successly been removed from fabric and `false` otherwise.
    bool RemovePrim(const SdfPath& path) const;

    // ------------------
    // Attribute access
    // ------------------

    //! Get the attribute at the given path if it is a valid prim
    //! by optionally prefetching it from USD..
    //! Loads the prim in fabric if it is not already.
    //! @param path The path to the prim.
    //! @param prefetchFromUsd Is prefetching from USD necessary.
    //! @return The attribute at the given path, or an invalid attribute object if not found.
    UsdAttribute GetAttributeAtPath(const SdfPath& path, bool prefetchFromUsd = true) const;

    //! Get the relationship at the given path if it is a valid prim
    //! by optionally prefetching it from USD..
    //! @param path The path to the prim.
    //! @param prefetchFromUsd Is prefetching from USD necessary.
    //! @return The relationship at the given path, or an invalid relationship object if not found.
    UsdRelationship GetRelationshipAtPath(const SdfPath& path, bool prefetchFromUsd = true) const;

    // ------------------
    // Traverse
    // ------------------

    //! Traverse the active, loaded, defined, non-abstract prims on this stage depth-first.
    //! @return Return a `UsdPrimRange`, which allows for iteratable depth-first traversal of the stage.
    UsdPrimRange Traverse();

    // ------------------
    // RT
    // ------------------

    //! Get the the Usd stage id for this stage. This id is consistent across USD and USDRT stages.
    //! @note For Fabric only stages, this will return omni::fabric::kUninitializedStage.
    //! @return Usd stage id
    omni::fabric::UsdStageId GetStageId() const;

    //! Get the fabric stage reader writer id associated with this usdrt stage.
    //! @return Return the stage reader writer id.
    omni::fabric::StageReaderWriterId GetStageReaderWriterId() const;

    //! \warning Deprecated, use GetStageReaderWriterId instead
    //!
    //! Get the fabric stage reader writer id associated with this usdrt stage.
    //! @return Return the stage reader writer id.
    omni::fabric::StageReaderWriterId GetStageInProgressId() const; // deprecated, 104 support

    //! Get the specific id for the fabric cache.
    //! @return Return the fabric Id.
    omni::fabric::FabricId GetFabricId() const;

    //! Check if this is a fabric only stage.
    //! @return Returns true if this stage does not have an underlying USD stage.
    bool IsFabricOnlyStage() const;

    //! Check if a specific sim stage with history exists.
    //! SimStageWithHistory is a container for fabric with a StageReaderWriter and read-only StageAtTime instances.
    //! @param stageId The Usd stage id to look for.
    //! @return Return `true` if the sim stage with history exists, `false` otherwise.
    static bool SimStageWithHistoryExists(omni::fabric::UsdStageId stageId);

    //! \warning Deprecated, use SimStageWithHistoryExists instead
    //!
    //! This is a default kit container for fabric for the stage reader writer and read-only stage at time instances.
    //! @param stageId The Usd stage id to look for.
    //! @return Return `true` if the sim stage with history exists, `false` otherwise.
    static bool StageWithHistoryExists(omni::fabric::UsdStageId stageId); // deprecated, 104 support

    //! Write Fabric data that has been modified since fetching from USD to the
    //! underlying USD Stage's current EditTarget and save it. If no underlying USD stage, do nothing.
    //! @note Note that WriteToStage will not export new prims created in Fabric.
    //! @param includePrivateFabricProperties Include _* and omni:fabric:* properties when writing USD. Default is true.
    //! @param convertFabricXforms Convert Fabric transforms to XformOps in USD. Default is false.
    void WriteToStage(bool includePrivateFabricProperties = true, bool convertFabricXforms = false) const;

    //! Write fabric data to a new temp stage with the layer @p filepath, and save it.
    //! @param filePath Path to the new temp stage.
    //! @param includePrivateFabricProperties Include _* and omni:fabric:* properties when writing USD. Default is true.
    //! @param convertFabricXforms Convert Fabric transforms to XformOps in USD. Default is false.
    void WriteToLayer(const std::string& filePath,
                      bool includePrivateFabricProperties = true,
                      bool convertFabricXforms = false) const;

    //! Check if prim at @p path exists in fabric, optionally including minimally populated prims.
    //! @param path The path to look for.
    //! @param excludeTags Exclude any prims in fabric that _only_ have minimal population tags. Default is true.
    //! @return Return `true` if the prim exists in fabric, `false` otherwise.
    bool HasPrimAtPath(const SdfPath& path, bool excludeTags = true) const;

    //! Find all prims on the fabric stage with type @p typename.
    //! @param typeName Prim type to find
    //! @return Return a vector of prim paths with the given @p typename.
    std::vector<SdfPath> GetPrimsWithTypeName(const TfToken& typeName) const;

    //! Find all prims on the fabric stage with applied API @p apiName.
    //! @param apiName The schema api name to look for.
    //! @return Return a vector of prim paths with the given @p apiName.
    std::vector<SdfPath> GetPrimsWithAppliedAPIName(const TfToken& apiName) const;

    //! Find all prims on the fabric stage with type name @p typeName and applied APIs @p apiNames.
    //! @param typeName Prim type to find
    //! @param apiNames The list of schema api names to look for.
    //! @return Return a vector of prim paths with the given @p apiNames and @p typeName.
    std::vector<SdfPath> GetPrimsWithTypeAndAppliedAPIName(const TfToken& typeName,
                                                           const std::vector<TfToken>& apiNames) const;

    //! Get the stage extent. Run minimal populate if FSD is not active, and if not yet populated, compute and
    //! populate the world extent attributes for all boundable prims. Then compute the
    //! global min/max for the stage.
    //! @note For a Fabric only stage, this does nothing.
    //! @return Return the min/max points range for the stage.
    GfRange3d GetStageExtent() const;

    //! Get an RtPrimSelection, a selection of the stage's prims accessible on
    //! CPU or GPU. For example, you can create an RtPrimSelection that selects
    //! all the Meshes on the stage, or all the Meshes with Physics applied,
    //! and then efficiently process that selection as a batch. An
    //! RtPrimSelection also selects a subset of the attributes of the selected
    //! prims, USDRT uses this information to minimize CPU<->GPU transfers.
    //! @param device kDeviceCpu to get the prim selection on CPU, or integer i
    //!               for CUDA device i.
    //! @param requireAppliedSchemas Only include prims that have all the
    //!                              applied schemas in this list.
    //! @param requireAttrs Provide access to the attributes in this list, only
    //!                     include prims with these attributes.
    //! @param requirePrimTypeName Only include prims that have this prim type
    //!                            (optional).
    //! @param wantPaths Provide access to prim paths within the selection -
    //!                  this has memory overhead and GPU transfer timing implications
    //!                  when enabled (optional)
    RtPrimSelection SelectPrims(std::vector<TfToken> requireAppliedSchemas,
                                std::vector<AttrSpec> requireAttrs,
                                std::optional<TfToken> requirePrimTypeName = {},
                                uint32_t device = kDeviceCpu,
                                bool wantPaths = false);

    //! Synchronizes all pending USD changes to Fabric and makes cached Fabric
    //! data (such as transformation caches) up to date.
    //! Cached Fabric data is made consistent even if there is no USD stage
    //! attached.
    //!
    //! For a Fabric only stage with no underlying USD stage, this does nothing.
    //!
    //! When @p is not set to TimeChange::NoUpdate, time-sampled USD data is
    //! sampled at the given @p time before writing it to Fabric, otherwise
    //! time-sampled data is ignored.
    //!
    //! Known issues:
    //! - Default time code is not supported
    //! - TimeChange::ForceUpdate is not supported
    //! - Time-sampled data is not updated when FSD is off
    //! @param timeChange How to synchronize time-sampled data.
    //!                   NoUpdate: ignore time samples.
    //!                   LazyUpdate: if @p time is different from the value
    //!                       passed in the previous call, evaluate attribute
    //!                       value at @p time and write it to Fabric.
    //!                   ForceUpdate: always evaluate attribute value at
    //!                       @p time and write it to Fabric.
    //! @param time Time in USD time codes at which time-sampled data is
    //!             evaluated. Ignored when @p timeChange is NoUpdate.
    void SynchronizeToFabric(TimeChange timeChange = TimeChange::NoUpdate,
                             const usdrt::UsdTimeCode& time = usdrt::UsdTimeCode::Default());

    //! @private
    omni::core::ObjectPtr<usdrt::IRtStage> m_stage;
};

//! @class UsdPrim
//!
//! @brief A UsdPrim is the principal container of other types of scene description.
//! It provides API for accessing and creating all of the contained kinds
//! of scene description
class UsdPrim
{
public:
    // --------------------
    // Attribute accessors
    // --------------------

    //! Check if this prim has an attribute named @p name in Fabric.
    //!  Does not check for attribute existence in the underlying USD stage.
    //!
    //! @param name The attribute name.
    //! @return Return true if the attribute exists on this prim, and false otherwise.
    bool HasAttribute(const TfToken& name) const;

    //! Get the attribute named @p name if it exists in fabric.
    //! Does not check for attribute existence in the underlying USD stage.
    //!
    //! @param name The attribute name.
    //! @return Return the attribute on this prim with name @p name, or
    //! an invalid attribute object if not found.
    UsdAttribute GetAttribute(const TfToken& name) const;

    //! Get all attributes on this prim.
    //! @note Current implementation only returns attributes that exist in Fabric
    //! @return Return a vector of attributes that are on the prim.
    std::vector<UsdAttribute> GetAttributes() const;

    //! Get all authored attributes on this prim.
    //! @return Return a vector of attributes that are authored on the prim.
    std::vector<UsdAttribute> GetAuthoredAttributes() const;

    //! Create a new attribute on this prim in fabric.
    //!
    //! TODO: SdfVariability parameter
    //!
    //! @param name The attribute name.
    //! @param typeName The type of the attribute.
    //! @param custom Indicate if the attribute is custom. Default is true.
    //! This currently does nothing as it is not represented in fabric.
    //! @return Return the new attribute.
    UsdAttribute CreateAttribute(const TfToken& name, const SdfValueTypeName& typeName, bool custom = true) const;

    // -----------------------
    // Relationship accessors
    // -----------------------

    //! Check if this prim has a relationship named @p name. Fabric is the
    //! ground truth for existence, so there is no USD fallback.
    //!
    //! @param name The relationship name.
    //! @return Return true if the relationship exists on this prim, and false otherwise.
    bool HasRelationship(const TfToken& name) const;

    //! Get the relationship named @p name if it exists.
    //!
    //! @note Fabric does not yet support lists of targets for relationships.
    //!
    //! @param name The relationship name.
    //! @return Return the relationship on this prim with name @p name, or
    //! an invalid relationship object if not found.
    UsdRelationship GetRelationship(const TfToken& name) const;

    //! Get all relationships on this prim.
    //!
    //! @note Fabric does not yet support lists of targets for relationships.
    //!
    //! @return Return a vector of relationship that are on the prim.
    std::vector<UsdRelationship> GetRelationships() const;

    //! Get all authored relationships on this prim.
    //!
    //! @note Fabric does not yet support lists of targets for relationships.
    //!
    //! @return Return a vector of relationships that are authored on the prim.
    std::vector<UsdRelationship> GetAuthoredRelationships() const;

    //! Create a new relationship on this prim in fabric.
    //!
    //! @param relName The relationship name.
    //! @param custom Indicate if the relationship is custom. Default is true.
    //! This currently does nothing as it is not represented in fabric.
    //! @return Return the new relationship.
    UsdRelationship CreateRelationship(const TfToken& relName, bool custom = true) const;

    // --------------------
    // Property accessors
    // --------------------

    //! Remove property from this prim in fabric.
    //! @param name Name of the property to remove.
    //! @return Return true if the property was removed, and false otherwise.
    bool RemoveProperty(const TfToken& name) const;

    //! Get all of this prim's properties (attributes and relationships).
    //! Includes build in properties.
    //! @return Return a TfTokenVector of property names.
    TfTokenVector GetPropertyNames() const;

    //! Get all of this prim's properties (attributes and relationships).
    //! Includes build in properties.
    //!
    //! Note: Fabric doesn't differientiate between authored properties,
    //! so this API is here for completeness but is the exact same as GetPropertyNames.
    //!
    //! @return Return a TfTokenVector of property names.
    TfTokenVector GetAuthoredPropertyNames() const;

    //! Check if the prim has property @p name.
    //! @param name Property name
    //! @returns True if this prim has property @p name.
    bool HasProperty(const TfToken& name) const;

    // --------------------
    // UsdObject methods
    // --------------------

    //! Check if this is a valid prim. A prim is valid if it
    //! exists in fabric. This includes minimally populated prims.
    //! @return Return true if this prim is valid, and false otherwise.
    bool IsValid() const;

    //! Get the fabric stage holding this UsdPrim.
    //! @return Return a pointer to the fabric stage that contains this prim.
    UsdStageRefPtr GetStage() const;

    //! UsdObject method required for UsdPrim to be a complete type.
    //! @return Return this prim.
    UsdPrim GetPrim() const;

    //! Get the name of this prim.
    //! @return Return the name of this prim.
    const TfToken GetName() const;

    //! Get the path to this prim.
    //! @return Returns the path to this prim.
    SdfPath GetPath() const;

    //! Get the path to this prim.
    //! @return Returns the path to this prim.
    const SdfPath GetPrimPath() const;

    // --------------------
    // Hierarchy accessors
    // --------------------

    //! Get child prim @p name from this prim's children
    //! by optionally prefetching it from USD.
    //! @param name The name of the child to look for.
    //! @param prefetchFromUsd Is prefetching from USD necessary.
    //! @return Return the child prim, or an invalid prim if not found.
    UsdPrim GetChild(const TfToken& name, bool prefetchFromUsd = true) const;

    //! Get child prims of this prim by optionally prefetching them from USD.
    //! If fabric population / hierarchy is active, get
    //! child prims using the fabric Connectivity API.
    //! Otherwise, fall back to `GetChildren` in USD and load the prims into fabric.
    //! @param prefetchFromUsd Is prefetching from USD necessary.
    //! @return Return a vector containing all child prims of this prim.
    std::vector<UsdPrim> GetChildren(bool prefetchFromUsd = true) const;

    //! Get list of child prim names when iterating over GetChildren,
    //! by optionally prefetching them from USD.
    //! @param prefetchFromUsd Is prefetching from USD necessary.
    //! @return TfTokenVector of child names.
    TfTokenVector GetChildrenNames(bool prefetchFromUsd = true) const;

    //! Get all child prims of this prim by optionally prefetching them from USD.
    //! If fabric population / hierarchy is active,
    //! get child prims using the fabric Connectivity API.
    //! Otherwise, fall back to `GetChildren` USD and load the prims into fabric.
    //!
    //! @note This differs from USD functionality. Same as @ref GetChildren.
    //!
    //! @param prefetchFromUsd Is prefetching from USD necessary.
    //! @return Return a vector containing all child prims of this prim.
    std::vector<UsdPrim> GetAllChildren(bool prefetchFromUsd = true) const;

    //! Get list of child prim names when iterating over GetAllChildren,
    //! by optionally prefetching them from USD.
    //! @param prefetchFromUsd Is prefetching from USD necessary.
    //! @return TfTokenVector of child names.
    TfTokenVector GetAllChildrenNames(bool prefetchFromUsd = true) const;

    //! Get this prim's parent prim by optionally prefetching it from USD.
    //! @param prefetchFromUsd Is prefetching from USD necessary.
    //! @return Return this prim's parent prim by optionally prefetching it from USD.
    UsdPrim GetParent(bool prefetchFromUsd = true) const;

    //! Get this prim's next sibling in the scene hierarchy
    //! by optionally prefetching it from USD.
    //! If population is active, get next sibling using Connectivity.
    //! Otherwise fall back to USD.
    //! @param prefetchFromUsd Is prefetching from USD necessary.
    //! @return Return this prim's next sibling if it has one. Otherwise
    //! return an invalid prim.
    UsdPrim GetNextSibling(bool prefetchFromUsd = true) const;

    // --------------------
    // Type
    // --------------------

    //! Get the type name for this prim.
    //! This looks for the attribute of type
    //! SdfValueTypeNames->PrimTypeTag in fabric.
    //! @return Return the prim type name.
    TfToken GetTypeName() const;

    //! Set this prim's type name. This clears any existing type
    //! name and sets the attribute SdfValueTypeNames->PrimTypeTag
    //! in fabric to @p typeName.
    //! @param typeName Prim's new type name to set.
    //! @return Return true if this prim's type name has been updated. False otherwise.
    bool SetTypeName(const TfToken& typeName) const;

    //! Clear this prim's typename. This removes the attribute of type
    //! SdfValueTypeNames->PrimTypeTag from fabric.

    //! @return Return true if this prim's type name has been cleared. False otherwise.
    bool ClearTypeName() const;

    //! Check if this prim has an authored typename. True if an attribute of
    //! type SdfValueTypeNames->PrimTypeTag has a value authored.
    //! @return Return true if this prim's typename tag is authored, false otherwise.
    bool HasAuthoredTypeName() const;

    // --------------------
    // Schema Types
    // --------------------

    //! Query if this prim's type is or is a child type of @p SchemaType.
    //! An error will be issued if @p SchemaType is an unknown schema.
    //! @tparam SchemaType The schema type name or alias type.
    //! @return Return true if this prim is or is a child type of @p SchemaType.
    template <typename SchemaType>
    bool IsA() const
    {
        static_assert(std::is_base_of<UsdSchemaBase, SchemaType>::value, "Provided type must derive UsdSchemaBase.");
        TfToken queryTypeName = SchemaType::_GetStaticTfType();
        return _IsA(queryTypeName, /*validateSchemaType=*/false);
    };

    //! Query if this prim's type is or is a child type of @p SchemaType.
    //! An error will be issued if the @p schemaType is an unknown schema.
    //!
    //! @param schemaType The schema c++ type.
    //! @return Return true if this prim is or is a child type of @p SchemaType.
    bool IsA(const TfToken& schemaType) const;

    // --------------------
    // API schemas
    // --------------------

    //! Apply schema of type @p appliedSchemaName. This authors an attribute
    //! of type SdfValueTypeNames->AppliedSchemaTypeTag with value @p appliedSchemaName.
    //! This method assumes:
    //! - input validation (if desired) has already been done by other API methods (UsdPrim::ApplyAPI).
    //! - the @p appliedSchemaName is the schema alias. For example: `MotionAPI` instead of `UsdGeomMotionAPI`. This is
    //! required for Fabric.
    //! - for multiple-apply schemas, @p appliedSchemaName contains both the namespace and instance name. For example:
    //! 'CollectionAPI:myStuff'.
    //!
    //! `ApplyAPI` is the preferred method for applying valid API schemas.
    //! Using `ApplyAPI` instead will convert schema names to alias and join namespace/instance names.
    //! @sa UsdPrim::ApplyAPI
    //!
    //! @param appliedSchemaName The full name or alias of the schema to apply.
    //! @return Return true if the schema has been applied, false otherwise.
    bool AddAppliedSchema(const TfToken& appliedSchemaName) const;

    //! Remove schema of type @p appliedSchemaName. This removes the attribute
    //! of type SdfValueTypeNames->AppliedSchemaTypeTag with value @p appliedSchemaName.
    //! This method assumes:
    //! - input validation has already been done by other API methods (UsdPrim::RemoveAPI).
    //! - the @p appliedSchemaName is the schema alias. For example: `MotionAPI` instead of `UsdGeomMotionAPI`. This is
    //! required for Fabric.
    //! - for multiple-apply schemas, @p appliedSchemaName contains both the namespace and instance name. For example:
    //! 'CollectionAPI:myStuff'.
    //!
    //! `RemoveAPI` is the preferred method for applying valid API schemas.
    //! Using `RemoveAPI` instead will convert schema names to alias and join namespace/instance names.
    //! @sa UsdPrim::RemoveAPI
    //!
    //! @param appliedSchemaName The full name or alias of the schema to remove.
    //! @return Return true if the schema has been removed, false otherwise.
    bool RemoveAppliedSchema(const TfToken& appliedSchemaName) const;

    //! Check is this prim has a schema @p schemaIdentifier applied. Looks for an
    //! authored attribute of type SdfValueTypeNames->AppliedSchemaTypeTag and
    //! value @p schemaIdentifier. For MultipleApplyAPI schemas, the query value
    //! is @p schemaIdentifier as the namespace, joined with @p instanceName
    //!
    //! @param schemaIdentifier The full name or alias of the schema to check.
    //! @param instanceName If non-empy, used to determine if a particular instance of a
    //! multiple-apply api schema has been applied to the prim if @p SchemaType is a
    //! multiple-apply api schema. Default empty.
    //! @return Return true if the schema is applied to this prim, false otherwise.
    bool HasAPI(const TfToken& schemaIdentifier, const TfToken& instanceName = TfToken()) const;

    //! Check is this prim has a schema of type @p SchemaType applied. Looks for an
    //! authored attribute of type SdfValueTypeNames->AppliedSchemaTypeTag and
    //! value @p SchemaType.
    //!
    //! An error will be issued if @p SchemaType does not a known applied API schema,
    //! or if, for a miltiple-apply API schema, @p instanceName is empty.
    //!
    //! @tparam SchemaType The schema type to check.
    //! @param instanceName If non-empy, used to determine if a particular instance of a
    //! multiple-apply api schema has been applied to the prim if @p SchemaType is a
    //! multiple-apply api schema. Default empty.
    //! @return Return true if the schema is applied to this prim, false otherwise.
    template <typename SchemaType>
    bool HasAPI(const TfToken& instanceName = TfToken()) const
    {
        // Validate
        static_assert(
            std::is_base_of<UsdAPISchemaBase, SchemaType>::value, "Provided type must derive UsdAPISchemaBase.");
        static_assert(!std::is_same<UsdAPISchemaBase, SchemaType>::value, "Provided type must not be UsdAPISchemaBase.");
        static_assert((SchemaType::schemaType == UsdSchemaType::SingleApplyAPI ||
                       SchemaType::schemaType == UsdSchemaType::MultipleApplyAPI),
                      "Provided schema type must be an applied API schema.");

        if (SchemaType::schemaType != UsdSchemaType::MultipleApplyAPI && !instanceName.IsEmpty())
        {
            // Single apply API must have a non-empty instance name.
            return false;
        }

        TfToken queryTypeName = SchemaType::_GetStaticTfType();
        return HasAPI(queryTypeName, instanceName);
    };

    //! Apply schema of type @p schemaIdentifier to the prim.
    //!
    //! For @p schemaIdentifier to be valid schema to apply, it must be a single-apply or
    //! multiple-apply api schema, and for multiple-apply, @p instanceName must not be empty.
    //! @sa UsdPrim::AddAppliedSchema
    //!
    //! @param schemaIdentifier The full name or alias of the schema to apply.
    //! @param instanceName If non-empy, used to determine if a particular instance of a
    //! multiple-apply api schema has been applied to the prim if @p SchemaType is a
    //! multiple-apply api schema. Default empty.
    //! @return Return true if the schema has been applied, false otherwise.
    bool ApplyAPI(const TfToken& schemaIdentifier, const TfToken& instanceName = TfToken()) const;

    //! Apply schema of type @p SchemaType to the prim.
    //!
    //! An error is raised for invalid @p SchemaType. For @p SchemaType to be valid schema
    //! to apply using this template, it must be a single-apply API schema.
    //! @sa UsdPrim::AddAppliedSchema
    //!
    //! @tparam SchemaType The schema type to apply.
    //! @return Return true if the schema has been applied, false otherwise.
    template <typename SchemaType>
    bool ApplyAPI() const
    {
        // Validate
        static_assert(
            std::is_base_of<UsdAPISchemaBase, SchemaType>::value, "Provided type must derive UsdAPISchemaBase.");
        static_assert(!std::is_same<UsdAPISchemaBase, SchemaType>::value, "Provided type must not be UsdAPISchemaBase.");
        static_assert(SchemaType::schemaType == UsdSchemaType::SingleApplyAPI,
                      "Provided schema type must be an single apply API schema.");

        TfToken queryTypeName = SchemaType::_GetStaticTfType();
        return ApplyAPI(queryTypeName);
    };

    //! Apply schema of type @p SchemaType to the prim.
    //!
    //! An error is raised for invalid @p SchemaType. For @p SchemaType to be valid schema
    //! to apply using this template, it must be a multiple-apply api schema and instanceName must not be empty.
    //! @sa UsdPrim::AddAppliedSchema
    //!
    //! @tparam SchemaType The schema type to apply.
    //! @param instanceName If non-empy, used to determine if a particular instance of a
    //! multiple-apply api schema has been applied to the prim if @p SchemaType is a
    //! multiple-apply api schema.
    //! @return Return true if the schema has been applied, false otherwise.
    template <typename SchemaType>
    bool ApplyAPI(const TfToken& instanceName) const
    {
        // Validate
        static_assert(
            std::is_base_of<UsdAPISchemaBase, SchemaType>::value, "Provided type must derive UsdAPISchemaBase.");
        static_assert(!std::is_same<UsdAPISchemaBase, SchemaType>::value, "Provided type must not be UsdAPISchemaBase.");
        static_assert(SchemaType::schemaType == UsdSchemaType::MultipleApplyAPI,
                      "Provided schema type must be an multiple apply API schema.");

        TfToken queryTypeName = SchemaType::_GetStaticTfType();
        return ApplyAPI(queryTypeName, instanceName);
    };

    //! Remove schema of type @p schemaIdentifier.
    //! @param schemaIdentifier The full name or alias of the schema to remove.
    //! @param instanceName If non-empy, used to remove a particular instance of a
    //! multiple-apply api schema from the prim if @p SchemaType is a
    //! multiple-apply api schema. Default empty.
    //! @return Return true if the schema has been removed, false otherwise.
    bool RemoveAPI(const TfToken& schemaIdentifier, const TfToken& instanceName = TfToken()) const;

    //! Remove single-apply API schema of type @p SchemaType.
    //!
    //! An error is raised for invalid @p SchemaType. For @p SchemaType to be valid schema
    //! to remove using this template, it must be a single apply-api schema.
    //! @sa UsdPrim::RemoveAppliedSchema
    //!
    //! @tparam SchemaType The schema type to remove.
    //! @return Return true if the schema has been removed, false otherwise.
    template <typename SchemaType>
    bool RemoveAPI() const
    {
        // Validate
        static_assert(
            std::is_base_of<UsdAPISchemaBase, SchemaType>::value, "Provided type must derive UsdAPISchemaBase.");
        static_assert(!std::is_same<UsdAPISchemaBase, SchemaType>::value, "Provided type must not be UsdAPISchemaBase.");
        static_assert(SchemaType::schemaType == UsdSchemaType::SingleApplyAPI,
                      "Provided schema type must be an single apply API schema.");

        TfToken queryTypeName = SchemaType::_GetStaticTfType();
        return RemoveAPI(queryTypeName);
    };

    //! Remove multiple-apply API schema of type @p SchemaType.
    //!
    //! An error is raised for invalid @p SchemaType. For @p SchemaType to be valid schema
    //! to remove using this template, it must be a multiple-apply api schema and instanceName must not be empty.
    //! @sa UsdPrim::RemoveAppliedSchema
    //!
    //! @tparam SchemaType The schema type to remove.
    //! @param instanceName Used to remove a particular instance of a
    //! multiple-apply api schema from the prim. Must not be empty.
    //! @return Return true if the schema has been removed, false otherwise.
    template <typename SchemaType>
    bool RemoveAPI(const TfToken& instanceName) const
    {
        // Validate
        static_assert(
            std::is_base_of<UsdAPISchemaBase, SchemaType>::value, "Provided type must derive UsdAPISchemaBase.");
        static_assert(!std::is_same<UsdAPISchemaBase, SchemaType>::value, "Provided type must not be UsdAPISchemaBase.");
        static_assert(SchemaType::schemaType == UsdSchemaType::MultipleApplyAPI,
                      "Provided schema type must be a multiple apply API schema.");

        TfToken queryTypeName = SchemaType::_GetStaticTfType();
        return RemoveAPI(queryTypeName, instanceName);
    };

    //! Get all applied schemas. Look for all attributes of
    //! type SdfValueTypeNames->AppliedSchemaTypeTag.
    //! @return Return a vector of applied schema alias names.
    TfTokenVector GetAppliedSchemas() const;

    //! Check if this prim is valid. See UsdPrim::IsValid.
    //! @return Return true if this prim is valid, and false otherwise.
    explicit operator bool() const;

    //! @private
    omni::core::ObjectPtr<usdrt::IRtPrim> m_prim;

private:
    bool _IsA(const TfToken& schemaType, bool validateSchemaType) const;
};

//! @class UsdAttribute
//!
//! @brief Scenegraph object for authoring and retrieving numeric, string, and array
//! valued data, sampled over time.
//!
//! Allowed value types for attributes are defined by SdfValueTypeNames.
class UsdAttribute
{
public:
    // --------------------
    // Value methods
    // --------------------

    //! Check if this attribute has an authored value in Fabric,
    //! or fall back to USD to check for an authored default value /
    //! time samples / fallback value provided by a schema.
    //!
    //! @return Return true if this attribute has an authored value in Fabric,
    //! or fall back to USD to check for an authored default value /
    //! time sampled value / fallback value provided by a schema.
    //! and false otherwise.
    bool HasValue() const;

    //! Check if this attribute has an authored value in Fabric,
    //! or fall back to USD to check for an authored default value or
    //! authored time samples.
    //!
    //! @return Return true if this attribute has an authored value in Fabric,
    //! or fall back to USD to check for an authored default value or
    //! authored time samples, and false otherwise.
    bool HasAuthoredValue() const;

    //! Perform value resolution to fetch the value of this attribute at
    //! the requested UsdTimeCode @p time.
    //!
    //! @note Current implementation ignores timecode.
    //!
    //! @tparam typename A valid type specified by SdfValueTypeNames.
    //! @param[out] value This attribute's value.
    //! @param[in] time UsdTimeCode Default is UsdTimeCode::Default().
    //! @return Return true if a value of type T was successfully read, and false otherwise.
    template <typename T>
    bool Get(T* value, UsdTimeCode time = UsdTimeCode::Default()) const;

    //! Fetch the value of this attribute at in fabric.
    //!
    //! @note Current implementation ignores timecode.
    //!
    //! @tparam typename Vt container for a valid type specified by SdfValueTypeNames.
    //! @param[out] value Vt container for this attribute's value.
    //! @param[in] time UsdTimeCode Default is UsdTimeCode::Default().
    //! @return Return true if a value of type T was successfully read, and false otherwise.
    template <typename T>
    bool Get(VtArray<T>* value, UsdTimeCode time = UsdTimeCode::Default()) const;


    //! Set the value of this attribute in fabric.
    //!
    //! @note Current implementation ignores timecode.
    //!
    //! @tparam typename A valid type specified by SdfValueTypeNames.
    //! @param value This attribute's new value to set.
    //! @param time UsdTimeCode Default is UsdTimeCode::Default().
    //! @return Return true if a value of type T was successfully set, and false otherwise.
    template <typename T>
    bool Set(const T& value, UsdTimeCode time = UsdTimeCode::Default());

    //! Set the array value of this attribute in fabric.
    //!
    //! @note Current implementation ignores timecode.
    //!
    //! @tparam typename A valid type specified by SdfValueTypeNames.
    //! @param value This attribute's new value to set.
    //! @param time UsdTimeCode Default is UsdTimeCode::Default().
    //! @return Return true if a value of type T was successfully set, and false otherwise.
    template <typename T>
    bool Set(const VtArray<T>& value, UsdTimeCode time = UsdTimeCode::Default());

    // --------------------
    // Core metadata
    // --------------------

    //! Get the SdfValueTypeName for this attribute.
    //! @return Return the value type name for this attribute.
    SdfValueTypeName GetTypeName() const;

    // --------------------
    // UsdObject methods
    // --------------------

    //! Check if the attribute is valid (i.e exists in fabric).
    //! @return Return true if the attribute exists in fabric, and false otherise.
    bool IsValid() const;

    //! Get the fabric stage holding this UsdAttribute.
    //! @return Return a pointer to the fabric stage that contains this attribute.
    UsdStageRefPtr GetStage() const;

    //! Get the prim associated with this attribute on the existing fabric stage.
    //! @return Return a pointer to the prim that has this attribute.
    UsdPrim GetPrim() const;

    //! Get this attribute's name.
    //! @return Return this attributes name as a TfToken.
    const TfToken GetName() const;

    //! Get the path to this attribute.
    //! @return Return the SdfPath path to this attribute.
    SdfPath GetPath() const;

    //! Get the path to the prim that has this attribute.
    //! @return Return the SdfPath to the prim that has this attribute.
    const SdfPath GetPrimPath() const;

    //! Check if this attribute is valid. See UsdAttribute::IsValid.
    //! @return Return true if this attribute is valid, and false otherwise.
    explicit operator bool() const;

    // --------------------
    // UsdProperty methods
    // --------------------

    //! Get this property's name with all namespace prefixes removed.
    //! @return Return this property's name with all namespace prefixes removed as a TfToken.
    TfToken GetBaseName() const;

    //! Get this property's complete namespace prefix.
    //! @return Return this property's complete namespace prefix as a TfToken.
    //! Empty token if not a namespaced property.
    TfToken GetNamespace() const;

    //! Get this property's name elements including namespaces and its base name as the final element.
    //! @return this property's name elements including namespaces and its base name as the final element.
    std::vector<std::string> SplitName() const;

    // ---------------------------------
    // Querying and Editing Connections
    // ---------------------------------

    //! Add @p source to list of connections based on the specified UsdListPosition heuristic.
    //!
    //! @note Multiple connection sources not supported in fabric. Adding a new source
    //! to will override any previously set source.
    //!
    //! @param source SdfPath to the new connection to add.
    //! @param position UsdListPosition heuristic for where to add the new connection.
    //! This is ignored for now since fabric does not support a list of sources.
    //! @return Return true if the new connection source has been set. False otherwise.
    bool AddConnection(const SdfPath& source, UsdListPosition position = UsdListPositionBackOfPrependList) const;

    //! Remove @p source from the list of connections.
    //!
    //! @note Note. Multiple connection sourced not supported in fabric. The requested source to remove
    //! must match the current set value. Trying to remove a source that does not match current is a no-op.
    //!
    //! @param source SdfPath to the connection to remove. This must match the current set connection value.
    //! @return Return true if the connection has been removed. False otherwise.
    bool RemoveConnection(const SdfPath& source) const;


    //! Clear all connections.
    //! TODO oops we didn't implement this...
    //! have this call remove connection
    bool BlockConnections() const;

    //! Explicitly set a new list of connection sources.
    //!
    //! @note Multiple sources not supported in fabric. For now, only a vector of size 1 is accepted.
    //!
    //! @param sources A vector of SdfPaths to set as the new list of connections. Only a vector of size 1 is accepted.
    //! @return Return true if the new connection source has been set. False otherwise.
    bool SetConnections(const SdfPathVector& sources) const;

    //! Remove all targets from the list of connections.
    //!
    //! @note Note. Multiple connection sourced not supported in fabric. This assumes one connection.
    //!
    //! @return Return true if the connection has been removed. False otherwise.
    bool ClearConnections() const;

    //! Get a list of connection sources.
    //!
    //! @note Multiple sources not supported in fabric. Result @p sources will be a vector of size 1.
    //!
    //! @param[out] sources The list of connections as an SdfPathVector. Result will be a vector of size 1.
    //! @return Return true if the list of connections has been successfully fetched. False otherwise.
    bool GetConnections(SdfPathVector* sources) const;

    //! Check if this attribute has any authored connections.
    //!
    //! @note This diverges from the USD behavior. USD checks for
    //! authored opinions that add or remove connections in the current
    //! edit target layer. These concepts don't apply to Fabric, so we only
    //! check if there is currently a connection set.
    //!
    //! @return Return true if this attribute has any authored conneections.
    bool HasAuthoredConnections() const;

    // --------------------
    // Fabric CPU / GPU helers
    // --------------------

    //! Check if Fabric CPU data is currently valid
    //!
    //! @returns true if CPU memory for this attribute value is valid
    bool IsCpuDataValid() const;

    //! Check if Fabric GPU data is currently valid
    //!
    //! @returns true if GPU memory for this attribute value is valid
    bool IsGpuDataValid() const;

    //! Force a sync to GPU memory from CPU memory
    //!
    //! Causes Fabric to synchronize data from CPU to
    //! GPU if GPU data is not currently valid.
    //! For debugging and testing.
    //!
    //! @returns true if GPU data was made valid
    bool SyncDataToGpu() const;

    //! Force a sync to CPU memory from GPU memory
    //!
    //! Causes Fabric to synchronize data from GPU to
    //! CPU if CPU data is not currently valid.
    //! For debugging and testing.
    //!
    //! @returns true if CPU data was made valid
    bool SyncDataToCpu() const;

    //! Invalidate GPU data
    //!
    //! Gets a write handle to CPU data, causing
    //! Fabric to mark GPU data as invalid.
    //!
    //! For debugging and testing.
    //!
    //! @returns true if GPU data was made invalid
    bool InvalidateGpuData() const;

    //! Invalidate CPU data
    //!
    //! Gets a write handle to GPU data, causing
    //! Fabric to mark CPU data as invalid.
    //!
    //! For debugging and testing.
    //!
    //! @returns true if CPU data was made invalid
    bool InvalidateCpuData() const;

    //! @private
    omni::core::ObjectPtr<usdrt::IRtAttribute> m_attribute;
};

//! @class UsdRelationship
//!
//! @brief A UsdRelationship creates dependencies between scenegraph objects by
//! allowing a prim to @em target other prims, attributes, or relationships
class UsdRelationship
{
public:
    //! Add @p target to list of targets based on the specified UsdListPosition heuristic.
    //!
    //! @param target SdfPath to the new target to add.
    //! @param position UsdListPosition heuristic for where to add the new target in the list.
    //! @return Return true if the new target has been set. False otherwise.
    bool AddTarget(const SdfPath& target, UsdListPosition position = UsdListPositionBackOfPrependList) const;

    //! Remove @p target from list of targets based.
    //!
    //! @param target SdfPath to the target to remove.
    //! @return Return true if the target has been removed or if it did not exist
    //! in the list of targets. False otherwise.
    bool RemoveTarget(const SdfPath& target) const;

    //! Explicitly set a new list of targets for this relationship.
    //!
    //! @param targets A vector of SdfPaths to set as the new list of targets.
    //! @return Return true if the list of targets has been set, and false otherwise.
    bool SetTargets(const SdfPathVector& targets) const;

    //! Remove all targets from this relationship.
    //!
    //! @param removeSpec This argument is ignored. Usdrt does not have prim specs.
    //! @return Return true if the list of targets has been set to empty.
    bool ClearTargets(bool removeSpec) const;

    //! Get a list of targets for this relationship.
    //!
    //! @param[out] targets The list of targets as an SdfPathVector.
    //! @return Return true if the targets have been fetched. False otherwise.
    bool GetTargets(SdfPathVector* targets) const;

    //! Get a list of targets for this relationship.
    //!
    //! @note Fabric does not resolve forwarded targets. This is equivalent to UsdRelationship::GetTargets.
    //!
    //! @param[out] targets The list of targets as an SdfPathVector.
    //! @return Return true if the targets have been fetched. False otherwise.
    bool GetForwardedTargets(SdfPathVector* targets) const;

    //! Check if this relationship has any authored targets.
    //!
    //! @note This diverges from the USD behavior. USD checks for
    //! authored opinions that add or remove targets in the current
    //! edit target layer. These concepts don't apply to Fabric, so we only
    //! check if there is currently at least one target set.
    //!
    //! @return Return true if this relationship has any authored targets.
    bool HasAuthoredTargets() const;

    // --------------------
    // UsdObject methods
    // --------------------

    //! Check if the relationship is valid (i.e exists in fabric).
    //! @return Return true if the attribute exists in fabric, and false otherise.
    bool IsValid() const;

    //! Get the fabric stage holding this UsdRelationship.
    //! @return Return a pointer to the fabric stage that contains this attribute.
    UsdStageRefPtr GetStage() const;

    //! Get the prim associated with this relationship on the existing fabric stage.
    //! @return Return a pointer to the prim that has this relationship.
    UsdPrim GetPrim() const;

    //! Get this relationship's name.
    //! @return Return this relationship name as a TfToken.
    const TfToken GetName() const;

    //! Get the path to this relationship.
    //! @return Return the SdfPath path to this relationship.
    SdfPath GetPath() const;

    //! Get the path to the prim that has this relationship.
    //! @return Return the SdfPath to the prim that has this relationship.
    const SdfPath GetPrimPath() const;

    //! Check if this relationship is valid. See UsdRelationship::IsValid.
    //! @return Return true if this relationship is valid, and false otherwise.
    explicit operator bool() const;

    // --------------------
    // UsdProperty methods
    // --------------------

    //! Get this property's name with all namespace prefixes removed.
    //! @return Return this property's name with all namespace prefixes removed as a TfToken.
    TfToken GetBaseName() const;

    //! Get this property's complete namespace prefix.
    //! @return Return this property's complete namespace prefix as a TfToken.
    //! Empty token if not a namespaced property.
    TfToken GetNamespace() const;

    //! Get this property's name elements including namespaces and its base name as the final element.
    //! @return this property's name elements including namespaces and its base name as the final element.
    std::vector<std::string> SplitName() const;

    //! @private
    omni::core::ObjectPtr<usdrt::IRtRelationship> m_relationship;
};

//! @class UsdPrimRange
//!
//! @brief a forward-iterable range that traverses a subtree of prims rooted at a
//! given prim in depth-first order.
//!
//! @note post-visit iterators not yet supported.
//!
//! @note The number of prims in the range differs slightly when using Fabric Scene Delegate
//! as `geomSubsets` are not represented as prims.
class UsdPrimRange
{
public:
    //! @struct iterator
    //! A forward iterator into a UsdPrimRange.
    struct iterator
    {
        using iterator_category = std::input_iterator_tag;
        using difference_type = std::ptrdiff_t;
        using value_type = UsdPrim;
        using pointer = UsdPrim*;
        using reference = UsdPrim&;

        iterator();
        iterator(omni::core::ObjectPtr<usdrt::IRtPrimRange> primRange);

        //! Behave as if the current prim has no children when next advanced.
        void PruneChildren();

        reference operator*();
        pointer operator->();
        iterator& operator++();
        iterator operator++(int);

#ifndef DOXYGEN_BUILD
        friend bool operator==(const iterator& lhs, const iterator& rhs);
        friend bool operator!=(const iterator& lhs, const iterator& rhs);
#endif // DOXYGEN_BUILD

    private:
        omni::core::ObjectPtr<usdrt::IRtPrimRange> m_primRange;
        UsdPrim m_startPrim;
        UsdPrim m_currentPrim;
        bool m_atEnd;
    };

    UsdPrimRange(){};

    //! Create a PrimRange that traverses the subtree rooted at \p start in
    //! depth-first order.
    //! @param start UsdPrim to use as root of traversal.
    UsdPrimRange(const UsdPrim& start);

    //! Return an iterator to the start of this range.
    iterator begin() const;

    //! Return a past-the-end iterator to the end of this range.
    iterator end() const;

    //! Check if this range is empty.
    //! @returns Return true if this range contains no prims, and false otherwise.
    bool empty() const;

    //! @returns Return true if this range contains one or more prims, false otherwise.
    explicit operator bool() const;

    //! Start prim for iteration
    UsdPrim m_startPrim;
};

//! @class UsdSchemaBase
//!
//! Base class for all Usd Schemas.
//! Schema objects hold a UsdPrim m_prim and an SdfPath m_primPath
//! and provide an additional layer of specific API.
//!
//!@section Usd_Create_Or_Get_Property Create vs Get Property Methods
//!
//! For a UsdAttribute named "points" defined in a schema class, you will
//! find two access methods in the schema class in C++ and python:
//!\li GetPointsAttr()
//!\li CreatePointsAttr()
//!
//! GetPointsAttr() returns a UsdAttribute and is used in read-only cases.
//!
//! CreatePointsAttr() returns a UsdAttribute, and also creates it on the
//! prim if it doesn't exist. There is no change if the attribute already exists.
class UsdSchemaBase
{
public:
    //! Construct and store \p prim as the held prim.
    //! @param prim The help prim in this schema.
    explicit UsdSchemaBase(const UsdPrim& prim = UsdPrim());
    //! Construct and store for the same prim held by \p otherSchema
    //! @param otherSchema Other schema to copy.
    explicit UsdSchemaBase(const UsdSchemaBase& otherSchema);
    //! Destructor.
    virtual ~UsdSchemaBase();
    //! Return this schema object's held prim.
    UsdPrim GetPrim() const;
    //! Return the SdfPath to this schema object's held prim.
    SdfPath GetPath() const;

    //! Compile time constant representing what kind of schema this class is.
    //! @sa See UsdSchemaType in usd/common.h
    static const UsdSchemaType schemaType = UsdSchemaType::AbstractBase;

    //! Return the type of schema this class is.
    //! @sa UsdSchemaBase::schemaType
    //! @note This diverges from Usd and returns a TfToken, since we don't implement TfType.
    static const TfToken _GetStaticTfType()
    {
        const static TfToken token("UsdSchemaBase");
        return token;
    }

    //! Check if this schema object is compatible with it's held prim and that the prim is valid.
    //!
    //! A typed schema object is compatible if the held prim's type is or
    //! is a subtype of the schema's type. Based on `prim.IsA()`.
    //!
    //! An API schema object is compatible if the API is of type SingleApplyAPI or
    //! UsdSchemaType::MultipleApplyAPI, and the schema has been applied to the prim. Based on `prim.HasAPI`.
    //!
    //! This method invokes polymorphic behaviour.
    //!
    //! @returns True if the help prim is valid, and the schema object is compatible with its held prim.
    //!
    //! @sa UsdSchemaBase::_IsCompatible()
    //!
    explicit operator bool() const
    {
        return m_prim.IsValid() && _IsCompatible();
    }

protected:
    //! Helper for subclasses to do specific compatibility
    //! checking with the given prim. Subclassess may override
    //! `_isCompatible` to for example check type compatibility or value
    //! compatibility on the prim.
    //!
    //! Overrides exist for UsdTyped and UsdAPISchemaBase.
    //!
    //! This check is called when clients invoke the bool operator.
    //! @returns True if the schema object is compatible with its held prim.
    virtual bool _IsCompatible() const;

    //! Helper for subclasses to get this schema's type token
    //! @returns The token representing the schema's TfType.
    //! @note This diverges from Usd and returns a TfToken, since we don't implements TfType.
    const TfToken _GetType() const
    {
        return _GetTfTypeToken();
    }

private:
    // The held prim and prim path.
    UsdPrim m_prim;
    SdfPath m_primPath;

    // Override implemented by schema code gen in each schema class.
    virtual const TfToken _GetTfTypeToken() const;
    mutable TfToken _tfTypeToken;
};

//! @class UsdTyped
//!
//! @brief The base class for all @em typed schemas, and therefore
//! the base class for all instantiable and "IsA" schemas.
class UsdTyped : public UsdSchemaBase
{
public:
    //! Construct a UsdTyped on UsdPrim @p prim.
    //! @param prim The held prim. Default UsdPrim().
    explicit UsdTyped(const UsdPrim& prim = UsdPrim()) : UsdSchemaBase(prim)
    {
    }

    //! Construct a UsdTyped on the prim wrapped by @p schema.
    //! @param schema The given schema.
    explicit UsdTyped(const UsdSchemaBase& schema) : UsdSchemaBase(schema)
    {
    }

    //! Compile time constant representing what kind of schema this class is.
    //! @sa See UsdSchemaType in usd/common.h
    static const UsdSchemaType schemaType = UsdSchemaType::AbstractBase;

    //! @private
    static const TfToken _GetStaticTfType()
    {
        const static TfToken token("UsdTyped");
        return token;
    }

protected:
    bool _IsCompatible() const
    {
        if (!UsdSchemaBase::_IsCompatible())
            return false;
        return GetPrim().IsA(_GetType());
    }


private:
    const TfToken _GetTfTypeToken() const override
    {
        const static TfToken token("UsdTyped");
        return token;
    }
};


} // namespace usdrt
