// Copyright (c) 2023-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
//
// This ABI is unstable and subject to change
/*  _    _  _____ ______         _______  __     ______  _    _ _____     ______          ___   _   _____  _____  _____ _  __
   | |  | |/ ____|  ____|     /\|__   __| \ \   / / __ \| |  | |  __ \   / __ \ \        / / \ | | |  __ \|_   _|/ ____| |/ /
   | |  | | (___ | |__       /  \  | |     \ \_/ / |  | | |  | | |__) | | |  | \ \  /\  / /|  \| | | |__) | | | | (___ | ' / 
   | |  | |\___ \|  __|     / /\ \ | |      \   /| |  | | |  | |  _  /  | |  | |\ \/  \/ / | . ` | |  _  /  | |  \___ \|  <  
   | |__| |____) | |____   / ____ \| |       | | | |__| | |__| | | \ \  | |__| | \  /\  /  | |\  | | | \ \ _| |_ ____) | . \
    \____/|_____/|______| /_/    \_\_|       |_|  \____/ \____/|_|  \_\  \____/   \/  \/   |_| \_| |_|  \_\_____|_____/|_|\_|
*/

#pragma once

#include <omni/graph/core/iComputeGraph.h>

namespace omni
{
namespace graph
{
namespace core
{
namespace unstable
{


// ======================================================================
// Support for attribute templates types
class AttributeTemplateHandle : public HandleBase<HandleInt, AttributeTemplateHandle>
{
public:
    using BaseHandleType = HandleInt;
    using HandleBase<HandleInt, AttributeTemplateHandle>::HandleBase;

    static constexpr HandleInt invalidValue()
    {
        return 0;
    }
};


struct IAttributeTemplate;
struct AttributeTemplateObj
{
    const IAttributeTemplate* iAttributeTemplate;
    AttributeTemplateHandle attributeTemplateHandle;

    bool isValid() const
    {
        return attributeTemplateHandle.isValid();
    }
};

/**
 * Structure with information about the default data stored
 * in an attribute template
 */
struct AttributeTemplateDefaultData
{
    // Pointer to the data. 
    const uint8_t* dataPtr;

    // The size of a single item in the array. For tuples, this represents the size of the tuple. 
    size_t itemSizeInBytes;

    // The number of items stored. For scalars and tuples this is always 1, otherwise it is the number of elements
    // in the array. 
    size_t elementCount;
};

/**
 * Carb interface representing an attribute template. An AttributeTemplate is the definition used
 * to create an attribute on a Node when created from a NodeType.
 *
 */
struct IAttributeTemplate
{
    CARB_PLUGIN_INTERFACE("omni::graph::core::unstable::IAttributeTemplate", 0, 2);

    /**
     * Returns the name of the attribute template, which includes any namespace prefixes prepended
     * by the NodeType. 
     *
     * @param[in] attributeObj. The attribute template to inspect
     * @returns Retreives the name of the attribute template wit
     */
    const char*(CARB_ABI* getName)(const AttributeTemplateObj& attributeObj);

    /**
     * Returns a string of the typename that will be used when creating the attribute.
     *
     * For extended attribute types, this will return "token". 
     * @see IAttribute::getTypeName
     * @param[in] attributeObj. The attribute template to inspect
     * @return The type name of the attribute template.
     */
    const char*(CARB_ABI* getTypeName)(const AttributeTemplateObj& attributeObj);

    /**
     * Gets the AttributePortType of the attribute template. Use this to check whether
     * an attribute template is an input, output, or state.
     *
     * @param[in] attributeObj. The attribute template to inspect
     * @return The AttributePortType of the attribute template.
     */
    AttributePortType(CARB_ABI* getPortType)(const AttributeTemplateObj& attributeObj);

    /**
     * Returns the extended type, if any, of the attribute template. Extended types are values such as "union" 
     * and "any" that indicate an attribute template can hold a set of different type.
     *
     * @param[in] attributeObj Reference to the AttributeTemplateObj representing the attribute template.
     * @return The extended type of the attribute template.
     */
    ExtendedAttributeType(CARB_ABI* getExtendedAttributeType)(const AttributeTemplateObj& attributeObj);

    /**
     * Returns the type of the attribute template object. If the extended type is 
     * kExtendedAttributeType_Regular, this will return the assigned type to the port,
     * otherwise it will return type representing an unknown type to indicate multiple values exist.
     *
     * To fetch all support types, use getExtendedAttributeTypes.
     * 
     * @param[in] attributeObj Reference to the AttributeTemplateObj representing the attribute template.
     * @return The type of the attribute template.
     */
    omni::graph::core::Type(CARB_ABI* getAttributeType)(const AttributeTemplateObj& attributeObj);


    /**
     * Returns the number of compatible types with an attribute template. If the extended type is a union type,
     * returns the number of concrete types available.If the extended type is a regular type, this always
     * returns 1. If is an "any", this will always return 0.
     *
     * @param[in] attributeObj Reference to the AttributeTemplateObj representing the attribute template.
     * @return The number of compatible types
     */
    size_t(CARB_ABI* getExtendedAttributeTypeCount)(const AttributeTemplateObj& attributeObj);

    /**
     * Returns the list of compatible types. Note that 0 types are returned if the attribute template
     * extended type is "any". 
     *
     * @param[in] attributeObj Reference to the AttributeTemplateObj representing the attribute template.
     * @param[out] typeBuffer A buffer to store the compatible types.
     * @param[in] typeBufferCount The number of types that can be stored in typeBuffer. 
     * @return The number of compatible types copied to typeBuffer.
     */
    size_t(CARB_ABI* getExtendedAttributeTypes)(const AttributeTemplateObj& attributeObj,
                                                omni::graph::core::Type* typeBuffer,
                                                size_t typeBufferCount);

    /**
     * Sets the extended type of the attribute. Note that this may clear any default data for the type,
     * as default data is only valid Regular typed attribute templates.
     *
     * When setting the extended type to be a regular type, use the setType function instead.
     * 
     * @param[in] attributeObj Reference to the AttributeTemplateObj representing the attribute template.
     * @param[in] attributeType The ExtendedAttributeType to change the template to. 
     * @param[in] typeList For union types, a comma separated list of union names or types to support. 
     */
    void(CARB_ABI* setExtendedType)(const AttributeTemplateObj& attributeObj,
                                    ExtendedAttributeType attributeType,
                                    const char* typeList);

    /**
     * Sets the attribute template to use a regular (non-extended) type.
     * 
     *
     * @param[in] attributeObj Reference to the AttributeTemplateObj representing the attribute template.
     * @param[in] attributeType The type to set.
     * @param[in] defaultValuePtr Pointer to default data to set on this type. Can be null to indicate
     *                            no default data.
     * @param[in] defaultElemCount If the type is an array type, this is the number of items. It is ignored for
     *                             scalar types.
     */
    void(CARB_ABI* setType)(const AttributeTemplateObj& attributeObj,
                            omni::graph::core::Type attributeType,
                            const void* defaultValuePtr,
                            size_t defaultElemCount);

    /**
     * If an attribute template is a compound node type, make the template expose an attribute on the associated compound graph. 
     * If the attribute template is an output, only one connection is supported, and this will overwrite the connection.
     * If the attribute template is an input, this will append to the current list of connections. 
     *
     * The connection must be on a child node of the graph template of the compound node type.
     * 
     * @param[in] attributeObj Reference to the AttributeTemplateObj representing the attribute template.
     * @param[in] path. The path to attribute to connect to.
     * @returns True if the connection was successfully set, false otherwise. 
     */
    bool(CARB_ABI* connectByPath)(const AttributeTemplateObj& attributeObj, const omni::fabric::PathC& path);

    /**
     * Disconnect all connections from the attribute template. Only works if the attribute template is
     * part of a compound node type
     * 
     * @param[in] attributeObj Reference to the AttributeTemplateObj representing the attribute template.
     */
    void(CARB_ABI* disconnectAll)(const AttributeTemplateObj& attributeObj);

    /**
     * Disconnect an attribute from the attribute template. Only applies if the attribute template is
     * part of a compound node type.
     *
     * @param[in] attributeObj Reference to the AttributeTemplateObj representing the attribute template.
     * @param[path] path The path to disconnect.
     * @returns True if the path was found and disconnected, false otherwise. 
     */
    bool(CARB_ABI* disconnectByPath)(const AttributeTemplateObj& attributeObj, const omni::fabric::PathC& path);

    /**
     * Retrieves the number of connections for an attribute template. Only applies if the attribute template is
     * part of a compound node type.
     * 
     * @param[in] attributeObj Reference to the AttributeTemplateObj representing the attribute template.
     */
    size_t(CARB_ABI* getConnectionCount)(const AttributeTemplateObj& attributeObj);

    /**
     * Retrieves the connections for an attribute template. Only applies if the attribute template is part of a
     * compound node type. 
     *
     * @param[in] attributeObj Reference to the AttributeTemplateObj representing the attribute template.
     * @param[out] pathsBuffer Pointer a buffer to store the paths
     * @param[in] pathBufferCount The number of paths that can be stored in pathsBuffer.
     */
    size_t(CARB_ABI* getConnections)(const AttributeTemplateObj& attributeObj,
                                     omni::fabric::PathC* pathsBuffer,
                                     size_t pathBufferCount);

    /**
     * Returns the number of metadata entries on this attribute template.
     *
     * @param[in] attributeObj Reference to the AttributeTemplateObj representing the attribute template.
     * @return the number of metadata key/value pairs on this attribute
     */
    size_t(CARB_ABI* getMetadataCount)(const AttributeTemplateObj& attributeObj);


    /**
     * Returns the set of all metadata on this attribute template.
     *
     * The keyBuf and valueBuf arrays preallocated by the caller, and contain at least "getMetadataCount()"
     * entries in them.
     * All returned strings are owned by the node type and not to be destroyed.
     * The returned keyBuf and valueBuf must have exactly the same size with corresponding index values; that is
     * keyBuf[i] is the metadata name for the string in valueBuf[i].
     *
     * @param[in] attributeObj Reference to the AttributeTemplateObj representing the attribute template.
     * @param[out] keyBuf Buffer in which to put the list of metadata keys
     * @param[out] valueBuf Buffer in which to put the list of metadata values
     * @param[in] bufferSize the number of strings each of the two buffers is able to hold
     * @return Number of metadata items successfully populated
     */
    size_t(CARB_ABI* getAllMetadata)(const AttributeTemplateObj& attributeObj,
                                     const char** keyBuf,
                                     const char** valueBuf,
                                     size_t bufferSize);
    
    /**
     * Retrieves a metadata value from this attribute
     *
     * @param[in] attributeObj Reference to the AttributeTemplateObj representing the attribute template.
     * @param[in] key The name of the metadata to be retrieved
     * @return The value of the metadata, or nullptr if the named metadata was not set on this attribute
     */
    const char*(CARB_ABI* getMetadata)(const AttributeTemplateObj& attributeObj, const char* key);


    /**
     * Sets a metadata value on this attribute template. Metadata applied to an AttributeTemplate does
     * not apply to the underlying USD attribute itself, but will be applied to any corresponding
     * attributes that are created from it. 
     *
     * @param[in] attrObj Reference to the attribute template..
     * @param[in] key The keyword, used as the name of the metadata. Cannot be null.
     * @param[in] value The value of the metadata. Only string values are supported. if null, clears the existing
     *                  metadata with the given key
     * @return true if the keyword was successfully set
     */
    bool(CARB_ABI* setMetadata)(const AttributeTemplateObj& attrObj, const char* key, const char* value);


   /** Retrieves a readonly memory buffer containing the default data set on this attribute templates.
     * If there is no default data set then nullptr will be returned. 
     *
     * @param[in] attributeObj Reference to the AttributeTemplateObj representing the attribute template.
     * @return Structure containing the raw data storing the default value and information about the memory stored.
     * The data format will change depending on the value returned by getAttributeType(). 
     */
    AttributeTemplateDefaultData(CARB_ABI* getDefaultData)(const AttributeTemplateObj& attributeObj);
};

STRUCT_INTEGRITY_CHECK(IAttributeTemplate, getDefaultData, 18);


}
}
}
}
