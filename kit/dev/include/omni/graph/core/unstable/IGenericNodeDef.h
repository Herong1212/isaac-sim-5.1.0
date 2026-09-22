// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

//! @file IGenericNodeDef.h
//!
//! @brief Defines @ref omni::graph::core::unstable::IGenericNodeDef.
#pragma once

#include <omni/graph/exec/unstable/INodeDef.h>

#include <omni/core/IObject.h>

#include <omni/graph/core/Handle.h>

namespace omni
{
namespace graph
{
namespace core
{
namespace unstable
{

// forward declarations needed by interface declaration
class IGenericNodeDef;
class IGenericNodeDef_abi;

//! Node definition interface for OmniGraph nodes.
//!
//! This interface allows us to reason about OmniGraph nodes during graph transformation phase and access authoring
//! node associated with this definition.
//!
//! Execution of this definition will callback to OmniGraph node compute method.
class IGenericNodeDef_abi : public omni::core::Inherits<exec::unstable::INodeDef, OMNI_TYPE_ID("omni.graph.core.unstable.IGenericNodeDef")>
{
protected:
    //! Returns a handle to authoring node associated with this definition.
    virtual NodeObj getAuthoringNode_abi() noexcept = 0;
};

//! Smart pointer managing an instance of @ref IGenericNodeDef.
using GenericNodeDefPtr = omni::core::ObjectPtr<IGenericNodeDef>;

} // namespace unstable
} // namespace core
} // namespace graph
} // namespace omni

// generated API declaration
#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/graph/core/unstable/IGenericNodeDef.gen.h>

// custom API declaration

//! @copydoc omni::graph::core::IGenericNodeDef_abi
class omni::graph::core::unstable::IGenericNodeDef : public omni::core::Generated<omni::graph::core::unstable::IGenericNodeDef_abi>
{ };

// additional headers needed for API implementation
// ...

// custom API implementation

// generated API implementation
#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/graph/core/unstable/IGenericNodeDef.gen.h>
