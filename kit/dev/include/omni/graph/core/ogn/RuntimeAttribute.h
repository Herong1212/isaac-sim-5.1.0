// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

// =================================================================================================================
// This file contains simple interface classes which wrap data in the OGN database for easier use.
//
//    RuntimeAttribute  Wrapper providing access to attributes whose type is only known at runtime
//                      This includes attributes inside bundles and attributes with extended types
//
// WARNING: These interfaces are subject to change without warning and are only meant to be used by generated code.
//          If you call them directly you may have to modify your code when they change.
// =================================================================================================================

#ifdef THIS_IS_INCLUDED_IN_THE_DOCUMENTATION
// The information bracketed here with begin/end describes the interface that is recommended for use with attributes
// whose data type is decided at runtime. The documentation uses these markers to perform a literal include of this
// code into the docs so that it can be the single source of truth.
// Note that the interface described here is not the complete set of C++ functions available, merely the ones that make
// sense for the user to access when dealing with runtime attributes.
//
//
// begin-extended-attribute-interface-description
// A runtime attribute can either be an attribute defined as one of the extended types ("union" or "any") or an
// attribute that is a member of a bundle. As you might guess, the defining feature of such attributes is the fact
// that the type of data they store is not known until runtime. And further, that type can change from one evaluation
// to the next. For that reason the runtime attribute accessors have different methods of acquiring their data than
// regular attributes.
//
// The two ways of acquiring the accessor for a runtime attribute are directly, for extended types
const auto& anyType = db.inputs.anyTypeAttribute();
// and as a member, for bundled attributes
const auto memberAttribute = db.inputs.myBundle().attributeByName(db.tokens.memberName);

// Runtime attributes can be copied, which copies both the type and the data of the attribute (unlike regular
// attributes, which would just copy the data)
auto newAttribute = anyType;

// There is also another method that will just copy the data, though it is up to you to ensure that the data
// types of the two attributes are the same.
newAttribute.copyData(anyType);

// As with regular attributes you can check if their data is valid...
const bool anyIsValid = anyType.isValid();
// ...get the number of elements in the array, if they are an array type...
const size_t howManyAnysDoIHave = anyType.size();
// ...and drop down to the ABI to get a handle for direct ABI calls (although for runtime attributes the handle
//    is AttributeDataHandle/ConstAttributeDataHandle, not AttributeHandle as it is for regular attributes since
//    the ABI has different capabilities for them)
const auto& abiHandle = anyType.abi_handle();

// They also have a method to determine if the actual type of the attribute has been resolved. Until the type is
// resolved the attribute's data cannot be accessed
const bool isTheTypeKnown = anyType.resolved();

// For bundled attributes the name is not known until runtime either so a method to access that is provided,
// returning the hardcoded name for extended attributes
const memberName&  = memberAttribute.name();

// And the resolved type information is also available. Checking for an unknown type is another way to determine
// if the attribute type has not yet been resolved.
const auto& anyAttributesType = anyType.type();

// Finally there are the data access methods. The primary one is a templated function through which you can access
// the attribute's data in its raw form. The value returned isn't the data itself, it is a thin wrapper around the
// data that has a few functions of its own.
//
// This is the function to call for the majority of attributes, whose memory space is fixed either to CPU or GPU.
// It returns an object that can be used to access information about the attribute's value, including its memory location.
const auto dataAsFloatObj = anyType.get<float>();

// The types allowed in the template are the set of all allowed attribute types, expressed as regular C++ types
// without the attribute roles. For example float, float[], float[3], float[][3], etc. In most cases trying to access
// the data with an unsupported type will result in a compile error (the exceptions being types that are aliases for
// a supported type, e.g. "using float3 = float[3]"). In fact, since the "NameToken" supported type is an alias for
// another supported type it must be retrieved with a special type set up for that purpose
const auto dataAsToken = anyType.get<OgnToken>();

// The wrapper has a boolean cast operator, which checks to see if the requested type matches the actual resolved
// data type of the attribute. This allows you to make a cascading check for types of attributes you are supporting
if (const auto dataAsFloatObj = anyType.get<float>())
{
    processAsFloat(*dataAsFloatObj);
}
else if (const auto dataAsDoubleObj = anyType.get<double>())
{
    processAsDouble(*dataAsDoubleObj);
}

// In addition to the simple boolean validity test, the wrapper returned will have a few different methods,
// depending on the template data type.
// The dereference operators return references to the actual underlying attribute data (on the CPU - if your
// attribute lives on the GPU you'll get a reference to a pointer to the underlying attribute data, which lives in
// the GPU memory space and cannot be dereferenced on the CPU). Note that the default memory location of a bundled
// attribute is whatever was specified for the bundle itself.
const auto dataAsFloatObj = anyType.get<float>();
float const& floatValueDeref = *dataAsFloatObj;
float const& floatValueFn = dataAsFloatObj();
float const* floatValuePtr = dataAsFloatObj.operator->();

// The same dereference operators work for tuple types as well
const auto dataAsFloat3Obj = anyType.get<float[3]();
float const (&float3ValueDeref)[3] = *dataAsFloat3Obj;

// The tuple values also give you access to the tuple count and element-wise access
float x = dataAsFloat3Obj[0];
assert( dataAsFloat3Obj.tupleSize() == 3);

// Array data type wrappers dereference to the same array wrappers you get from regular attributes
const auto dataAsFloatArrayObj = anyType.get<float[]>();
for (const auto& floatValue : *dataAsFloatArrayObj)
{ /* ... */ }
size_t arrayElements = dataAsFloatArrayObj->size();

// For GPU attributes, which do not have the ability to dereference their array memory location, the wrapper instead
// returns a raw pointer to the underlying GPU memory location of the array.
const auto gpuFloatArrayObj = anyType.get<float[]>();
float const ***ptrToRawGpuData = *gpuFloatArrayObj;

// When the node is configured to extract CUDA pointers on the CPU there is one fewer level of indirection for
// arrays as the pointer returned is on the CPU.
const auto gpuFloatArrayObj = anyType.get<float[]>();
float const ***ptrToGpuDataOnCpu = *gpuFloatArrayObj;
float const **ptrToRawGpuData = *ptrToGpuDataOnCpu;

// As with regular array attributes, before writing to elements of an output array attribute you must first resize
// it to have the desired number of elements.
auto outputFloatArrayObj = data.outputs.results().get<float[]>();
outputFloatArrayObj.resize( howManyDoINeed );

// For attributes whose memory space is determined at runtime, or when you want to access attribute data in a different
// memory space than they were originally defined, you can force the retrieved data to be either on the CPU or GPU.
const auto gpuVersionObj = anyType.getGpu<float>();
const auto cpuVersionObj = anyType.getCpu<float>();

// On rare occasions you may need to resolve the attribute's type at runtime, inside a node's compute() function. In
// those cases the runtime attribute data can get out of sync so you need to notify it that a change has been made.
AttributeObj out = db.abi_node().iNode->getAttributeByToken(db.abi_node(), outputs::anyOutput.m_token);
out.iAttribute->setResolvedType(out, someNewType);
anyOutput.reset(db.abi_context(), out.iAttribute->getAttributeDataHandle(out, kAccordingToContextIndex));
// end-extended-attribute-interface-description
//
#endif

#include <omni/graph/core/ogn/TypeConversion.h>
#include <omni/graph/core/ogn/Types.h>
#include <omni/graph/core/ogn/array.h>
#include <omni/graph/core/ogn/string.h>
#include <omni/fabric/Enums.h>
using omni::fabric::PtrToPtrKind;

namespace omni {
namespace graph {
namespace core {
namespace ogn {


// ==============================================================================================================
// House the shared data types that will be used by all data type accessors.
// Not all types are used by all classes, this just provides a single point of type definitions.
template <typename CppType, bool readOnly, eMemoryType MemoryType, PtrToPtrKind GpuPtrType>
struct data_type_traits : attribute_type_traits<CppType>
{
    using parent_t = attribute_type_traits<CppType>;

    // Type that allows switching on memory type
    using isCpu_t = std::integral_constant<bool, MemoryType == kCpu>;

    // Template inheritance isn't smart enough to forward the types and constexprs so manually forward them here
    static constexpr bool isArray = parent_t::isArray;
    static constexpr uint8_t tupleCount = parent_t::tupleCount;
    static constexpr uint8_t arrayDepth = parent_t::arrayDepth;
    static constexpr BaseDataType baseType = parent_t::baseType;
    using data_t = typename parent_t::data_t;

    // The type of attribute handle used to call the ABI functions
    using handle_t = std::conditional_t<readOnly, const ConstAttributeDataHandle, AttributeDataHandle>;

    // The type that will be returned from individual element access (simple or tuple data)
    using element_t = typename std::conditional_t<
        readOnly,
        typename parent_t::element_t const,
        typename parent_t::element_t>;

    // The types used for storage where the constness is hardcoded into the attribute type
    using data_access_t = std::conditional_t<readOnly, data_t const, data_t>;
    using array_t = std::conditional_t<
        readOnly,
        std::conditional_t<std::is_same<const char, data_access_t>::value, const_string, const_array<data_access_t>>,
        std::conditional_t<std::is_same<char, data_access_t>::value, string, array<data_access_t>>>;

    // const, non-const, and appropriate const pointers to the Fabric data
    using data_ptr_t = std::conditional_t<isArray, data_t**, data_t*>;
    using data_ptr_const_t = std::conditional_t<isArray, data_t const**, data_t const*>;
    using data_ptr_access_t = std::conditional_t<readOnly, data_ptr_const_t, data_ptr_t>;

    // CPU array data lives in the wrappers, GPU data is raw since it cannot be dereferenced
    using array_data_t = std::conditional_t<MemoryType == kCpu, array_t, data_ptr_access_t>;

    // ==============================================================================================================
    // Simple test to see if the type of data in the template parameter is compatible with a specific Type()
    static bool matchesType(const Type& attributeType)
    {
        return attributeType.baseType == baseType
            && attributeType.componentCount == tupleCount
            && attributeType.arrayDepth == arrayDepth;
    }

    // ==============================================================================================================
    // Templated access to getting read-only and writable values, calling the correct ABI functions based on memory location
    static data_ptr_const_t readOnlyData(const GraphContextObj& contextObj, const ConstAttributeDataHandle& attrHandle)
    {
        return _readOnlyData(contextObj, attrHandle, std::conditional_t<MemoryType == kCpu, std::false_type, std::true_type>());
    }
    static data_ptr_t writableData(const GraphContextObj& contextObj, AttributeDataHandle const& attrHandle)
    {
        return _writableData(contextObj, attrHandle, std::conditional_t<MemoryType == kCpu, std::false_type, std::true_type>());
    }
    // Calling the right one depending on the handle type
    static data_ptr_const_t data(const GraphContextObj& contextObj, const ConstAttributeDataHandle& attrHandle)
    {
        return _readOnlyData(contextObj, attrHandle, std::conditional_t<MemoryType == kCpu, std::false_type, std::true_type>());
    }
    static data_ptr_t data(const GraphContextObj& contextObj, AttributeDataHandle const& attrHandle)
    {
        return _writableData(contextObj, attrHandle, std::conditional_t<MemoryType == kCpu, std::false_type, std::true_type>());
    }


    // ==============================================================================================================
    // Retrieving a reference on existing data.
    // If data is not located at the right place (gpu/cpu), returns nullptr
    static void dataReference(const GraphContextObj& contextObj,
                              ConstAttributeDataHandle const& attrHandle,
                              ConstRawPtr& ref,
                              size_t& size)
    {
        _dataReference(contextObj, attrHandle, ref, size,
                       std::conditional_t<MemoryType == kCpu, std::false_type, std::true_type>(),
                       std::conditional_t<readOnly, std::true_type, std::false_type>());
    }

    static void dataReference(const GraphContextObj& contextObj,
                              AttributeDataHandle const& attrHandle,
                              RawPtr& ref,
                              size_t& size)
    {
        _dataReference(contextObj, attrHandle, ref, size,
                       std::conditional_t<MemoryType == kCpu, std::false_type, std::true_type>(),
                       std::conditional_t<readOnly, std::true_type, std::false_type>());
    }

private:
    // These methods could not use the getDataX<> templates due to an oddity in how const is handled in composed typedefs.
    // It's slightly more efficient to build anyway, and since it goes through the ABI it's just as safe
    static data_ptr_const_t _readOnlyData(const GraphContextObj& contextObj, ConstAttributeDataHandle const& attrHandle, std::true_type)
    {
        data_ptr_const_t out{ nullptr };
        const void** outPtr = (const void**)(&out);
        contextObj.iAttributeData->getDataRGpuAt(outPtr, contextObj, &attrHandle, 1, GpuPtrType);
        return out;
    }
    static data_ptr_const_t _readOnlyData(const GraphContextObj& contextObj, ConstAttributeDataHandle const& attrHandle, std::false_type)
    {
        data_ptr_const_t out{ nullptr };
        const void** outPtr = (const void**)(&out);
        contextObj.iAttributeData->getDataR(outPtr, contextObj, &attrHandle, 1);
        return out;
    }
    static data_ptr_t _writableData(const GraphContextObj& contextObj, AttributeDataHandle const& attrHandle, std::true_type)
    {
        data_ptr_t out{ nullptr };
        void** outPtr = (void**)(&out);
        contextObj.iAttributeData->getDataWGpuAt(outPtr, contextObj, &attrHandle, 1, GpuPtrType);
        return out;
    }
    static data_ptr_t _writableData(const GraphContextObj& contextObj, AttributeDataHandle const& attrHandle, std::false_type)
    {
        data_ptr_t out{ nullptr };
        void** outPtr = (void**)(&out);
        contextObj.iAttributeData->getDataW(outPtr, contextObj, &attrHandle, 1);
        return out;
    }
    static void _dataReference(const GraphContextObj& contextObj, ConstAttributeDataHandle const& attrHandle,
                               ConstRawPtr& ref, size_t& size, std::true_type isGpu, std::true_type isRO)
    {
        contextObj.iAttributeData->getDataReferenceRGpuAt(attrHandle, contextObj, GpuPtrType, ref, size);
    }
    static void _dataReference(const GraphContextObj& contextObj, ConstAttributeDataHandle const& attrHandle,
                               ConstRawPtr& ref, size_t& size, std::false_type isGpu, std::true_type isRO)
    {
        contextObj.iAttributeData->getDataReferenceR(attrHandle, contextObj, ref, size);
    }
    static void _dataReference(const GraphContextObj& contextObj, AttributeDataHandle const& attrHandle,
                               RawPtr& ref, size_t& size, std::true_type isGpu, std::false_type isRO)
    {
        contextObj.iAttributeData->getDataReferenceWGpuAt(attrHandle, contextObj, GpuPtrType, ref, size);
    }
    static void _dataReference(const GraphContextObj& contextObj, AttributeDataHandle const& attrHandle,
                               RawPtr& ref, size_t& size, std::false_type isGpu, std::false_type isRO)
    {
        contextObj.iAttributeData->getDataReferenceW(attrHandle, contextObj, ref, size);
    }
};

// ==============================================================================================================
// Simple wrapper to access the actual value with potential conversion on the read one
template <typename CppType, eMemoryType MemoryType, PtrToPtrKind GpuPtrType = PtrToPtrKind::eNotApplicable>
struct SimpleDataReadOnly
{
    using data_traits = data_type_traits<CppType, true, MemoryType, GpuPtrType>;
    using return_type = const typename data_traits::data_t;
    typename data_traits::data_ptr_access_t m_value{nullptr};
    Converter<typename data_traits::data_t> m_converter;
    Type const& m_type;
    explicit SimpleDataReadOnly(typename data_traits::data_access_t* value, Type const& type) : m_value{ value }, m_type{ type } {}
    return_type& operator*() const { return *m_converter.convertValue(m_value, m_type); }
    return_type* operator->() const { return m_converter.convertValue(m_value, m_type); }
    gsl::span<return_type> vectorized(size_t count) const&& = delete;//not callable on rvalues, as it might return ref on internals when using auto conversion
    gsl::span<return_type> vectorized(size_t count) const&
    {
        if (m_converter.willConvert(m_type))
        {
            if (count != 1)
                return gsl::span<return_type>{};
            return gsl::span<return_type>{ m_converter.convertValue(m_value, m_type), 1 };
        }
        return gsl::span<return_type>{ m_value, count };
    }
    bool isValid() const  { return m_value; }
    operator bool() const { return isValid(); }
};

template <typename CppType, eMemoryType MemoryType, PtrToPtrKind GpuPtrType = PtrToPtrKind::eNotApplicable>
struct SimpleDataWritable
{
    using data_traits = data_type_traits<CppType, false, MemoryType, GpuPtrType>;
    using return_type = typename data_traits::data_t;
    typename data_traits::data_ptr_access_t m_value{ nullptr };
    SimpleDataWritable(typename data_traits::data_access_t* m_value, Type const&) : m_value{m_value} {}
    return_type& operator*() { return *this->m_value; }
    return_type* operator->() { return this->m_value; }
    gsl::span<return_type> vectorized(size_t count) const { return { m_value, count }; }
    bool isValid() const  { return m_value; }
    operator bool() const { return isValid(); }
};

// ==============================================================================================================
// Tuple data behaves the same as simple data, with the addition of element accessors and a size function.
template <typename CppType, eMemoryType MemoryType, PtrToPtrKind GpuPtrType = PtrToPtrKind::eNotApplicable>
struct TupleDataReadOnly : SimpleDataReadOnly<CppType, MemoryType, GpuPtrType>
{
    using data_traits = data_type_traits<CppType, true, MemoryType, GpuPtrType>;
    TupleDataReadOnly(typename data_traits::data_access_t* value, Type const& type) : SimpleDataReadOnly<CppType, MemoryType, GpuPtrType>{value, type} {}

    // GPU data is passed as a pointer to the tuple so for now there is no need for elementwise access here
    const typename data_traits::element_t& operator[](uint8_t index) const
    {
        static_assert(MemoryType == kCpu, "Cannot access individual tuple elements on GPU data");
        CARB_ASSERT(index < this->tupleSize());
        return (**this)[index];
    }
    uint8_t tupleSize() const { return data_traits::tupleCount; }
};
template <typename CppType, eMemoryType MemoryType, PtrToPtrKind GpuPtrType = PtrToPtrKind::eNotApplicable>
struct TupleDataWritable : SimpleDataWritable<CppType, MemoryType, GpuPtrType>
{
    using data_traits = data_type_traits<CppType, false, MemoryType, GpuPtrType>;
    TupleDataWritable(typename data_traits::data_access_t* value, Type const& type) : SimpleDataWritable<CppType, MemoryType, GpuPtrType>{value, type} {}

    // GPU data is passed as a pointer to the tuple so for now there is no need for elementwise access here
    typename data_traits::element_t& operator[](uint8_t index)
    {
        static_assert(MemoryType == kCpu, "Cannot access individual tuple elements on GPU data");
        CARB_ASSERT(index < this->tupleSize());
        return (**this)[index];
    }
    uint8_t tupleSize() const { return data_traits::tupleCount; }
};

// ==============================================================================================================
//Default version, for CPU
template <typename CppType, bool readOnly, eMemoryType MemoryType, PtrToPtrKind GpuPtrType = PtrToPtrKind::eNotApplicable>
struct ArrayData
{
    using data_traits = data_type_traits<CppType, readOnly, MemoryType, GpuPtrType>;
    using return_type = typename data_traits::array_data_t;
    using handle_type = typename data_traits::handle_t;

    explicit ArrayData(const GraphContextObj& context, handle_type const* handle, bool isValid)
    {
        if (isValid)
        {
            m_arrayData.setContext(context);
            m_arrayData.setHandle(*handle);
        }
    }
    size_t size() const { return m_arrayData.isValid() ? m_arrayData.size() : 0; }
    return_type& operator*()  { return m_arrayData; }
    return_type& operator()() { return m_arrayData; }
    return_type* operator->() { return &m_arrayData; }

    //const accessors
    return_type const& operator*()  const { return m_arrayData; }
    return_type const& operator()() const { return m_arrayData; }
    return_type const* operator->() const { return &m_arrayData; }

    //Bool operator
    bool isValid() const  { return m_arrayData.isValid(); }
    operator bool() const { return isValid(); }

    //Invalidate
    void invalidate() { m_arrayData.setDirty();}

    GraphContextObj const* context() const { return m_arrayData.context(); }
    handle_type const& handle() const { return m_arrayData.handle(); }

protected:
    return_type m_arrayData;
};

// ==============================================================================================================
// Special version, for GPU
template <typename CppType, bool readOnly, PtrToPtrKind GpuPtrType>
struct ArrayData<CppType, readOnly, kCuda, GpuPtrType>
{
    using data_traits = data_type_traits<CppType, readOnly, kCuda, GpuPtrType>;
    using return_type = typename data_traits::array_data_t;
    using handle_type = typename data_traits::handle_t;
    using this_t = ArrayData<CppType, readOnly, kCuda, GpuPtrType>;

    explicit ArrayData(const GraphContextObj& context, handle_type const* handle, bool isValid)
    {
        if (isValid)
        {
            m_ctx = &context;
            m_hdl = handle;
        }
        else
        {
            m_ctx = nullptr;
            m_hdl = nullptr;
        }
    }

    size_t size() const
    {
        if (!isValid())
        {
            CARB_LOG_ERROR("Accessing an invalid array");
            return 0;
        }
        size_t count = 0;
        ConstAttributeDataHandle hdl = *m_hdl;
        m_ctx->iAttributeData->getElementCount(&count, *m_ctx, &hdl, 1);
        return count;
    }

    //accessors
    return_type deref()
    {
        if (!isValid())
        {
            CARB_LOG_ERROR("Accessing an invalid array");
            return 0;
        }
        using PtrType = typename std::conditional<readOnly, ConstRawPtr, RawPtr>::type;
        return_type dataPtr{ nullptr };
        size_t size = 0;
        data_traits::dataReference(*m_ctx, *m_hdl, (PtrType&) dataPtr, size);
        return size ? dataPtr : 0;
    }
    return_type operator*()  { return data_traits::data(*this->m_ctx, *this->m_hdl); }
    return_type operator()() { return data_traits::data(*this->m_ctx, *this->m_hdl); }

    //const accessors
    return_type const operator*()  const { return const_cast<this_t*>(this)->operator*(); }
    return_type const operator()() const { return const_cast<this_t*>(this)->operator()(); }

    bool isValid() const  { return m_ctx && m_hdl; }
    operator bool() const { return isValid(); }

    void invalidate() {}
    GraphContextObj const* context() const { return m_ctx; }
    handle_type const& handle() const { return *m_hdl; }

protected:
    GraphContextObj const* m_ctx;
    handle_type const* m_hdl;
};

template <typename CppType, eMemoryType MemoryType, PtrToPtrKind GpuPtrType = PtrToPtrKind::eNotApplicable>
struct ArrayDataReadOnly : ArrayData<CppType, true, MemoryType, GpuPtrType>
{
    ArrayDataReadOnly(const GraphContextObj& context, ConstAttributeDataHandle const* handle, bool isValid)
        : ArrayData<CppType, true, MemoryType, GpuPtrType>{ context, handle, isValid }
    {}
};


template <typename CppType, eMemoryType MemoryType, PtrToPtrKind GpuPtrType = PtrToPtrKind::eNotApplicable>
struct ArrayDataWritable : ArrayData<CppType, false, MemoryType, GpuPtrType>
{
    ArrayDataWritable(const GraphContextObj& context, AttributeDataHandle const* handle, bool isValid)
    : ArrayData<CppType, false, MemoryType, GpuPtrType>{context, handle, isValid}
    {}

    void resize(size_t newCount)
    {
        if (!this->isValid())
        {
            CARB_LOG_ERROR("Trying to resize an invalid array");
            return;
        }
        auto const& ctx = *this->context();
        const IAttributeData& iData = *(ctx.iAttributeData);
        iData.setElementCount(ctx, this->handle(), newCount);
        this->invalidate();
    }
};

// ==============================================================================================================
template <typename CppType, eMemoryType MemoryType, PtrToPtrKind GpuPtrType = PtrToPtrKind::eNotApplicable>
struct TupleArrayDataReadOnly : ArrayDataReadOnly<CppType, MemoryType, GpuPtrType>
{
    using data_traits = data_type_traits<CppType, true, MemoryType, GpuPtrType>;
    TupleArrayDataReadOnly(const GraphContextObj& context, ConstAttributeDataHandle const* handle, bool isValid)
    : ArrayDataReadOnly<CppType, MemoryType, GpuPtrType>{context, handle, isValid} {}

    // GPU data is passed as a pointer to the tuple so for now there is no need for element wise access here
    const typename data_traits::data_t& operator[] (uint8_t index) const
    {
        static_assert(MemoryType == kCpu, "Cannot access individual tuple elements on GPU data");
        CARB_ASSERT(index < this->tupleSize());
        return this->m_arrayData[index];
    }
    uint8_t tupleSize() const { return data_traits::tupleCount; }
};
template <typename CppType, eMemoryType MemoryType, PtrToPtrKind GpuPtrType = PtrToPtrKind::eNotApplicable>
struct TupleArrayDataWritable : ArrayDataWritable<CppType, MemoryType, GpuPtrType>
{
    using data_traits = data_type_traits<CppType, false, MemoryType, GpuPtrType>;
    TupleArrayDataWritable(const GraphContextObj& context, AttributeDataHandle const* handle, bool isValid)
    : ArrayDataWritable<CppType, MemoryType, GpuPtrType>{context, handle, isValid} {}

    // GPU data is passed as a pointer to the tuple so for now there is no need for element wise access here
    typename data_traits::data_t& operator[](uint8_t index)
    {
        static_assert(MemoryType == kCpu, "Cannot access individual tuple elements on GPU data");
        CARB_ASSERT(index < this->tupleSize());
        return this->m_arrayData[index];
    }
    uint8_t tupleSize() const { return data_traits::tupleCount; }
};

// ======================================================================
/**
 * Class responsible for managing the interaction with an attribute whose data type is determined at runtime.
 * These attributes may or may not not have a corresponding node attribute object. Those within bundles are virtual
 * and do not have a concrete attribute. Those with extended types, do.
 *
 * It wraps the attribute information in an interface with a more natural interaction than the raw ABI calls.
 */
template <eAttributeType AttributeType, eMemoryType MemoryType, PtrToPtrKind GpuPtrType = PtrToPtrKind::eNotApplicable>
class RuntimeAttribute
{
public :
    // Make const-ness aware at compile time so that this class be used in const and non-const contexts
    static constexpr bool readOnly = (AttributeType == ogn::kOgnInput);

    //! The handle types are not simply "X" and "const X" variations so the type has to be explicitly defined
    //! for writable (output/state) and non-writable (input) attribute types.
    using dataHandle_t = typename std::conditional_t<readOnly, ConstAttributeDataHandle, AttributeDataHandle>;

private:
    //! Traits for generic access to the raw memory.
    template <eMemoryType MT>
    using raw_data_traits_mt = data_type_traits<uint8_t, readOnly, MT, GpuPtrType>;
    using raw_data_traits = raw_data_traits_mt<MemoryType>;

    template <typename CppType, eMemoryType AccessorMemoryType, PtrToPtrKind AccessorGpuPtrType = PtrToPtrKind::eNotApplicable>
    using simpleData_t = std::conditional_t<
        readOnly,
        ogn::SimpleDataReadOnly<CppType, AccessorMemoryType, AccessorGpuPtrType>,
        ogn::SimpleDataWritable<CppType, AccessorMemoryType, AccessorGpuPtrType>
    >;
    template <typename CppType, eMemoryType AccessorMemoryType, PtrToPtrKind AccessorGpuPtrType = PtrToPtrKind::eNotApplicable>
    using tupleData_t = typename std::conditional_t<
        readOnly,
        ogn::TupleDataReadOnly<CppType, AccessorMemoryType, AccessorGpuPtrType>,
        ogn::TupleDataWritable<CppType, AccessorMemoryType, AccessorGpuPtrType>
    >;
    template <typename CppType, eMemoryType AccessorMemoryType, PtrToPtrKind AccessorGpuPtrType = PtrToPtrKind::eNotApplicable>
    using arrayData_t = typename std::conditional_t<
        readOnly,
        ogn::ArrayDataReadOnly<CppType, AccessorMemoryType, AccessorGpuPtrType>,
        ogn::ArrayDataWritable<CppType, AccessorMemoryType, AccessorGpuPtrType>
    >;
    template <typename CppType, eMemoryType AccessorMemoryType, PtrToPtrKind AccessorGpuPtrType = PtrToPtrKind::eNotApplicable>
    using tupleArrayData_t = typename std::conditional_t<
        readOnly,
        ogn::TupleArrayDataReadOnly<CppType, AccessorMemoryType, AccessorGpuPtrType>,
        ogn::TupleArrayDataWritable<CppType, AccessorMemoryType, AccessorGpuPtrType>
    >;


    /**
     * helper that allows to make the proper call depending on the type of the handle
     */
    inline void _moveHdl(const IAttributeData& iData, size_t index, ConstAttributeDataHandle& hdl) const
    {
        hdl = iData.moveToAnotherInstanceR(m_context, hdl, (int)index);
    }
    inline void _moveHdl(const IAttributeData& iData, size_t index, AttributeDataHandle& hdl) const
    {
        hdl = iData.moveToAnotherInstanceW(m_context, hdl, (int)index);
    }

    /**
     * helper that prefetch the data pointer for the attribute
     */
    template <eMemoryType MT = MemoryType>
    inline void _prefetch() const
    {
        if (MT != kAny)
            m_cachedData = raw_data_traits_mt<MT>::data(m_context, m_handle);
    }

    GraphContextObj m_context{ 0 }; //!< Evaluation context for which this attribute is valid
    NameToken m_name; //!< Name by which this attribute is accessed
    Type m_type; //!< Type information for the actual attribute data
    Type m_resolvedType; //!< Type information for the attribute interface
    dataHandle_t m_handle; //!< Handle of the attribute data
    mutable typename raw_data_traits::data_access_t* m_cachedData{ nullptr };

public:
    /**
     * Default constructor will create an invalid attribute
     */
    RuntimeAttribute()
        : m_type(BaseDataType::eUnknown),
          m_resolvedType(BaseDataType::eUnknown),
          m_handle(dataHandle_t::invalidValue())
    {
    }

    /**
     * Although the destructor should always be implemented with copy constructors it has no resources to release
     */
    ~RuntimeAttribute() = default;

    /**
     * Copy constructor, to allow these objects to be easily passed around.
     * Only attributes with the same accessibility and memory type should be copied.
     */
    RuntimeAttribute(const RuntimeAttribute<AttributeType, MemoryType, GpuPtrType>& toCopy)
        : m_context(toCopy.m_context),
          m_name(toCopy.m_name),
          m_type(toCopy.m_type),
          m_resolvedType(toCopy.m_resolvedType),
          m_handle(toCopy.m_handle)
    {
        if (m_handle != dataHandle_t::invalidHandle())
            _prefetch<>();
        else
            m_cachedData = nullptr;
    }

    /**
     * Move constructor, to allow these objects to be efficiently passed around
     * Only attributes with the same accessibility and memory type should be copied.
     */
    RuntimeAttribute(RuntimeAttribute<AttributeType, MemoryType, GpuPtrType>&& toCopy)
        : m_context(toCopy.m_context),
          m_name(toCopy.m_name),
          m_type(toCopy.m_type),
          m_resolvedType(toCopy.m_resolvedType),
          m_handle(toCopy.m_handle)
    {
        if (m_handle != dataHandle_t::invalidHandle())
            _prefetch();
        else
            m_cachedData = nullptr;
    }

    /**
     * Copy assignment, to match the constructor
     * Only attributes with the same accessibility and memory type should be copied.
     */
    RuntimeAttribute<AttributeType, MemoryType, GpuPtrType>&
    operator=(const RuntimeAttribute<AttributeType, MemoryType, GpuPtrType>& toCopy)
    {
        m_context = toCopy.m_context;
        m_name = toCopy.m_name;
        m_type = toCopy.m_type;
        m_resolvedType = toCopy.m_resolvedType;
        m_handle = toCopy.m_handle;
        m_cachedData = toCopy.m_cachedData;
        return *this;
    }

    /**
     * Move assignment, to match the constructor
     * Only attributes with the same accessibility and memory type should be copied.
     */
    RuntimeAttribute<AttributeType, MemoryType, GpuPtrType>&
    operator=(RuntimeAttribute<AttributeType, MemoryType, GpuPtrType>&& toCopy)
    {
        m_context = toCopy.m_context;
        m_name = toCopy.m_name;
        m_type = toCopy.m_type;
        m_resolvedType = toCopy.m_resolvedType;
        m_handle = toCopy.m_handle;
        m_cachedData = toCopy.m_cachedData;
        return *this;
    }

    /**
     * Standard constructor, extracts the attribute information if it is valid.
     *
     * @param[in] context Evaluaton context of this attribute
     * @param[in] handle Handle to the attribute
     * @param[in] resolvedType The type exposed to end user (conversion will happen if different from the actual real type)
     */
    RuntimeAttribute(const GraphContextObj& context, dataHandle_t& handle, Type const& resolvedType = { BaseDataType::eUnknown })
        : m_context(context), m_type(BaseDataType::eUnknown), m_resolvedType(resolvedType), m_handle(handle)
    {
        if (m_handle.isValid())
        {
            m_name = context.iAttributeData->getName(context, handle);
            m_type = context.iAttributeData->getType(context, handle);
            if (m_resolvedType.baseType == BaseDataType::eUnknown)
                m_resolvedType = m_type;
            _prefetch();
        }
        else
        {
            m_cachedData = nullptr;
        }
    }

    /**
     * Standard constructor, extracts the attribute information if it is valid.
     *
     * @param[in] context Evaluaton context of this attribute
     * @param[in] handle Handle to the attribute
     * @param[in] @param[in] resolvedType The type exposed to end user (conversion will happen if different from the actual real type)
     */
    RuntimeAttribute(GraphContextObj&& context, dataHandle_t&& handle, Type const& resolvedType = { BaseDataType::eUnknown })
        : m_context(context), m_type(BaseDataType::eUnknown), m_resolvedType(resolvedType), m_handle(handle)
    {
        if (m_handle.isValid())
        {
            m_name = context.iAttributeData->getName(context, handle);
            m_type = context.iAttributeData->getType(context, handle);
            if (m_resolvedType.baseType == BaseDataType::eUnknown)
                m_resolvedType = m_type;
            _prefetch();
        }
        else
        {
            m_cachedData = nullptr;
        }
    }

    /**
     * Forces to re-fetch the data pointer
     */
    void invalidateCachedPointer()
    {
        _prefetch();
    }

    /**
     * Copy the data from another runtime attribute into this one (only valid for non-const objects)
     *
     * @param[in] rhs Runtime attribute being copied
     */
    template <typename SourceAttribute>
    void copyData(const SourceAttribute& rhs)
    {
        static_assert(! readOnly, "Attribute data can only be copied to writable attributes");
        ConstAttributeDataHandle constSrcHandle(rhs.abi_handle());
        m_context.iAttributeData->copyData(m_handle, m_context, constSrcHandle);
    }

    /**
     * Set the context and attribute handle for evaluation. Delayed so that the contents can be created
     * early with just-in-time initialization.
     *
     * @param[in] context Evaluation context to use when extracting information
     * @param[in] handle Handle to the attribute being wrapped
     * @param[in] attr The attribute object represented by this wrapper
     */
    void reset(const GraphContextObj& context, const dataHandle_t& handle, const AttributeObj& attr)
    {
        m_handle = handle;
        m_context = context;

        // Set the name even if the data handle isn't valid right now. For union dynamic attribute types, we only get a
        // valid data handle after type resolution. There is code in the databases (See onTypeResolutionChanged) to mark
        // the runtime attribute dirty and have it fetch it on first access (See fetchDetails). But this cannot be
        // triggered unless we can identify which RuntimeAttribute object corresponds to the attribute
        m_name = attr.iAttribute->getNameToken(attr);

        if (m_handle.isValid())
        {
            m_type = context.iAttributeData->getType(context, handle);
            m_resolvedType = attr.iAttribute->getResolvedType(attr);
            if (m_resolvedType.baseType == BaseDataType::eUnknown)
                m_resolvedType = m_type;
            _prefetch();
        }
        else
        {
            m_type = Type{BaseDataType::eUnknown};
            m_resolvedType = Type{ BaseDataType::eUnknown };
            m_cachedData = nullptr;
        }
    }

    /**
     * @return true if the handle and context point to valid data within the fabric
     */
    bool isValid() const
    {
        return m_handle.isValid();
    }

    /**
     * @return Name by which this attribute's data is referenced
     */
    const NameToken& name() const
    {
        return m_name;
    }

    /**
     * @return Type information for this attribute's data
     */
    const Type& type() const
    {
        return m_resolvedType.baseType != BaseDataType ::eUnknown ? m_resolvedType : m_type;
    }

    /**
     * @return True if the data can be accessed in a vectorized manner for this attribute
     */
    const bool canVectorize() const
    {
        //attrib needs to exists, and to be resolved as the the same type (ie. no auto conversion)
        //we don't care about role
        return  m_type.baseType != BaseDataType::eUnknown &&
                m_type.baseType ==  m_resolvedType.baseType &&
                m_type.componentCount == m_resolvedType.componentCount &&
                m_type.arrayDepth == m_resolvedType.arrayDepth;
    }

    /**
     * @return The standardized type name for this attribute's data
     */
    std::string typeName() const
    {
        return getOgnTypeName(type());
    }

    /**
     * @return True if the attribute has a fully resolved type
     */
    bool resolved() const
    {
        return m_type.baseType != BaseDataType::eUnknown;
    }

    /**
     * @return Raw attribute data handle to use for direct ABI manipulation
     */
    dataHandle_t abi_handle() const
    {
        return m_handle;
    }

    /**
     * In vectorized context, make this attribute point to another instance
     * @param[in] offset The distance at which the target instance is located relative to the currently pointed one
     */
    void adjustHandle(size_t offset)
    {
        const IAttributeData& iData = *m_context.iAttributeData;
        _moveHdl(iData, offset, m_handle);
        _prefetch();
    }

    /**
     * @return Raw graph context assotiated to the handle to use for direct ABI manipulation
     */
    GraphContextObj const& abi_context() const
    {
        return m_context;
    }

    /**
     * @return the number of elements in the array, or 1 if it is not an array type
     */
    size_t size() const
    {
        size_t count{ 1 };
        if (m_type.arrayDepth > 0)
        {
            ConstAttributeDataHandle constHandle{ m_handle }; // getElementCount requires the Const version
            m_context.iAttributeData->getElementCount(&count, m_context, &constHandle, 1);
        }
        return count;
    }

    // ------------------------------------------------------------------------------------------------------------
    // Support for the various methods to retrieve a generic value type as get<TYPE>().
    //
    // The details in the template and traits information is intended to make access to the data is generic as possible
    // given the information provided by the data types and this attribute's class members.
    //
    // Almost all of the time you will access what appears to be a single templated method as this:
    //
    //      auto dataAccessor = thisAttribute.get<DATA_TYPE>();
    //      if (dataAccessor.isValid()) ... // The data is the right type, and is valid
    //      // e.g. auto intData = intAttribute.get<int>();
    //
    // This hardcodes the compile time information about whether the attribute was read-only, what type of data it
    // accepts, and the memory location, into what appears to be a single accessor (though behind the scenes it is
    // actually a small set of them that provide appropriate access points for the type of data).
    //
    // For special attributes who have their memory location designated as "any", the decision of memory location is
    // made at access time so two variations of the above method are available which explicitly get accessors on either
    // the CPU or GPU memory locations:
    //
    //      auto dataAccessorCpu = thisAttribute.getCpu<DATA_TYPE>();
    //      auto dataAccessorGpu = thisAttribute.getGpu<DATA_TYPE>();
    //
    // Note: Use only one of the two memory location accessors as accessing one type will often invalidate the other
    //       type, potentially causing excessive slow copying of data.
    //
    template <typename POD, eMemoryType GetAtMemoryType, PtrToPtrKind GetAtGpuPtrType = PtrToPtrKind::eNotApplicable, typename std::enable_if_t<attribute_type_traits<POD>::isSimpleType, int> = 0>
    const simpleData_t<POD, GetAtMemoryType, GetAtGpuPtrType> getAt() const
    {
        using data_traits = data_type_traits<POD, readOnly, GetAtMemoryType, GetAtGpuPtrType>;
        using data_ptr_access_t = typename data_traits::data_ptr_access_t;
        return simpleData_t<POD, GetAtMemoryType, GetAtGpuPtrType>(
            data_traits::matchesType(m_resolvedType) ? data_ptr_access_t(m_cachedData) : nullptr,
            m_type);
    }
    template <typename POD, eMemoryType GetAtMemoryType, PtrToPtrKind GetAtGpuPtrType = PtrToPtrKind::eNotApplicable, typename std::enable_if_t<attribute_type_traits<POD>::isSimpleType, int> = 0>
    simpleData_t<POD, GetAtMemoryType, GetAtGpuPtrType> getAt()
    {
        static_assert(! readOnly, "non-const get() can only be called on output attributes");
        using data_traits = data_type_traits<POD, readOnly, GetAtMemoryType, GetAtGpuPtrType>;
        using data_ptr_access_t = typename data_traits::data_ptr_access_t;
        return simpleData_t<POD, GetAtMemoryType, GetAtGpuPtrType>(
            data_traits::matchesType(m_type) ? data_ptr_access_t(m_cachedData) : nullptr,
            m_type);
    }
    template <typename POD, eMemoryType GetAtMemoryType, PtrToPtrKind GetAtGpuPtrType = PtrToPtrKind::eNotApplicable, typename std::enable_if_t<attribute_type_traits<POD>::isTupleType, int> = 0>
    const tupleData_t<POD, GetAtMemoryType, GetAtGpuPtrType> getAt() const
    {
        using data_traits = data_type_traits<POD, readOnly, GetAtMemoryType, GetAtGpuPtrType>;
        using data_ptr_access_t = typename data_traits::data_ptr_access_t;
        return tupleData_t<POD, GetAtMemoryType, GetAtGpuPtrType>(
            data_traits::matchesType(m_resolvedType) ? data_ptr_access_t(m_cachedData) : nullptr,
            m_type);
    }
    template <typename POD, eMemoryType GetAtMemoryType, PtrToPtrKind GetAtGpuPtrType = PtrToPtrKind::eNotApplicable, typename std::enable_if_t<attribute_type_traits<POD>::isTupleType, int> = 0>
    tupleData_t<POD, GetAtMemoryType, GetAtGpuPtrType> getAt()
    {
        static_assert(! readOnly, "non-const get() can only be called on output attributes");
        using data_traits = data_type_traits<POD, readOnly, GetAtMemoryType, GetAtGpuPtrType>;
        using data_ptr_access_t = typename data_traits::data_ptr_access_t;
        return tupleData_t<POD, GetAtMemoryType, GetAtGpuPtrType>(
            data_traits::matchesType(m_type) ? data_ptr_access_t(m_cachedData) : nullptr,
            m_type);
    }
    template <typename POD, eMemoryType GetAtMemoryType, PtrToPtrKind GetAtGpuPtrType = PtrToPtrKind::eNotApplicable, typename std::enable_if_t<attribute_type_traits<POD>::isArrayType, int> = 0>
    const arrayData_t<POD, GetAtMemoryType, GetAtGpuPtrType> getAt() const
    {
        using data_traits = data_type_traits<POD, readOnly, GetAtMemoryType, GetAtGpuPtrType>;
        return arrayData_t<POD, GetAtMemoryType, GetAtGpuPtrType>(m_context, &m_handle, data_traits::matchesType(m_type));
    }
    template <typename POD, eMemoryType GetAtMemoryType, PtrToPtrKind GetAtGpuPtrType = PtrToPtrKind::eNotApplicable, typename std::enable_if_t<attribute_type_traits<POD>::isArrayType, int> = 0>
    arrayData_t<POD, GetAtMemoryType, GetAtGpuPtrType> getAt()
    {
        static_assert(! readOnly, "non-const get() can only be called on output attributes");
        using data_traits = data_type_traits<POD, readOnly, GetAtMemoryType, GetAtGpuPtrType>;
        return arrayData_t<POD, GetAtMemoryType, GetAtGpuPtrType>(m_context, &m_handle, data_traits::matchesType(m_type));
    }
    template <typename POD, eMemoryType GetAtMemoryType, PtrToPtrKind GetAtGpuPtrType = PtrToPtrKind::eNotApplicable, typename std::enable_if_t<attribute_type_traits<POD>::isTupleArrayType, int> = 0>
    const tupleArrayData_t<POD, GetAtMemoryType, GetAtGpuPtrType> getAt() const
    {
        using data_traits = data_type_traits<POD, readOnly, GetAtMemoryType, GetAtGpuPtrType>;
        return tupleArrayData_t<POD, GetAtMemoryType, GetAtGpuPtrType>(m_context, &m_handle, data_traits::matchesType(m_type));
    }
    template <typename POD, eMemoryType GetAtMemoryType, PtrToPtrKind GetAtGpuPtrType = PtrToPtrKind::eNotApplicable, typename std::enable_if_t<attribute_type_traits<POD>::isTupleArrayType, int> = 0>
    tupleArrayData_t<POD, GetAtMemoryType, GetAtGpuPtrType> getAt()
    {
        static_assert(! readOnly, "non-const get() can only be called on output attributes");
        using data_traits = data_type_traits<POD, readOnly, GetAtMemoryType, GetAtGpuPtrType>;
        return tupleArrayData_t<POD, GetAtMemoryType, GetAtGpuPtrType>(m_context, &m_handle, data_traits::matchesType(m_type));
    }

    // ------------------------------------------------------------------------------------------------------------
    // Variations of the get<>() functions that force either CPU or GPU memory location. These are used when the
    // memory location of the attributes was set to "any", meaning they decide CPU or GPU at runtime, though there's
    // no reason they can't be used for explicit memory locations either.
    template <typename POD, typename std::enable_if_t<attribute_type_traits<POD>::isSimpleType, int> = 0>
    const simpleData_t<POD, MemoryType, GpuPtrType> get() const
    {
        static_assert(MemoryType != kAny, "Use getCpu() or getGpu() to specify where the attribute's memory lives");
        return getAt<POD, MemoryType, GpuPtrType>();
    }
    template <typename POD, typename std::enable_if_t<attribute_type_traits<POD>::isSimpleType, int> = 0>
    simpleData_t<POD, MemoryType, GpuPtrType> get()
    {
        static_assert(MemoryType != kAny, "Use getCpu() or getGpu() to specify where the attribute's memory lives");
        return getAt<POD, MemoryType, GpuPtrType>();
    }
    template <typename POD, typename std::enable_if_t<attribute_type_traits<POD>::isTupleType, int> = 0>
    const tupleData_t<POD, MemoryType, GpuPtrType> get() const
    {
        static_assert(MemoryType != kAny, "Use getCpu() or getGpu() to specify where the attribute's memory lives");
        return getAt<POD, MemoryType, GpuPtrType>();
    }
    template <typename POD, typename std::enable_if_t<attribute_type_traits<POD>::isTupleType, int> = 0>
    tupleData_t<POD, MemoryType, GpuPtrType> get()
    {
        static_assert(MemoryType != kAny, "Use getCpu() or getGpu() to specify where the attribute's memory lives");
        return getAt<POD, MemoryType, GpuPtrType>();
    }
    template <typename POD, typename std::enable_if_t<attribute_type_traits<POD>::isArrayType, int> = 0>
    const arrayData_t<POD, MemoryType, GpuPtrType> get() const
    {
        static_assert(MemoryType != kAny, "Use getCpu() or getGpu() to specify where the attribute's memory lives");
        return getAt<POD, MemoryType, GpuPtrType>();
    }
    template <typename POD, typename std::enable_if_t<attribute_type_traits<POD>::isArrayType, int> = 0>
    arrayData_t<POD, MemoryType, GpuPtrType> get()
    {
        static_assert(MemoryType != kAny, "Use getCpu() or getGpu() to specify where the attribute's memory lives");
        return getAt<POD, MemoryType, GpuPtrType>();
    }
    template <typename POD, typename std::enable_if_t<attribute_type_traits<POD>::isTupleArrayType, int> = 0>
    const tupleArrayData_t<POD, MemoryType, GpuPtrType> get() const
    {
        static_assert(MemoryType != kAny, "Use getCpu() or getGpu() to specify where the attribute's memory lives");
        return getAt<POD, MemoryType, GpuPtrType>();
    }
    template <typename POD, typename std::enable_if_t<attribute_type_traits<POD>::isTupleArrayType, int> = 0>
    tupleArrayData_t<POD, MemoryType, GpuPtrType> get()
    {
        static_assert(MemoryType != kAny, "Use getCpu() or getGpu() to specify where the attribute's memory lives");
        return getAt<POD, MemoryType, GpuPtrType>();
    }
    // --------------------------------------------------------------------------------------------------------------
    template <typename POD, typename std::enable_if_t<attribute_type_traits<POD>::isSimpleType, int> = 0>
    const simpleData_t<POD, kCpu> getCpu() const
    {
        _prefetch<kCpu>();
        return getAt<POD, kCpu>();
    }
    template <typename POD, typename std::enable_if_t<attribute_type_traits<POD>::isSimpleType, int> = 0>
    simpleData_t<POD, kCpu> getCpu()
    {
        _prefetch<kCpu>();
        return getAt<POD, kCpu>();
    }
    template <typename POD, typename std::enable_if_t<attribute_type_traits<POD>::isTupleType, int> = 0>
    const tupleData_t<POD, kCpu> getCpu() const
    {
        _prefetch<kCpu>();
        return getAt<POD, kCpu>();
    }
    template <typename POD, typename std::enable_if_t<attribute_type_traits<POD>::isTupleType, int> = 0>
    tupleData_t<POD, kCpu> getCpu()
    {
        _prefetch<kCpu>();
        return getAt<POD, kCpu>();
    }
    template <typename POD, typename std::enable_if_t<attribute_type_traits<POD>::isArrayType, int> = 0>
    const arrayData_t<POD, kCpu> getCpu() const
    {
        return getAt<POD, kCpu>();
    }
    template <typename POD, typename std::enable_if_t<attribute_type_traits<POD>::isArrayType, int> = 0>
    arrayData_t<POD, kCpu> getCpu()
    {
        return getAt<POD, kCpu>();
    }
    template <typename POD, typename std::enable_if_t<attribute_type_traits<POD>::isTupleArrayType, int> = 0>
    const tupleArrayData_t<POD, kCpu> getCpu() const
    {
        return getAt<POD, kCpu>();
    }
    template <typename POD, typename std::enable_if_t<attribute_type_traits<POD>::isTupleArrayType, int> = 0>
    tupleArrayData_t<POD, kCpu> getCpu()
    {
        return getAt<POD, kCpu>();
    }
    // --------------------------------------------------------------------------------------------------------------
    template <typename POD, typename std::enable_if_t<attribute_type_traits<POD>::isSimpleType, int> = 0>
    const simpleData_t<POD, kCuda, GpuPtrType> getGpu() const
    {
        _prefetch<kCuda>();
        return getAt<POD, kCuda, GpuPtrType>();
    }
    template <typename POD, typename std::enable_if_t<attribute_type_traits<POD>::isSimpleType, int> = 0>
    simpleData_t<POD, kCuda, GpuPtrType> getGpu()
    {
        _prefetch<kCuda>();
        return getAt<POD, kCuda, GpuPtrType>();
    }
    template <typename POD, typename std::enable_if_t<attribute_type_traits<POD>::isTupleType, int> = 0>
    const tupleData_t<POD, kCuda, GpuPtrType> getGpu() const
    {
        _prefetch<kCuda>();
        return getAt<POD, kCuda, GpuPtrType>();
    }
    template <typename POD, typename std::enable_if_t<attribute_type_traits<POD>::isTupleType, int> = 0>
    tupleData_t<POD, kCuda, GpuPtrType> getGpu()
    {
        _prefetch<kCuda>();
        return getAt<POD, kCuda, GpuPtrType>();
    }
    template <typename POD, typename std::enable_if_t<attribute_type_traits<POD>::isArrayType, int> = 0>
    const arrayData_t<POD, kCuda, GpuPtrType> getGpu() const
    {
        return getAt<POD, kCuda, GpuPtrType>();
    }
    template <typename POD, typename std::enable_if_t<attribute_type_traits<POD>::isArrayType, int> = 0>
    arrayData_t<POD, kCuda, GpuPtrType> getGpu()
    {
        return getAt<POD, kCuda, GpuPtrType>();
    }
    template <typename POD, typename std::enable_if_t<attribute_type_traits<POD>::isTupleArrayType, int> = 0>
    const tupleArrayData_t<POD, kCuda, GpuPtrType> getGpu() const
    {
        return getAt<POD, kCuda, GpuPtrType>();
    }
    template <typename POD, typename std::enable_if_t<attribute_type_traits<POD>::isTupleArrayType, int> = 0>
    tupleArrayData_t<POD, kCuda, GpuPtrType> getGpu()
    {
        return getAt<POD, kCuda, GpuPtrType>();
    }
    // --------------------------------------------------------------------------------------------------------------
    // Raw data access method, which returns size and pointer but ignores type information. Its usage should be rare,
    // but it is useful to have it available for those times.
    template <eMemoryType RawMemoryType = MemoryType, PtrToPtrKind RawGpuPtrType = PtrToPtrKind::eNotApplicable>
    void rawData(ConstRawPtr& ptr, size_t& size) const
    {
        static_assert(RawMemoryType != kAny, "Cannot access raw data on an attribute with runtime memory location");
        using data_traits = data_type_traits<uint8_t, readOnly, RawMemoryType, RawGpuPtrType>;
        data_traits::dataReference(m_context, m_handle, ptr, size);
    }
    template <eMemoryType RawMemoryType = MemoryType, PtrToPtrKind RawGpuPtrType = PtrToPtrKind::eNotApplicable>
    void rawData(RawPtr& ptr, size_t& size)
    {
        static_assert(RawMemoryType != kAny, "Cannot access raw data on an attribute with runtime memory location");
        static_assert(! readOnly, "Cannot access writable raw data on a read-only attribute");
        using data_traits = data_type_traits<uint8_t, readOnly, RawMemoryType, RawGpuPtrType>;
        data_traits::dataReference(m_context, m_handle, ptr, size);
    }
};


/* Runtime Attribute type traits */
template<class T>
struct is_runtime_data : std::false_type {};
template<class T, bool ReadOnly, eMemoryType MemoryType>
struct is_runtime_data<ArrayData<T, ReadOnly, MemoryType, PtrToPtrKind::eNotApplicable>> : std::true_type {};
template<class T, eMemoryType MemoryType>
struct is_runtime_data<SimpleDataReadOnly<T, MemoryType, PtrToPtrKind::eNotApplicable>> : std::true_type {};
template<class T, eMemoryType MemoryType>
struct is_runtime_data<SimpleDataWritable<T, MemoryType, PtrToPtrKind::eNotApplicable>> : std::true_type {};
template<class T, eMemoryType MemoryType>
struct is_runtime_data<TupleDataReadOnly<T, MemoryType, PtrToPtrKind::eNotApplicable>> : std::true_type {};
template<class T, eMemoryType MemoryType>
struct is_runtime_data<TupleDataWritable<T, MemoryType, PtrToPtrKind::eNotApplicable>> : std::true_type {};
template<class T, eMemoryType MemoryType>
struct is_runtime_data<ArrayDataReadOnly<T, MemoryType, PtrToPtrKind::eNotApplicable>> : std::true_type {};
template<class T, eMemoryType MemoryType>
struct is_runtime_data<ArrayDataWritable<T, MemoryType, PtrToPtrKind::eNotApplicable>> : std::true_type {};
template<class T, eMemoryType MemoryType>
struct is_runtime_data<TupleArrayDataReadOnly<T, MemoryType, PtrToPtrKind::eNotApplicable>> : std::true_type {};
template<class T, eMemoryType MemoryType>
struct is_runtime_data<TupleArrayDataWritable<T, MemoryType, PtrToPtrKind::eNotApplicable>> : std::true_type {};

} // namespace ogn
} // namespace core
} // namespace graph
} // namespace omni
