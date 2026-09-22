// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#ifndef __CUDACC__
#    include <carb/InterfaceUtils.h>
#else
// The above include crashes CUDA compiler, but is required for one function
// Just forward declaring it to please the compiler
// As it's not actually used in CUDA code, implementation is not required
namespace carb
{
template <typename T, const char* PluginName = nullptr>
T* getCachedInterface();
}
#endif
#include <omni/fabric/IFabric.h>
#include <omni/fabric/IPath.h>
#include <omni/fabric/IToken.h>
#include <omni/graph/core/TemplateUtils.h>


// Support for generic handles for interface objects.
// Ideally each of the handle types would be put into interface files for their corresponding types. In the
// current scheme they are too intertwined to separate them cleanly. Having this file provides a way for code
// to have access to handles for passing around without pulling in all of the unrelated interfaces.

namespace omni
{
namespace graph
{
namespace core
{

/**
 * Macro to validate the structure of the interface definitions. New functions must be added at the end,
 * and the struct itself must be a standard layout POD, as per Carbonite requirements.
 * @param[in] StructName Name of the structure being validated
 * @param[in] LastFunction Name of the last function declared in the structure
 * @param[in] NumberOfFunctions Total number of functions declared in the structure
 */
#define STRUCT_INTEGRITY_CHECK(StructName, LastFunction, NumberOfFunctions)                                            \
    static_assert(CARB_OFFSETOF2(StructName, LastFunction) == NumberOfFunctions * sizeof(void (*)()),                        \
                  "New " #StructName " ABI methods must be added at the end");                                         \
    static_assert(std::is_trivial<StructName>::value, #StructName " must be a POD");                                   \
    static_assert(std::is_standard_layout<StructName>::value, #StructName " must have std layout");                    \
    static_assert(sizeof(StructName) == (NumberOfFunctions + 1) * sizeof(void (*)()),                                  \
                  "Please update the integrity check macro to point to the last method of " #StructName);

// ==============================================================================================================
/**
 * @brief Template class for defining handles to various OmniGraph data types
 *
 * @tparam T The underlying type of the handle being defined
 * @tparam SUBCLASS The handle subclass being defined
 */
template <typename T, typename SUBCLASS>
class HandleBase
{
public:
    //! Default constructor, gives an invalid handle
    HandleBase() = default;
    //! Default copy constructor, bitwise copy of handle data
    HandleBase(const HandleBase&) = default;
    //! Construct a handle from the underlying data it represents
    explicit HandleBase(const T& h) : handle(h)
    {
    }
    //! Default assignment operator, bitwise copy of the handle data
    HandleBase& operator=(const HandleBase&) = default;
    //! Cast to the underlying data type of the handle
    explicit operator T() const
    {
        return handle;
    }
    //! Returns true if the handle is currently valid
    bool isValid() const
    {
        return (handle != SUBCLASS::invalidValue());
    }
    //! Equality operator - only identical handles are equal
    bool operator==(HandleBase rhs) const
    {
        return handle == rhs.handle;
    }
    //! Inequality operator - only identical handles are equal
    bool operator!=(HandleBase rhs) const
    {
        return !(handle == rhs.handle);
    }

    //! Constant representing a unique invalid handle for this instantiation
    static constexpr SUBCLASS invalidHandle()
    {
        return static_cast<SUBCLASS>(SUBCLASS::invalidValue());
    }

protected:
    T handle; //!< Instantiation of the underlying type of the handle
};

//! Underlying data type for a handle being represented as an integer
using HandleInt = uint64_t;

//! Representation of a string that is referenced via a unique token. Note that although this token is
//! reference counted this is the raw value which is not. Use ogn::Token at the high level to get that
//! reference counting if you intend to hang on to copies of the token.
using NameToken = omni::fabric::TokenC;

//! Representation of a path. Note that although this path is reference counted this is the raw value
//! which is not. Use ogn::Path at the high level to get that reference counting if you intend to hang
//! on to copies of the path.
using TargetPath = omni::fabric::PathC;

//! Location of rows of data in Fabric
using BucketId = omni::fabric::BucketId;

//! Representation of an internal type used by AutoNode
using ObjectId = HandleInt;

// NOTE: Due to Linux debug linking pre-C++17 not liking constexpr static variables,
//       other than built-in integer types, being passed by const reference,
//       invalid values for handles are now constructed via inline functions, instead
//       of using constexpr static variables.  Just to play it safe, we're using a macro
//       here, in case it also has an issue with built-in integer types being referenced
//       from an inline function at compile-time.  Note that the link errors don't show
//       up until *runtime*, since they appear to be handled via dynamic linking.
//! Representation of an invalid handle as an integer
#define OG_INVALID_HANDLE_INT_VALUE (~HandleInt(0))
//! Representation of an invalid handle as an integer
constexpr static HandleInt kInvalidHandleIntValue = OG_INVALID_HANDLE_INT_VALUE;

// ==============================================================================================================
//! Handle type representing attributes, which require two parts to be valid
struct AttrKey
{
    constexpr AttrKey(HandleInt const p = omni::fabric::kUninitializedPath.path,
                      HandleInt const t = omni::fabric::kUninitializedToken.token)
        : m_path(p), m_token(t)
    {
    }
    constexpr AttrKey(omni::fabric::PathC const fullPath, omni::fabric::FabricId fabricID)
        : m_path(fullPath), m_fabricId(fabricID.id), m_hasFabricId(1)
    {
    }
    constexpr AttrKey(AttrKey const&) = default;
    constexpr AttrKey(AttrKey&&) = default;

    omni::fabric::PathC path() const noexcept
    {
        if (m_hasFabricId)
            return carb::getCachedInterface<fabric::IPath>()->getParent(m_path);
        return m_path;
    }

    omni::fabric::TokenC token() const noexcept
    {
        if (m_hasFabricId)
            return carb::getCachedInterface<fabric::IPath>()->getNameToken(m_path);
        return m_token;
    }

    omni::fabric::FabricId fabricId() const noexcept
    {
        if (m_hasFabricId)
            return { m_fabricId };
        return omni::fabric::kInvalidFabricId;
    }

    AttrKey& operator=(std::pair<HandleInt, HandleInt> const& p)
    {
        m_path.path = p.first;
        m_token.token = p.second;
        return *this;
    }
    AttrKey& operator=(AttrKey const& other)
    {
        m_path = other.m_path;
        m_token = other.m_token;
        return *this;
    }

    bool operator==(AttrKey const& other) const
    {
        return m_path == other.m_path && m_token == other.m_token;
    }

    bool operator!=(AttrKey const& other) const
    {
        return !(*this == other);
    }

private:
    omni::fabric::PathC m_path;
    union
    {
        omni::fabric::TokenC m_token;
        struct
        {
            uint64_t m_fabricId : 63;
            uint64_t m_hasFabricId : 1;
        };
    };

    friend struct AttrKeyHash;
};

//! Make sure to warn developer if an incompatibility is introduced
static_assert(sizeof(AttrKey) == 16,
              "AttrKey is supposed to 2 pointers wide: the change you just made is an ABI breakage");

//! This is here so we can use AttrKey and ConstAttributeDataHandle as a key to std::unordered_map.
//! There is another below in ConstAttributeDataHandleHash, intentionally the same as they represent the same data.
//!
//! See https://www.techiedelight.com/use-std-pair-key-std-unordered_map-cpp/ for a full discussion.
struct AttrKeyHash
{
    //! Return a hash value for the underlying handle data
    std::size_t operator()(const AttrKey& attrKey) const
    {
        return std::hash<HandleInt>()(attrKey.m_path.path) ^ std::hash<HandleInt>()(attrKey.m_token.token);
    }
};

// ==============================================================================================================
//! Object representing a handle to an AttributeData type
class ConstAttributeDataHandle : public HandleBase<AttrKey, ConstAttributeDataHandle>
{
public:
    using HandleBase<AttrKey, ConstAttributeDataHandle>::HandleBase;

    //! Path to the prim or bundle of the attribute, e.g. in "/world/cube.size", this returns "/world/cube"
    omni::fabric::PathC path() const noexcept
    {
        return handle.path();
    }

    //! Name of the attribute, e.g. in "/world/cube.size", this would be "size"
    omni::fabric::TokenC name() const noexcept
    {
        return handle.token();
    }

    //! The specific fabric ID associated to this handle
    //! Returns omni::fabric::kInvalidFabricId if this handle is meant to be used with the default one assotiated to the
    //! graph
    omni::fabric::FabricId fabricId() const noexcept
    {
        return handle.fabricId();
    }

    //! Returns an invalid AttributeData handle value
    static constexpr AttrKey invalidValue()
    {
        return AttrKey();
    }
};

// --------------------------------------------------------------------------------------------------------------
//! Hash definition so that AttributeDataHandle can be used in a map
struct ConstAttributeDataHandleHash
{
    //! Returns a hash value unique for AttributeData handles
    std::size_t operator()(const ConstAttributeDataHandle& attrDataHandle) const
    {
        AttrKey attrKey(attrDataHandle);
        return AttrKeyHash()(attrKey);
    }
};

// --------------------------------------------------------------------------------------------------------------
//! Object representing a handle to a variable AttributeData type
class AttributeDataHandle : public HandleBase<AttrKey, AttributeDataHandle>
{
public:
    using HandleBase<AttrKey, AttributeDataHandle>::HandleBase;

    //! Returns an invalid AttributeData handle value
    static constexpr AttrKey invalidValue()
    {
        return AttrKey();
    }

    //! Path to the prim or bundle of the attribute, e.g. in "/world/cube.size", this returns "/world/cube"
    omni::fabric::PathC path() const noexcept
    {
        return handle.path();
    }

    //! Name of the attribute, e.g. in "/world/cube.size", this would be "size"
    omni::fabric::TokenC name() const noexcept
    {
        return handle.token();
    }

    //! The specific fabric ID associated to this handle
    //! Returns omni::fabric::kInvalidFabricId if this handle is meant to be used with the default one assotiated to the
    //! graph
    omni::fabric::FabricId fabricId() const noexcept
    {
        return handle.fabricId();
    }

    //! Returns a constant AttributeDataHandle pointing to the same AttributeData as this variable one
    operator ConstAttributeDataHandle() const
    {
        return ConstAttributeDataHandle(AttrKey(*this));
    }
};

// ==============================================================================================================
//! Object representing a handle to a constant OmniGraph Bundle
class ConstBundleHandle : public HandleBase<HandleInt, ConstBundleHandle>
{
public:
    using HandleBase<HandleInt, ConstBundleHandle>::HandleBase;

    //! Returns an invalid Bundle handle value
    static constexpr HandleInt invalidValue()
    {
        return omni::fabric::kUninitializedPath.path;
    }
};

// --------------------------------------------------------------------------------------------------------------
//! Hash definition so that BundleHandle can be used in a map
struct ConstBundleHandleHash
{
    //! Returns a hash value unique for Bundle handles
    std::size_t operator()(const ConstBundleHandle& handle) const
    {
        return std::hash<HandleInt>()(HandleInt(handle));
    }
};

// --------------------------------------------------------------------------------------------------------------
//! Object representing a handle to an OmniGraph Bundle
class BundleHandle : public HandleBase<HandleInt, BundleHandle>
{
public:
    using HandleBase<HandleInt, BundleHandle>::HandleBase;

    //! Returns an invalid Bundle handle value
    static constexpr HandleInt invalidValue()
    {
        return omni::fabric::kUninitializedPath.path;
    }

    //! Returns a constant BundleHandle pointing to the same Bundle as this variable one
    operator ConstBundleHandle() const
    {
        return ConstBundleHandle(HandleInt(*this));
    }
};

//! Deprecated - for backward compatibility only
using ConstPrimHandle [[deprecated("Use ConstBundleHandle!")]] = ConstBundleHandle;
//! Deprecated - for backward compatibility only
using ConstPrimHandleHash [[deprecated("Use ConstBundleHandleHash!")]] = ConstBundleHandleHash;
//! Deprecated - for backward compatibility only
using PrimHandle [[deprecated("Use BundleHandle!")]] = BundleHandle;

// ==============================================================================================================
//! Object representing a handle to an OmniGraph NodeContext
class NodeContextHandle : public HandleBase<HandleInt, NodeContextHandle>
{
public:
    using HandleBase<HandleInt, NodeContextHandle>::HandleBase;

    //! Returns an invalid NodeContext handle value
    static constexpr HandleInt invalidValue()
    {
        return kInvalidHandleIntValue;
    }
};

// ======================================================================
// Support for attributes
using AttributeHandle = uint64_t; //!< Handle to an OmniGraph Attribute
using AttributeHash = uint64_t; //!< Hash value type for OmniGraph Attributes
static constexpr AttributeHandle kInvalidAttributeHandle = 0; //!< Constant representing an invalid attribute handle
struct IAttribute;
//! Object representing an OmniGraph Attribute
struct AttributeObj
{
    const IAttribute* iAttribute; //!< Interface to functionality on the attribute
    AttributeHandle attributeHandle; //!< Opaque handle to actual underlying attribute

    //! Returns true if this object refers to a valid attribute
    bool isValid() const
    {
        return iAttribute && (attributeHandle != kInvalidAttributeHandle);
    }
};

// ======================================================================
// Support for node types
using NodeTypeHandle = uint64_t; //!< Handle to an OmniGraph NodeType
static constexpr NodeTypeHandle kInvalidNodeTypeHandle = 0; //!< Constant representing an invalid node type handle
struct INodeType;
//! Object representing an OmniGraph NodeType
struct NodeTypeObj
{
    const INodeType* iNodeType; //!< Interface to functionality on the node type
    NodeTypeHandle nodeTypeHandle; //!< Opaque handle to actual underlying node type - managed by OmniGraph

    //! Returns true if this object refers to a valid node type
    bool isValid() const
    {
        return iNodeType && (nodeTypeHandle != kInvalidNodeTypeHandle);
    }
};

// ======================================================================
// Support for evaluation contexts
struct IGraphContext;
struct IBundle;
struct IAttributeData;
using GraphContextHandle = uint64_t; //!< Handle to an OmniGraph GraphContext
static constexpr GraphContextHandle kInvalidGraphContextHandle = 0; //!< Constant representing an invalid graph context
                                                                    //!< handle
/**
 * @brief Object representing an OmniGraph GraphContext
 */
struct GraphContextObj
{
    const IGraphContext* iContext; //!< Interfaces to functionality on the context
    // Convenience location for commonly used interfaces
    const IBundle* iBundle; //!< Cached ABI interface pointer
    const IAttributeData* iAttributeData; //!< Cached ABI interface pointer
    const omni::fabric::IToken* iToken; //!< Cached ABI interface pointer
    const omni::fabric::IPath* iPath; //!< Cached ABI interface pointer
    GraphContextHandle contextHandle; //!< Opaque handle to actual underlying graph context

    //! Returns true if this object refers to a valid graph context
    bool isValid() const
    {
        return iContext && (contextHandle != kInvalidGraphContextHandle);
    }
};

// ======================================================================
// Support for nodes
using NodeHandle = uint64_t;
static constexpr NodeHandle kInvalidNodeHandle = 0; //!< Constant representing an invalid node handle
struct INode;
//! Object representing an OmniGraph Node
struct NodeObj
{
    //! Interface to functionality on the node
    const INode* iNode{ nullptr };
    //! Opaque handle to actual underlying node - managed by compute graph system
    NodeHandle nodeHandle{ kInvalidNodeHandle };
    //! handle used to retrieve data on the node - every node has a NodeContextHandle, but not the other way around
    NodeContextHandle nodeContextHandle{ NodeContextHandle::invalidValue() };

    //! Returns true if this object refers to a valid node
    bool isValid() const
    {
        return iNode && (nodeHandle != kInvalidNodeHandle);
    }
};

// ======================================================================
// Support for graphs
using GraphHandle = uint64_t;
static constexpr GraphHandle kInvalidGraphHandle = 0; //!< Constant representing an invalid graph handle
struct IGraph;
//! Object representing an OmniGraph Graph
struct GraphObj
{
    IGraph* iGraph; //!< Interface to functionality on the graph
    GraphHandle graphHandle; //!< Opaque handle to actual underlying graph

    //! Returns true if this object refers to a valid graph
    bool isValid() const
    {
        return iGraph && (graphHandle != kInvalidGraphHandle);
    }
};

// ======================================================================
/**
 * SFINAE function that will call setContext on an object if it exists as "void setContext(GraphContextObj&)".
 * This allows setting a context in the wrapper functions to percolate down to the member implementations
 * when appropriate.
 *
 * Usage:
 *      OptionalMethod::setContext<ClassType>(classMember, context);
 */
template <class NodeTypeClass>
using has_setContext =
    typename std::is_same<void,
                          decltype(std::declval<NodeTypeClass&>().setContext(std::declval<const GraphContextObj&>()))>::value_type;

/**
 * SFINAE function that will call setHandle on an object if it exists as "void setHandle(GraphContextObj&)".
 * This allows setting a handle in the wrapper functions to percolate down to the member implementations
 * when appropriate.
 *
 * Usage:
 *      OptionalMethod::setHandle<ClassType, HandleType>(classMember, handle);
 */
template <class NodeTypeClass, typename HandleType>
using has_setHandle =
    typename std::is_same<void, decltype(std::declval<NodeTypeClass&>().setHandle(std::declval<HandleType>()))>::value_type;

//! Helper struct to make it easy to reference methods on a class that may or may not be defined.
struct OptionalMethod
{
private:
    template <typename ClassToSet, typename HandleType>
    static void call_setHandle(ClassToSet& member, HandleType handle, std::true_type)
    {
        member.setHandle(handle);
    }
    template <typename ClassToSet, typename HandleType>
    static void call_setHandle(ClassToSet& member, HandleType handle, std::false_type)
    {
    }

    template <typename ClassToSet>
    static void call_setContext(ClassToSet& member, const GraphContextObj& context, std::true_type)
    {
        member.setContext(context);
    }
    template <typename ClassToSet>
    static void call_setContext(ClassToSet& member, const GraphContextObj& context, std::false_type)
    {
    }

public:
    /**
     * @brief Set the Handle object
     *
     * @tparam ClassToSet Object class on which to set the handle
     * @tparam HandleType Handle class that is the object class member containing the handle
     * @param member Object on which the handle is to be set
     * @param handle Handle to be set on the object
     */
    template <typename ClassToSet, typename HandleType>
    static void setHandle(ClassToSet& member, HandleType handle)
    {
        call_setHandle(member, handle, is_detected<has_setHandle, ClassToSet, HandleType>());
    }
    /**
     * @brief Set the Context object, if an implementation exists
     *
     * @tparam ClassToSet Object class on which to set the context
     * @param member Object on which the context is to be set
     * @param context Context to be set on the object
     */
    template <typename ClassToSet>
    static void setContext(ClassToSet& member, const GraphContextObj& context)
    {
        call_setContext(member, context, is_detected<has_setContext, ClassToSet>());
    }
};

/**
 * Permanent value representing an instance.
 */
struct GraphInstanceID
{
    constexpr GraphInstanceID() : id(0){};
    constexpr GraphInstanceID(NameToken _token) : id(_token){};

    /** Returns true if this GraphInstanceID is equal to the @p other */
    bool operator==(GraphInstanceID const& other) const
    {
        return id == other.id;
    }
    /** Returns true if this GraphInstanceID is not equal to the @p other */
    bool operator!=(GraphInstanceID const& other) const
    {
        return id != other.id;
    }
    /** Returns true if this GraphInstanceID is less than the @p other */
    bool operator<(GraphInstanceID const& other) const
    {
        return id < other.id;
    }

    NameToken id; //!< Unique token value for the instance
};
static constexpr GraphInstanceID kUninitializedGraphId{ 0 };
static_assert(std::is_standard_layout<GraphInstanceID>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

/*
  _____                                _           _
 |  __ \                              | |         | |
 | |  | | ___ _ __  _ __ ___  ___ __ _| |_ ___  __| |
 | |  | |/ _ \ '_ \| '__/ _ \/ __/ _` | __/ _ \/ _` |
 | |__| |  __/ |_) | | |  __/ (_| (_| | ||  __/ (_| |
 |_____/ \___| .__/|_|  \___|\___\__,_|\__\___|\__,_|
             | |
             |_|
May go away at any time - what you should use are in the comments
*/
//! Deprecated - use kInvalidTokenValue
constexpr static HandleInt INVALID_TOKEN_VALUE = ~HandleInt(0);

} // namespace core
} // namespace graph
} // namespace omni

namespace std
{

/**
 * Hash specialization for omni::graph::core::GraphInstanceID.
 */
template <>
struct hash<omni::graph::core::GraphInstanceID>
{
    uint64_t operator()(const omni::graph::core::GraphInstanceID& graphInstanceId) const noexcept
    {
        return graphInstanceId.id.token;
    }
};

}
