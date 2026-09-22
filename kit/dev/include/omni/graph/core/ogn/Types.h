// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/graph/core/Handle.h>
#include <omni/fabric/IPath.h>
#include <omni/fabric/IToken.h>

namespace omni {
namespace graph {
namespace core {
namespace ogn {

// ======================================================================
/**
 * Enumeration of the memory locations an attribute's data might have. The data location will determine which of
 * the data accessors will be used, and what type of data they will return. (GPU data will always be returned
 * as raw pointers since the CPU cannot access that memory.)
 *
 * This type will be used as a template parameter to adjust the behaviour of OGN wrapper classes.
 */
enum eMemoryType
{
    kCpu, //!< The attribute's data is always on the CPU
    kCuda, //!< The attribute's data is always on the GPU
    kAny //!< The attribute's data location can be either, decided at runtime
};

// ======================================================================
/**
 * Enumeration of an attribute's access type. In order to provide information to the scheduler about how
 * fabric data will be accessed, one of these access types is associated with all generated attributes.
 *
 * This type will be used as a template parameter to adjust the behaviour of OGN wrapper classes.
 */
enum eAttributeType
{
    kOgnInput,
    kOgnOutput,
    kOgnState
};

// ======================================================================
/**
 * Severity level for logging messages.
 */
enum class Severity : uint8_t
{
    eInfo = 0,
    eWarning,
    eError,

    eCount
};

// ======================================================================
/**
 * When templating methods by data type the template types must be unique. The implementation of
 * NameToken in iComputeGraph defines it as a simple uint64_t, which is also a raw data type used by OGN.
 * To allow different templates to be instantiated for these two data types, identical in implementation but
 * vastly different in semantics, this wrapper can be used instead as a drop-in replacement for NameToken.
 *
 * Thus these two template instantiations will be determined to be unique by the compiler, but the data
 * passed in will be identical, to be interpreted in the correct way by the function:
 *
 * template <typename DataType> void myData(DataType& value);
 *     myData(OgnToken&); // Receives an OgnToken, which is directly convertible to NameToken
 *     myData(uint64_t&); // Receives a raw uint64_t
 *
 * This type will be used as a template parameter to adjust the behaviour of OGN wrapper classes.
 */
using Token = omni::fabric::Token;
static_assert(::std::is_convertible<Token, NameToken>::value, "ogn::Token must be equivalent to NameToken");

using Path = omni::fabric::Path;
static_assert(::std::is_convertible<Path, TargetPath>::value, "ogn::Path must be equivalent to TargetPath");

} // namespace ogn
} // namespace core
} // namespace graph
} // namespace omni

// Declare this outside of the namespaces, relying on the uniqueness of the name to provide easy access
using OgnToken = omni::graph::core::ogn::Token;
using OgnPath = omni::graph::core::ogn::Path;

// Generated code is kept smaller by assuming this namespace is active. The alternative would be to explicitly
// reference all types and values used by the generated code, which would end up amounting to the same thing.
// Core types can be accessed directly (e.g. getDataW()) and OGN types use the shortened "ogn::string"
using namespace omni::graph::core;
