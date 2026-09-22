// Copyright (c) 2022-2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/graph/core/Handle.h>

namespace omni
{
namespace graph
{
namespace core
{

// ======================================================================
/** Interface for bundle attribute data */
struct IBundle
{
    //! @private to avoid doxygen problems
    CARB_PLUGIN_INTERFACE("omni::graph::core::IBundle", 1, 7);

    /**
     * Counts the number of attributes contained in the bundle.
     *
     * @param[in] contextObj The context to which the bundle belongs
     * @param[in] bundle The handle to the bundle data
     * @return the number of attributes in the bundle
     */
    size_t(CARB_ABI* getAttributesCount)(const GraphContextObj& contextObj, ConstBundleHandle bundle);

    /**
     * Get all of the attributes on the bundle in read-only form.
     *
     * @param[out] attrsOut Handles to the attributes on the bundle (preallocated to hold "count" members)
     * @param[in] contextObj The context to which the bundle belongs
     * @param[in] bundle The handle to the bundle data
     * @param[in] count The number of attribute slots allocated in attrsOut (should be >= getAttributesCount())
     */
    void(CARB_ABI* getAttributesR)(ConstAttributeDataHandle* attrsOut,
                                   const GraphContextObj& contextObj,
                                   ConstBundleHandle bundle,
                                   size_t count);

    /**
     * Get all of the attributes on the bundle in writable form.
     *
     * @param[out] attrsOut Handles to the attributes on the bundle (preallocated to hold "count" members)
     * @param[in] contextObj The context to which the bundle belongs
     * @param[in] bundle The handle to the bundle data
     * @param[in] count The number of attribute slots allocated in attrsOut (should be >= getAttributesCount())
     */
    void(CARB_ABI* getAttributesW)(AttributeDataHandle* attrsOut,
                                   const GraphContextObj& contextObj,
                                   BundleHandle bundle,
                                   size_t count);

    /**
     * Get attributes on the bundle whose names appear in "attrNames" in read-only form.
     *
     * @param[out] attrsOut Handles to the attributes on the bundle (preallocated to hold "count" members)
     * @param[in] contextObj The context to which the bundle belongs
     * @param[in] bundle The handle to the bundle data
     * @param[in] attrNames The list of attribute names to be looked up
     * @param[in] count The number of attribute slots allocated in attrsOut (should be >= getAttributesCount())
     */
    void(CARB_ABI* getAttributesByNameR)(ConstAttributeDataHandle* attrsOut,
                                         const GraphContextObj& contextObj,
                                         ConstBundleHandle bundle,
                                         const NameToken* attrNames,
                                         size_t count);
    /**
     * Get attributes on the bundle whose names appear in "attrNames" in writable form.
     *
     * @param[out] attrsOut Handles to the attributes on the bundle (preallocated to hold "count" members)
     * @param[in] contextObj The context to which the bundle belongs
     * @param[in] bundle The handle to the bundle data
     * @param[in] attrNames The list of attribute names to be looked up
     * @param[in] count The number of attribute slots allocated in attrsOut (should be >= getAttributesCount())
     */
    void(CARB_ABI* getAttributesByNameW)(AttributeDataHandle* attrsOut,
                                         const GraphContextObj& contextObj,
                                         BundleHandle bundle,
                                         const NameToken* attrNames,
                                         size_t count);

    /**
     * Get the names and types of all attributes on the bundle.
     *
     * @param[out] namesOut Handles to the names of attributes on the bundle (preallocated to hold "count" members)
     * @param[out] typesOut Handles to the types of attributes on the bundle (preallocated to hold "count" members)
     * @param[in] contextObj The context to which the bundle belongs
     * @param[in] bundle The handle to the bundle data
     * @param[in] count The number of attribute slots allocated in attrsOut (should be >= getAttributesCount())
     */
    void (CARB_ABI* getAttributeNamesAndTypes)(NameToken* namesOut,
                                               Type* typesOut,
                                               const GraphContextObj& contextObj,
                                               ConstBundleHandle bundle,
                                               size_t count);

    /**
     * Create a new attribute and add it to the bundle.
     *
     * @param[in] contextObj The context to which the bundle belongs
     * @param[in] destination The handle to the bundle data
     * @param[in] attrName Name for the new attribute
     * @param[in] attrType Type for the new attribute
     * @return Handle to the newly created attribute
     */
    AttributeDataHandle(CARB_ABI* addAttribute)(const GraphContextObj& contextObj,
                                                BundleHandle destination,
                                                NameToken attrName,
                                                Type attrType);

    /**
     * Create a new attribute and add it to the bundle.
     *
     * @param[in] contextObj The context to which the bundle belongs
     * @param[in] destination The handle to the bundle data
     * @param[in] pattern Attribute whose name and type is to be copied for the new attribute
     * @return Handle to the newly created attribute
     */
    AttributeDataHandle(CARB_ABI* addAttributeLike)(const GraphContextObj& contextObj,
                                                    BundleHandle destination,
                                                    ConstAttributeDataHandle pattern);

    /**
     * Create a new array attribute and add it to the bundle.
     *
     * @param[in] contextObj The context to which the bundle belongs
     * @param[in] destination The handle to the bundle data
     * @param[in] attrName Name for the new attribute
     * @param[in] attrType Type for the new attribute
     * @param[in] elementCount Starting element count for the array attribute
     * @return Handle to the newly created attribute
     */
    AttributeDataHandle(CARB_ABI* addArrayAttribute)(const GraphContextObj& contextObj,
                                                     BundleHandle destination,
                                                     NameToken attrName,
                                                     Type attrType,
                                                     size_t elementCount);

    /**
     * Create a new array-of-arrays attribute and add it to the bundle.
     *
     * Note: At the moment only arrays and arrays-of-tuples are fully supported so use with caution
     *
     * @param[in] contextObj The context to which the bundle belongs
     * @param[in] destination The handle to the bundle data
     * @param[in] attrName Name for the new attribute
     * @param[in] baseType Base data type for the new attribute
     * @param[in] numComponents Number of tuple elements for the new attribute (e.g. 3 for float[3])
     * @param[in] numArrays How many levels of arrays are on the attribute (currently only 1 is supported)
     * @param[in] ... Variadic list containing the starting element count for each level of array
     * @return Handle to the newly created attribute
     */
    AttributeDataHandle(CARB_ABI* addArrayOfArraysAttribute)(const GraphContextObj& contextObj,
                                                             BundleHandle destination,
                                                             NameToken attrName,
                                                             BaseDataType baseType,
                                                             size_t numComponents,
                                                             size_t numArrays,
                                                             ...);

    /**
     * Create a new attribute by copying an existing one, including its data, and renaming and add it to the bundle.
     *
     * @param[in] contextObj The context to which the bundle belongs
     * @param[in] destination The handle to the bundle data
     * @param[in] destinationAttrName Name for the new attribute
     * @param[in] source Handle to attribute whose data type is to be copied
     * @return Handle to the newly created attribute
     */
    void(CARB_ABI* copyAttribute)(const GraphContextObj& contextObj,
                                  BundleHandle destination,
                                  NameToken destinationAttrName,
                                  ConstAttributeDataHandle source);

    /**
     * Get the unique data ID of a bundle.
     *
     * @param[in] bundle The bundle whose ID is to be found
     * @return The unique ID of the bundle
     */
    uint64_t(CARB_ABI* getDataID)(ConstBundleHandle bundle);

    //! @cond Doxygen_Suppress
    //! Deprecated function - do not use
    [[deprecated("Use getBundlePath")]] const char*(CARB_ABI* getPrimPath)(ConstBundleHandle);
    //! @endcond

    /**
     * Remove an existing attribute from the bundle.
     *
     * @param[in] contextObj The context to which the bundle belongs
     * @param[in] destination The handle to the bundle data
     * @param[in] attrName Name of the attribute to remove
     */
    void (*removeAttribute)(const GraphContextObj& contextObj, BundleHandle destination, NameToken attrName);

    /**
     * Add a batch of attributes to a bundle.
     *
     * @param[in] contextObj The context to which the bundle belongs
     * @param[in] destination The handle to the bundle data
     * @param[in] attributeCount Number of attributes to be added
     * @param[in] attrNames Array of names for the new attributes
     * @param[in] attrTypes Array of types for the new attributes
     * @return Whether addition was successful
     */
    bool(CARB_ABI* addAttributes)(const GraphContextObj& contextObj,
                                  BundleHandle destination,
                                  size_t attributeCount,
                                  const NameToken* attrNames,
                                  const Type* attrTypes);

    /**
     * Remove a batch of attributes from a bundle.
     *
     * @param[in] contextObj The context to which the bundle belongs
     * @param[in] destination The handle to the bundle data
     * @param[in] attributeCount Number of attributes to be removed
     * @param[in] attrNames Array of names to be removed
     */
    bool(CARB_ABI* removeAttributes)(const GraphContextObj& contextObj,
                                     BundleHandle destination,
                                     size_t attributeCount,
                                     const NameToken* attrNames);


    /**
     * Copy a set of attributes from a source bundle/node to another bundle/node
     * Attributes that don't exists on the destination will be created
     * The name on the destination can differ from the one on the source
     *
     * @param[in] contextObj The context object used to find the variable data.
     * @param[in] destBundleHandle The destination node/bundle on which to copy/create the the attributes.
     * @param[in] sourceBundleHandle The source node/bundle from which to read the data.
     * @param[in] srcNames The attributes to copy
     * @param[in] dstNames Optional - the name of the destination attribute.
     *                     if nullptr, the name of input will be used
     *                     if not nullptr, lenght must be equal to namesCount
     * @param[in] namesCount Length of srcNames array (and dstNames if provided)
     *
     */
    void(CARB_ABI* copyAttributes)(const GraphContextObj& contextObj,
                                   BundleHandle destBundle,
                                   ConstBundleHandle sourceBundle,
                                   NameToken const* srcNames,
                                   NameToken const* dstNames,
                                   size_t namesCount);

    /**
     * Retrieves the path to the bundle. It will be part of the node in which it is defined.
     *
     * @param[in] bundle A handle pointing to a bundle
     * @return the bundle path
     */
    const char*(CARB_ABI* getBundlePath)(ConstBundleHandle bundle);

    /**
     * Copy a set of attributes from a source bundle/node to another bundle/node
     * Attributes that don't exists on the destination will be created
     * The name on the destination can differ from the one on the source
     *
     * @param[in] dstFabric The fabric in which the destination bundle lives.
     * @param[in] destBundleHandle The destination node/bundle on which to copy/create the the attributes.
     * @param[in] srcFabric The fabric in which the source bundle lives.
     * @param[in] sourceBundleHandle The source node/bundle from which to read the data.
     * @param[in] srcNames The attributes to copy
     * @param[in] dstNames Optional - the name of the destination attribute.
     *                     if nullptr, the name of input will be used
     *                     if not nullptr, lenght must be equal to namesCount
     * @param[in] namesCount Length of srcNames array (and dstNames if provided)
     * @param[in] includeMetaData Whether or not metadata should be copied as well
     *
     */
    void(CARB_ABI* copyAttributesWithFabric)(omni::fabric::FabricId dstFabric,
                                             BundleHandle destBundle,
                                             omni::fabric::FabricId srcFabric,
                                             ConstBundleHandle sourceBundle,
                                             NameToken const* srcNames,
                                             NameToken const* dstNames,
                                             size_t namesCount,
                                             bool includeMetaData);
};
// Update this every time a new ABI function is added, to ensure one isn't accidentally added in the middle
STRUCT_INTEGRITY_CHECK(IBundle, copyAttributesWithFabric, 18)

}
}
}
