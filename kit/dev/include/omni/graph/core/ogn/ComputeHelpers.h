// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

// =================================================================================================================
// This file contains helper functions for building c++ nodes that perform the operations on union runtime attributes
// with lots of different types. These helpers also support array broadcasting. This is especially useful
// for generic utility nodes such as Add, Multiply, etc.
// =================================================================================================================
#ifdef THIS_IS_INCLUDED_IN_THE_DOCUMENTATION
// The folllowing block describes the ogn::compute API and how it is intended to be used.
//
// begin-compute-helpers-interface-description

/*
 * In python, working with extended unions types is easy - dynamic type resolution is incredibly simple, and NumPy
 * handles array broadcasting, where a vector with smaller dimensions will be "repeated" so the inputs are compatible
 * the compute helpers API hopes to provide utilities that make working with C++ union types significantly easier
 */

// The compute helpers API primarily relies on using generic lambdas for operations.
// The compiler will resolve the input types, allowing us to use the add function for a variety
// of different types (eg: double, float, int)
auto add = [](auto const& a, auto const& b, auto& result) { result = a + b; };

// We can use the ogn::compute::tryCompute function to attempt to apply add() to a variety of different types
// tryCompute will return true if the types are resolved properly, and false if they aren't. an ogn::compute::InputError
// will be thrown if the types are resolved but the computation is impossible (due to different array sizes, for example)
if (ogn::compute::tryCompute(db.inputs.a().get<int>(), db.inputs.b().get<int>(), db.inputs.result().get<int>(), add))
    return true;
else if (ogn::compute::tryCompute(db.inputs.a().get<float>(), db.inputs.b().get<float>(), db.inputs.result().get<float>(), add))
    return true;
// For arrays, add() will be called with each input in parallel, ie: add(a[i], b[i], result[i]).
else if (ogn::compute::tryCompute(db.inputs.a().get<double[]>(), db.inputs.b().get<double[]>(), db.inputs.result().get<double[]>(), add))
    return true;
// For a mixture of arrays and singulars, the singular will be broadcast: add(a[i], b, result[i])
else if (ogn::compute::tryCompute(db.inputs.a().get<double[]>(), db.inputs.b().get<double>(), db.inputs.result().get<double[]>(), add))
    return true;
else
{
    db.logWarning("Failed to resolve input types");
    return false;
}

/*
 * Sometimes we want to support a mix of arrays and singular values, using broadcasting to match the singular values
 * to the dimensions of the array. For this, we can use ogn::compute::tryComputeWithArrayBroadcasting().
 */

// Assuming a, b, and result all have base type int, tryComputeUsingArrrayBroadcasting will attempt to resolve each
// input to int or int[]. Then, perform broadcasting as necessary.
if (ogn::compute::tryComputeUsingArrrayBroadcasting<int>(db.inputs.a(), db.inputs.b(), db.inputs.sum(), add))
    return true;
// Assumes a has base type int, b has base type float, and result has base type float
else if (ogn::compute::tryComputeUsingArrrayBroadcasting<int, float, float>(db.inputs.a(), db.inputs.b(), db.inputs.sum(), add))
    return true;
// Also supports a random number of arguments, and a result. Here is an example with 3 arguments:
else if (ogn::compute::tryComputeUsingArrrayBroadcasting<int>(db.inputs.a(), db.inputs.b(), db.inputs.c(), db.inputs.sum(), add3))
    return true;
else if (ogn::compute::tryComputeUsingArrrayBroadcasting<float, int, int, float>(db.inputs.a(), db.inputs.b(), db.inputs.c(), db.inputs.sum(), add3))
    return true;

/*
 * For tuple types, you'll have to change your lambda function to work with c++ fixed size arrays T[N]
 * Your lambda function will need to be specialized for each different N.
 * For this, I recommend using a helper function in your node implementation
 */

// Empty namespace to avoid multiple declarations at linking
namespace {
// compute helper assuming a scalar base type
template<typename T>
bool tryComputeAssumingType(db_type& db)
{
    auto functor = [](auto const& a, auto const& b, auto& result)
    {
        result = a + b;
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<T>(db.inputs.a(), db.inputs.b(), db.outputs.sum(), functor);
}
// compute helper assuming a tuple base type
template<typename T, size_t N>
bool tryComputeAssumingType(db_type& db)
{
    auto functor = [](auto const& a, auto const& b, auto& result)
    {
        for(size_t i = 0; i < N; i++)
        {
            result[i] = a[i] + b[i];
        }
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<T[N]>(db.inputs.a(), db.inputs.b(), db.outputs.sum(), functor);
}
} // namespace

// ...

if (tryComputeAssumingType<int>(db)) return true;  // Calls the scalar helper
else if (tryComputeAssumingType<float>(db)) return true;
else if (tryComputeAssumingType<int, 3>(db)) return true;  // Calls the tuple helper
else if (tryComputeAssumingType<float, 3>(db)) return true;

/*
 * You may also want to support adding scalars to tuples. The above code unfortunately won't support that.
 *  For Tuple broadcasting, you can use ogn::compute::tryComputeWithTupleBroadcasting. This function will
 *  resolve each input to type T, T[], T[N] or T[N][], performing broadcasting as necessary.
 */

template<typename T, size_t N>
bool tryComputeAssumingType(db_type& db)
{
    auto functor = [](auto const& a, auto const& b, auto& result)
    {
        result = a + b;
    };
    // Perform computation with tuple AND array broadcasting
    return ogn::compute::tryComputeWithTupleBroadcasting<T, N>(db.inputs.a(), db.inputs.b(), db.outputs.sum(), functor);
}

// end-compute-helpers-interface-description
//
#endif

#include <algorithm>
#include <utility>
#include <type_traits>
#include <string>
#include <exception>

// clang-format off
#include <omni/graph/core/PreUsdInclude.h>
#include <pxr/base/gf/traits.h>
#include <omni/graph/core/PostUsdInclude.h>
// clang-format on

#include <omni/graph/core/ogn/RuntimeAttribute.h>
#include <omni/graph/core/ogn/SimpleAttribute.h>
#include <omni/graph/core/ogn/ArrayAttribute.h>
#include <omni/graph/core/ogn/array.h>

namespace omni {
namespace graph {
namespace core {
namespace ogn {
namespace compute {

/* Tuple Attribute type traits */
template<class T>
using is_tuple_data = PXR_NS::GfIsGfVec<T>;

// Error thrown when inputs are not valid
struct InputError : public std::exception
{
   std::string s;
   InputError(std::string ss) : s(ss) {}
   ~InputError() throw () {}
   const char* what() const throw() { return s.c_str(); }
};

#include <omni/graph/core/ogn/ComputeHelpersDetails.h>
#include <omni/graph/core/ogn/ComputeHelpersDynamicInputsDetails.h>


/** ========================= TryCompute utility =========================== */

/**
 * Syntax:
 *   tryCompute(inputs..., result, functor [, count])
 * 
 * Tries to apply the provided functor to the provided
 * arguments.
 * The number of inputs is random, and determined by the provided functor.
 * It is assumed that the "result" argument is a RuntimeAttribute
 * while inputs can be either RuntimeAttribute or direct POD/const_array<>.
 *
 * @param inputs: Random number of inputs
 * @param result: the last argument for the functor and the destination for the computation
 * @param functor: The computation to perform. Should have signature: (inputs const&..., result&) -> void
 * @param [Optional] count: Activates vectorized compute of 'count' elements
 * @return True if the inputs were resolved properly, false if not
 */

template <typename... Arguments>
inline bool tryCompute(Arguments&&... args)
{
    using VH = Private::VectorizationHelper<Arguments...>;

    return Private::tryCompute_ReverseHelper(
                        std::forward_as_tuple(args...),
                        std::make_index_sequence<sizeof...(Arguments) - 2 - VH::Offset>(),
                        VH::count(std::forward_as_tuple(args...)));
}

/** ========================= TryComputeArray utility =========================== */

/**
 * Syntax:
 *   tryComputeWithArrayBroadcasting<T>(inputs..., result, functor [, count])
 * OR
 *   tryComputeWithArrayBroadcasting<TypeIn0, TypeIn1,..., TypeResult>(inputs..., result, functor [, count])
 * 
 * Apply the functor to runtime/regular set of attributes, assuming they all have base types T (syntax #1),
 *   or the provided set of types (syntax #2).
 * The result is assumed to be a runtime attribute. If if it a singular value, inputs must be as well.
 * If it is an array, each input is either an array or a singular value.
 *   IE, this function will attempt to resolve each input to T or T[] etc.
 * Singular values will be broadcast to the length of the largest array in the input.
 * All input arrays must be of the same length, or an ogn::compute::InputError will be thrown
 *
 *  @param inputs: Random number of inputs passed to the functor
 *  @param result: the last argument for the functor and the destination for the computation
 *  @param functor: The computation to perform. Should have signature: (inputs const&..., result&) -> void
 *  @param [Optional] count: Activates vectorized compute of 'count' elements
 *  @return True if the inputs were resolved properly, false if not
 */

template <typename... ComputeTypes, typename... Arguments>
inline bool tryComputeWithArrayBroadcasting(Arguments&&... args)
{
    using VH = Private::VectorizationHelper<Arguments...>;

    //Validation of template arguments number
    static_assert(
        sizeof...(ComputeTypes) == 1 /*single type*/ || sizeof...(ComputeTypes) == sizeof...(Arguments) - 1 /*functor*/ - VH::Offset,
        "Wrong number of template arguments provided to tryComputeWithArrayBroadcasting");

    //Make the call
    return Private::tryComputeWithArrayBroadcasting_ReverseHelper<1, ComputeTypes...>(
        std::forward_as_tuple(args...), std::make_index_sequence<sizeof...(Arguments) - 2 /*functor and output*/ - VH::Offset>(),
        VH::count(std::forward_as_tuple(args...)));
}



/** ========================= TryComputeTuple utility =========================== */

// Public interface
//  Template argument(s): Single type + tuple components count,
//                     or Type pack to apply to input/output + tuple components count
// Arguments: input, input, input, ..., output, functor

/**
 * Syntax:
 *   #1: tryComputeWithTupleBroadcasting<SIZE, T>(inputs..., result, functor [, count])
 * OR
 *   #2: tryComputeWithTupleBroadcasting<SIZE, TypeIn0, TypeIn1,..., TypeResult>(inputs..., result, functor [, count])
 *
 * Apply the functor to runtime/regular set of attributes, assuming they all have base types T (syntax #1),
 *   or the provided set of types (syntax #2).
 * The result is assumed to be a runtime attribute.
 *   If it is a singular value, inputs must be as well.
 *   If it is a tuple[SIZE] value, inputs can be either a singular value or a tuple[SIZE].
 *   If it is an array of (tuple) values, each input is either an array of (tuple) value or a singular (tuple) value.
 *    IE, function will attempt to resolve each input to T, T[SIZE], T[] or T[SIZE][]
 * Singular values will be broadcast to the length of the largest array in the input.
 * All input arrays must be of the same length, or an ogn::compute::InputError will be thrown
 *
 *  @param inputs: Random number of inputs passed to the functor
 *  @param result: the last argument for the functor and the destination for the computation
 *  @param functor: The computation to perform. Should have signature: (inputs const&..., result&) -> void
 *  @param [Optional] count: Activates vectorized compute of 'count' elements
 *  @return True if the inputs were resolved properly, false if not
 */

/** ========================= UPGRADE NOTE / COMPILE ERROR ON EXISTING USAGE =========================== */
// Order of the template arguments has changed, starting in kit 105.
// The tuple count is now the first argument instead of the last one.
// 
// If you get there with a compile error,  modify your code as follow:
// 
//    [OLD]  tryComputeWithTupleBroadcasting<T0, T1, ..., N>(...)
//    [NEW]  tryComputeWithTupleBroadcasting<N, T0, T1, ...>(...)
/** ==================================================================================================== */

template <size_t N, typename... ComputeTypes, typename... Arguments>
inline bool tryComputeWithTupleBroadcasting(Arguments&&... args)
{
    using VH = Private::VectorizationHelper<Arguments...>;

    static_assert(sizeof...(ComputeTypes) == 1 /*single type*/ ||
        sizeof...(ComputeTypes) == sizeof...(Arguments) - 1 /*functor*/ - VH::Offset,
        "Wrong number of template arguments provided to tryComputeWithTupleBroadcasting");

    return Private::tryComputeWithArrayBroadcasting_ReverseHelper<N, ComputeTypes...>(
        std::forward_as_tuple(args...),
        std::make_index_sequence<sizeof...(Arguments) - 2 - VH::Offset>(),
        VH::count(std::forward_as_tuple(args...)));
}


/** ========================= TryComputeArrayWithMultipleInputs utility =========================== */

/**
 * Syntax:
 *   tryComputeInputsWithArrayBroadcasting<T>(inputArray, result, functor [, count])
 *
 * Apply the functor to an array of runtime attributes, assuming they all have base types T.
 * The result is assumed to be a runtime attribute. If if it a singular value, inputs must be as well.
 * If it is an array, each input is either an array or a singular value.
 *   IE, this function will attempt to resolve each input to T or T[] etc.
 * Singular values will be broadcast to the length of the largest array in the input.
 * All input arrays must be of the same length, or an ogn::compute::InputError will be thrown.
 *
 * Note: The functor is an accumulator. It always receives one input and the result value
 *       and expects the input to be iteratively added to the result.
 *       The result is initialized with the first input before the functor is invoked.
 *
 * For example, to subtract all inputs from the first input the functor can be implemented as follows:
 *      auto functor = [](const auto& input, auto& result)
 *      {
 *          result = result - input;
 *      };
 *
 *  @param inputs: An array of runtime input attributes
 *  @param result: The last argument for the functor and the destination for the computation
 *  @param functor: The computation to perform. Should have signature: (input const&..., result&) -> void
 *  @param [Optional] count: Activates vectorized compute of 'count' elements
 *  @return True if the inputs were resolved properly, false if not
 */
 
template <typename ComputeType, typename Functor>
inline bool tryComputeInputsWithArrayBroadcasting(gsl::span<ogn::RuntimeAttribute<ogn::kOgnInput, ogn::kCpu> const> const inputs,
                                                  ogn::RuntimeAttribute<ogn::kOgnOutput, ogn::kCpu> result,
                                                  Functor functor,
                                                  size_t count = 1)
{
    using InputType = typename ogn::RuntimeAttribute<ogn::kOgnInput, ogn::kCpu>;
    return Private::tryComputeInputsWithArrayBroadcasting<ComputeType, InputType, Functor>(inputs, result, functor, count);
}


/** ========================= TryComputeTupleWithMultipleInputs utility =========================== */

/**
 * Syntax:
 *   tryComputeInputsWithTupleBroadcasting<T>(inputArray, result, functor [, count])
 *
 * Apply the functor to an array of runtime attributes, assuming they all have base types T.
 * The result is assumed to be a runtime attribute.
 *   If it is a singular value, inputs must be as well.
 *   If it is a tuple[SIZE] value, inputs can be either a singular value or a tuple[SIZE].
 *   If it is an array of (tuple) values, each input is either an array of (tuple) value or a singular (tuple) value.
 *    IE, function will attempt to resolve each input to T, T[SIZE], T[] or T[SIZE][]
 * Singular values will be broadcast to the length of the largest array in the input.
 * All input arrays must be of the same length, or an ogn::compute::InputError will be thrown.
 *
 * Note: The functor is an accumulator. It always receives one input and the result value
 *       and expects the input to be iteratively added to the result.
 *       The result is initialized with the first input before the functor is invoked.
 *
 * For example, to subtract all inputs from the first input the functor can be implemented as follows:
 *      auto functor = [](const auto& input, auto& result)
 *      {
 *          result = result - input;
 *      };
 *
 *  @param inputs: An array of runtime input attributes
 *  @param result: the last argument for the functor and the destination for the computation
 *  @param functor: The computation to perform. Should have signature: (input const&..., result&) -> void
 *  @param [Optional] count: Activates vectorized compute of 'count' elements
 *  @return True if the inputs were resolved properly, false if not
 */

template <size_t TUPLE_SIZE, typename ComputeType, typename Functor>
inline bool tryComputeInputsWithTupleBroadcasting(gsl::span<ogn::RuntimeAttribute<ogn::kOgnInput, ogn::kCpu> const> const inputs,
                                                  ogn::RuntimeAttribute<ogn::kOgnOutput, ogn::kCpu> result,
                                                  Functor functor,
                                                  size_t count = 1)
{
    using InputType = typename ogn::RuntimeAttribute<ogn::kOgnInput, ogn::kCpu>;
    return Private::tryComputeInputsWithTupleBroadcasting<TUPLE_SIZE, ComputeType, InputType, Functor>(inputs, result, functor, count);
}


} // namespace compute
} // namespace ogn
} // namespace core
} // namespace graph
} // namespace omni
