// Copyright (c) 2023-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

//! @file IPrivateNodeDef.h
//!
//! @brief Defines @ref omni::graph::core::unstable::IPrivateNodeDef.
#pragma once

#include <omni/graph/core/Handle.h>
#include <omni/graph/core/iComputeGraph.h>
#include <omni/graph/exec/unstable/ConstName.h>
#include <omni/graph/exec/unstable/IBase.h>
#include <omni/graph/exec/unstable/SchedulingInfo.h>
#include <omni/graph/exec/unstable/Status.h>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

// forward declarations needed by interface declaration
class ExecutionTask;

}
}

namespace core
{
namespace unstable
{

// forward declarations needed by interface declaration
class IPrivateNodeDef;
class IPrivateNodeDef_abi;

//! Base class for guard objects used to set the correct CUDA device during the node execution.
class ICudaDeviceScopeGuard
{
public:
    //! Destructor.
    virtual ~ICudaDeviceScopeGuard()
    {
    }
};

//! This is a private interface.  Rather than directly using this private interface,
//! access the functionality this interface provides by subclassing GenericNodeDef
class IPrivateNodeDef_abi
    : public omni::core::Inherits<exec::unstable::IBase, OMNI_TYPE_ID("omni.graph.core.unstable.IPrivateNodeDef")>
{
protected:
    //! Acquire internal information about bucketing of instances for vectorized execution
    //!
    //! Arguments must not be @c nullptr.
    virtual void getInstanceInfo_abi(OMNI_ATTR("in, out, not_null, ref")
                                         omni::graph::exec::unstable::ExecutionTask* info,
                                     OMNI_ATTR("out, not_null, ref") InstanceIndex* retBaseInstanceIndex,
                                     OMNI_ATTR("out, not_null, ref") size_t* retNumberOfInstances) noexcept = 0;

    //! Creates a scope object which guarantees that the CUDA device is set for the host thread is active.
    //! The CUDA device is reverted when the object is destroyed.
    //!
    //! If the current CUDA device is already active, it is not changed.
    //!
    //! @return Returns the scope object which should be destroyed at the end of the scope.
    virtual ICudaDeviceScopeGuard* enforceCudaDevice_abi() noexcept = 0;
};

} // namespace unstable
} // namespace core
} // namespace graph
} // namespace omni

// generated API declaration
#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/graph/core/unstable/IPrivateNodeDef.gen.h>

// custom API declaration

//! @copydoc omni::graph::core::IPrivateNodeDef_abi
class omni::graph::core::unstable::IPrivateNodeDef
    : public omni::core::Generated<omni::graph::core::unstable::IPrivateNodeDef_abi>
{
};

// custom API implementation

// generated API implementation
#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/graph/core/unstable/IPrivateNodeDef.gen.h>
