// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/graph/core/CppWrappers.h>
#include <omni/graph/core/CudaUtils.h>
#include <omni/graph/core/Type.h>
#include <omni/graph/core/tuple.h>
#include <omni/graph/core/Handle.h>

namespace omni
{
namespace graph
{
namespace core
{

/**
 * Retrieves the Nth upstream connected attribute, invalid object if it isn't there. This is a utility function
 * that lets callers avoid the hassle of going through the allocation/deallocation required for ABI access.
 *
 * @template N Index of the upstream attribute
 * @param[in] attrObj The attribute object for which to retrieve the connection
 * @return Nth upstream attribute, or invalid if there is none
 */
template <int Count>
AttributeObj getNthUpstreamAttribute(const AttributeObj& attrObj)
{
    size_t connectionCount = attrObj.iAttribute->getUpstreamConnectionCount(attrObj);
    if (connectionCount > Count)
    {
        AttributeObj* attrObjs = reinterpret_cast<AttributeObj*>(alloca(sizeof(AttributeObj) * connectionCount));
        attrObj.iAttribute->getUpstreamConnections(attrObj, attrObjs, connectionCount);
        AttributeObj toReturn = attrObjs[Count];
        return toReturn;
    }
    return AttributeObj{nullptr, kInvalidAttributeHandle};
}

/**
 * Retrieves the Nth upstream attribute if it exists, or the passed-in attribute if not.
 *
 * @template N Index of the upstream attribute
 * @param[in] attrObj The attribute object for which to retrieve the connection
 * @return Nth upstream attribute, or the passed-in attribute if there is none
 */
template <int Count>
AttributeObj getNthUpstreamAttributeOrSelf(const AttributeObj& attrObj)
{
    AttributeObj nth = getNthUpstreamAttribute<Count>(attrObj);
    return nth.iAttribute ? nth : attrObj;
}


template <typename T>
constexpr BaseDataType baseDataTypeForType()
{
    using Type = typename std::remove_cv<T>::type;
    if (std::is_same<Type, int>::value)
    {
        return BaseDataType::eInt;
    }
    if (std::is_same<Type, int64_t>::value)
    {
        return BaseDataType::eInt64;
    }
    if (std::is_same<Type, float>::value)
    {
        return BaseDataType::eFloat;
    }
    if (std::is_same<Type, double>::value)
    {
        return BaseDataType::eDouble;
    }
    CUDA_SAFE_ASSERT("Type not implemented");
    return BaseDataType::eUnknown;
}

constexpr bool isNumericBaseType(BaseDataType type)
{
    switch (type)
    {
    case BaseDataType::eInt:
    case BaseDataType::eInt64:
    case BaseDataType::eFloat:
    case BaseDataType::eDouble:
        return true;
    default:
        return false;
    }
}

// Scalar numeric attribute accessor.
template <typename T>
class NumericAccessor
{
public:
    static constexpr BaseDataType expectedType = baseDataTypeForType<T>();
    static constexpr bool readOnly = std::is_const<T>::value;

    using RawType = typename std::remove_cv<T>::type;

    using HandleType = typename std::conditional<readOnly, ConstAttributeDataHandle, AttributeDataHandle>::type;

    NumericAccessor() : attributeType(BaseDataType::eUnknown), data(nullptr), componentCount(0), elementCount(0)
    {
    }

    NumericAccessor(const NumericAccessor&) = default;
    NumericAccessor& operator=(const NumericAccessor&) = default;

#if 0
    // The enable_if makes this valid only if T is const, since a non-const accessor can't
    // be initialized with a const attribute handle, but a const accessor can be initialized
    // from a const or non-const attribute handle.
    template <typename HANDLE_TYPE,
        typename IGNORED = typename std::enable_if<readOnly && (std::is_same<HANDLE_TYPE, ConstAttributeDataHandle>::value ||
            std::is_same<HANDLE_TYPE, AttributeDataHandle>::value),
        int>::type>
        NumericAccessor(const GraphContextObj& context,
            HANDLE_TYPE attributeHandle,
            IGNORED = 0)
        : NumericAccessor()
    {
        if (!attributeHandle.isValid())
            return;
        Type type = context.iAttributeData->getType(context, attributeHandle);
        BaseDataType baseType = type.baseType;
        if (isNumericBaseType(baseType))
        {
            size_t depth = type.arrayDepth;
            if (depth < 2)
            {
                attributeType = baseType;
                const void* pData;
                context.iAttributeData->getDataR(&pData, context, &attributeHandle, 1);
                data = (depth == 0) ? pData : (*(const void* const*)pData);
                componentCount = type.componentCount;
                elementCount = omni::graph::core::getElementCount(context, attributeHandle);
            }
        }
    }

    // The enable_if makes this valid only if T is non-const, since a non-const accessor can
    // only be initialized with a non-const attribute handle.
    template <typename IGNORED = typename std::enable_if<!readOnly, int>::type>
    NumericAccessor(const GraphContextObj& context,
        AttributeDataHandle attributeHandle,
        IGNORED = 0)
        : NumericAccessor()
    {
        if (!attributeHandle.isValid())
            return;
        Type type = context.iAttributeData->getType(context, attributeHandle);
        BaseDataType baseType = type.baseType;
        if (isNumericBaseType(baseType))
        {
            size_t depth = type.arrayDepth;
            if (depth < 2)
            {
                attributeType = baseType;
                void* pData;
                context.iAttributeData->getDataW(&pData, context, &attributeHandle, 1);
                data = (depth == 0) ? pData : (*(void* const*)pData);
                componentCount = type.componentCount;
                elementCount = omni::graph::core::getElementCount(context, attributeHandle);
            }
        }
    }

    // Construct a NumericAccessor by prim and attribute name.
    //
    // The enable_if makes this valid only if T is const, since a non-const accessor can't
    // be initialized with a const attribute handle, but a const accessor can be initialized
    // from a const or non-const attribute handle.
    template <typename HANDLE_TYPE,
        typename IGNORED = typename std::enable_if<readOnly && (std::is_same<HANDLE_TYPE, ConstBundleHandle>::value ||
            std::is_same<HANDLE_TYPE, BundleHandle>::value),
        int>::type>
        NumericAccessor(const GraphContextObj& context,
            HANDLE_TYPE primHandle,
            Token attributeName,
            IGNORED = 0)
        : NumericAccessor()
    {
        if (!primHandle.isValid())
            return;
        ConstAttributeDataHandle attributeHandle;
        NameToken nameToken(attributeName);
        context.iBundle->getAttributesByNameR(&attributeHandle, context, primHandle, &nameToken, 1);
        *this = NumericAccessor(context, attributeHandle);
    }

    // Construct a NumericAccessor by non-const prim and attribute name.
    //
    // The enable_if makes this valid only if T is non-const, since a non-const accessor can
    // only be initialized with a non-const attribute handle.
    template <typename IGNORED = typename std::enable_if<!readOnly, int>::type>
    NumericAccessor(const GraphContextObj& context,
        BundleHandle primHandle,
        NameToken attributeName,
        IGNORED = 0)
        : NumericAccessor()
    {
        if (!primHandle.isValid())
            return;
        AttributeDataHandle attributeHandle;
        context.iBundle->getAttributesByNameW(&attributeHandle, context, primHandle, &attributeName, 1);
        *this = NumericAccessor(context, attributeHandle);
    }
#endif
    bool isValid() const
    {
        return (data != nullptr);
    }
    size_t getComponentCount() const
    {
        return componentCount;
    }
    size_t getElementCount() const
    {
        return elementCount;
    }

    // Returns a pointer to the data if it's a perfect type match, else nullptr.
    T* getPerfectMatch() const
    {
        return reinterpret_cast<T*>((attributeType == expectedType) ? data : nullptr);
    }

    CUDA_CALLABLE
    RawType get(size_t i = 0) const
    {
        CUDA_SAFE_ASSERT(data != nullptr);
        CUDA_SAFE_ASSERT(i < componentCount * elementCount);
        if (attributeType == expectedType)
        {
            return reinterpret_cast<const RawType*>(data)[i];
        }
        switch (attributeType)
        {
        case BaseDataType::eInt:
            return RawType(reinterpret_cast<const int*>(data)[i]);
        case BaseDataType::eInt64:
            return RawType(reinterpret_cast<const int64_t*>(data)[i]);
        case BaseDataType::eFloat:
            return RawType(reinterpret_cast<const float*>(data)[i]);
        case BaseDataType::eDouble:
            return RawType(reinterpret_cast<const double*>(data)[i]);
        }
        CUDA_SAFE_ASSERT(0);
        return RawType(0);
    }

    // The enable_if makes this valid only if T is non-const.

    template <bool IsEnabled = true, typename std::enable_if<(IsEnabled && !readOnly), int>::type = 0>
    CUDA_CALLABLE void set(RawType value, size_t i = 0) const
    {
        CUDA_SAFE_ASSERT(data != nullptr);
        CUDA_SAFE_ASSERT(i < componentCount * elementCount);
        if (attributeType == expectedType)
        {
            reinterpret_cast<RawType*>(data)[i] = value;
        }
        else
        {
            switch (attributeType)
            {
            case BaseDataType::eInt:
                reinterpret_cast<int*>(data)[i] = int(value);
                break;
            case BaseDataType::eInt64:
                reinterpret_cast<int64_t*>(data)[i] = int64_t(value);
                break;
            case BaseDataType::eFloat:
                reinterpret_cast<float*>(data)[i] = float(value);
                break;
            case BaseDataType::eDouble:
                reinterpret_cast<double*>(data)[i] = double(value);
                break;
            default:
                CUDA_SAFE_ASSERT(0);
                break;
            }
        }
    }

    // TODO: make getNumericAccessor functions be friends of this class and make data private again
    // private:
    BaseDataType attributeType;

    using VoidType = typename std::conditional<readOnly, const void, void>::type;
    VoidType* data;

    size_t componentCount;
    size_t elementCount;
};

// CPU accessors

// When the dest is const, source can either be ConstBundleHandle or BundleHandle
template <typename T,
          typename HANDLE_TYPE,
          typename IGNORED =
              typename std::enable_if<std::is_const<T>::value && (std::is_same<HANDLE_TYPE, ConstBundleHandle>::value ||
                                                                  std::is_same<HANDLE_TYPE, BundleHandle>::value),
                                      int>::type>
NumericAccessor<T> getNumericAccessor(const GraphContextObj& context,
                                      HANDLE_TYPE primHandle,
                                      Token attributeName,
                                      IGNORED = 0)
{
    NumericAccessor<T> accessor;

    if (!primHandle.isValid())
        return accessor;

    ConstAttributeDataHandle attributeHandle;
    NameToken nameToken(attributeName);
    context.iBundle->getAttributesByNameR(&attributeHandle, context, primHandle, &nameToken, 1);

    if (!attributeHandle.isValid())
        return accessor;

    Type type = context.iAttributeData->getType(context, attributeHandle);
    BaseDataType baseType = type.baseType;
    if (isNumericBaseType(baseType))
    {
        size_t depth = type.arrayDepth;
        if (depth < 2)
        {
            accessor.attributeType = baseType;
            const void* pData;
            context.iAttributeData->getDataR(&pData, context, &attributeHandle, 1);
            accessor.data = (depth == 0) ? pData : (*(const void* const*)pData);
            accessor.componentCount = type.componentCount;
            accessor.elementCount = omni::graph::core::getElementCount(context, attributeHandle);
        }
    }
    return accessor;
}

// When the dest is non-const, source can only be BundleHandle
template <typename T, typename IGNORED = typename std::enable_if<!std::is_const<T>::value, int>::type>
NumericAccessor<T> getNumericAccessor(const GraphContextObj& context,
                                      BundleHandle primHandle,
                                      Token attributeName,
                                      IGNORED = 0)
{
    NumericAccessor<T> accessor;

    if (!primHandle.isValid())
        return accessor;
    AttributeDataHandle attributeHandle;
    NameToken nameToken(attributeName);
    context.iBundle->getAttributesByNameW(&attributeHandle, context, primHandle, &nameToken, 1);

    if (!attributeHandle.isValid())
        return accessor;

    Type type = context.iAttributeData->getType(context, attributeHandle);
    BaseDataType baseType = type.baseType;
    if (isNumericBaseType(baseType))
    {
        size_t depth = type.arrayDepth;
        if (depth < 2)
        {
            accessor.attributeType = baseType;
            void* pData;
            context.iAttributeData->getDataW(&pData, context, &attributeHandle, 1);
            accessor.data = (depth == 0) ? pData : (*(void* const*)pData);
            accessor.componentCount = type.componentCount;
            accessor.elementCount = omni::graph::core::getElementCount(context, attributeHandle);
        }
    }
    return accessor;
}

// GPU accessors

// When the dest is const, source can either be ConstBundleHandle or BundleHandle
template <typename T,
          typename HANDLE_TYPE,
          typename IGNORED =
              typename std::enable_if<std::is_const<T>::value && (std::is_same<HANDLE_TYPE, ConstBundleHandle>::value ||
                                                                  std::is_same<HANDLE_TYPE, BundleHandle>::value),
                                      int>::type>
NumericAccessor<T> getNumericAccessorGPU(const GraphContextObj& context, HANDLE_TYPE primHandle, Token attributeName)
{
    NumericAccessor<T> accessor;

    if (!primHandle.isValid())
        return accessor;

    ConstAttributeDataHandle attributeHandle;
    NameToken nameToken(attributeName);
    context.iBundle->getAttributesByNameR(&attributeHandle, context, primHandle, &nameToken, 1);

    if (!attributeHandle.isValid())
        return accessor;

    Type type = context.iAttributeData->getType(context, attributeHandle);
    BaseDataType baseType = type.baseType;
    if (isNumericBaseType(baseType))
    {
        size_t depth = type.arrayDepth;
        if (depth < 2)
        {
            accessor.attributeType = baseType;
            const void* pData;
            context.iAttributeData->getDataRGPU(&pData, context, &attributeHandle, 1);
            accessor.data = (depth == 0) ? pData : (*(const void* const*)pData);
            accessor.componentCount = type.componentCount;
            accessor.elementCount = omni::graph::core::getElementCount(context, attributeHandle);
        }
    }
    return accessor;
}

// When the dest is non-const, source can only be BundleHandle
template <typename T, typename IGNORED = typename std::enable_if<!std::is_const<T>::value, int>::type>
NumericAccessor<T> getNumericAccessorGPU(const GraphContextObj& context,
                                         BundleHandle primHandle,
                                         Token attributeName,
                                         IGNORED = 0)
{
    NumericAccessor<T> accessor;

    if (!primHandle.isValid())
        return accessor;
    AttributeDataHandle attributeHandle;
    NameToken nameToken(attributeName);
    context.iBundle->getAttributesByNameW(&attributeHandle, context, primHandle, &nameToken, 1);

    if (!attributeHandle.isValid())
        return accessor;

    Type type = context.iAttributeData->getType(context, attributeHandle);
    BaseDataType baseType = type.baseType;
    if (isNumericBaseType(baseType))
    {
        size_t depth = type.arrayDepth;
        if (depth < 2)
        {
            accessor.attributeType = baseType;
            void* pData;
            context.iAttributeData->getDataWGPU(&pData, context, &attributeHandle, 1);
            accessor.data = (depth == 0) ? pData : (*(void* const*)pData);
            accessor.componentCount = type.componentCount;
            accessor.elementCount = omni::graph::core::getElementCount(context, attributeHandle);
        }
    }
    return accessor;
}


template <typename T, size_t N>
class VectorAccessor
{
public:
    static constexpr BaseDataType expectedType = baseDataTypeForType<T>();
    static constexpr size_t componentCount = N;
    static constexpr bool readOnly = std::is_const<T>::value;

    using RawBaseType = typename std::remove_cv<T>::type;
    using RawVectorType = tuple<RawBaseType, N>;
    using VectorType = typename std::conditional<readOnly, const tuple<RawBaseType, N>, tuple<RawBaseType, N>>::type;
    using VoidType = typename std::conditional<readOnly, const void, void>::type;

    using HandleType = typename std::conditional<readOnly, ConstAttributeDataHandle, AttributeDataHandle>::type;

    VectorAccessor() : attributeType(BaseDataType::eUnknown), data(nullptr), elementCount(0)
    {
    }

    VectorAccessor(const VectorAccessor&) = default;
    VectorAccessor& operator=(const VectorAccessor&) = default;

    // The enable_if makes this valid only if T is const, since a non-const accessor can't
    // be initialized with a const attribute handle, but a const accessor can be initialized
    // from a const or non-const attribute handle.
    template <typename HANDLE_TYPE,
              typename IGNORED = typename std::enable_if<readOnly && (std::is_same<HANDLE_TYPE, ConstAttributeDataHandle>::value ||
                                                                      std::is_same<HANDLE_TYPE, AttributeDataHandle>::value),
                                                         int>::type>
    VectorAccessor(const GraphContextObj& context, HANDLE_TYPE attributeHandle, IGNORED = 0) : VectorAccessor()
    {
        if (!attributeHandle.isValid())
            return;
        Type type = context.iAttributeData->getType(context, attributeHandle);
        size_t componentCount = type.componentCount;
        if (componentCount == N)
        {
            BaseDataType baseType = type.baseType;
            if (isNumericBaseType(baseType))
            {
                size_t depth = type.arrayDepth;
                if (depth < 2)
                {
                    attributeType = baseType;
                    const void* pData;
                    context.iAttributeData->getDataR(&pData, context, &attributeHandle, 1);
                    data = (depth == 0) ? pData : (*(const void* const*)pData);
                    elementCount = omni::graph::core::getElementCount(context, attributeHandle);
                }
            }
        }
    }

    // The enable_if makes this valid only if T is non-const, since a non-const accessor can
    // only be initialized with a non-const attribute handle.
    template <typename IGNORED = typename std::enable_if<!readOnly, int>::type>
    VectorAccessor(const GraphContextObj& context, AttributeDataHandle attributeHandle, IGNORED = 0) : VectorAccessor()
    {
        if (!attributeHandle.isValid())
            return;
        Type type = context.iAttributeData->getType(context, attributeHandle);
        size_t componentCount = type.componentCount;
        if (componentCount == N)
        {
            BaseDataType baseType = type.baseType;
            if (isNumericBaseType(baseType))
            {
                size_t depth = type.arrayDepth;
                if (depth < 2)
                {
                    attributeType = baseType;
                    void* pData;
                    context.iAttributeData->getDataW(&pData, context, &attributeHandle, 1);
                    data = (depth == 0) ? pData : (*(void* const*)pData);
                    elementCount = omni::graph::core::getElementCount(context, attributeHandle);
                }
            }
        }
    }

    // Construct a VectorAccessor by prim and attribute name.
    //
    // The enable_if makes this valid only if T is const, since a non-const accessor can't
    // be initialized with a const attribute handle, but a const accessor can be initialized
    // from a const or non-const attribute handle.
    template <typename HANDLE_TYPE,
              typename IGNORED = typename std::enable_if<readOnly && (std::is_same<HANDLE_TYPE, ConstBundleHandle>::value ||
                                                                      std::is_same<HANDLE_TYPE, BundleHandle>::value),
                                                         int>::type>
    VectorAccessor(const GraphContextObj& context, HANDLE_TYPE primHandle, NameToken attributeName, IGNORED = 0)
        : VectorAccessor()
    {
        if (!primHandle.isValid())
            return;
        ConstAttributeDataHandle attributeHandle;
        context.iBundle->getAttributesByNameR(&attributeHandle, context, primHandle, &attributeName, 1);
        *this = VectorAccessor(context, attributeHandle);
    }

    // Construct a VectorAccessor by non-const prim and attribute name.
    //
    // The enable_if makes this valid only if T is non-const, since a non-const accessor can
    // only be initialized with a non-const attribute handle.
    template <typename IGNORED = typename std::enable_if<!readOnly, int>::type>
    VectorAccessor(const GraphContextObj& context, BundleHandle primHandle, NameToken attributeName, IGNORED = 0)
        : VectorAccessor()
    {
        if (!primHandle.isValid())
            return;
        AttributeDataHandle attributeHandle;
        context.iBundle->getAttributesByNameW(&attributeHandle, context, primHandle, &attributeName, 1);
        *this = VectorAccessor(context, attributeHandle);
    }

    bool isValid() const
    {
        return (data != nullptr);
    }
    size_t getElementCount() const
    {
        return elementCount;
    }

    // Returns a pointer to the data if it's a perfect type match, else nullptr.
    VectorType* getPerfectMatch() const
    {
        return reinterpret_cast<VectorType*>((attributeType == expectedType) ? data : nullptr);
    }

    RawVectorType get(size_t i = 0) const
    {
        CUDA_SAFE_ASSERT(data != nullptr);
        CUDA_SAFE_ASSERT(i < elementCount);
        if (attributeType == expectedType)
        {
            return reinterpret_cast<const RawVectorType*>(data)[i];
        }
        switch (attributeType)
        {
        case BaseDataType::eInt:
            return RawVectorType(reinterpret_cast<const tuple<int, N>*>(data)[i]);
        case BaseDataType::eInt64:
            return RawVectorType(reinterpret_cast<const tuple<int64_t, N>*>(data)[i]);
        case BaseDataType::eFloat:
            return RawVectorType(reinterpret_cast<const tuple<float, N>*>(data)[i]);
        case BaseDataType::eDouble:
            return RawVectorType(reinterpret_cast<const tuple<double, N>*>(data)[i]);
        }
        CUDA_SAFE_ASSERT(0);
        return RawVectorType(T(0));
    }

    // The enable_if makes this valid only if T is non-const.
    template <typename IGNORED = typename std::enable_if<!readOnly, int>::type>
    void set(const RawVectorType& value, size_t i = 0, IGNORED = 0) const
    {
        CUDA_SAFE_ASSERT(data != nullptr);
        CUDA_SAFE_ASSERT(i < componentCount * elementCount);
        if (attributeType == expectedType)
        {
            reinterpret_cast<RawVectorType*>(data)[i] = value;
        }
        else
        {
            switch (attributeType)
            {
            case BaseDataType::eInt:
                reinterpret_cast<tuple<int, N>*>(data)[i] = tuple<int, N>(value);
                break;
            case BaseDataType::eInt64:
                reinterpret_cast<tuple<int64_t, N>*>(data)[i] = tuple<int64_t, N>(value);
                break;
            case BaseDataType::eFloat:
                reinterpret_cast<tuple<float, N>*>(data)[i] = tuple<float, N>(value);
                break;
            case BaseDataType::eDouble:
                reinterpret_cast<tuple<double, N>*>(data)[i] = tuple<double, N>(value);
                break;
            default:
                CUDA_SAFE_ASSERT(0);
                break;
            }
        }
    }

private:
    BaseDataType attributeType;

    VoidType* data;

    size_t elementCount;
};

// Bulk scalar numeric array attribute accessor (non-const implementation).
template <typename T>
class BulkNumericAccessor
{
public:
    static constexpr BaseDataType expectedType = baseDataTypeForType<T>();
    static constexpr bool readOnly = false;

    using RawType = typename std::remove_cv<T>::type;

    using HandleType = AttributeDataHandle;

    BulkNumericAccessor()
        : attributeType(BaseDataType::eUnknown), data(nullptr), matchingData(nullptr), componentCount(0), elementCount(0)
    {
    }

    BulkNumericAccessor(BulkNumericAccessor&& that)
    {
        attributeType = that.attributeType;
        data = that.data;
        matchingData = that.matchingData;
        componentCount = that.componentCount;
        elementCount = that.elementCount;
        that.attributeType = BaseDataType::eUnknown;
        that.data = nullptr;
        that.matchingData = nullptr;
        that.componentCount = 0;
        that.elementCount = 0;
    }
    BulkNumericAccessor& operator=(BulkNumericAccessor&& that)
    {
        attributeType = that.attributeType;
        data = that.data;
        matchingData = that.matchingData;
        componentCount = that.componentCount;
        elementCount = that.elementCount;
        that.attributeType = BaseDataType::eUnknown;
        that.data = nullptr;
        that.matchingData = nullptr;
        that.componentCount = 0;
        that.elementCount = 0;
        return *this;
    }

    BulkNumericAccessor(const BulkNumericAccessor& that) = delete;
    BulkNumericAccessor& operator=(const BulkNumericAccessor& that) = delete;


    // This is valid only if T is non-const, since a non-const accessor can
    // only be initialized with a non-const attribute handle.
    BulkNumericAccessor(const GraphContextObj& context, AttributeDataHandle attributeHandle) : BulkNumericAccessor()
    {
        if (!attributeHandle.isValid())
            return;
        Type type = context.iAttributeData->getType(context, attributeHandle);
        BaseDataType baseType = type.baseType;
        if (isNumericBaseType(baseType))
        {
            size_t depth = type.arrayDepth;
            if (depth < 2)
            {
                attributeType = baseType;
                void* pData;
                context.iAttributeData->getDataW(&pData, context, &attributeHandle, 1);
                data = (depth == 0) ? pData : (*(void* const*)pData);
                componentCount = type.componentCount;
                elementCount = omni::graph::core::getElementCount(context, attributeHandle);
                if (attributeType != expectedType)
                {
                    size_t fullCount = componentCount * elementCount;
                    RawType* converted = new RawType[fullCount];
                    convertToMatching(converted, fullCount);
                    matchingData = converted;
                }
                else
                {
                    matchingData = reinterpret_cast<T*>(data);
                }
            }
        }
    }

    // Construct a BulkNumericAccessor by non-const prim and attribute name.
    //
    // This is valid only if T is non-const, since a non-const accessor can
    // only be initialized with a non-const attribute handle.
    BulkNumericAccessor(const GraphContextObj& context, BundleHandle primHandle, NameToken attributeName)
        : BulkNumericAccessor()
    {
        if (!primHandle.isValid())
            return;
        AttributeDataHandle attributeHandle;
        context.iBundle->getAttributesByNameW(&attributeHandle, context, primHandle, &attributeName, 1);
        *this = BulkNumericAccessor(context, attributeHandle);
    }

    ~BulkNumericAccessor()
    {
        if (attributeType != expectedType && matchingData != nullptr)
        {
            flushInternal(matchingData);
            delete[] matchingData;
        }
    }

    bool isValid() const
    {
        return (data != nullptr);
    }
    size_t getComponentCount() const
    {
        return componentCount;
    }
    size_t getElementCount() const
    {
        return elementCount;
    }

    // Returns a pointer to the data if it's convertible, else nullptr.
    T* getData() const
    {
        return matchingData;
    }

    // Returns a pointer to the data if it's convertible, else nullptr.
    // Convertible types are always treated as a perfect match for bulk conversion.
    // This function is just provided for compatibility with the NumericAccessor
    // and VectorAccessor classes above.
    T* getPerfectMatch() const
    {
        return matchingData;
    }

    void flush()
    {
        flushInternal(matchingData);
    }

private:
    void flushInternal(RawType* matchData)
    {
        CUDA_SAFE_ASSERT(data != nullptr);
        if (attributeType == expectedType)
        {
            return;
        }

        const size_t fullCount = componentCount * elementCount;
        switch (attributeType)
        {
        case BaseDataType::eInt:
        {
            int* source = reinterpret_cast<int*>(data);
            for (size_t i = 0; i < fullCount; ++i)
            {
                source[i] = int(matchData[i]);
            }
            break;
        }
        case BaseDataType::eInt64:
        {
            int64_t* source = reinterpret_cast<int64_t*>(data);
            for (size_t i = 0; i < fullCount; ++i)
            {
                source[i] = int64_t(matchData[i]);
            }
            break;
        }
        case BaseDataType::eFloat:
        {
            float* source = reinterpret_cast<float*>(data);
            for (size_t i = 0; i < fullCount; ++i)
            {
                source[i] = float(matchData[i]);
            }
            break;
        }
        case BaseDataType::eDouble:
        {
            double* source = reinterpret_cast<double*>(data);
            for (size_t i = 0; i < fullCount; ++i)
            {
                source[i] = double(matchData[i]);
            }
            break;
        }
        default:
            CUDA_SAFE_ASSERT(0);
            break;
        }
    }

    void convertToMatching(RawType* converted, const size_t fullCount)
    {
        switch (attributeType)
        {
        case BaseDataType::eInt:
        {
            const int* source = reinterpret_cast<const int*>(data);
            for (size_t i = 0; i < fullCount; ++i)
            {
                converted[i] = RawType(source[i]);
            }
            break;
        }
        case BaseDataType::eInt64:
        {
            const int64_t* source = reinterpret_cast<const int64_t*>(data);
            for (size_t i = 0; i < fullCount; ++i)
            {
                converted[i] = RawType(source[i]);
            }
            break;
        }
        case BaseDataType::eFloat:
        {
            const float* source = reinterpret_cast<const float*>(data);
            for (size_t i = 0; i < fullCount; ++i)
            {
                converted[i] = RawType(source[i]);
            }
            break;
        }
        case BaseDataType::eDouble:
        {
            const double* source = reinterpret_cast<const double*>(data);
            for (size_t i = 0; i < fullCount; ++i)
            {
                converted[i] = RawType(source[i]);
            }
            break;
        }
        default:
            CUDA_SAFE_ASSERT(0);
            break;
        }
    }

    BaseDataType attributeType;

    using VoidType = void;
    VoidType* data;

    T* matchingData;

    size_t componentCount;
    size_t elementCount;
};

// Bulk scalar numeric array attribute accessor (const implementation).
template <typename T>
class BulkNumericAccessor<const T>
{
public:
    static constexpr BaseDataType expectedType = baseDataTypeForType<T>();
    static constexpr bool readOnly = true;

    using RawType = typename std::remove_cv<T>::type;

    using HandleType = ConstAttributeDataHandle;

    BulkNumericAccessor()
        : attributeType(BaseDataType::eUnknown), data(nullptr), matchingData(nullptr), componentCount(0), elementCount(0)
    {
    }

    BulkNumericAccessor(BulkNumericAccessor&& that)
    {
        attributeType = that.attributeType;
        data = that.data;
        matchingData = that.matchingData;
        componentCount = that.componentCount;
        elementCount = that.elementCount;
        that.attributeType = BaseDataType::eUnknown;
        that.data = nullptr;
        that.matchingData = nullptr;
        that.componentCount = 0;
        that.elementCount = 0;
    }
    BulkNumericAccessor& operator=(BulkNumericAccessor&& that)
    {
        attributeType = that.attributeType;
        data = that.data;
        matchingData = that.matchingData;
        componentCount = that.componentCount;
        elementCount = that.elementCount;
        that.attributeType = BaseDataType::eUnknown;
        that.data = nullptr;
        that.matchingData = nullptr;
        that.componentCount = 0;
        that.elementCount = 0;
        return *this;
    }

    BulkNumericAccessor(const BulkNumericAccessor& that) = delete;
    BulkNumericAccessor& operator=(const BulkNumericAccessor& that) = delete;

    // HANDLE_TYPE can be ConstAttributeDataHandle or AttributeDataHandle.
    template <typename HANDLE_TYPE>
    BulkNumericAccessor(const GraphContextObj& context, HANDLE_TYPE attributeHandle) : BulkNumericAccessor()
    {
        if (!attributeHandle.isValid())
            return;
        Type type = context.iAttributeData->getType(context, attributeHandle);
        BaseDataType baseType = type.baseType;
        if (isNumericBaseType(baseType))
        {
            size_t depth = type.arrayDepth;
            if (depth < 2)
            {
                attributeType = baseType;
                const void* pData;
                context.iAttributeData->getDataR(&pData, context, &attributeHandle, 1);
                data = (depth == 0) ? pData : (*(const void* const*)pData);
                componentCount = type.componentCount;
                elementCount = omni::graph::core::getElementCount(context, attributeHandle);
                if (attributeType != expectedType)
                {
                    size_t fullCount = componentCount * elementCount;
                    RawType* converted = new RawType[fullCount];
                    convertToMatching(converted, fullCount);
                    matchingData = converted;
                }
                else
                {
                    matchingData = reinterpret_cast<const T*>(data);
                }
            }
        }
    }

    // Construct a BulkNumericAccessor by prim and attribute name.
    //
    // HANDLE_TYPE can be ConstAttributeDataHandle or AttributeDataHandle.
    template <typename HANDLE_TYPE>
    BulkNumericAccessor(const GraphContextObj& context, HANDLE_TYPE primHandle, NameToken attributeName)
        : BulkNumericAccessor()
    {
        if (!primHandle.isValid())
            return;
        ConstAttributeDataHandle attributeHandle;
        context.iBundle->getAttributesByNameR(&attributeHandle, context, primHandle, &attributeName, 1);
        *this = BulkNumericAccessor(context, attributeHandle);
    }

    ~BulkNumericAccessor()
    {
    }

    bool isValid() const
    {
        return (data != nullptr);
    }
    size_t getComponentCount() const
    {
        return componentCount;
    }
    size_t getElementCount() const
    {
        return elementCount;
    }

    // Returns a pointer to the data if it's convertible, else nullptr.
    const T* getData() const
    {
        return matchingData;
    }

    // Returns a pointer to the data if it's convertible, else nullptr.
    // Convertible types are always treated as a perfect match for bulk conversion.
    // This function is just provided for compatibility with the NumericAccessor
    // and VectorAccessor classes above.
    const T* getPerfectMatch() const
    {
        return matchingData;
    }

private:
    void convertToMatching(RawType* converted, const size_t fullCount)
    {
        switch (attributeType)
        {
        case BaseDataType::eInt:
        {
            const int* source = reinterpret_cast<const int*>(data);
            for (size_t i = 0; i < fullCount; ++i)
            {
                converted[i] = RawType(source[i]);
            }
            break;
        }
        case BaseDataType::eInt64:
        {
            const int64_t* source = reinterpret_cast<const int64_t*>(data);
            for (size_t i = 0; i < fullCount; ++i)
            {
                converted[i] = RawType(source[i]);
            }
            break;
        }
        case BaseDataType::eFloat:
        {
            const float* source = reinterpret_cast<const float*>(data);
            for (size_t i = 0; i < fullCount; ++i)
            {
                converted[i] = RawType(source[i]);
            }
            break;
        }
        case BaseDataType::eDouble:
        {
            const double* source = reinterpret_cast<const double*>(data);
            for (size_t i = 0; i < fullCount; ++i)
            {
                converted[i] = RawType(source[i]);
            }
            break;
        }
        default:
            CUDA_SAFE_ASSERT(0);
            break;
        }
    }

    BaseDataType attributeType;

    using VoidType = const void;
    VoidType* data;

    const T* matchingData;

    size_t componentCount;
    size_t elementCount;
};

// Bulk vector numeric array attribute accessor (non-const implementation).
template <typename T, size_t N>
class BulkVectorAccessor
{
public:
    static constexpr BaseDataType expectedType = baseDataTypeForType<T>();
    static constexpr size_t componentCount = N;
    static constexpr bool readOnly = false;

    using RawBaseType = typename std::remove_cv<T>::type;
    using RawVectorType = tuple<RawBaseType, N>;
    using VectorType = tuple<RawBaseType, N>;

    using HandleType = AttributeDataHandle;

    BulkVectorAccessor() : attributeType(BaseDataType::eUnknown), data(nullptr), matchingData(nullptr), elementCount(0)
    {
    }

    BulkVectorAccessor(BulkVectorAccessor&& that)
    {
        attributeType = that.attributeType;
        data = that.data;
        matchingData = that.matchingData;
        elementCount = that.elementCount;
        that.attributeType = BaseDataType::eUnknown;
        that.data = nullptr;
        that.matchingData = nullptr;
        that.elementCount = 0;
    }
    BulkVectorAccessor& operator=(BulkVectorAccessor&& that)
    {
        attributeType = that.attributeType;
        data = that.data;
        matchingData = that.matchingData;
        elementCount = that.elementCount;
        that.attributeType = BaseDataType::eUnknown;
        that.data = nullptr;
        that.matchingData = nullptr;
        that.elementCount = 0;
        return *this;
    }

    BulkVectorAccessor(const BulkVectorAccessor& that) = delete;
    BulkVectorAccessor& operator=(const BulkVectorAccessor& that) = delete;

    // A non-const accessor can only be initialized with a non-const attribute handle.
    BulkVectorAccessor(const GraphContextObj& context, AttributeDataHandle attributeHandle) : BulkVectorAccessor()
    {
        if (!attributeHandle.isValid())
            return;
        Type type = context.iAttributeData->getType(context, attributeHandle);
        size_t componentCount = type.componentCount;
        if (componentCount == N)
        {
            BaseDataType baseType = type.baseType;
            if (isNumericBaseType(baseType))
            {
                size_t depth = type.arrayDepth;
                if (depth < 2)
                {
                    void* pData;
                    context.iAttributeData->getDataW(&pData, context, &attributeHandle, 1);
                    data = (depth == 0) ? pData : (*(void* const*)pData);

                    attributeType = baseType;
                    elementCount = omni::graph::core::getElementCount(context, attributeHandle);
                    if (attributeType != expectedType)
                    {
                        size_t fullCount = componentCount * elementCount;
                        RawVectorType* converted = new RawVectorType[fullCount];
                        convertToMatching(converted, fullCount);
                        matchingData = converted;
                    }
                    else
                    {
                        matchingData = reinterpret_cast<VectorType*>(data);
                    }
                }
            }
        }
    }

    // A non-const accessor can only be initialized with a non-const attribute handle.
    BulkVectorAccessor(const GraphContextObj& context, BundleHandle bundleHandle, Token attributeName)
        : BulkVectorAccessor()
    {
        if (!bundleHandle.isValid())
            return;
        AttributeDataHandle attributeHandle;
        NameToken attributeNameToken(attributeName);
        context.iBundle->getAttributesByNameW(&attributeHandle, context, bundleHandle, &attributeNameToken, 1);
        *this = BulkVectorAccessor(context, attributeHandle);
    }

    ~BulkVectorAccessor()
    {
        if (attributeType != expectedType && matchingData != nullptr)
        {
            flushInternal(matchingData);
            delete[] matchingData;
        }
    }

    bool isValid() const
    {
        return (data != nullptr);
    }
    size_t getElementCount() const
    {
        return elementCount;
    }

    // Returns a pointer to the data if it's convertible, else nullptr.
    VectorType* getData() const
    {
        return matchingData;
    }

    // Returns a pointer to the data if it's convertible, else nullptr.
    // Convertible types are always treated as a perfect match for bulk conversion.
    // This function is just provided for compatibility with the NumericAccessor
    // and VectorAccessor classes above.
    VectorType* getPerfectMatch() const
    {
        return matchingData;
    }

    void flush()
    {
        flushInternal(matchingData);
    }

private:
    void flushInternal(RawVectorType* matchData)
    {
        CUDA_SAFE_ASSERT(data != nullptr);
        if (attributeType == expectedType)
        {
            return;
        }

        const size_t fullCount = componentCount * elementCount;
        switch (attributeType)
        {
        case BaseDataType::eInt:
        {
            tuple<int, N>* source = reinterpret_cast<tuple<int, N>*>(data);
            for (size_t i = 0; i < fullCount; ++i)
            {
                source[i] = tuple<int, N>(matchData[i]);
            }
            break;
        }
        case BaseDataType::eInt64:
        {
            tuple<int64_t, N>* source = reinterpret_cast<tuple<int64_t, N>*>(data);
            for (size_t i = 0; i < fullCount; ++i)
            {
                source[i] = tuple<int64_t, N>(matchData[i]);
            }
            break;
        }
        case BaseDataType::eFloat:
        {
            tuple<float, N>* source = reinterpret_cast<tuple<float, N>*>(data);
            for (size_t i = 0; i < fullCount; ++i)
            {
                source[i] = tuple<float, N>(matchData[i]);
            }
            break;
        }
        case BaseDataType::eDouble:
        {
            tuple<double, N>* source = reinterpret_cast<tuple<double, N>*>(data);
            for (size_t i = 0; i < fullCount; ++i)
            {
                source[i] = tuple<double, N>(matchData[i]);
            }
            break;
        }
        default:
            CUDA_SAFE_ASSERT(0);
            break;
        }
    }

    void flushInternal(const RawVectorType* matchData)
    {
        // Does nothing.  This signature is just for compiling purposes.
    }

    void convertToMatching(RawVectorType* converted, const size_t fullCount)
    {
        switch (attributeType)
        {
        case BaseDataType::eInt:
        {
            const tuple<int, N>* source = reinterpret_cast<const tuple<int, N>*>(data);
            for (size_t i = 0; i < fullCount; ++i)
            {
                converted[i] = RawVectorType(source[i]);
            }
            break;
        }
        case BaseDataType::eInt64:
        {
            const tuple<int64_t, N>* source = reinterpret_cast<const tuple<int64_t, N>*>(data);
            for (size_t i = 0; i < fullCount; ++i)
            {
                converted[i] = RawVectorType(source[i]);
            }
            break;
        }
        case BaseDataType::eFloat:
        {
            const tuple<float, N>* source = reinterpret_cast<const tuple<float, N>*>(data);
            for (size_t i = 0; i < fullCount; ++i)
            {
                converted[i] = RawVectorType(source[i]);
            }
            break;
        }
        case BaseDataType::eDouble:
        {
            const tuple<double, N>* source = reinterpret_cast<const tuple<double, N>*>(data);
            for (size_t i = 0; i < fullCount; ++i)
            {
                converted[i] = RawVectorType(source[i]);
            }
            break;
        }
        default:
            CUDA_SAFE_ASSERT(0);
            break;
        }
    }

    BaseDataType attributeType;

    using VoidType = void;
    VoidType* data;

    VectorType* matchingData;

    size_t elementCount;
};

// Bulk vector numeric array attribute accessor (const implementation).
template <typename T, size_t N>
class BulkVectorAccessor<const T, N>
{
public:
    static constexpr BaseDataType expectedType = baseDataTypeForType<T>();
    static constexpr size_t componentCount = N;
    static constexpr bool readOnly = true;

    using RawBaseType = typename std::remove_cv<T>::type;
    using RawVectorType = tuple<RawBaseType, N>;
    using VectorType = const tuple<RawBaseType, N>;

    using HandleType = ConstAttributeDataHandle;

    BulkVectorAccessor() : attributeType(BaseDataType::eUnknown), data(nullptr), matchingData(nullptr), elementCount(0)
    {
    }

    BulkVectorAccessor(BulkVectorAccessor&& that)
    {
        attributeType = that.attributeType;
        data = that.data;
        matchingData = that.matchingData;
        elementCount = that.elementCount;
        that.attributeType = BaseDataType::eUnknown;
        that.data = nullptr;
        that.matchingData = nullptr;
        that.elementCount = 0;
    }
    BulkVectorAccessor& operator=(BulkVectorAccessor&& that)
    {
        attributeType = that.attributeType;
        data = that.data;
        matchingData = that.matchingData;
        elementCount = that.elementCount;
        that.attributeType = BaseDataType::eUnknown;
        that.data = nullptr;
        that.matchingData = nullptr;
        that.elementCount = 0;
        return *this;
    }

    BulkVectorAccessor(const BulkVectorAccessor& that) = delete;
    BulkVectorAccessor& operator=(const BulkVectorAccessor& that) = delete;

    // A const accessor can be initialized from a const or non-const attribute handle.
    template <typename HANDLE_TYPE>
    BulkVectorAccessor(const GraphContextObj& context, HANDLE_TYPE attributeHandle) : BulkVectorAccessor()
    {
        if (!attributeHandle.isValid())
            return;
        Type type = context.iAttributeData->getType(context, attributeHandle);
        size_t componentCount = type.componentCount;
        if (componentCount == N)
        {
            BaseDataType baseType = type.baseType;
            if (isNumericBaseType(baseType))
            {
                size_t depth = type.arrayDepth;
                if (depth < 2)
                {
                    attributeType = baseType;
                    const void* pData;
                    context.iAttributeData->getDataR(&pData, context, &attributeHandle, 1);
                    data = (depth == 0) ? pData : (*(const void* const*)pData);
                    elementCount = omni::graph::core::getElementCount(context, attributeHandle);
                    if (attributeType != expectedType)
                    {
                        size_t fullCount = componentCount * elementCount;
                        RawVectorType* converted = new RawVectorType[fullCount];
                        convertToMatching(converted, fullCount);
                        matchingData = converted;
                    }
                    else
                    {
                        matchingData = reinterpret_cast<VectorType*>(data);
                    }
                }
            }
        }
    }

    // A const accessor can be initialized from a const or non-const attribute handle.
    template <typename HANDLE_TYPE>
    BulkVectorAccessor(const GraphContextObj& context, HANDLE_TYPE primHandle, Token attributeName)
        : BulkVectorAccessor()
    {
        if (!primHandle.isValid())
            return;
        ConstAttributeDataHandle attributeHandle;
        NameToken attributeNameToken(attributeName);
        context.iBundle->getAttributesByNameR(&attributeHandle, context, primHandle, &attributeNameToken, 1);
        *this = BulkVectorAccessor(context, attributeHandle);
    }

    ~BulkVectorAccessor()
    {
        if (attributeType != expectedType && matchingData != nullptr)
        {
            delete[] matchingData;
        }
    }

    bool isValid() const
    {
        return (data != nullptr);
    }
    size_t getElementCount() const
    {
        return elementCount;
    }

    // Returns a pointer to the data if it's convertible, else nullptr.
    VectorType* getData() const
    {
        return matchingData;
    }

    // Returns a pointer to the data if it's convertible, else nullptr.
    // Convertible types are always treated as a perfect match for bulk conversion.
    // This function is just provided for compatibility with the NumericAccessor
    // and VectorAccessor classes above.
    VectorType* getPerfectMatch() const
    {
        return matchingData;
    }

private:
    void convertToMatching(RawVectorType* converted, const size_t fullCount)
    {
        switch (attributeType)
        {
        case BaseDataType::eInt:
        {
            const tuple<int, N>* source = reinterpret_cast<const tuple<int, N>*>(data);
            for (size_t i = 0; i < fullCount; ++i)
            {
                converted[i] = RawVectorType(source[i]);
            }
            break;
        }
        case BaseDataType::eInt64:
        {
            const tuple<int64_t, N>* source = reinterpret_cast<const tuple<int64_t, N>*>(data);
            for (size_t i = 0; i < fullCount; ++i)
            {
                converted[i] = RawVectorType(source[i]);
            }
            break;
        }
        case BaseDataType::eFloat:
        {
            const tuple<float, N>* source = reinterpret_cast<const tuple<float, N>*>(data);
            for (size_t i = 0; i < fullCount; ++i)
            {
                converted[i] = RawVectorType(source[i]);
            }
            break;
        }
        case BaseDataType::eDouble:
        {
            const tuple<double, N>* source = reinterpret_cast<const tuple<double, N>*>(data);
            for (size_t i = 0; i < fullCount; ++i)
            {
                converted[i] = RawVectorType(source[i]);
            }
            break;
        }
        default:
            CUDA_SAFE_ASSERT(0);
            break;
        }
    }

    BaseDataType attributeType;

    using VoidType = const void;
    VoidType* data;

    VectorType* matchingData;

    size_t elementCount;
};


// Relationship attribute accessor.
// NOTE: This isn't yet supported.
#if 0
template <bool isReadOnly>
class RelationshipAccessor
{
public:
    static constexpr BaseDataType expectedType = BaseDataType::eRelationship;
    static constexpr bool readOnly = isReadOnly;

    using BundleHandleType = typename std::conditional<readOnly, ConstBundleHandle, BundleHandle>::type;
    using PrimHandleType [[deprecated("Use BundleHandleType!")]] = BundleHandleType;

    using HandleType = typename std::conditional<readOnly, ConstAttributeDataHandle, AttributeDataHandle>::type;

    RelationshipAccessor()
        : data(nullptr),
          elementCount(0),
          m_context(nullptr),
          m_attributeHandle(AttributeDataHandle::invalidValue()),
          m_iAttributeData(nullptr)
    {
    }

    RelationshipAccessor(const RelationshipAccessor&) = default;
    RelationshipAccessor& operator=(const RelationshipAccessor&) = default;

    RelationshipAccessor(RelationshipAccessor&& that)
    {
        data = that.data;
        elementCount = that.componentCount;
        m_context = that.m_context;
        m_attributeHandle = that.m_attributeHandle;
        m_iAttributeData = that.m_iAttributeData;
        that.data = nullptr;
        that.elementCount = 0;
        that.m_context = nullptr;
        that.m_attributeHandle = AttributeDataHandle(AttributeDataHandle::invalidValue());
        that.m_iAttributeData = nullptr;
    }
    RelationshipAccessor& operator=(RelationshipAccessor&& that)
    {
        data = that.data;
        elementCount = that.componentCount;
        m_context = that.m_context;
        m_attributeHandle = that.m_attributeHandle;
        m_iAttributeData = that.m_iAttributeData;
        that.data = nullptr;
        that.elementCount = 0;
        that.m_context = nullptr;
        that.m_attributeHandle = AttributeDataHandle(AttributeDataHandle::invalidValue());
        that.m_iAttributeData = nullptr;
    }

    // The enable_if makes this valid only if readOnly is true, since a non-const accessor can't
    // be initialized with a const attribute handle, but a const accessor can be initialized
    // from a const or non-const attribute handle.
    template <typename HANDLE_TYPE,
              typename IGNORED = typename std::enable_if<readOnly && (std::is_same<HANDLE_TYPE, ConstAttributeDataHandle>::value ||
                                                                      std::is_same<HANDLE_TYPE, AttributeDataHandle>::value),
                                                         int>::type>
    RelationshipAccessor(const GraphContextObj& context, HANDLE_TYPE attributeHandle, IGNORED = 0)
        : RelationshipAccessor()
    {
        if (!attributeHandle.isValid())
            return;
        Type type = context.iAttributeData->getType(context, attributeHandle);
        BaseDataType baseType = type.baseType;
        if (baseType == BaseDataType::eRelationship)
        {
            size_t componentCount = type.componentCount;
            if (componentCount == 1)
            {
                size_t depth = type.arrayDepth;
                if (depth < 2)
                {
                    const void* pData;
                    context.iAttributeData->getDataR(&pData, context, &attributeHandle, 1);
                    data = (depth == 0) ? pData : (*(const void* const*)pData);
                    elementCount = omni::graph::core::getElementCount(context, attributeHandle);
                }
            }
        }
    }

    // The enable_if makes this valid only if readOnly is false, since a non-const accessor can
    // only be initialized with a non-const attribute handle.
    template <typename IGNORED = typename std::enable_if<!readOnly, int>::type>
    RelationshipAccessor(const GraphContextObj& context, AttributeDataHandle attributeHandle, IGNORED = 0)
        : RelationshipAccessor()
    {
        if (!attributeHandle.isValid())
            return;
        Type type = context.iAttributeData->getType(context, attributeHandle);
        BaseDataType baseType = type.baseType;
        if (baseType == BaseDataType::eRelationship)
        {
            size_t componentCount = type.componentCount;
            if (componentCount == 1)
            {
                size_t depth = type.arrayDepth;
                if (depth < 2)
                {
                    void* pData;
                    context.iAttributeData->getDataW(&pData, context, &attributeHandle, 1);
                    data = (depth == 0) ? pData : (*(void* const*)pData);
                    elementCount = omni::graph::core::getElementCount(context, attributeHandle);
                    m_context = context.context;
                    m_attributeHandle = attributeHandle;
                    m_iAttributeData = context.iAttributeData;
                }
            }
        }
    }

    // Construct a RelationshipAccessor by prim and attribute name.
    //
    // The enable_if makes this valid only if T is const, since a non-const accessor can't
    // be initialized with a const attribute handle, but a const accessor can be initialized
    // from a const or non-const attribute handle.
    template <typename HANDLE_TYPE,
              typename IGNORED = typename std::enable_if<readOnly && (std::is_same<HANDLE_TYPE, ConstBundleHandle>::value ||
                                                                      std::is_same<HANDLE_TYPE, BundleHandle>::value),
                                                         int>::type>
    RelationshipAccessor(const GraphContextObj& context, HANDLE_TYPE primHandle, NameToken attributeName, IGNORED = 0)
        : RelationshipAccessor()
    {
        if (!primHandle.isValid())
            return;
        ConstAttributeDataHandle attributeHandle;
        context.iBundle->getAttributesByNameR(&attributeHandle, context, primHandle, &attributeName, 1);
        *this = RelationshipAccessor(context, attributeHandle);
    }

    // Construct a RelationshipAccessor by non-const prim and attribute name.
    //
    // The enable_if makes this valid only if T is non-const, since a non-const accessor can
    // only be initialized with a non-const attribute handle.
    template <typename IGNORED = typename std::enable_if<!readOnly, int>::type>
    RelationshipAccessor(const GraphContextObj& context, BundleHandle primHandle, NameToken attributeName, IGNORED = 0)
        : RelationshipAccessor()
    {
        if (!primHandle.isValid())
            return;
        AttributeDataHandle attributeHandle;
        context.iBundle->getAttributesByNameW(&attributeHandle, context, primHandle, &attributeName, 1);
        *this = RelationshipAccessor(context, attributeHandle);
    }

    ~RelationshipAccessor()
    {
        if (m_context != nullptr && m_iAttributeData != nullptr && m_attributeHandle.isValid())
        {
            CUDA_SAFE_ASSERT(!readOnly, "Only non-const RelationshipAccessor's should update the reference counts!");
            m_iAttributeData->updateRelationshipRefCounts(*m_context, m_attributeHandle);
        }
    }

    bool isValid() const
    {
        return (data != nullptr);
    }
    size_t getElementCount() const
    {
        return elementCount;
    }

    // Returns a pointer to the data if it's a perfect type match, else nullptr.
    BundleHandleType* getData() const
    {
        return data;
    }

    BundleHandleType get(size_t i = 0) const
    {
        CUDA_SAFE_ASSERT(data != nullptr);
        CUDA_SAFE_ASSERT(i < elementCount);
        return data[i];
    }

    // The enable_if makes this valid only if T is non-const.
    template <typename IGNORED = typename std::enable_if<!readOnly, int>::type>
    void set(BundleHandleType value, size_t i = 0, IGNORED = 0) const
    {
        CUDA_SAFE_ASSERT(data != nullptr);
        CUDA_SAFE_ASSERT(i < elementCount);
        // FIXME: Does reference counting of the prims need to be updated now, or will it be updated later?
        data[i] = value;
    }

private:
    BundleHandleType* data;

    size_t elementCount;

    GraphContext* m_context;
    AttributeDataHandle m_attributeHandle;
    IAttributeData* m_iAttributeData;
};
#endif

}
}
}
