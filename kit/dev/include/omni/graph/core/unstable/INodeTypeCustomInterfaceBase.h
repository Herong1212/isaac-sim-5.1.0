// Copyright (c) 2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

//! @file INodeTypeCustomInterfaceBase.h
//!
//! @brief Defines @ref omni::graph::core::unstable::INodeTypeCustomInterfaceBase.
#pragma once

#include <omni/graph/core/Handle.h>
#include <omni/graph/exec/unstable/IBase.h>

namespace omni
{
namespace graph
{
namespace core
{
namespace unstable
{

// Forward declarations needed by interface declaration.
class INodeTypeCustomInterfaceBase;
class INodeTypeCustomInterfaceBase_abi;

//! Base class from which all custom interfaces that wish to be registered against specific node types derive from.
//!
//! Note that any classes which implement this interface should have a public constructor of the form
//! `Impl(const char* const nodeTypeName, ...)`, i.e. a constructor whose first argument is the name of the node type.
class INodeTypeCustomInterfaceBase_abi
    : public omni::core::Inherits<exec::unstable::IBase, OMNI_TYPE_ID("omni.graph.core.unstable.INodeTypeCustomInterfaceBase")>
{
protected:
    //! Callback method that's invoked upon OG node destruction. Allows custom interface implementations (which are
    //! created for specific node types) to clear out any cached stateful data that they may have keyed against specific
    //! node objects.
    virtual void clearSharedState_abi(const NodeObj& nodeObj) noexcept = 0;

    //! Callback method that's invoked during instanced graph destruction. Allows custom interface implementations
    //! (which are created for specific node types) to clear out any cached stateful data that they may have keyed
    //! against specific instances of node objects (i.e., node objects residing in specific graph instances).
    virtual void clearPerInstanceState_abi(const NodeObj& nodeObj, const GraphInstanceID& graphInstanceId) noexcept = 0;
};

} // namespace unstable
} // namespace core
} // namespace graph
} // namespace omni

// Generated API declaration.
#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/graph/core/unstable/INodeTypeCustomInterfaceBase.gen.h>

//! @copydoc omni::graph::core::unstable::INodeTypeCustomInterfaceBase_abi
class omni::graph::core::unstable::INodeTypeCustomInterfaceBase
    : public omni::core::Generated<omni::graph::core::unstable::INodeTypeCustomInterfaceBase_abi>
{
};

// Additional headers needed for API implementation.

// Generated API implementation.
#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/graph/core/unstable/INodeTypeCustomInterfaceBase.gen.h>
