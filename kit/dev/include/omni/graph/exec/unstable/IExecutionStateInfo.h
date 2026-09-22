// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file IExecutionStateInfo.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::IExecutionStateInfo.
#pragma once

#include <omni/Expected.h>
#include <omni/graph/exec/unstable/Assert.h>
#include <omni/graph/exec/unstable/IBase.h>
#include <omni/graph/exec/unstable/Span.h>
#include <omni/graph/exec/unstable/Stamp.h>
#include <omni/graph/exec/unstable/Types.h>

#include <memory>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

// forward declarations needed by interface declaration
class IExecutionStateInfo;
class IExecutionStateInfo_abi;

//! State associated with a given execution task
//!
//! Execution state is separated from the execution graph to allow concurrent and/or nested execution.  See @ref
//! omni::graph::exec::unstable::IExecutionContext for details.
//!
//! @thread_safety Since multiple threads can concurrently traverse a graph, implementors of methods within this class
//! should expect that multiple threads will be accessing this object in parallel.
class IExecutionStateInfo_abi : public omni::core::Inherits<omni::graph::exec::unstable::IBase,
                                                            OMNI_TYPE_ID("omni.graph.exec.unstable.IExecutionStateInfo")>
{
protected:
    //! Query used by some executors to determine if computation of a node is necessary
    virtual bool needsCompute_abi(Stamp execVersion) noexcept = 0;

    //! Set to request computation
    virtual void requestCompute_abi() noexcept = 0;

    //! Reset request to compute after computation was performed
    virtual void setComputed_abi() noexcept = 0;

    //! Get current/last exec version set for this node during execution
    virtual SyncStamp getExecutionStamp_abi() noexcept = 0;

    //! Set current exec version for this node. Returns true if version wasn't in sync.
    virtual bool setExecutionStamp_abi(Stamp execVersion) noexcept = 0;

    //! Returns a value from the key/value datastore.
    //!
    //! The @p key is used as a look-up in the node's key/value datastore.
    //!
    //! @p outPtr will be updated with a pointer to the actual data.  @p outPtr must not be @c nullptr.
    //!
    //! @p outItemSize store the size of each item in the returned array. @p outItemSize must not be @c nullptr
    //!
    //! @p outItemCount contains the number of items returned (i.e. the number of items @p outPtr points to).  For an
    //! array, this will be greater than 1. @p outItemCount must not be @c nullptr.
    //!
    //! If the key is not found, @ref omni::core::kResultNotFound is returned.
    //!
    //! The returned @p data may point to @c nullptr is @ref
    //! omni::graph::exec::unstable::IExecutionContext::setNodeData() was previously called with a @c nullptr data
    //! pointer.
    //!
    //! See @rstref{Error Handling<ef_error_handling>} to understand the error handling/reporting responsibilities of
    //! implementors of this method.
    //!
    //! @thread_safety Accessing the key/value datastore is not thread safe.
    virtual OMNI_ATTR("nodiscard") omni::core::Result
        getNodeData_abi(NodeDataKey key,
                        OMNI_ATTR("out, not_null") omni::core::TypeId* outTypeId,
                        OMNI_ATTR("out, not_null, *out, *in") void** outPtr,
                        OMNI_ATTR("out, not_null") uint64_t* outItemSize,
                        OMNI_ATTR("out, not_null") uint64_t* outItemCount) noexcept = 0;

    //! Sets a value in the key/value datastore.
    //!
    //! The @p key is used as a look-up in the node's key/value datastore.
    //!
    //! The type of each data item is set with @p typeId.
    //!
    //! The type of each data item is set with @p typeId.
    //!
    //! If data already exists at the given key, it will be replaced.
    //!
    //! @p data points to an array of data items.  @p data may be @c nullptr.
    //!
    //! @p itemSize is the size of each item in the given array.
    //!
    //! @p itemCount contains the number of items pointed to by @p data. For an
    //! array, this will be greater than 1.
    //!
    //! @p deleter is a function used to delete @p data when either a new value
    //! is set at the key or the context is invalidated.  If @p deleter is @c
    //! nullptr, it is up to the calling code to manage the lifetime of the @p
    //! data.
    //!
    //! @thread_safety Accessing the key/value datastore is not thread safe.
    virtual void setNodeData_abi(NodeDataKey key,
                                 omni::core::TypeId typeId,
                                 OMNI_ATTR("in, out") void* data,
                                 uint64_t itemSize,
                                 uint64_t itemCount,
                                 OMNI_ATTR("in, out") NodeDataDeleterFn* deleter) noexcept = 0;
};

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni

// generated API declaration
#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/graph/exec/unstable/IExecutionStateInfo.gen.h>

//! @copydoc omni::graph::exec::unstable::IExecutionStateInfo_abi
//!
//! @ingroup groupOmniGraphExecInterfaces
class omni::graph::exec::unstable::IExecutionStateInfo
    : public omni::core::Generated<omni::graph::exec::unstable::IExecutionStateInfo_abi>
{
public:
    //! Returns a pointer to a value stored in the key/value datastore.
    //!
    //! The type @c T must match the type specified in @p desiredType.  Prefer using @ref
    //! OMNI_GRAPH_EXEC_GET_NODE_DATA_AS() instead of this method, which will ensure @p desiredType and @p T match.
    //!
    //! If @p desiredType does not match the type of the stored data, @ref omni::core::kResultInvalidDataType is
    //! returned.
    //!
    //! If no data exists at the given @p key (i.e @ref omni::graph::exec::unstable::IExecutionStateInfo::setNodeData()
    //! has not previously been called at the given @p key), @ref omni::core::kResultNotFound is returned.
    //!
    //! The returned span may point to @c nullptr if @ref
    //! omni::graph::exec::unstable::IExecutionStateInfo::setNodeData() was previously called with a @c nullptr data
    //! pointer.
    //!
    //! @thread_safety See thread safety information in interface description.
    template <typename T>
    CARB_NODISCARD inline omni::expected<Span<T>, omni::core::Result> getNodeDataAs(omni::core::TypeId desiredType,
                                                                                    NodeDataKey key) noexcept;

    //! Stores a value in the key/value datastore.
    //!
    //! If a value is already stored at the given @p key it will be replaced.
    //!
    //! @p SpecifiedT, @p itemType, and @p DataT describe the type of the supplied data and must all be the same type.
    //! Prefer using @ref OMNI_GRAPH_EXEC_SET_NODE_DATA() instead of this method, which will populate the @p itemType
    //! for you.
    //!
    //! @p data may be @c nullptr.
    //!
    //! Returns a pointer to @p data.
    //!
    //! @thread_safety See thread safety information in interface description.
    template <typename SpecifiedT, typename DataT>
    inline DataT* setNodeData(omni::core::TypeId itemType, NodeDataKey key, std::unique_ptr<DataT> data) noexcept;
    using Generated<IExecutionStateInfo_abi>::setNodeData;
};

#ifndef DOXYGEN_BUILD // templates and doxygen are not friends (remove this line to see why)

template <typename T>
inline omni::expected<omni::graph::exec::unstable::Span<T>, omni::core::Result> omni::graph::exec::unstable::
    IExecutionStateInfo::getNodeDataAs(omni::core::TypeId desiredType, NodeDataKey key) noexcept
{
    omni::core::TypeId outType;
    void* outPtr;
    uint64_t outItemSize, outItemCount;
    auto result = getNodeData_abi(key, &outType, &outPtr, &outItemSize, &outItemCount);
    if (OMNI_SUCCEEDED(result) && outPtr)
    {
        OMNI_GRAPH_EXEC_FATAL_UNLESS(outType == desiredType);
        OMNI_GRAPH_EXEC_FATAL_UNLESS(outItemSize == sizeof(T));
    }

    OMNI_GRAPH_EXEC_RETURN_EXPECTED(Span<T>(reinterpret_cast<T*>(outPtr), outItemCount), result);
}

template <typename SpecifiedT, typename DataT>
inline DataT* omni::graph::exec::unstable::IExecutionStateInfo::setNodeData(omni::core::TypeId desiredType,
                                                                            NodeDataKey key,
                                                                            std::unique_ptr<DataT> data) noexcept
{
    static_assert(std::is_same<SpecifiedT, DataT>::value, "given TypeId does not match the data type");
    static_assert(!std::is_array<DataT>::value, "setting arrays as node data via unique_ptr not yet implemented");

    setNodeData_abi(key, desiredType, data.get(), sizeof(DataT), 1,
                    [](void* p)
                    {
                        typename std::unique_ptr<DataT>::deleter_type deleter;
                        deleter(reinterpret_cast<DataT*>(p));
                    });
    return data.release(); // now safe to release ownership
}

#endif // DOXYGEN_BUILD

//! Calls either @ref omni::graph::exec::unstable::IExecutionContext::getNodeDataAs() or @ref
//! omni::graph::exec::unstable::IExecutionStateInfo::getNodeDataAs() (dependent on the type of the first argument).
//!
//! The purpose of this macro is to generate an appropriate @ref omni::core::TypeId at compile time from the data item's
//! type.  The user can manually do this, but this macro is much less error prone.
//!
//! @code
//! auto data = OMNI_GRAPH_EXEC_GET_NODE_DATA_AS(
//!     task->getContext(),        // pointer to either IExecutionContext or IExecutionStateInfo
//!     GraphContextCacheOverride, // the type of the data to retrieve
//!     task->getUpstreamPath(),   // node path
//!     tokens::kInstanceContext   // key to use as a lookup in the node's key/value datastore
//! );
//!
//! if (data)
//! {
//!      GraphContextCacheOverride* item = data.value();
//!      // ...
//! }
//! else
//! {
//!      omni::core::Result badResult = data.error(); // e.g. kResultNotFound (see docs)
//!      // ...
//! }
//! @endcode
//!
//! The macro itself is a variadic macro and can map to multiple overloads of @c getNodeDataAs() methods in the
//! interface given as the first argument
//!
//! With newer compilers (GCC >= 8), this macro can be replaced with templated methods (without breaking the ABI).
#define OMNI_GRAPH_EXEC_GET_NODE_DATA_AS(context_, type_, ...)                                                         \
    context_->getNodeDataAs<type_>(CARB_HASH_STRING(CARB_STRINGIFY(type_)), __VA_ARGS__)
// the ugly macro above is used to hash the type of the data at compile time.
//
// it's possible to get the type of data at compile time by inspecting the function name (e.g. __FUNCSIG__ and
// __PRETTY_FUNCTION__).  however __PRETTY_FUNCTION__ was not a constexpr until GCC 8.  omniverse currently uses GCC 7
// so were left with this hack.
//
// https://gcc.gnu.org/bugzilla/show_bug.cgi?id=66639

//! Calls either @ref omni::graph::exec::unstable::IExecutionContext::setNodeData() or @ref
//! omni::graph::exec::unstable::IExecutionStateInfo::setNodeData() (dependent on the type of the first argument).
//!
//! The purpose of this macro is to generate an appropriate @ref omni::core::TypeId at compile time from the data item's
//! type.  The user can manually do this, but this macro is much less error prone.
//!
//! @code
//! OMNI_GRAPH_EXEC_SET_NODE_DATA(
//!     stateInfo,                      // pointer to either IExecutionContext or IExecutionStateInfo
//!     GraphContextCacheOverride,      // type of the data to store
//!     tokens::kInstanceContext,       // key to store the data at in the node's key/value datastore
//!     std::move(contextOverridePtr)   // pointer to the data to store
//! );
//! @endcode
//!
//! The macro itself is a variadic macro and can map to multiple overloads of @c setNodeData() methods in the interface
//! given as the first argument
//!
//! Returns a pointer to the given data.
//!
//! With newer compilers (GCC >= 8), this macro can be replaced with templated methods (without breaking the ABI).
#define OMNI_GRAPH_EXEC_SET_NODE_DATA(context_, type_, ...)                                                            \
    context_->setNodeData<type_>(CARB_HASH_STRING(CARB_STRINGIFY(type_)), __VA_ARGS__)
// the ugly macro above is used to hash the type of the data at compile time.
//
// it's possible to get the type of data at compile time by inspecting the function name (e.g. __FUNCSIG__ and
// __PRETTY_FUNCTION__).  however __PRETTY_FUNCTION__ was not a constexpr until GCC 8.  omniverse currently uses GCC 7
// so were left with this hack.
//
// https://gcc.gnu.org/bugzilla/show_bug.cgi?id=66639

// generated API implementation
#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/graph/exec/unstable/IExecutionStateInfo.gen.h>
