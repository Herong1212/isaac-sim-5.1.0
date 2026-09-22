// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include "TemplateUtils.h"

#include <omni/graph/core/iComputeGraph.h>

#include <cstddef>
#include <tuple>
#include <vector>

namespace omni
{
namespace graph
{
namespace core
{

// The templates for extracting data do not like double pointers so use this type for assigning strings
using CString = char*;

// NOTE: This file is a work in progress, for assessing possible interfaces, not yet for use.

// -Wall will warn about these inline functions not being used
#if defined(__GNUC__)
#    pragma GCC diagnostic push
#    pragma GCC diagnostic ignored "-Wunused-function"
#endif

using Path = omni::fabric::Path;
using Token = omni::fabric::Token;

// ----------------------------------------------------------------------------
// Accessors for accessing attributes by name

static ConstAttributeDataHandle getAttributeR(GraphContextObj const& contextObj,
                                              ConstBundleHandle bundleHandle,
                                              fabric::TokenC name)
{
    ConstAttributeDataHandle out;
    contextObj.iBundle->getAttributesByNameR(&out, contextObj, bundleHandle, &name, 1);
    return out;
}

static ConstAttributeDataHandle getAttributeR(GraphContextObj const& contextObj,
                                              ConstBundleHandle bundleHandle,
                                              Token const& name)
{
    NameToken nameToken = name;
    return getAttributeR(contextObj, bundleHandle, nameToken);
}

template <typename... Types, typename... NameTypes>
std::tuple<Types...> getAttributesR(const GraphContextObj& contextObj,
                                    ConstBundleHandle& primHandle,
                                    std::tuple<NameTypes...> names)
{
    // Check that size(out)==len(names) and that every element of names has type size_t
    const size_t inCount = std::tuple_size<std::tuple<NameTypes...>>::value;
    const size_t outCount = std::tuple_size<std::tuple<Types...>>::value;
    static_assert(inCount == outCount, "Input and output tuples must be of same length");
    static_assert(areTypeT<NameToken, NameTypes...>::value || areTypeT<Token, NameTypes...>::value,
                  "Attribute names must have type NameToken or Token");
    static_assert(areTypeT<ConstAttributeDataHandle, Types...>::value, "Outputs must have type ConstAttributeDataHandle");

    std::tuple<Types...> out;

    // Cast to C-ABI compatible types
    std::tuple<Types...>* outTuplePtr = &out;
    ConstAttributeDataHandle* outPtr = reinterpret_cast<ConstAttributeDataHandle*>(outTuplePtr);
    std::tuple<NameTypes...>* inTuplePtr = &names;
    NameToken* namesPtr = reinterpret_cast<NameToken*>(inTuplePtr);

    // Call C-ABI version of method
    contextObj.iBundle->getAttributesByNameR(outPtr, contextObj, primHandle, namesPtr, inCount);

    return out;
}

static AttributeDataHandle getAttributeW(const GraphContextObj& contextObj, BundleHandle& primHandle, const Token& name)
{
    AttributeDataHandle out;
    NameToken nameToken = name;
    contextObj.iBundle->getAttributesByNameW(&out, contextObj, primHandle, &nameToken, 1);
    return out;
}

template <typename... Types, typename... NameTypes>
std::tuple<Types...> getAttributesW(const GraphContextObj& contextObj,
                                    BundleHandle& primHandle,
                                    std::tuple<NameTypes...> names)
{
    // Check that size(out)==len(names) and that every element of names has type size_t
    const size_t inCount = std::tuple_size<std::tuple<NameTypes...>>::value;
    const size_t outCount = std::tuple_size<std::tuple<Types...>>::value;
    static_assert(inCount == outCount, "Input and output tuples must be of same length");
    static_assert(areTypeT<NameToken, NameTypes...>::value || areTypeT<Token, NameTypes...>::value,
                  "Attribute names must have type NameToken or Token");
    static_assert(areTypeT<AttributeDataHandle, Types...>::value, "Outputs must have type AttributeDataHandle");

    std::tuple<Types...> out;

    // Cast to C-ABI compatible types
    std::tuple<Types...>* outTuplePtr = &out;
    AttributeDataHandle* outPtr = reinterpret_cast<AttributeDataHandle*>(outTuplePtr);
    std::tuple<NameTypes...>* inTuplePtr = &names;
    HandleInt* namesPtr = reinterpret_cast<HandleInt*>(inTuplePtr);

    // Call C-ABI version of method
    contextObj.iBundle->getAttributesByNameW(outPtr, contextObj, primHandle, namesPtr, inCount);

    return out;
}

// ----------------------------------------------------------------------------
// Accessors for accessing attributes by AttributeDataHandle

// Specialization for the read-only data of a single attribute. Get a single attribute handle from getAttributeR
// to pass in as the second parameter.
//     auto constHandle = getAttributeR(contextObj, node, Token("myAttribute"))
//     // Note that the template parameter for the special case is the data type, not a pointer type
//     const auto dataPtr = getDataR<float>(contextObj, constHandle);
template <typename T>
const T* getDataR(const GraphContextObj& contextObj, const ConstAttributeDataHandle& attrHandle)
{
    const T* out;

    const void** outPtr = reinterpret_cast<const void**>(&out);
    contextObj.iAttributeData->getDataR(outPtr, contextObj, &attrHandle, 1);

    return out;
}

// Get the read-only data for an arbitrary list of attributes. Get a tuple attribute handle from getAttributesR
// to pass in as the second parameter.
//     auto constHandles = getAttributesR<ConstAttributeDataHandle, ConstAttributeDataHandle>(contextObj, node,
//                             std::make_tuple(Token("a"), Token("b")))
//     const float* a_value{nullptr};
//     const float* b_value{nullptr};
//     // Note that the template parameters for the general case are pointers to the data type
//     std::tie(a_value, b_value) = getDataR<float*, float*>(contextObj, constHandles);
template <typename... Types, typename... HandleTypes>
std::tuple<Types...> getDataR(const GraphContextObj& contextObj, std::tuple<HandleTypes...> handles)
{
    // Check that size(out)==len(names) and that every element of names has type size_t
    const size_t inCount = std::tuple_size<std::tuple<HandleTypes...>>::value;
    const size_t outCount = std::tuple_size<std::tuple<Types...>>::value;
    static_assert(inCount == outCount, "Input and output tuples must be of same length");
    static_assert(areTypeT<ConstAttributeDataHandle, HandleTypes...>::value,
                  "Attribute handles must have type ConstAttributeDataHandle");

    std::tuple<Types...> out;

    // Cast to C-ABI compatible types
    std::tuple<Types...>* outTuplePtr = &out;
    const void** outPtr = reinterpret_cast<const void**>(outTuplePtr);
    std::tuple<HandleTypes...>* inTuplePtr = &handles;
    ConstAttributeDataHandle* handlesPtr = reinterpret_cast<ConstAttributeDataHandle*>(inTuplePtr);

    // Call C-ABI version of method
    contextObj.iAttributeData->getDataR(outPtr, contextObj, handlesPtr, inCount);

    return out;
}

// Specialization for the read-only GPU data of a single attribute. Get a single attribute handle from getAttributeR
// to pass in as the second parameter.
//     auto handle = getAttributeR(contextObj, node, Token("myAttribute"))
//     // Note that the template parameter for the special case is the data type, not a pointer type
//     const auto gpuData = getDataRGPU<float>(contextObj, handle);
// If you wish to get CPU pointers to GPU data for arrays then use the alternative version:
//     const auto gpuData = getDataRGPUOnCPU<float>(contextObj, handle);
template <typename T>
const T* getDataRGpuAt(const GraphContextObj& contextObj, const ConstAttributeDataHandle& attrHandle, omni::fabric::PtrToPtrKind where)
{
    const T* out;

    const void** outPtr = reinterpret_cast<const void**>(&out);
    contextObj.iAttributeData->getDataRGpuAt(outPtr, contextObj, &attrHandle, 1, where);

    return out;
}
// Syntactic sugar
template <typename T>
const T* getDataRGPU(const GraphContextObj& contextObj, const ConstAttributeDataHandle& attrHandle)
{
    return getDataRGpuAt<T>(contextObj, attrHandle, omni::fabric::PtrToPtrKind::eGpuPtrToGpuPtr);
}
template <typename T>
const T* getDataRGPUOnCPU(const GraphContextObj& contextObj, const ConstAttributeDataHandle& attrHandle)
{
    return getDataRGpuAt<T>(contextObj, attrHandle, omni::fabric::PtrToPtrKind::eCpuPtrToGpuPtr);
}

// Get the read-only GPU data for an arbitrary list of attributes. Get a tuple attribute handle from getAttributesR
// to pass in as the second parameter.
//     auto handles = getAttributesR<ConstAttributeDataHandle, ConstAttributeDataHandle>(contextObj, node,
//                             std::make_tuple(Token("a"), Token("b")))
//     const float* a_gpu_value{nullptr};
//     const float* b_gpu_value{nullptr};
//     // Note that the template parameters for the general case are pointers to the data type
//     std::tie(a_gpu_value, b_gpu_value) = getDataRGPU<float*, float*>(contextObj, handles);
// If you wish to get CPU pointers to GPU data for arrays then use the alternative version:
//     std::tie(a_gpu_value, b_gpu_value) = getDataRGPUOnCPU<float*, float*>(contextObj, handles);
template <typename... Types, typename... NameTypes>
std::tuple<Types...> getDataRGpuAt(const GraphContextObj& contextObj, std::tuple<NameTypes...> handles, omni::fabric::PtrToPtrKind where)
{
    // Check that size(out)==len(names) and that every element of names has type size_t
    const size_t inCount = std::tuple_size<std::tuple<NameTypes...>>::value;
    const size_t outCount = std::tuple_size<std::tuple<Types...>>::value;
    static_assert(inCount == outCount, "Input and output tuples must be of same length");
    static_assert(areTypeT<ConstAttributeDataHandle, NameTypes...>::value,
                  "Attribute handles must have type ConstAttributeDataHandle");

    std::tuple<Types...> out;

    // Cast to C-ABI compatible types
    std::tuple<Types...>* outTuplePtr = &out;
    const void** outPtr = reinterpret_cast<const void**>(outTuplePtr);
    std::tuple<NameTypes...>* inTuplePtr = &handles;
    ConstAttributeDataHandle* handlesPtr = reinterpret_cast<ConstAttributeDataHandle*>(inTuplePtr);

    // Call C-ABI version of method
    contextObj.iAttributeData->getDataRGpuAt(outPtr, contextObj, handlesPtr, inCount, where);

    return out;
}
// Syntactic sugar
template <typename... Types, typename... NameTypes>
std::tuple<Types...> getDataRGPU(const GraphContextObj& contextObj, std::tuple<NameTypes...> handles)
{
    return getDataRGpuAt<Types...>(contextObj, handles, omni::fabric::PtrToPtrKind::eGpuPtrToGpuPtr);
}
template <typename... Types, typename... NameTypes>
std::tuple<Types...> getDataRGPUOnCPU(const GraphContextObj& contextObj, std::tuple<NameTypes...> handles)
{
    return getDataRGpuAt<Types...>(contextObj, handles, omni::fabric::PtrToPtrKind::eCpuPtrToGpuPtr);
}

// Specialization for the writable data of a single attribute. Get a single attribute handle from getAttributeW
// to pass in as the second parameter.
//     auto handle = getAttributeW(contextObj, node, Token("myAttribute"))
//     // Note that the template parameter for the special case is the data type, not a pointer type
//     auto dataPtr = getDataW<float>(contextObj, handle);
template <typename T>
T* getDataW(const GraphContextObj& contextObj, AttributeDataHandle const& attrHandle)
{
    T* out;

    void** outPtr = reinterpret_cast<void**>(&out);
    contextObj.iAttributeData->getDataW(outPtr, contextObj, &attrHandle, 1);

    return out;
}

// Get the writable data for an arbitrary list of attributes. Get a tuple attribute handle from getAttributesW
// to pass in as the second parameter.
//     auto handles = getAttributesW<AttributeDataHandle, AttributeDataHandle>(contextObj, node,
//                             std::make_tuple(Token("a"), Token("b")))
//     float* a_value{nullptr};
//     float* b_value{nullptr};
//     // Note that the template parameters for the general case are pointers to the data type
//     std::tie(a_value, b_value) = getDataW<float*, float*>(contextObj, handles);
template <typename... Types, typename... NameTypes>
std::tuple<Types...> getDataW(const GraphContextObj& contextObj, std::tuple<NameTypes...> handles)
{
    // Check that size(out)==len(names) and that every element of names has type size_t
    const size_t inCount = std::tuple_size<std::tuple<NameTypes...>>::value;
    const size_t outCount = std::tuple_size<std::tuple<Types...>>::value;
    static_assert(inCount == outCount, "Input and output tuples must be of same length");
    static_assert(
        areTypeT<AttributeDataHandle, NameTypes...>::value, "Attribute handles must have type AttributeDataHandle");

    std::tuple<Types...> out;

    // Cast to C-ABI compatible types
    std::tuple<Types...>* outTuplePtr = &out;
    void** outPtr = reinterpret_cast<void**>(outTuplePtr);
    std::tuple<NameTypes...>* inTuplePtr = &handles;
    AttributeDataHandle* handlesPtr = reinterpret_cast<AttributeDataHandle*>(inTuplePtr);

    // Call C-ABI version of method
    contextObj.iAttributeData->getDataW(outPtr, contextObj, handlesPtr, inCount);

    return out;
}

// Specialization for the writable GPU data of a single attribute. Get a single attribute handle from getAttributeW
// to pass in as the second parameter.
//     auto handle = getAttributeW(contextObj, node, Token("myAttribute"))
//     // Note that the template parameter for the special case is the data type, not a pointer type
//     auto gpuData = getDataWGPU<float>(contextObj, handle);
// If you wish to get CPU pointers to GPU data for arrays then use the alternative version:
//     auto gpuData = getDataWGPUOnCPU<float>(contextObj, handle);
template <typename T>
T* getDataWGpuAt(const GraphContextObj& contextObj, AttributeDataHandle const& attrHandle, omni::fabric::PtrToPtrKind whereGpuPtrs)
{
    T* out;

    void** outPtr = reinterpret_cast<void**>(&out);
    contextObj.iAttributeData->getDataWGpuAt(outPtr, contextObj, &attrHandle, 1, whereGpuPtrs);

    return out;
}
// Syntactic sugar
template <typename T>
T* getDataWGPU(const GraphContextObj& contextObj, AttributeDataHandle const& attrHandle)
{
    return getDataWGpuAt<T>(contextObj, attrHandle, omni::fabric::PtrToPtrKind::eGpuPtrToGpuPtr);
}
template <typename T>
T* getDataWGPUOnCPU(const GraphContextObj& contextObj, AttributeDataHandle const& attrHandle)
{
    return getDataWGpuAt<T>(contextObj, attrHandle, omni::fabric::PtrToPtrKind::eCpuPtrToGpuPtr);
}

// Get the writable GPU data for an arbitrary list of attributes. Get a tuple attribute handle from getAttributesW
// to pass in as the second parameter.
//     auto handles = getAttributesW<AttributeDataHandle, AttributeDataHandle>(contextObj, node,
//                             std::make_tuple(Token("a"), Token("b")))
//     float* a_gpu_value{nullptr};
//     float* b_gpu_value{nullptr};
//     // Note that the template parameters for the general case are pointers to the data type
//     std::tie(a_gpu_value, b_gpu_value) = getDataWGPU<float*, float*>(contextObj, handles);
// If you wish to get CPU pointers to GPU data for arrays then use the alternative version:
//     std::tie(a_gpu_value, b_gpu_value) = getDataWGPUOnCPU<float*, float*>(contextObj, handles);
template <typename... Types, typename... NameTypes>
std::tuple<Types...> getDataWGpuAt(const GraphContextObj& contextObj, std::tuple<NameTypes...> handles, omni::fabric::PtrToPtrKind whereGpuPtrs)
{
    // Check that size(out)==len(names) and that every element of names has type size_t
    const size_t inCount = std::tuple_size<std::tuple<NameTypes...>>::value;
    const size_t outCount = std::tuple_size<std::tuple<Types...>>::value;
    static_assert(inCount == outCount, "Input and output tuples must be of same length");
    static_assert(
        areTypeT<AttributeDataHandle, NameTypes...>::value, "Attribute handles must have type AttributeDataHandle");

    std::tuple<Types...> out;

    // Cast to C-ABI compatible types
    std::tuple<Types...>* outTuplePtr = &out;
    void** outPtr = reinterpret_cast<void**>(outTuplePtr);
    std::tuple<NameTypes...>* inTuplePtr = &handles;
    AttributeDataHandle* handlesPtr = reinterpret_cast<AttributeDataHandle*>(inTuplePtr);

    // Call C-ABI version of method
    contextObj.iAttributeData->getDataWGpuAt(outPtr, contextObj, handlesPtr, inCount, whereGpuPtrs);

    return out;
}
// Syntactic sugar
template <typename... Types, typename... NameTypes>
std::tuple<Types...> getDataWGPU(const GraphContextObj& contextObj, std::tuple<NameTypes...> handles)
{
    return getDataWGpuAt<Types...>(contextObj, handles, omni::fabric::PtrToPtrKind::eGpuPtrToGpuPtr);
}
template <typename... Types, typename... NameTypes>
std::tuple<Types...> getDataWGPUOnCPU(const GraphContextObj& contextObj, std::tuple<NameTypes...> handles)
{
    return getDataWGpuAt<Types...>(contextObj, handles, omni::fabric::PtrToPtrKind::eCpuPtrToGpuPtr);
}

static size_t getElementCount(const GraphContextObj& contextObj, AttributeDataHandle const& attrHandle)
{
    size_t out;
    ConstAttributeDataHandle constAttrHandle = attrHandle;
    contextObj.iAttributeData->getElementCount(&out, contextObj, &constAttrHandle, 1);
    return out;
}

static size_t getElementCount(const GraphContextObj& contextObj, ConstAttributeDataHandle const& attrHandle)
{
    size_t out;
    contextObj.iAttributeData->getElementCount(&out, contextObj, &attrHandle, 1);
    return out;
}

template <typename... Types, typename... HandleTypes>
std::tuple<Types...> getElementCount(const GraphContextObj& contextObj, std::tuple<HandleTypes...> handles)
{
    // Check that size(out)==len(names) and that every element of names has type size_t
    const size_t inCount = std::tuple_size<std::tuple<HandleTypes...>>::value;
    const size_t outCount = std::tuple_size<std::tuple<Types...>>::value;
    static_assert(inCount == outCount, "Input and output tuples must be of same length");
    static_assert(areTypeT<ConstAttributeDataHandle, HandleTypes...>::value ||
                      areTypeT<AttributeDataHandle, HandleTypes...>::value,
                  "Attribute handles must have type ConstAttributeDataHandle or AttributeDataHandle");
    static_assert(areTypeT<size_t, Types...>::value, "Outputs must have type size_t");

    std::tuple<Types...> out;

    // Cast to C-ABI compatible types
    std::tuple<Types...>* outTuplePtr = &out;
    size_t* outPtr = reinterpret_cast<size_t*>(outTuplePtr);
    std::tuple<HandleTypes...>* inTuplePtr = &handles;
    ConstAttributeDataHandle* handlesPtr = reinterpret_cast<ConstAttributeDataHandle*>(inTuplePtr);

    // Call C-ABI version of method
    contextObj.iAttributeData->getElementCount(outPtr, contextObj, handlesPtr, inCount);

    return out;
}

//-----------------------------------------------------------------------------
static std::vector<ConstAttributeDataHandle> getAttributes(const GraphContextObj& contextObj, ConstBundleHandle bundle)
{
    size_t count = contextObj.iBundle->getAttributesCount(contextObj, bundle);
    std::vector<ConstAttributeDataHandle> attrsOut(count);
    contextObj.iBundle->getAttributesR(attrsOut.data(), contextObj, bundle, count);

    return attrsOut;
}

static std::vector<AttributeDataHandle> getAttributes(const GraphContextObj& contextObj, BundleHandle bundle)
{
    size_t count = contextObj.iBundle->getAttributesCount(contextObj, bundle);
    std::vector<AttributeDataHandle> attrsOut(count);
    contextObj.iBundle->getAttributesW(attrsOut.data(), contextObj, bundle, count);

    return attrsOut;
}

static void getAttributesByName(ConstAttributeDataHandle* attrsOut,
                                const GraphContextObj& contextObj,
                                ConstBundleHandle prim,
                                const Token* attrNames,
                                size_t count)
{
    const NameToken* nameTokens = reinterpret_cast<const NameToken*>(attrNames);
    contextObj.iBundle->getAttributesByNameR(attrsOut, contextObj, prim, nameTokens, count);
}

static void getAttributesByName(AttributeDataHandle* attrsOut,
                                const GraphContextObj& contextObj,
                                BundleHandle prim,
                                const Token* attrNames,
                                size_t count)
{
    const NameToken* nameTokens = reinterpret_cast<const NameToken*>(attrNames);
    contextObj.iBundle->getAttributesByNameW(attrsOut, contextObj, prim, nameTokens, count);
}

// ======================================================================
// Context wrappers

// getAttributeR is to be used in conjunction with the single item getDataR specialization to extract read-only data
// from a single attribute. If you have more than one attribute it is best to use getAttributesR, to minimize the calls
// across the ABI boundary. See the getDataR description for more information.
static ConstAttributeDataHandle getAttributeR(const GraphContextObj& contextObj,
                                              NodeContextHandle node,
                                              const Token& name,
                                              InstanceIndex instanceIndex)
{
    ConstAttributeDataHandle out;
    NameToken nameToken = name;
    contextObj.iContext->getAttributesByNameR(&out, contextObj, node, &nameToken, 1, instanceIndex);
    return out;
}

// getAttributesR is to be used in conjunction with the general version of getDataR to extract read-only data from an
// arbitrary list of attributes. It uses variadic templates to gather all arguments into a single ABI call. See the
// getDataR description for more information. Sample usage:
//    std::tie(a, b, c) = getAttributesR(contextObj, node, std::make_tuple(Token("a"), Token("b"), Token("c")), instanceIndex)
template <typename... Types, typename... NameTypes>
std::tuple<Types...> getAttributesR(const GraphContextObj& contextObj,
                                    NodeContextHandle node,
                                    std::tuple<NameTypes...> names,
                                    InstanceIndex instanceIndex)
{
    // Check that size(out)==len(names) and that every element of names has type size_t
    const size_t inCount = std::tuple_size<std::tuple<NameTypes...>>::value;
    const size_t outCount = std::tuple_size<std::tuple<Types...>>::value;
    static_assert(inCount == outCount, "Input and output tuples must be of same length");
    static_assert(areTypeT<NameToken, NameTypes...>::value || areTypeT<Token, NameTypes...>::value,
                  "Attribute names must have type NameToken or Token");
    static_assert(areTypeT<ConstAttributeDataHandle, Types...>::value, "Outputs must have type ConstAttributeDataHandle");

    std::tuple<Types...> out;

    // Cast to C-ABI compatible types
    std::tuple<Types...>* outTuplePtr = &out;
    ConstAttributeDataHandle* outPtr = reinterpret_cast<ConstAttributeDataHandle*>(outTuplePtr);
    std::tuple<NameTypes...>* inTuplePtr = &names;
    NameToken* namesPtr = reinterpret_cast<NameToken*>(inTuplePtr);

    // Call C-ABI version of method
    contextObj.iContext->getAttributesByNameR(outPtr, contextObj, node, namesPtr, inCount, instanceIndex);

    return out;
}

// getAttributeW is to be used in conjunction with the single item getDataW specialization to extract writable data
// from a single attribute. If you have more than one attribute it is best to use getAttributesW, to minimize the calls
// across the ABI boundary. See the getDataW description for more information.
static AttributeDataHandle getAttributeW(const GraphContextObj& contextObj,
                                         NodeContextHandle node,
                                         const Token& name,
                                         InstanceIndex instanceIndex)
{
    AttributeDataHandle out;
    NameToken nameToken = name;
    contextObj.iContext->getAttributesByNameW(&out, contextObj, node, &nameToken, 1, instanceIndex);
    return out;
}

// getAttributesW is to be used in conjunction with the general version of getDataW to extract read-only data from an
// arbitrary list of attributes. It uses variadic templates to gather all arguments into a single ABI call. See the
// getDataW description for more information. Sample usage:
//    std::tie(a, b, c) = getAttributesW(contextObj, node, std::make_tuple(Token("a"), Token("b"), Token("c")), instanceIndex)
template <typename... Types, typename... NameTypes>
std::tuple<Types...> getAttributesW(const GraphContextObj& contextObj,
                                    NodeContextHandle node,
                                    std::tuple<NameTypes...> names,
                                    InstanceIndex instanceIndex)
{
    // Check that size(out)==len(names) and that every element of names has type size_t
    const size_t inCount = std::tuple_size<std::tuple<NameTypes...>>::value;
    const size_t outCount = std::tuple_size<std::tuple<Types...>>::value;
    static_assert(inCount == outCount, "Input and output tuples must be of same length");
    static_assert(areTypeT<NameToken, NameTypes...>::value || areTypeT<Token, NameTypes...>::value,
                  "Attribute names must have type NameToken or Token");
    static_assert(areTypeT<AttributeDataHandle, Types...>::value, "Outputs must have type AttributeDataHandle");

    std::tuple<Types...> out;

    // Cast to C-ABI compatible types
    std::tuple<Types...>* outTuplePtr = &out;
    AttributeDataHandle* outPtr = reinterpret_cast<AttributeDataHandle*>(outTuplePtr);
    std::tuple<NameTypes...>* inTuplePtr = &names;
    NameToken* namesPtr = reinterpret_cast<NameToken*>(inTuplePtr);

    // Call C-ABI version of method
    contextObj.iContext->getAttributesByNameW(outPtr, contextObj, node, namesPtr, inCount, instanceIndex);

    return out;
}

#if defined(__GNUC__)
#    pragma GCC diagnostic pop
#endif

}
}
}
