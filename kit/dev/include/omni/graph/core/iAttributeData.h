// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/graph/core/Handle.h>
#include <omni/graph/core/Type.h>

namespace omni
{
namespace graph
{
namespace core
{

using RawPtr = uint8_t*; //!< Type for casting byte arrays to actual values
using ConstRawPtr = uint8_t const*; //!< Type for casting const byte arrays to actual values

// ======================================================================
/** Interface to data belonging to a specific attribute */
struct IAttributeData
{
    //! @private to avoid doxygen problems
    CARB_PLUGIN_INTERFACE("omni::graph::core::IAttributeData", 1, 6);

    /**
     * Gets the name of the attribute containing this attribute data.
     *
     * The attribute data handle may refer to attribute data from an attribute that is upstream
     * of the attribute from which the handle was retrieved, in which case, this will
     * return the upstream attribute's name.
     *
     * @param[in] contextObj The GraphContextObj containing the attribute data
     * @param[in] handle The handle to the attribute whose name is being requested
     * @return A NameToken representing the attribute's name, for which the text can be retrieved
     *         using IToken::getText
     */
    NameToken (CARB_ABI* getName)(const GraphContextObj& contextObj, ConstAttributeDataHandle handle);

    /**
     * Gets the name of the type of this attribute data.  Use getType to get a representation of
     * the type that is easier to interpret in code.
     *
     * The actual attribute data may have a different type than an associated attribute on a node,
     * for example, if the upstream source of the data has a different type.
     * This function returns the type of the data, not the type of the associated attribute.
     *
     * @param[in] contextObj The GraphContextObj containing the attribute data
     * @param[in] handle The handle to the attribute data whose type name is being requested
     * @return A NameToken representing the attribute data's type name, for which the text can be retrieved
     *         using IToken::getText
     */
    NameToken (CARB_ABI* getTypeName)(const GraphContextObj& contextObj, ConstAttributeDataHandle handle);

    /**
     * Gets the type of this attribute data in a representation that is easily interpreted by code.
     *
     * The actual attribute data may have a different type than an associated attribute on a node,
     * for example, if the upstream source of the data has a different type.
     * This function returns the type of the data, not the type of the associated attribute.
     *
     * @param[in] contextObj The GraphContextObj containing the attribute data
     * @param[in] handle The handle to the attribute data whose type is being requested
     * @return A Type structure representing the attribute data's type, whose members provide
     *         information about the type
     */
    Type (CARB_ABI* getType)(const GraphContextObj& contextObj, ConstAttributeDataHandle handle);

    /**
     * Checks whether the type of this attribute data is an array type, i.e. array depth of 1
     * (array) or 2 (array of arrays; not yet supported).
     *
     * @param[in] contextObj The GraphContextObj containing the attribute data
     * @param[in] handle The handle to the attribute data to check
     * @return true if the attribute data is an array type, else false
     */
    bool isArray(const GraphContextObj& contextObj, ConstAttributeDataHandle handle)
    {
        return (*getType)(contextObj, handle).arrayDepth != 0;
    }

    /**
     deprecated function, do not use
     */
    void(CARB_ABI* deprecated_0)(const void**, const GraphContextObj&, const ConstAttributeDataHandle*, size_t);

    /**
     * Gets GPU pointers to the read-only GPU data of some number of attributes.
     *
     * Any invalid attributes will have null pointers.  Array attributes have an extra level of indirection.
     * For example, after requesting int attribute data, attrsOut will effectively be of type
     * const int** upon returning, but after requesting int array attribute data, attrsOut will effectively be
     * of type const int* const**.
     *
     * If the attribute data is not on the GPU at the time of this call, but is on the CPU,
     * it will be copied to the GPU before returning.
     *
     * Deprecated: Use getDataRGpuAt
     *
     * @param[out] attrsOut Array to be filled in with pointers to data of each attribute
     * @param[in] contextObj The GraphContextObj containing the attribute data
     * @param[in] attrHandles Array of attribute data handles whose data are being requested
     * @param[in] attrCount Number of attributes whose data are being requested
     */
    void (CARB_ABI* getDataRGPU)(const void** attrsOut,
                        const GraphContextObj& contextObj,
                        const ConstAttributeDataHandle* attrHandles,
                        size_t attrCount);

    /**
     * Gets CPU pointers to the writable CPU data of some number of attributes.
     *
     * Any invalid attributes will have null pointers.  Array attributes have an extra level of indirection.
     * For example, after requesting int attribute data, attrsOut will effectively be of type
     * int** upon returning, but after requesting int array attribute data, attrsOut will effectively be
     * of type int*const**.
     *
     * If the attribute data is not on the CPU at the time of this call, but is on the GPU,
     * it will be copied to the CPU and invalidated on the GPU before returning.
     *
     * @param[out] attrsOut Array to be filled in with pointers to data of each attribute
     * @param[in] contextObj The GraphContextObj containing the attribute data
     * @param[in] attrHandles Array of attribute data handles whose data are being requested
     * @param[in] attrCount Number of attributes whose data are being requested
     */
    void (CARB_ABI* getDataW)(void** attrsOut,
                     const GraphContextObj& contextObj,
                     const AttributeDataHandle* attrHandles,
                     size_t attrCount);

    /**
     * Gets GPU pointers to the writable GPU data of some number of attributes.
     *
     * Any invalid attributes will have null pointers.  Array attributes have an extra level of indirection.
     * For example, after requesting int attribute data, attrsOut will effectively be of type
     * int** upon returning, but after requesting int array attribute data, attrsOut will effectively be
     * of type int*const**.
     *
     * If the attribute data is not on the GPU at the time of this call, but is on the CPU,
     * it will be copied to the GPU and invalidated on the CPU before returning.
     *
     * Deprecated: Use getDataWGpuAt
     *
     * @param[out] attrsOut Array to be filled in with pointers to data of each attribute
     * @param[in] contextObj The GraphContextObj containing the attribute data
     * @param[in] attrHandles Array of attribute data handles whose data are being requested
     * @param[in] attrCount Number of attributes whose data are being requested
     */
    void (CARB_ABI* getDataWGPU)(void** attrsOut,
                        const GraphContextObj& contextObj,
                        const AttributeDataHandle* attrHandles,
                        size_t attrCount);

    /**
     Deprecated function, do not use
     */
    void (CARB_ABI* deprecated_1)(const GraphContextObj&, const AttributeDataHandle*, size_t);

    /**
     * Gets the number of array elements in each of the specified attributes.
     *
     * Any invalid attributes will considered to have 0 elements.  Attributes that are not
     * arrays will be considered to have 1 element.  Array of array attributes are not
     * yet supported.
     *
     * @param[out] countOut Array to be filled in with number of elements in each attribute
     * @param[in] contextObj The GraphContextObj containing the attribute data
     * @param[in] attrHandles Array of attribute data handles whose element counts are being requested
     * @param[in] attrCount Number of attributes whose element counts are being requested
     */
    void (CARB_ABI* getElementCount)(size_t* countOut,
                            const GraphContextObj& contextObj,
                            const ConstAttributeDataHandle* attrHandles,
                            size_t attrCount);

    /**
     * Sets the number of array elements in the specified array attribute.
     *
     * The array attribute's data will not be resized until a pointer to its data is requested.
     *
     * @param[in] contextObj The GraphContextObj containing the attribute data
     * @param[in] handle Attribute data handle referring to an array attribute
     * @param[in] count Element count to which the array attribute data should be resized.
     */
    void (CARB_ABI* setElementCount)(const GraphContextObj& contextObj, AttributeDataHandle handle, size_t count);

    /**
     * Copies the data from an existing attribute data value into this one.
     * As only data is being copied a name for the destination is not required and will remain unchanged.
     *
     * @param[in] destination Data location to be overwritten
     * @param[in] contextObj Location of both sets of attribute data
     * @param[in] source Data being copied
     */
    void (CARB_ABI* copyData)(AttributeDataHandle destination,
                     const GraphContextObj& contextObj,
                     ConstAttributeDataHandle source);

    /**
     * Get the location and total number of bytes occupied by the readable attribute data on the CPU.
     *
     * If the data is not currently valid on the CPU the pointer returned will be nullptr.
     *
     * @param[in] contextObj Location of both sets of attribute data
     * @param[in] attrHandle Handle to the attribute whose size is to be returned
     * @param[out] refToData Resulting pointer to the attribute data
     * @param[out] refToSize Size of the data being pointed at
     */
    void (CARB_ABI* getDataReferenceR)(const ConstAttributeDataHandle attrHandle,
                              const GraphContextObj& contextObj,
                              ConstRawPtr& refToData,
                              size_t& refToSize);

    /**
     * Get the location and total number of bytes occupied by the readable attribute data on the GPU.
     *
     * If the data is not currently valid on the GPU the pointer returned will be nullptr.
     * If it is then it will point to GPU memory, and should not be dereferenced on the CPU side.
     *
     * Deprecated: Use getDataReferenceRGpuAt
     *
     * @param[in] contextObj Location of both sets of attribute data
     * @param[in] attrHandle Handle to the attribute whose size is to be returned
     * @param[out] refToData Resulting pointer to the attribute data
     * @param[out] refToSize Size of the data being pointed at
     */
    void (CARB_ABI* getDataReferenceRGpu)(const ConstAttributeDataHandle attrHandle,
                                 const GraphContextObj& contextObj,
                                 ConstRawPtr& refToData,
                                 size_t& refToSize);

    /**
     * Get the location and total number of bytes occupied by the writable attribute data on the CPU.
     *
     * If the data is not currently valid on the CPU the pointer returned will be nullptr.
     *
     * @param[in] contextObj Location of both sets of attribute data
     * @param[in] attrHandle Handle to the attribute whose size is to be returned
     * @param[out] refToData Resulting pointer to the attribute data
     * @param[out] refToSize Size of the data being pointed at
     */
    void (CARB_ABI* getDataReferenceW)(const AttributeDataHandle attrHandle,
                              const GraphContextObj& contextObj,
                              RawPtr& refToData,
                              size_t& refToSize);

    /**
     * Get the location and total number of bytes occupied by the writable attribute data on the GPU.
     *
     * If the data is not currently valid on the GPU the pointer returned will be nullptr.
     * If it is then it will point to GPU memory, and should not be dereferenced on the CPU side.
     *
     * Deprecated: Use getDataReferenceWGpuAt
     *
     * @param[in] contextObj Location of both sets of attribute data
     * @param[in] attrHandle Handle to the attribute whose size is to be returned
     * @param[out] refToData Resulting pointer to the attribute data
     * @param[out] refToSize Size of the data being pointed at
     */
    void (CARB_ABI* getDataReferenceWGpu)(const AttributeDataHandle attrHandle,
                                 const GraphContextObj& contextObj,
                                 RawPtr& refToData,
                                 size_t& refToSize);

    /**
     * Check if the cpu data of the given attribute is currently valid
     *
     * @param[in] contextObj Location of both sets of attribute data
     * @param[in] attrHandle Handle to the attribute
     */
    bool (CARB_ABI* cpuValid)(const ConstAttributeDataHandle attrHandle, const GraphContextObj& contextObj);

    /**
     * Check if the gpu data of the given attribute is currently valid
     *
     * @param[in] contextObj Location of both sets of attribute data
     * @param[in] attrHandle Handle to the attribute
     */
    bool (CARB_ABI* gpuValid)(const ConstAttributeDataHandle attrHandle, const GraphContextObj& contextObj);

    /**
     * Gets GPU pointers to the read-only GPU data of some number of attributes.
     *
     * Any invalid attributes will have null pointers.  Array attributes have an extra level of indirection.
     * For example, after requesting int attribute data, attrsOut will effectively be of type
     * const int** upon returning, but after requesting int array attribute data, attrsOut will effectively be
     * of type const int* const**.
     *
     * If the attribute data is not on the GPU at the time of this call, but is on the CPU,
     * it will be copied to the GPU before returning.
     *
     * @param[out] attrsOut Array to be filled in with pointers to data of each attribute
     * @param[in] contextObj The GraphContextObj containing the attribute data
     * @param[in] attrHandles Array of attribute data handles whose data are being requested
     * @param[in] attrCount Number of attributes whose data are being requested
     * @param[in] whereGpuPtrs For array data, the location of the array pointer - either on the CPU or on the GPU
     */
    void (CARB_ABI* getDataRGpuAt)(const void** attrsOut,
                        const GraphContextObj& contextObj,
                        const ConstAttributeDataHandle* attrHandles,
                        size_t attrCount,
                        omni::fabric::PtrToPtrKind whereGpuPtrs);

    /**
     * Gets GPU pointers to the writable GPU data of some number of attributes.
     *
     * Any invalid attributes will have null pointers.  Array attributes have an extra level of indirection.
     * For example, after requesting int attribute data, attrsOut will effectively be of type
     * int** upon returning, but after requesting int array attribute data, attrsOut will effectively be
     * of type int*const**.
     *
     * If the attribute data is not on the GPU at the time of this call, but is on the CPU,
     * it will be copied to the GPU and invalidated on the CPU before returning.
     *
     * @param[out] attrsOut Array to be filled in with pointers to data of each attribute
     * @param[in] contextObj The GraphContextObj containing the attribute data
     * @param[in] attrHandles Array of attribute data handles whose data are being requested
     * @param[in] attrCount Number of attributes whose data are being requested
     * @param[in] whereGpuPtrs For array data, the location of the array pointer - either on the CPU or on the GPU
     */
    void (CARB_ABI* getDataWGpuAt)(void** attrsOut,
                        const GraphContextObj& contextObj,
                        const AttributeDataHandle* attrHandles,
                        size_t attrCount,
                        omni::fabric::PtrToPtrKind whereGpuPtrs);

    /**
     * Get the location and total number of bytes occupied by the readable attribute data on the GPU.
     *
     * If the data is not currently valid on the GPU the pointer returned will be nullptr.
     * If it is then it will point to GPU memory, and should not be dereferenced on the CPU side.
     *
     * @param[in] attrHandle Handle to the attribute whose size is to be returned
     * @param[in] contextObj Location of both sets of attribute data
     * @param[in] whereGpuPtrs For array data, the location of the array pointer - either on the CPU or on the GPU
     * @param[out] refToData Resulting pointer to the attribute data
     * @param[out] refToSize Size of the data being pointed at
     */
    void (CARB_ABI* getDataReferenceRGpuAt)(const ConstAttributeDataHandle attrHandle,
                                 const GraphContextObj& contextObj,
                                 omni::fabric::PtrToPtrKind whereGpuPtrs,
                                 ConstRawPtr& refToData,
                                 size_t& refToSize);

    /**
     * Get the location and total number of bytes occupied by the writable attribute data on the GPU.
     *
     * If the data is not currently valid on the GPU the pointer returned will be nullptr.
     * If it is then it will point to GPU memory, and should not be dereferenced on the CPU side.
     *
     * @param[in] attrHandle Handle to the attribute whose size is to be returned
     * @param[in] contextObj Location of both sets of attribute data
     * @param[in] whereGpuPtrs For array data, the location of the array pointer - either on the CPU or on the GPU
     * @param[out] refToData Resulting pointer to the attribute data
     * @param[out] refToSize Size of the data being pointed at
     */
    void (CARB_ABI* getDataReferenceWGpuAt)(AttributeDataHandle attrHandle,
                                 const GraphContextObj& contextObj,
                                 omni::fabric::PtrToPtrKind whereGpuPtrs,
                                 RawPtr& refToData,
                                 size_t& refToSize);

    /**
     * Perform a conversion between 2 data types
     *
     * The actual attribute data may have a different type than an associated attribute on a node,
     * for example, if the upstream source of the data has a different type.
     * This function can be used to perform the conversion from the actual attribute data,
     * to the provided buffer of the type of the attribute
     *
     * @param[out] dstDataOut A pointer to the destination buffer to be filled with the result of the conversion
     * @param[in] dstType The type the destination buffer
     * @param[in] srcDataIn A pointer to the actual attribute data
     * @param[in] srcType The type of the attribute data pointer
     * @return True if a conversion exists and succeeded, False otherwise.
     */
    bool(CARB_ABI* performConversion)(void* dstDataOut, Type dstType, void* srcDataIn, Type srcType);

    /**
     * Gets CPU pointers to the read-only CPU data of some number of attributes.
     *
     * Any invalid attributes will have null pointers.  Array attributes have an extra level of indirection.
     * For example, after requesting int attribute data, attrsOut will effectively be of type
     * const int** upon returning, but after requesting int array attribute data, attrsOut will effectively be
     * of type const int* const**.
     *
     * If the attribute data is not on the CPU at the time of this call, but is on the GPU,
     * it will be copied to the CPU before returning.
     *
     * @param[out] attrsOut Array to be filled in with pointers to data of each attribute
     * @param[in] contextObj The GraphContextObj containing the attribute data
     * @param[in] attrHandles Array of attribute data handles whose data are being requested
     * @param[in] attrCount Number of attributes whose data are being requested
     */
    void (CARB_ABI* getDataR)(const void** attrsOut,
        const GraphContextObj& contextObj,
        const ConstAttributeDataHandle* attrHandles,
        size_t attrCount);

     /**
     * In a vectorized context, retrieve the write handle to another instance from a given one
     *
     * @param[in] contextObj Location of attribute data
     * @param[in] attrHandle The source handle to offset
     * @param[in] offset An offset to apply to the provided handle. Can be negative.
     * @return A handle to the instance located at the provided offset relative to the provided handle
     */
    AttributeDataHandle(CARB_ABI* moveToAnotherInstanceW)(const GraphContextObj& contextObj,
                                                          AttributeDataHandle attrHandle,
                                                          int offset);

    /**
     * In a vectorized context, retrieve the read handle to another instance from a given one
     *
     * @param[in] contextObj Location of attribute data
     * @param[in] attrHandle The source handle to offset
     * @param[in] offset An offset to apply to the provided handle. Can be negative.
     * @return A handle to the instance located at the provided offset relative to the provided handle
     */
    ConstAttributeDataHandle(CARB_ABI* moveToAnotherInstanceR)(const GraphContextObj& contextObj,
                                                               ConstAttributeDataHandle attrHandle,
                                                               int offset);
};
// Update this every time a new ABI function is added, to ensure one isn't accidentally added in the middle
STRUCT_INTEGRITY_CHECK(IAttributeData, moveToAnotherInstanceR, 24)

} // namespace core
} // namespace graph
} // namespace omni
