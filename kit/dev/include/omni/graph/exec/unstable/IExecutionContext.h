// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file IExecutionContext.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::IExecutionContext.
#pragma once

#include <omni/Expected.h>
#include <omni/graph/exec/unstable/Assert.h>
#include <omni/graph/exec/unstable/ConstName.h>
#include <omni/graph/exec/unstable/IBase.h>
#include <omni/graph/exec/unstable/Span.h>
#include <omni/graph/exec/unstable/Stamp.h>
#include <omni/graph/exec/unstable/Status.h>
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

class ExecutionPath;
class ExecutionTask;
class IApplyOnEachFunction;
class IDef;
class IExecutionContext_abi;
class IExecutionContext;
class IExecutionStateInfo;
class INode;

//! Stores and provides access to the execution state of the graph.
//!
//! The @rstref{execution graph <ef_execution_graph>} is only a description of what needs to be executed. The actual
//! graph state is stored separately in an instance of this object.
//!
//! The execution context allows computing the same graph description within multiple contexts. It also enables the
//! ability to perform this computation concurrently.  Some example use cases of this class:
//!
//! - Computing the state of a graph at a time different than the current time (e.g. asynchronous caching, fake
//!   dynamics)
//!
//! - Computing the state of a graph with a inputs different than the current input state (e.g. double solve)
//!
//! All execution begins with a call to one of the execute methods on this interface. @ref
//! omni::graph::exec::unstable::IExecutionContext::execute() is used to execute the entire execution graph while @ref
//! omni::graph::exec::unstable::IExecutionContext::executeNode() can be used to execute only a part of the graph.
//!
//! Part of this interface defines a key/value store.  The *key* in this store is an @ref
//! omni::graph::exec::unstable::ExecutionPath.  The *value* is an implementation of @ref
//! omni::graph::exec::unstable::IExecutionStateInfo, which in addition to storing computation state, can also store
//! user defined data.  The computation state and user data can be accessed with the `getStateInfo` / `getNodeData`
//! methods (though the latter is slightly faster) and set with the `setNodeData`.
//!
//! Another feature of @ref omni::graph::exec::unstable::IExecutionContext is the ability to quickly search for nodes
//! using a particular definition and apply a function on them.  Definitions can be searched by name or by pointer (see
//! @ref omni::graph::exec::unstable::IExecutionContext::applyOnEach()).  These methods are used extensively during
//! @rstref{Graph Construction <ef_pass_concepts>}.
//!
//! See @rstref{Execution Concepts <ef_execution_concepts>} for an in-depth guide on how this object is used during
//! execution.
//!
//! @thread_safety Since multiple threads can concurrently traverse a graph, implementors of methods within this class
//! should expect that multiple threads will be accessing this object in parallel.
class IExecutionContext_abi : public omni::core::Inherits<omni::graph::exec::unstable::IBase,
                                                          OMNI_TYPE_ID("omni.graph.exec.unstable.IExecutionContext")>
{
protected:
    //! Current execution version. Incremented with each execution of the context.
    //!
    //! @thread_safety See thread safety information in interface description.
    virtual Stamp getExecutionStamp_abi() noexcept = 0;

    //! Returns `true` if context is currently executing
    //!
    //! @thread_safety See thread safety information in interface description.
    virtual bool inExecute_abi() noexcept = 0;

    //! Returns `true` if the current thread is one, of potentially many, which started this context's
    //! execution. In other words, invoking this method in any thread that kickstarted this context's
    //! execution will return `true`.
    //!
    //! When a given context's execution from within a thread completes, that thread will no longer
    //! be associated with that context as a "kickstarting" thread, so any subsequent calls to this
    //! method from within that same thread will return `false` until execution is invoked on the context
    //! once again.
    //!
    //! Note, do not assume that the "main" thread acts as an evaluation kickstarter to any given context.
    //!
    //! @thread_safety See thread safety information in interface description.
    virtual bool isExecutingThread_abi() noexcept = 0;

    //! Main execution method.  Executes the entire execution graph.
    //!
    //! See @rstref{Error Handling<ef_error_handling>} to understand the error handling/reporting responsibilities of
    //! implementors of this method.
    //!
    //! @thread_safety See thread safety information in interface description.
    virtual OMNI_ATTR("nodiscard") Status execute_abi() noexcept = 0;

    //! On-demand execution method.  Executes the given node.
    //!
    //! The given path must not be @c nullptr.
    //!
    //! The given node must not be @c nullptr.
    //!
    //! See @rstref{Error Handling<ef_error_handling>} to understand the error handling/reporting responsibilities of
    //! implementors of this method.
    //!
    //! @thread_safety See thread safety information in interface description.
    virtual OMNI_ATTR("nodiscard") Status
        executeNode_abi(OMNI_ATTR("in, not_null, ref") const ExecutionPath* upstreamPath,
                        OMNI_ATTR("not_null") INode* node) noexcept = 0;

    //! Context initialization. Responsible to propagate initialization to graphs.
    //!
    //! @thread_safety See thread safety information in interface description.
    virtual void initialize_abi() noexcept = 0;

    //! Access state for a given execution path.
    //!
    //! If the given node is not @c nullptr, a copy of the given path with the node appended will be used as the lookup
    //! key.
    //!
    //! This method always returns a valid pointer.
    //!
    //! @thread_safety See thread safety information in interface description.
    //!
    //! @warning    This method should be used for read only access by downstream nodes, example accessing graph state
    //!             when executing downstream nodes. Extra care needs to be taken if this state has to be mutated
    //!             concurrently.
    virtual OMNI_ATTR("no_acquire") IExecutionStateInfo* getStateInfo_abi(OMNI_ATTR("in, not_null, ref")
                                                                              const ExecutionPath* path,
                                                                          INode* node) noexcept = 0;

    //! Returns a value from a node's key/value datastore.
    //!
    //! The node from which to grab data is identified by the given @p path and @p node.  The @p node may be @c nullptr.
    //!
    //! The @p key is used as a look-up in the node's key/value datastore.
    //!
    //! The type of each data item is returned in @p outTypeId.
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
    //! The returned @p data may point to @c nullptr if @ref
    //! omni::graph::exec::unstable::IExecutionContext::setNodeData() was previously called with a @c nullptr data
    //! pointer.
    //!
    //! @p path must not be @c nullptr.
    //!
    //! See @rstref{Error Handling<ef_error_handling>} to understand the error handling/reporting responsibilities of
    //! implementors of this method.
    //!
    //! @thread_safety See thread safety information in interface description.
    virtual OMNI_ATTR("no_api") omni::core::Result
        getNodeData_abi(OMNI_ATTR("in, not_null, ref") const ExecutionPath* path,
                        INode* node,
                        NodeDataKey key,
                        OMNI_ATTR("out, not_null") omni::core::TypeId* outTypeId,
                        OMNI_ATTR("out, not_null, *out, *in") void** outPtr,
                        OMNI_ATTR("out, not_null") uint64_t* outItemSize,
                        OMNI_ATTR("out, not_null") uint64_t* outItemCount) noexcept = 0;

    //! Sets a value in a node's key/value datastore.
    //!
    //! The node in which to set the data is identified by the given path and
    //! node.  @p path must not be @c nullptr.  The @p node may be @c nullptr.
    //!
    //! The @p key is used as a look-up in the node's key/value datastore.
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
    //! @thread_safety See thread safety information in interface description.
    virtual OMNI_ATTR("no_api") void setNodeData_abi(OMNI_ATTR("in, not_null, ref") const ExecutionPath* path,
                                                     INode* node,
                                                     NodeDataKey key,
                                                     omni::core::TypeId typeId,
                                                     OMNI_ATTR("in, out") void* data,
                                                     uint64_t itemSize,
                                                     uint64_t itemCount,
                                                     OMNI_ATTR("in, out") NodeDataDeleterFn* deleter) noexcept = 0;

    //! Discover all execution paths leading to the given definition and invoke the given function with each of them.
    //!
    //! Implementations of this interface may cache results to remove the traversal cost for subsequent call. Any change
    //! in the execution graph topology will invalidate this cache.
    //!
    //! This method must not be called during graph construction.
    //!
    //! @p def is the definition for which to look.  This pointer may be @c nullptr.
    //!
    //! @p callback is the callback to execute with each path to given definition.  This pointer must not be @c nullptr.
    //!
    //! The given @p callback is free to invoke this method.
    //!
    //! @thread_safety The given @p callback will be called serially by this method.  However, other threads may also
    //! invoke this method, meaning the @p callback must coordinate access to shared data.
    virtual OMNI_ATTR("no_api") void applyOnEachDef_abi(OMNI_ATTR("not_null") IDef* def,
                                                        OMNI_ATTR("not_null")
                                                            IApplyOnEachFunction* callback) noexcept = 0;

    //! Discover all execution paths leading to definitions with the given name and invoke the given function with each
    //! of them.
    //!
    //! Implementation of this interface may cache results to remove the traversal cost for subsequent calls. Any change
    //! in the execution graph topology will invalidate this cache.
    //!
    //! This method must not be called during graph construction.
    //!
    //! @p name is the name of definition for which to look.  This pointer must not be @c nullptr.
    //!
    //! @p callback is the callback to execute with each path to given definition.  This pointer must not be @c nullptr.
    //!
    //! The given @p callback is free to invoke this method.
    //!
    //! @thread_safety The given @p callback will be called serially by this method.  However, other threads may also
    //! invoke this method, meaning the @p callback must coordinate access to shared data.
    virtual OMNI_ATTR("no_api") void applyOnEachDefWithName_abi(OMNI_ATTR("in, not_null, ref") const ConstName* name,
                                                                OMNI_ATTR("not_null")
                                                                    IApplyOnEachFunction* callback) noexcept = 0;
};

//! Smart pointer managing an instance of @ref IExecutionContext.
using ExecutionContextPtr = omni::core::ObjectPtr<IExecutionContext>;

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni

#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/graph/exec/unstable/IExecutionContext.gen.h>

//! @copydoc omni::graph::exec::unstable::IExecutionContext_abi
//!
//! @ingroup groupOmniGraphExecInterfaces
class omni::graph::exec::unstable::IExecutionContext
    : public omni::core::Generated<omni::graph::exec::unstable::IExecutionContext_abi>
{
public:
    //! @copydoc omni::graph::exec::unstable::IExecutionContext_abi::executeNode_abi
    CARB_NODISCARD Status execute(const ExecutionPath& path, omni::core::ObjectParam<INode> node) noexcept
    {
        return executeNode(path, node);
    }
    using Generated<IExecutionContext_abi>::execute;

    //! Retrieves the state info for the node in the given task.
    //!
    //! The task's upstream path and node are hashed for the lookup.
    //!
    //! The returned @ref omni::graph::exec::unstable::IExecutionStateInfo will
    //! not have @ref omni::core::IObject::acquire() called on it.
    //!
    //! This method always returns a valid pointer.
    //!
    //! See @ref omni::graph::exec::unstable::IExecutionContext::getStateInfo_abi() for further details.
    //!
    //! @thread_safety See thread safety information in interface description.
    inline IExecutionStateInfo* getStateInfo(const ExecutionTask& task) noexcept;
    using Generated<IExecutionContext_abi>::getStateInfo;

    //! Retrieves the state info at the given execution path.
    //!
    //! The returned @ref omni::graph::exec::unstable::IExecutionStateInfo will
    //! not have @ref omni::core::IObject::acquire() called on it.
    //!
    //! This method always returns a valid pointer.
    //!
    //! See @ref omni::graph::exec::unstable::IExecutionContext::getStateInfo_abi() for further details.
    //!
    //! @thread_safety See thread safety information in interface description.
    inline IExecutionStateInfo* getStateInfo(const ExecutionPath& path) noexcept;

    //! Access state for the node in a given task.  The returned object will be the given template type.
    //!
    //! @c nullptr may be returned if the retrieved @ref omni::graph::exec::unstable::IExecutionStateInfo could not be
    //! casted to @p T.
    //!
    //! See @ref omni::graph::exec::unstable::IExecutionContext::getStateInfo_abi() for further details.
    //!
    //! @thread_safety See thread safety information in interface description.
    template <typename T>
    inline T* getStateInfoAs(const ExecutionTask& info) noexcept;

    //! Access state for a given execution path.  The returned object will be the given template type.
    //!
    //! @c nullptr may be returned if the retrieved @ref omni::graph::exec::unstable::IExecutionStateInfo could not be
    //! casted to @p T.
    //!
    //! See @ref omni::graph::exec::unstable::IExecutionContext::getStateInfo_abi() for further details.
    //!
    //! @thread_safety See thread safety information in interface description.
    template <typename T>
    inline T* getStateInfoAs(const ExecutionPath& path) noexcept;

    //! Access state for a given node under the given execution path.  The returned object will be the given template
    //! type.
    //!
    //! @c nullptr may be returned if the retrieved @ref omni::graph::exec::unstable::IExecutionStateInfo could not be
    //! casted to @p T.
    //!
    //! The given @p node may be @c nullptr.
    //!
    //! See @ref omni::graph::exec::unstable::IExecutionContext::getStateInfo_abi() for further details.
    //!
    //! @thread_safety See thread safety information in interface description.
    template <typename T>
    inline T* getStateInfoAs(const ExecutionPath& path, omni::core::ObjectParam<INode> node) noexcept;

    //! Returns a pointer to a value stored in a node's key/value datastore.
    //!
    //! The node whose key/value datastore should be used is identified by combining the given @p path and @p node.  @p
    //! node may be @c nullptr.
    //!
    //! The type @c T must match the type specified in @p desiredType.  Prefer using @ref
    //! OMNI_GRAPH_EXEC_GET_NODE_DATA_AS() instead of this method, which will ensure @p desiredType and @p T match.
    //!
    //! If @p desiredType does not match the type of the stored data, @ref omni::core::kResultInvalidDataType is
    //! returned.
    //!
    //! If no data exists at the given @p key (i.e @ref omni::graph::exec::unstable::IExecutionContext::setNodeData()
    //! has not previously been called at the given @p key), @ref omni::core::kResultNotFound is returned.
    //!
    //! The returned span may point to @c nullptr if @ref omni::graph::exec::unstable::IExecutionContext::setNodeData()
    //! was previously called with a @c nullptr data pointer.
    //!
    //! @thread_safety See thread safety information in interface description.
    template <typename T>
    CARB_NODISCARD inline omni::expected<Span<T>, omni::core::Result> getNodeDataAs(omni::core::TypeId desiredType,
                                                                                    const ExecutionPath& path,
                                                                                    omni::core::ObjectParam<INode> node,
                                                                                    NodeDataKey key) noexcept;

    //! Returns a pointer to a value stored in a node's key/value datastore.
    //!
    //! The node whose key/value datastore should be used is identified by combining the given path and node in the
    //! given task.
    //!
    //! The type @c T must match the type specified in @p desiredType.  Prefer using @ref
    //! OMNI_GRAPH_EXEC_GET_NODE_DATA_AS() instead of this method, which will populate the @p desiredType for you.
    //!
    //! If @p desiredType does not match the type of the stored data, @ref omni::core::kResultInvalidDataType is
    //! returned.
    //!
    //! If no data exists at the given @p key (i.e @ref omni::graph::exec::unstable::IExecutionContext::setNodeData()
    //! has not previously been called at the given @p key), @ref omni::core::kResultNotFound is returned.
    //!
    //! The returned span may point to @c nullptr if @ref omni::graph::exec::unstable::IExecutionContext::setNodeData()
    //! was previously called with a @c nullptr data pointer.
    //!
    //! @thread_safety See thread safety information in interface description.
    template <typename T>
    CARB_NODISCARD inline omni::expected<Span<T>, omni::core::Result> getNodeDataAs(omni::core::TypeId desiredType,
                                                                                    const ExecutionTask& path,
                                                                                    NodeDataKey key) noexcept;

    //! Stores a value in a node's key/value datastore.
    //!
    //! The node whose key/value datastore should be used is identified by combining the given @p path and @p node.  @p
    //! node may be @c nullptr.
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
    inline DataT* setNodeData(omni::core::TypeId itemType,
                              const ExecutionPath& path,
                              omni::core::ObjectParam<INode> node,
                              NodeDataKey key,
                              std::unique_ptr<DataT> data) noexcept;

    //! Stores a value in a node's key/value datastore.
    //!
    //! The node whose key/value datastore should be used is identified by combining the given path and node in the
    //! given task.
    //!
    //! If a value is already stored at the given @p key it will be replaced.
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
    inline DataT* setNodeData(omni::core::TypeId itemType,
                              const ExecutionTask& path,
                              NodeDataKey key,
                              std::unique_ptr<DataT> data) noexcept;

    //! Discover all execution paths leading to given definition and invoke given function with each of them
    //!
    //! This inline implementation wraps lambda into IApplyOnEachFunction
    //!
    //! The supplied function should have the signature of `void(const ExecutionPath&)`.
    //!
    //! The given @p callback is free to invoke this method.
    //!
    //! @thread_safety The given function will be called serially by this method.  However, other threads may also
    //! invoke this method, meaning the callback must coordinate access to shared data.
    template <typename Fn>
    inline void applyOnEach(omni::core::ObjectParam<omni::graph::exec::unstable::IDef> def, Fn&& callback) noexcept;

    //! Discover all execution paths leading to definition with the given name and invoke the given function with each
    //! of them
    //!
    //! This inline implementation wraps lambda into IApplyOnEachFunction
    //!
    //! The supplied function should have the signature of `void(const ExecutionPath&)`.
    //!
    //! The given @p callback is free to invoke this method.
    //!
    //! @thread_safety The given function will be called serially by this method.  However, other threads may also
    //! invoke this method, meaning the callback must coordinate access to shared data.
    template <typename Fn>
    inline void applyOnEach(const ConstName& name, Fn&& callback) noexcept;
};

#include <omni/graph/exec/unstable/ExecutionTask.h>
#include <omni/graph/exec/unstable/IApplyOnEachFunction.h>
#include <omni/graph/exec/unstable/IDef.h>
#include <omni/graph/exec/unstable/IExecutionStateInfo.h>
#include <omni/graph/exec/unstable/INode.h>

#ifndef DOXYGEN_BUILD // templates are hard to understand, even for doxygen...

inline omni::graph::exec::unstable::IExecutionStateInfo* omni::graph::exec::unstable::IExecutionContext::getStateInfo(
    const ExecutionTask& info) noexcept
{
    return getStateInfo_abi(&(info.getUpstreamPath()), info.getNode());
}

inline omni::graph::exec::unstable::IExecutionStateInfo* omni::graph::exec::unstable::IExecutionContext::getStateInfo(
    const ExecutionPath& path) noexcept
{
    return getStateInfo_abi(&path, nullptr);
}

template <typename T>
inline T* omni::graph::exec::unstable::IExecutionContext::getStateInfoAs(const ExecutionTask& info) noexcept
{
    return omni::graph::exec::unstable::cast<T>(getStateInfo_abi(&(info.getUpstreamPath()), info.getNode()));
}

template <typename T>
inline T* omni::graph::exec::unstable::IExecutionContext::getStateInfoAs(const ExecutionPath& path) noexcept
{
    return omni::graph::exec::unstable::cast<T>(getStateInfo_abi(&path, nullptr));
}

template <typename T>
inline T* omni::graph::exec::unstable::IExecutionContext::getStateInfoAs(const ExecutionPath& path,
                                                                         omni::core::ObjectParam<INode> node) noexcept
{
    return omni::graph::exec::unstable::cast<T>(getStateInfo_abi(&path, node.get()));
}

template <typename T>
inline omni::expected<omni::graph::exec::unstable::Span<T>, omni::core::Result> omni::graph::exec::unstable::
    IExecutionContext::getNodeDataAs(omni::core::TypeId desiredType,
                                     const ExecutionPath& path,
                                     omni::core::ObjectParam<INode> node,
                                     NodeDataKey key) noexcept
{
    omni::core::TypeId outType;
    void* outPtr = nullptr;
    uint64_t outItemSize, outItemCount;
    auto result = getNodeData_abi(&path, node.get(), key, &outType, &outPtr, &outItemSize, &outItemCount);
    if (OMNI_SUCCEEDED(result) && outPtr)
    {
        OMNI_GRAPH_EXEC_FATAL_UNLESS(outType == desiredType);
        OMNI_GRAPH_EXEC_FATAL_UNLESS(outItemSize == sizeof(T));
    }

    OMNI_GRAPH_EXEC_RETURN_EXPECTED(Span<T>(reinterpret_cast<T*>(outPtr), outItemCount), result);
}

template <typename T>
inline omni::expected<omni::graph::exec::unstable::Span<T>, omni::core::Result> omni::graph::exec::unstable::
    IExecutionContext::getNodeDataAs(omni::core::TypeId desiredType, const ExecutionTask& info, NodeDataKey key) noexcept
{
    return getNodeDataAs<T>(desiredType, info.getUpstreamPath(), info.getNode(), key);
}

template <typename SpecifiedT, typename DataT>
inline DataT* omni::graph::exec::unstable::IExecutionContext::setNodeData(omni::core::TypeId itemType,
                                                                          const ExecutionPath& path,
                                                                          omni::core::ObjectParam<INode> node,
                                                                          NodeDataKey key,
                                                                          std::unique_ptr<DataT> data) noexcept
{
    static_assert(std::is_same<SpecifiedT, DataT>::value, "given TypeId does not match the data type");
    static_assert(!std::is_array<DataT>::value, "setting arrays as node data via unique_ptr not yet implemented");

    setNodeData_abi(&path, node.get(), key, itemType, data.get(), sizeof(DataT), 1,
                    [](void* p)
                    {
                        typename std::unique_ptr<DataT>::deleter_type deleter;
                        deleter(reinterpret_cast<DataT*>(p));
                    });
    return data.release(); // now safe to release ownership
}

template <typename SpecifiedT, typename DataT>
inline DataT* omni::graph::exec::unstable::IExecutionContext::setNodeData(omni::core::TypeId itemType,
                                                                          const ExecutionTask& task,
                                                                          NodeDataKey key,
                                                                          std::unique_ptr<DataT> data) noexcept
{
    return setNodeData<SpecifiedT>(itemType, task.getUpstreamPath(), task.getNode(), key, std::move(data));
}

template <typename Fn>
inline void omni::graph::exec::unstable::IExecutionContext::applyOnEach(
    omni::core::ObjectParam<omni::graph::exec::unstable::IDef> def, Fn&& callback) noexcept
{
    class Forwarder : public Implements<IApplyOnEachFunction>
    {
    public:
        Forwarder(Fn&& fn) : m_fn(std::move(fn))
        {
        }

    protected:
        void invoke_abi(const ExecutionPath* path) noexcept override
        {
            OMNI_GRAPH_EXEC_FATAL_UNLESS_ARG(path);
            m_fn(*path);
        }

        Fn m_fn;
    };

    applyOnEachDef_abi(def.get(), omni::core::steal(new Forwarder(std::forward<Fn>(callback))).get());
}

template <typename Fn>
inline void omni::graph::exec::unstable::IExecutionContext::applyOnEach(const ConstName& name, Fn&& callback) noexcept
{
    class Forwarder : public Implements<IApplyOnEachFunction>
    {
    public:
        Forwarder(Fn&& fn) : m_fn(std::move(fn))
        {
        }

    protected:
        void invoke_abi(const ExecutionPath* path) noexcept override
        {
            OMNI_GRAPH_EXEC_FATAL_UNLESS_ARG(path);
            m_fn(*path);
        }

        Fn m_fn;
    };

    applyOnEachDefWithName_abi(&name, omni::core::steal(new Forwarder(std::forward<Fn>(callback))).get());
}
#endif // DOXYGEN_BUILD

#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/graph/exec/unstable/IExecutionContext.gen.h>
