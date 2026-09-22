// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once
#include <omni/core/Omni.h>
#include "IInspector.h"
namespace omni { using namespace omni::core; }

namespace omni {
namespace inspect {

OMNI_DECLARE_INTERFACE(IInspectJsonSerializer);

//! Base class for object inspection requests.
class IInspectJsonSerializer_abi
    : public omni::Inherits<omni::inspect::IInspector, OMNI_TYPE_ID("omni.inspect.IInspectJsonSerializer")>
{
protected:
    /** Set the output location of the serializer data to be a specified file path.
     * Doesn't actually do anything with it until data is being written though.
     *
     * @param[in] filePath Absolute location of the file to be written.
     */
    virtual void setOutputToFilePath_abi(OMNI_ATTR("c_str, not_null") const char* filePath) noexcept = 0;

    /** Set the output location of the serializer data to be a local string.
     * No check is made to ensure that the string size doesn't get too large so when in doubt use a file path.
     */
    virtual void setOutputToString_abi() noexcept = 0;

    /** Get the current location of the output data.
     *
     * @returns Path to the output file, or nullptr if output is going to a string
     */
    virtual const char* getOutputLocation_abi() noexcept = 0;

    /** Get the current output as a string. If the output is being sent to a file path then read the file at that path
     * and return the contents of the file (with the usual caveats about file size).
     *
     * @returns String representation of the output so far
     */
    virtual const char* asString_abi() noexcept = 0;

    /** Clear the contents of the serializer output, either emptying the file or clearing the string, depending on
     * where the current output is directed.
     */
    virtual void clear_abi() noexcept = 0;

    /** Write out a JSON key for an object property.
     *
     * @param[in] key    The string value for the key. This can be nullptr.
     * @param[in] keyLen The length of @ref key, excluding the null terminator.
     * @returns whether or not validation succeeded.
     */
    virtual bool writeKeyWithLength_abi(OMNI_ATTR("c_str")const char* key, size_t keyLen) noexcept = 0;

    /** Write out a JSON key for an object property.
     *
     * @param[in] key The key name for this property. This may be nullptr.
     * @returns whether or not validation succeeded.
     */
    virtual bool writeKey_abi(OMNI_ATTR("c_str")const char* key) noexcept = 0;

    /** Write out a JSON null value.
     *
     * @returns whether or not validation succeeded.
     */
    virtual bool writeNull_abi() noexcept = 0;

    /** Write out a JSON boolean value.
     *
     * @param[in] value The boolean value.
     * @returns whether or not validation succeeded.
     */
    virtual bool writeBool_abi(bool value) noexcept = 0;

    /** Write out a JSON integer value.
     *
     * @param[in] value The integer value.
     * @returns whether or not validation succeeded.
     */
    virtual bool writeInt_abi(int32_t value) noexcept = 0;

    /** Write out a JSON unsigned integer value.
     *
     * @param[in] value The unsigned integer value.
     * @returns whether or not validation succeeded.
     */
    virtual bool writeUInt_abi(uint32_t value) noexcept = 0;

    /** Write out a JSON 64-bit integer value.
     *
     * @param[in] value The 64-bit integer value.
     * @returns whether or not validation succeeded.
     * @note 64 bit integers will be written as a string of they are too long
     * to be stored as a number that's interoperable with javascript's
     * double precision floating point format.
     */
    virtual bool writeInt64_abi(int64_t value) noexcept = 0;

    /** Write out a JSON 64-bit unsigned integer value.
     *
     * @param[in] value The 64-bit unsigned integer value.
     * @returns whether or not validation succeeded.
     * @note 64 bit integers will be written as a string of they are too long
     * to be stored as a number that's interoperable with javascript's
     * double precision floating point format.
     */
    virtual bool writeUInt64_abi(uint64_t value) noexcept = 0;

    /** Write out a JSON pointer value as an unsigned int 64.
     * Not available through the Python bindings as Python has no concept of pointers. Use either writeUInt64()
     * or writeBase64Encoded() to write out binary data.
     *
     * @param[in] value The pointer value.
     * @returns whether or not validation succeeded.
     * @note Pointers will be written as a string of they are too long
     * to be stored as a number that's interoperable with javascript's
     * double precision floating point format.
     */
    virtual OMNI_ATTR("no_py") bool writePointer_abi(OMNI_ATTR("in")const void* value) noexcept = 0;

    /** Write out a JSON double (aka number) value.
     *
     * @param[in] value The double value.
     * @returns whether or not validation succeeded.
     */
    virtual bool writeDouble_abi(double value) noexcept = 0;

    /** Write out a JSON float (aka number) value.
     *
     * @param[in] value The double value.
     * @returns whether or not validation succeeded.
     */
    virtual bool writeFloat_abi(float value) noexcept = 0;

    /** Write out a JSON string value.
     *
     * @param[in] value The string value. This can be nullptr if @p len is 0.
     * @param[in] len   The length of @p value, excluding the null terminator.
     * @returns whether or not validation succeeded.
     */
    virtual bool writeStringWithLength_abi(OMNI_ATTR("c_str")const char* value, size_t len) noexcept = 0;

    /** Write out a JSON string value.
     *
     * @param[in] value The string value. This can be nullptr.
     * @returns whether or not validation succeeded.
     */
    virtual bool writeString_abi(OMNI_ATTR("c_str")const char* value) noexcept = 0;

    /** Write a binary blob into the output JSON as a base64 encoded string.
     *
     * @param[in] value The binary blob to write in.
     * @param[in] size   The number of bytes of data in @p value.
     * @returns whether or not validation succeeded.
     * @remarks This will take the input bytes and encode it in base64, then store that as base64 data in a string.
     */
    virtual OMNI_ATTR("no_py") bool writeBase64Encoded_abi(OMNI_ATTR("in")const void* value, size_t size) noexcept = 0;

    /** Begin a JSON array.
     *
     * @returns whether or not validation succeeded.
     * @note This may throw a std::bad_alloc or a std::length_error if the stack of scopes gets too large
     */
    virtual bool openArray_abi() noexcept = 0;

    /** Finish writing a JSON array.
     *
     * @returns whether or not validation succeeded.
     */
    virtual bool closeArray_abi() noexcept = 0;

    /** Begin a JSON object.
     *
     * @returns whether or not validation succeeded.
     */
    virtual bool openObject_abi() noexcept = 0;

    /** Finish writing a JSON object.
     *
     * @returns whether or not validation succeeded.
     */
    virtual bool closeObject_abi() noexcept = 0;

    /** Finishes writing the entire JSON dictionary.
     *
     * @returns whether or not validation succeeded.
     */
    virtual bool finish_abi() noexcept = 0;
};

} // namespace inspect
} // namespace omni

#include "IInspectJsonSerializer.gen.h"
