// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file NodeDef.h
//!
//! @brief Declares @ref omni::graph::exec::unstable::INodeDef.
#pragma once

#include <omni/graph/exec/unstable/Assert.h>
#include <omni/graph/exec/unstable/INodeDef.h>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

//! @copydoc omni::graph::exec::unstable::INodeDef
template <typename... Bases>
class NodeDefT : public Implements<Bases...>
{
public:
    //! Construct node definition
    //!
    //! This function always returns a valid pointer.
    //!
    //! @param definitionName Definition name is considered as a token that transformation passes can register
    //!                       against.  This name must not be @c nullptr.
    static omni::core::ObjectPtr<NodeDefT> create(const carb::cpp::string_view& definitionName) noexcept
    {
        OMNI_GRAPH_EXEC_ASSERT(definitionName.data());
        return omni::core::steal(new NodeDefT(definitionName));
    }

protected:
    //! @copydoc omni::graph::exec::unstable::IDef::execute_abi
    //!
    //! Unless overriden by a subclass, returns @ref Status::eSuccess.
    Status execute_abi(ExecutionTask* info) noexcept override
    {
        return Status::eSuccess;
    }

    //! @copydoc omni::graph::exec::unstable::IDef::getSchedulingInfo_abi
    //!
    //! Unless overriden by a subclass, returns @ref SchedulingInfo::eSerial.
    SchedulingInfo getSchedulingInfo_abi(const ExecutionTask* info) noexcept override
    {
        return SchedulingInfo::eSerial;
    }

    //! @copydoc omni::graph::exec::unstable::IDef::getName_abi
    const ConstName* getName_abi() noexcept override
    {
        return &m_name;
    }

    //! Constructor
    NodeDefT(const carb::cpp::string_view& definitionName) noexcept : m_name{ definitionName }
    {
    }

private:
    ConstName m_name; //!< We associate a name with each opaque definition. This is where we store it.
};

//! Core NodeDef implementation for @ref omni::graph::exec::unstable::INodeDef
//!
//! See @ref omni::graph::exec::unstable::NodeDefT for documentation on this type.
using NodeDef = NodeDefT<INodeDef>;

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni
