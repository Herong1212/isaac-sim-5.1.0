// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once
#include <omni/core/IObject.h>
#include <omni/core/Omni.h>
#include <omni/inspect/IInspector.h>
#include <omni/graph/core/ISchedulingHints.h>

namespace omni
{
namespace graph
{
namespace core
{

//! The purity of the node implementation. For some context, a "pure" node is
//! one whose initialize, compute, and release methods are entirely deterministic,
//! i.e. they will always produce the same output attribute values for a given set
//! of input attribute values, and do not access, rely on, or otherwise mutate data
//! external to the node's scope
enum class ePurityStatus
{
    //! Node is assumed to not be pure
    eImpure,
    //! Node can be considered pure if explicitly specified by the node author
    ePure
};

//! Declare the ISchedulingHints2 interface definition
OMNI_DECLARE_INTERFACE(ISchedulingHints2);

//! Interface extension for ISchedulingHints that adds a new "pure" hint
class ISchedulingHints2_abi
    : public omni::core::Inherits<ISchedulingHints, OMNI_TYPE_ID("omni.graph.core.ISchedulingHints2")>
{
protected:
    /**
     * Get the flag describing the node's purity state.
     *
     * @returns Value of the PurityStatus flag.
     */
    virtual ePurityStatus getPurityStatus_abi() noexcept = 0;

    /**
     * Set the flag describing the node's purity status.
     *
     * @param[in] newPurityStatus New value of the PurityStatus flag.
     */
    virtual void setPurityStatus_abi(ePurityStatus newPurityStatus) noexcept = 0;
};

} // namespace core
} // namespace graph
} // namespace omni

#include "ISchedulingHints2.gen.h"

//! @cond Doxygen_Suppress
//!
//! API part of the scheduling hints 2 interface
//! @copydoc omni::graph::core::ISchedulingHints2_abi
OMNI_DEFINE_INTERFACE_API(omni::graph::core::ISchedulingHints2)
//! @endcond
{
public:
    //! @copydoc omni::graph::core::ISchedulingHints2::getPurityStatus_abi
    inline omni::graph::core::ePurityStatus getPurityStatus() noexcept
    {
        return getPurityStatus_abi();
    }

    //! @copydoc omni::graph::core::ISchedulingHints2::setPurityStatus_abi
    inline void setPurityStatus(omni::graph::core::ePurityStatus newPurityStatus) noexcept
    {
        setPurityStatus_abi(newPurityStatus);
    }
};
