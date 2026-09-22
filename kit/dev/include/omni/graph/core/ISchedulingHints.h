// Copyright (c) 2021-2023, NVIDIA CORPORATION. All rights reserved.
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

namespace omni
{
namespace graph
{
namespace core
{

//! How does the node access the data described by the enum eAccessLocation
enum class eAccessType
{
    //! There is no access to data of the associated type
    eNone,
    //! There is only read access to data of the associated type
    eRead,
    //! There is only write access to data of the associated type
    eWrite,
    //! There is both read and write access to data of the associated type
    eReadWrite
};

//! What type of non-attribute data does this node access
enum class eAccessLocation
{
    //! Accesses the USD stage data
    eUsd,
    //! Accesses data that is not part of the node or node type
    eGlobal,
    //! Accesses data that is shared by every instance of a particular node type
    eStatic,
    //! Accesses information on the topology of the graph to which the node belongs
    eTopology
};

//! How thread safe is the node during evaluation
enum class eThreadSafety
{
    //! Nodes can be evaluated in multiple threads safely
    eSafe,
    //! Nodes cannot be evaluated in multiple threads safely
    eUnsafe,
    //! The thread safety status of the node type is unknown
    eUnknown
};

//! How the node is allowed to be computed
enum class eComputeRule
{
    //! Nodes are computed according to the default evaluator rules
    eDefault,
    //! The evaluator may skip computing this node until explicitly requested with INode::requestCompute
    eOnRequest
};

//! Declare the ISchedulingHints interface definition
OMNI_DECLARE_INTERFACE(ISchedulingHints);

//! Interface to the list of scheduling hints that can be applied to a node type
class ISchedulingHints_abi
    : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.graph.core.ISchedulingHints")>
{
protected:
    /**
     * Get the threadSafety status (i.e. can be run in parallel with other nodes)
     *
     * @returns Is the node compute threadsafe?
     */
    virtual eThreadSafety getThreadSafety_abi() noexcept = 0;

    /**
     * Set the flag indicating if a node is threadsafe or not.
     *
     * @param[in] newThreadSafety New value of the threadsafe flag
     */
    virtual void setThreadSafety_abi(eThreadSafety newThreadSafety) noexcept = 0;

    /**
     * Get the type of access the node has for a given data type
     *
     * @param[in] dataType Type of data for which access type is being modified
     * @returns Value of the access type flag
     */
    virtual eAccessType getDataAccess_abi(eAccessLocation dataType) noexcept = 0;

    /**
     * Set the flag describing how a node accesses particular data in its compute _abi (defaults to no access).
     * Setting any of these flags will, in most cases, automatically mark the node as "not threadsafe".
     * One current exception to this is allowing a node to be both threadsafe and a writer to USD, since
     * such behavior can be achieved if delayed writebacks (e.g. "registerForUSDWriteBack") are utilized
     * in the node's compute method.
     *
     * @param[in] dataType Type of data for which access type is being modified
     * @param[in] newAccessType New value of the access type flag
     */
    virtual void setDataAccess_abi(eAccessLocation dataType, eAccessType newAccessType) noexcept = 0;

    /**
     * Get the flag describing the compute rule which may be followed by the evaluator.
     *
     * @returns Value of the ComputeRule flag
     */
    virtual eComputeRule getComputeRule_abi() noexcept = 0;

    /**
     * Set the flag describing the compute rule which may be followed by the evaluator.
     *
     * @param[in] newComputeRule New value of the ComputeRule flag
     */
    virtual void setComputeRule_abi(eComputeRule newComputeRule) noexcept = 0;

    /**
     * Runs the inspector on the scheduling hints.
     *
     * @param[in] inspector The inspector class
     * @return true if the inspection ran successfully, false if the inspection type is not supported
     */
    virtual bool inspect_abi(omni::inspect::IInspector* inspector) noexcept = 0;
};

} // namespace core
} // namespace graph
} // namespace omni

#include "ISchedulingHints.gen.h"
