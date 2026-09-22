// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file INodeFactory.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::INodeFactory.
#pragma once

#include <omni/graph/exec/unstable/Assert.h>
#include <omni/graph/exec/unstable/IBase.h>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

// forward declarations needed by interface declaration
class IDef;
class INode;
class INodeFactory;
class INodeFactory_abi;

//! Factory interface for creating @ref omni::graph::exec::unstable::INode objects.
//!
//! Usually used in conjunction with @ref omni::graph::exec::unstable::INodeGraphDef.
//!
//! Factory objects are used by passes (e.g. @ref omni::graph::exec::unstable::IPartitionPass) to create new nodes in a
//! graph definition.
//!
//! It is the responsibility of the factory to hold a reference to the created node. This reference is generally
//! released when the graph is updated.
//!
//! See @ref omni::graph::exec::unstable::createNodeFactory() to generate one of these objects from an invocable object
//! (e.g. @c std::function).
class INodeFactory_abi
    : public omni::core::Inherits<omni::graph::exec::unstable::IBase, OMNI_TYPE_ID("omni.graph.exec.unstable.INodeFactory")>
{
protected:
    //! Creates and returns a new node within the topology from which this factory was created.
    //!
    //! The given node name must not be @c nullptr.
    //!
    //! The given definition must be either @c nullptr, an instance of @ref omni::graph::exec::unstable::INodeDef, or an
    //! instance of @ref omni::graph::exec::unstable::INodeGraphDef.
    //!
    //! It is the responsibility of the factory to hold a reference to the created node. This reference is generally
    //! released when the graph is updated.
    //!
    //! The returned @ref omni::graph::exec::unstable::INode will not have @ref omni::core::IObject::acquire() called on
    //! it.
    //!
    //! The returned pointer must not be @c nullptr.
    //!
    //! @thread_safety This method is not thread safe.
    virtual OMNI_ATTR("not_null, no_acquire") INode* createNode_abi(OMNI_ATTR("in, not_null, c_str") const char* name,
                                                                    IDef* def) noexcept = 0;
};

//! Smart pointer managing an instance of @ref INodeFactory.
using NodeFactoryPtr = omni::core::ObjectPtr<INodeFactory>;

//! Generates an @ref INodeFactory from an invocable object such as a function pointer, functor, etc.
//!
//! The given function should have the signature `INode*(const char*, IDef*)`.
//!
//! It is the responsibility of the factory to hold a reference to the created node. This reference is generally
//! released when the graph is updated.
//!
//! The returned @ref omni::graph::exec::unstable::INode will not have @ref omni::core::IObject::acquire() called on it.
template <typename Fn>
NodeFactoryPtr createNodeFactory(Fn&& fn);

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni

// generated API declaration
#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/graph/exec/unstable/INodeFactory.gen.h>

//! @copydoc omni::graph::exec::unstable::INodeFactory_abi
//!
//! @ingroup groupOmniGraphExecInterfaces
class omni::graph::exec::unstable::INodeFactory
    : public omni::core::Generated<omni::graph::exec::unstable::INodeFactory_abi>
{
public:
    //! @copydoc omni::graph::exec::unstable::INodeFactory_abi::createNode_abi
    INode* createNode(const std::string& name, omni::core::ObjectParam<IDef> def) noexcept
    {
        return createNode_abi(name.c_str(), def.get());
    }

    using omni::core::Generated<omni::graph::exec::unstable::INodeFactory_abi>::createNode;
};

// additional headers needed for API implementation
#include <omni/graph/exec/unstable/INode.h>

#ifndef DOXYGEN_BUILD

template <typename Fn>
omni::graph::exec::unstable::NodeFactoryPtr omni::graph::exec::unstable::createNodeFactory(Fn&& fn)
{
    class FactoryImpl : public Implements<INodeFactory>
    {
    public:
        FactoryImpl(Fn&& fn) : m_fn(std::move(fn))
        {
        }

    protected:
        INode* createNode_abi(const char* name, IDef* def) noexcept override
        {
            return m_fn(name, def); // may throw
        }

        Fn m_fn;
    };

    return omni::core::steal(new FactoryImpl(std::forward<Fn>(fn)));
}

#endif // DOXYGEN_BUILD

// generated API implementation
#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/graph/exec/unstable/INodeFactory.gen.h>
