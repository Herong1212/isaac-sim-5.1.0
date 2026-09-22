// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file IPassFactory.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::IPassFactory.
#pragma once

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
class IGraphBuilder;
class IPass;
class IPassFactory;
class IPassFactory_abi;

//! Factory interface for creating @ref omni::graph::exec::unstable::IPass objects.
//!
//! Usually used in conjunction with @ref omni::graph::exec::unstable::IPassRegistry.
//!
//! See @ref omni::graph::exec::unstable::createPassFactory() to generate one of these objects from an invocable object
//! (e.g. @c std::function).
//!
//! See @rstref{Pass Concepts <ef_pass_concepts>} for an in-depth guide on how passes are used during graph
//! construction.
//!
//! See @ref groupOmniGraphExecPassRegistration for more information about pass registration.
//!
//! See @ref groupOmniGraphExecPasses for more pass related functionality.
class IPassFactory_abi
    : public omni::core::Inherits<omni::graph::exec::unstable::IBase, OMNI_TYPE_ID("omni.graph.exec.unstable.IPassFactory")>
{
protected:
    //! Creates and returns a pass.
    //!
    //! The returned pointer is always valid.
    //!
    //! @p builder is the graph builder the new pass should use.  @p builder must not be @c nullptr.
    //!
    //! The returned @ref omni::graph::exec::unstable::IPass will have @ref omni::core::IObject::acquire() called on it.
    //!
    //! @thread_safety This method is thread safe and expected to be called concurrently by @ref
    //! omni::graph::exec::unstable::IPassPipeline.
    virtual OMNI_ATTR("not_null") IPass* createPass_abi(OMNI_ATTR("not_null") IGraphBuilder* builder) noexcept = 0;
};

//! Smart pointer managing an instance of @ref IPassFactory.
using PassFactoryPtr = omni::core::ObjectPtr<IPassFactory>;

//! Generates an @ref IPassFactory from an invocable object such as a function pointer, functor, etc.
//!
//! The given function should have the signature `IPass*(IGraphBuilder*)`.
//!
//! This function always returns a valid pointer.
//!
//! The given invocable object must be thread safe since it will be called concurrently in @ref
//! omni::graph::exec::unstable::IPassPipeline.
template <typename Fn>
PassFactoryPtr createPassFactory(Fn&& fn) noexcept;

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni

// generated API declaration
#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/graph/exec/unstable/IPassFactory.gen.h>

//! @copydoc omni::graph::exec::unstable::IPassFactory_abi
//!
//! @ingroup groupOmniGraphExecPassRegistration groupOmniGraphExecInterfaces
class omni::graph::exec::unstable::IPassFactory
    : public omni::core::Generated<omni::graph::exec::unstable::IPassFactory_abi>
{
};

// additional headers needed for API implementation
#include <omni/graph/exec/unstable/IGraphBuilder.h>
#include <omni/graph/exec/unstable/IPass.h>

#ifndef DOXYGEN_BUILD

template <typename Fn>
omni::graph::exec::unstable::PassFactoryPtr omni::graph::exec::unstable::createPassFactory(Fn&& fn) noexcept
{
    class FactoryImpl : public Implements<IPassFactory>
    {
    public:
        FactoryImpl(Fn&& fn) : m_fn(std::move(fn))
        {
        }

    protected:
        IPass* createPass_abi(IGraphBuilder* builder) noexcept override
        {
            PassPtr pass = m_fn(builder); // may throw
            return pass.detach();
        }

        Fn m_fn;
    };

    return omni::core::steal(new FactoryImpl(std::forward<Fn>(fn)));
}

#endif // DOXYGEN_BUILD

// generated API implementation
#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/graph/exec/unstable/IPassFactory.gen.h>
