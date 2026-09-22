// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once
#include <omni/graph/core/iComputeGraph.h>

#include <carb/Defines.h>
#include <carb/Interface.h>
#include <carb/Types.h>

#include <omni/graph/core/Handle.h>
#include <omni/graph/core/Type.h>
#include <omni/inspect/IInspector.h>

namespace omni {
namespace graph {
namespace core {

// ======================================================================
/**
 * @brief Interface class managing various features of attribute types
 *
 */
struct IAttributeType
{
    //! @private to avoid doxygen problems
    CARB_PLUGIN_INTERFACE("omni::graph::core::IAttributeType", 1, 4);

    /**
     * @brief Returns an attribute type object corresponding to the OGN-style type name
     *
     * The type name is assumed to contain no whitespace for efficiency, so prune it before calling if necessary.
     *
     * @param[in] ognTypeName Attribute type name in the format used by the .ogn files
     * @return The attribute type description corresponding to the type name
     */
    Type (CARB_ABI* typeFromOgnTypeName)(const char* ognTypeName);

    /**
     * @brief Returns an attribute type object corresponding to the Sdf-style type name.
     *
     * The type name is assumed to contain no whitespace for efficiency, so prune it before calling if necessary.
     * Note that some types cannot be expressed in this form (e.g. the extended types such as "union" and "any", and
     * OGn-only types such as "bundle") so where possible use the typeFromOgnTypeName() method.
     *
     * @param[in] sdfTypeName Attribute type name in the format used by pxr::SdfValueTypeNames
     * @return The attribute type description corresponding to the type name
     */
    Type (CARB_ABI* typeFromSdfTypeName)(const char* sdfTypeName);

    /**
     * @brief Returns the size of the base data (without tuples or array counts) for the given attribute type
     *
     * @param[in] type Attribute type whose size is to be returned
     * @return Size of the base data stored by the attribute type, 0 if none is stored
     */
    size_t (CARB_ABI* baseDataSize)(Type const& type);

    /**
     * @brief Runs the inspector on the attribute data with the given type.
     *
     * @param[in] type The attribute type of the raw data
     * @param[in] data Pointer to the raw data of the given type.
     * @param[in] elementCount Number of array elements in the data (1 if not an array)
     * @param[in] inspector The inspector class
     * @return true if the inspection ran successfully, false if the inspection type is not supported
     */
    bool(CARB_ABI* inspect)(Type const& type, void const* data, size_t arrayElementCount, inspect::IInspector* inspector);

    /**
     * @brief Returns the SdfValueTypeName corresponding to the given type.
     *
     * @note Not all OGN Types are fully represented in the Sdf schema since they have additional semantics in OGN
     *       which do not exist in USD. In that case the SdfValueTypeName of the base type will be returned, which is
     *       what is used to serialize the attribute.
     *
     * For example Type(BaseDataType::UInt64, 1, 0, AttributeRole::eObjectId) is an OGN "objectId" which will
     * return just "uint64" from this function.
     *
     * @param[in] type The Type in question
     * @return The token of the corresponding SdfTypeName
     */
    NameToken(CARB_ABI* sdfTypeNameFromType)(Type const& type);

    /**
     * @brief Checks to see if the Type passed in corresponds to a legal OGN type.
     *
     * @param[in] type Type to be checked
     * @return true if the Type can be fully represented by OGN
     * @return false if the Type does not correspond exactly to an OGN type
     *
     */
    bool(CARB_ABI* isLegalOgnType)(Type const& type);

    /**
     * @brief Retrieves the number of attribute unions.
     *
     * @return The number of attribute union types.
     */
    size_t(CARB_ABI* getUnionTypeCount)();

    /**
     * @brief Retrieves the name of the available union types
     *
     * @param[in] buffer       The array of pointers to fill in with names of the union types.
     *                         The values returned are only valid while the list of unions is not changing.
     * @param[in] bufferSize   The number of entries to retrieve. Use getUnionTypeCount to retrieve the number
     *                         available.
     * @return    The number of entries written to buffer.
     *
     */
    size_t(CARB_ABI* getUnionTypes)(const char** buffer, size_t bufferSize);

    /**
     * @brief Retrieves the number of entries for the attribute union of the given name
     *
     * @param[in] unionType The name of the attribute union to retrieve.
     * @return The number of entries associated with unionType. If unionType is not valid, 0 is returned.
     *
     */
    size_t(CARB_ABI* getUnionTypeEntryCount)(const char* unionType);

    /**
     * @brief Gets the list of ogn type names associated with an attribute union.
     *
     * The list of returned types is fully expanded. This means if an attribute union is defined in terms
     * of other attributes unions, the entries returned will have recursively expanded each entry and the
     * final list will only contain ogn type names and not other attribute unions names.
     *
     * @param[in] unionType The name of the attribute union to retrieve.
     * @param[in] buffer    The array of pointers to fill in with names of the ogn types names.
     *                      The values returned are only valid while the list of unions is not changing.
     * @param[in] bufferSize The number of entries to retrieve. Use getUnionTypeEntryCount to find the maximum available.
     * @return The number of items written to buffer. If unionType is not valid, 0 is returned.
     *
     */
    size_t(CARB_ABI* getUnionTypeEntries)(const char* unionType, const char** buffer, size_t bufferSize);
};
// Update this every time a new ABI function is added, to ensure one isn't accidentally added in the middle
STRUCT_INTEGRITY_CHECK(IAttributeType, getUnionTypeEntries, 9)


} // namespace core
} // namespace graph
} // namespace omni
