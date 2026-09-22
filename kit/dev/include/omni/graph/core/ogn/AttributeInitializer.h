// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/graph/core/iComputeGraph.h>
#include <omni/graph/core/ogn/Types.h>

// =================================================================================================================
// This file contains simple interface classes which wrap data in the OGN database for easier use.
//
//    AttributeInitializer   Generated code uses this to store unchanging attribute information
//
// WARNING: These interfaces are subject to change without warning and are only meant to be used by generated code.
//          If you call them directly you may have to modify your code when they change.
// =================================================================================================================

namespace omni {
namespace graph {
namespace core {
namespace ogn {

// Determine if the underlying data type can be copy-constructed or if it has to use a raw memcpy
template<class DataType>
constexpr bool needs_memcpy_v = ! std::is_copy_constructible<DataType>::value;

// Copy an array into the default value, where the array elements are copy-constructible
template <typename FromDataType, typename ToDataType, std::enable_if_t<! needs_memcpy_v<std::remove_pointer_t<ToDataType>>, int> = 0>
void copyArrayValue(FromDataType from, ToDataType& to, size_t elementCount)
{
    if (elementCount == 0)
    {
        to = nullptr;
        return;
    }
    to = new std::remove_pointer_t<ToDataType>[elementCount];
    for (size_t i=0; i<elementCount; ++i)
    {
        to[i] = from[i];
    }
}
// Copy an array into the default value, where the array elements are not copy-constructible and have to be memcpy'd
template <typename FromDataType, typename ToDataType, std::enable_if_t<needs_memcpy_v<std::remove_pointer_t<ToDataType>>, int> = 0>
void copyArrayValue(FromDataType from, ToDataType& to, size_t elementCount)
{
    if (elementCount == 0)
    {
        to = nullptr;
        return;
    }
    to = new std::remove_pointer_t<ToDataType>[elementCount];
    memcpy(to, from, elementCount * sizeof(std::remove_pointer_t<ToDataType>));
}
template <typename DataType, std::enable_if_t<std::is_pointer<DataType>::value, int> = 0>
void destroyArrayValue(DataType& defaultValuePointer)
{
    delete [] defaultValuePointer;
}
template <typename DataType, std::enable_if_t<! std::is_pointer<DataType>::value, int> = 0>
void destroyArrayValue(DataType&)
{
}

// ======================================================================
/**
 * Templated class containing the minimal amount of information required to
 * manage the information on attributes that is independent of evaluation context.
 * Some of the structures are a little non-standard, intentionally so to make
 * access to the attribute and node type ABI easier.
 *
 * The DataType of the attribute is solely used for storing its default value. For single values the default member is
 * an instance of the attribute data type. For arrays it is a pointer to the type, used in conjunction with an element
 * count to determine the size of the array.
 *
 * None of this interface should be called directly; only from generated code.
 * The "attributeType" template parameter is used to selectively enable or disable features
 * that are specific to input, output, or state types (e.g. the INodeType method addInput/addOuput/addState)
 */
template <typename DataType, ogn::eAttributeType attributeType = ogn::kOgnInput>
struct AttributeInitializer
{
    // This is needed due to the way const types are specified. add_const(int*) -> "int* const", not "int const*"
    using DefaultParameterType = std::conditional_t<
        std::is_pointer<DataType>::value,
        std::add_pointer_t<std::add_const_t<std::remove_pointer_t<DataType>>>,
        std::add_const_t<DataType>&
    >;
    using DefaultMemberType = std::conditional_t<
        std::is_pointer<DataType>::value,
        std::add_pointer_t<std::remove_const_t<std::remove_pointer_t<DataType>>>,
        std::remove_const_t<DataType>
    >;

    // TODO: Much of this information is already stored internally; there should be a way to avoid this duplication
    const char* m_name{ nullptr }; //!< Unique name of this attribute
    const char* m_dataType{ nullptr }; //!< Identifying name for the data type of the attribute
    NameToken m_token; //!< Unique token for this attribute's name
    DefaultMemberType m_defaultValue; //!< Default value for this attribute
    size_t m_elementCount{ 0 }; //!< Element count for the attribute values type
    ExtendedAttributeType m_extendedType{kExtendedAttributeType_Regular}; //!< Extended type of this attribute
    bool m_isRequired{ true }; //!< Is the attribute required?
    bool m_hasDefaultValue{ false }; //!< Was a default value explicitly set?
    bool m_hasElementCount{ false }; //!< Was an element count value explicitly set?

    /**
     * This interface is helpful in nodes, to make it easier to find attributes by name.
     * Internal storage may change but this method will continue to exist.
     * @return Pointer to raw string with attribute name in it
     */
    const char* name() const { return m_name; }

    /**
     * This interface is helpful in nodes, to make it easier to find attributes by name
     * Internal storage may change but this method will continue to exist.
     * @return Token with the attribute name in it
     */
    NameToken const& token() const { return m_token; }

    /**
     * Destroy the allocated default value
     */
    ~AttributeInitializer()
    {
        if (m_hasElementCount)
        {
            destroyArrayValue<DefaultMemberType>(m_defaultValue);
        }
    }

    /**
     * Minimal constructor for attributes with no defaults
     *
     * @param[in] attributeName Name of the attribute to be accessed
     * @param[in] dataTypeName Name of the attribute's data type
     * @param[in] extendedType Extended type of the attribute
     */
    AttributeInitializer(const char* attributeName, const char* dataTypeName, ExtendedAttributeType extendedType)
        : m_name(attributeName)
        , m_dataType(dataTypeName)
        , m_extendedType(extendedType)
    {
    }

    /**
     * Constructor for attributes with a default value but no element counts (i.e. not arrays) where the type supports
     * a copy constructor. There is a specialization of types for strings as "const char*" is not equivalent to
     * "char const*", which is required to initialize strings from a raw string.
     *
     * @param[in] Name of the attribute to be accessed
     * @param[in] Name of the attribute's data type
     * @param[in] Reference to the default value of the attribute's data type
     */
    template <typename ConstructedDataType = DataType, typename std::enable_if_t<! needs_memcpy_v<ConstructedDataType>, int> = 0>
    AttributeInitializer(const char* attributeName,
                         const char* dataTypeName,
                         ExtendedAttributeType extendedType,
                         DefaultParameterType newDefault)
        : m_name(attributeName)
        , m_dataType(dataTypeName)
        , m_defaultValue(newDefault)
        , m_extendedType(extendedType)
        , m_hasDefaultValue(true)
    {
    }

    /**
     * Constructor for attributes with a default value but no element counts (i.e. not arrays) where the type does not
     * support a copy constructor. There is a specialization of types for strings as "const char*" is not equivalent to
     * "char const*", which is required to initialize strings from a raw string.
     *
     * @param[in] Name of the attribute to be accessed
     * @param[in] Name of the attribute's data type
     * @param[in] Reference to the default value of the attribute's data type
     */
    template <typename ConstructedDataType = DataType, typename std::enable_if_t<needs_memcpy_v<ConstructedDataType>, int> = 0>
    AttributeInitializer(const char* attributeName,
                         const char* dataTypeName,
                         ExtendedAttributeType extendedType,
                         DefaultParameterType newDefault)
        : m_name(attributeName)
        , m_dataType(dataTypeName)
        , m_extendedType(extendedType)
        , m_hasDefaultValue(true)
    {
        // As this constructor is only called when there is no copy constructor it's reasonable to use a plain
        // memcpy to get the bytes from one object to another. They are required to be bytewise compatible.
        memcpy(&m_defaultValue, &newDefault, sizeof(ConstructedDataType));
    }

    /**
     * Constructor for array attributes with a default value where the type supports a copy constructor
     *
     * @param[in] Name of the attribute to be accessed
     * @param[in] Name of the attribute's data type
     * @param[in] Reference to the default value of the attribute's data type
     * @param[in] Number of elements in the default value
     */
    AttributeInitializer(const char* attributeName,
                         const char* dataTypeName,
                         ExtendedAttributeType extendedType,
                         DefaultParameterType newDefault,
                         size_t newElementCount)
        : m_name(attributeName)
        , m_dataType(dataTypeName)
        , m_defaultValue(nullptr)
        , m_elementCount(newElementCount)
        , m_extendedType(extendedType)
        , m_hasDefaultValue(true)
        , m_hasElementCount(true)
    {
        copyArrayValue<DefaultParameterType, DefaultMemberType>(newDefault, m_defaultValue, newElementCount);
    }

    /**
     * Set a default value after the fact; for types that could have problems with static initialization order
     * if they tried to do this in the constructor (e.g. NameToken)
     *
     * @param[in] newDefault Reference to the default value of the attribute's data type
     */
    void setDefault(DefaultParameterType newDefault)
    {
        CARB_ASSERT(m_extendedType == kExtendedAttributeType_Regular, "Extended attribute types cannot set defaults");
        m_hasDefaultValue = true;
        m_defaultValue = newDefault;
    }

    /**
     * Set a default array value after the fact; for types that could have problems with static initialization order
     * if they tried to do this in the constructor (e.g. NameToken[])
     *
     * @param[in] newDefault Reference to the default value of the attribute's data type
     */
    void setDefault(DefaultParameterType newDefault, size_t elementCount)
    {
        CARB_ASSERT(m_extendedType == kExtendedAttributeType_Regular, "Extended attribute types cannot set defaults");
        if (m_hasDefaultValue && m_elementCount > 0 && m_defaultValue)
        {
            delete [] m_defaultValue;
        }
        m_hasDefaultValue = true;
        copyArrayValue<DefaultParameterType, DefaultMemberType>(newDefault, m_defaultValue, elementCount);
        m_elementCount = elementCount;
    }

    /**
     * Initializer that looks up the attribute name's token; must be done before using it.
     * This variation is for input attributes.
     *
     * @param[in] iNodeType Node type interface to which the attribute will be added as an input
     * @param[in] nodeTypeObj Node to which the attribute will be added as an input
     * @param[in] enable Template metaprogrammed value that enables this version of the method when the attribute is an input
     */
    template <ogn::eAttributeType enabled = attributeType>
    void addToNodeType(const INodeType& iNodeType,
                       const NodeTypeObj& nodeTypeObj,
                       typename std::enable_if<enabled == ogn::kOgnInput>::type* = 0)
    {
        if (m_extendedType == kExtendedAttributeType_Regular)
        {
            iNodeType.addInput(nodeTypeObj, m_name, m_dataType, m_isRequired,
                               m_hasDefaultValue ? &m_defaultValue : nullptr,
                               m_hasElementCount ? &m_elementCount : nullptr);
        }
        else
        {
            iNodeType.addExtendedInput(nodeTypeObj, m_name, m_dataType, m_isRequired, m_extendedType);
        }
    }

    /**
     * Initializer that looks up the attribute name's token; must be done before using it.
     * This variation is for output attributes.
     *
     * @param[in] iNodeType Node type interface to which the attribute will be added as an output
     * @param[in] nodeTypeObj Node to which the attribute will be added as an output
     * @param[in] enable Template metaprogrammed value that enables this version of the method when the attribute is an output
     */
    template <ogn::eAttributeType enabled = attributeType>
    void addToNodeType(const INodeType& iNodeType,
                       const NodeTypeObj& nodeTypeObj,
                       typename std::enable_if<enabled == ogn::kOgnOutput>::type* = 0)
    {
        if (m_extendedType == kExtendedAttributeType_Regular)
        {
            iNodeType.addOutput(nodeTypeObj, m_name, m_dataType, m_isRequired,
                                m_hasDefaultValue ? &m_defaultValue : nullptr,
                                m_hasElementCount ? &m_elementCount : nullptr);
        }
        else
        {
            iNodeType.addExtendedOutput(nodeTypeObj, m_name, m_dataType, m_isRequired, m_extendedType);
        }
    }

    /**
     * Initializer that looks up the attribute name's token; must be done before using it.
     * This variation is for state attributes.
     *
     * @param[in] iNodeType Node type interface to which the attribute will be added as a state
     * @param[in] nodeTypeObj Node to which the attribute will be added as a state
     * @param[in] enable Template metaprogrammed value that enables this version of the method when the attribute is a state
     */
    template <ogn::eAttributeType enabled = attributeType>
    void addToNodeType(const INodeType& iNodeType,
                       const NodeTypeObj& nodeTypeObj,
                       typename std::enable_if<enabled == ogn::kOgnState>::type* = 0)
    {
        if (m_extendedType == kExtendedAttributeType_Regular)
        {
            iNodeType.addState(nodeTypeObj, m_name, m_dataType, m_isRequired,
                               m_hasDefaultValue ? &m_defaultValue : nullptr,
                               m_hasElementCount ? &m_elementCount : nullptr);
        }
        else
        {
            iNodeType.addExtendedState(nodeTypeObj, m_name, m_dataType, m_isRequired, m_extendedType);
        }
    }

    /**
     * Initialization for the attribute on the node type, happens once for any given attribute.
     *
     * @param[in] iToken Attribute's token, for lookup
     * @param[in] iNodeType Node type interface to which the attribute will be added
     * @param[in] nodeTypeObj Node to which the attribute will be added
     */
    void initialize(fabric::IToken& iToken, const INodeType& iNodeType, const NodeTypeObj& nodeTypeObj)
    {
        m_token = iToken.getHandle(m_name);
        addToNodeType(iNodeType, nodeTypeObj);
    }
};

} // namespace ogn
} // namespace core
} // namespace graph
} // namespace omni
