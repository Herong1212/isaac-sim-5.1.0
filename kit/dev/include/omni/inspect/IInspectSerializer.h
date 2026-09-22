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

OMNI_DECLARE_INTERFACE(IInspectSerializer);

//! Base class for object serialization requests.
class IInspectSerializer_abi
    : public omni::Inherits<omni::inspect::IInspector, OMNI_TYPE_ID("omni.inspect.IInspectSerializer")>
{
protected:
    /** Write a fixed string to the serializer output location
     *
     * @param[in] toWrite String to be written to the serializer
     */
    virtual void writeString_abi(OMNI_ATTR("c_str, not_null") const char* toWrite) noexcept = 0;

    /** Write a printf-style formatted string to the serializer output location
     *
     * @param[in] fmt Formatting string in the printf() style
     * @param[in] args Variable list of arguments to the formatting string
     */
    virtual OMNI_ATTR("no_py") void write_abi(OMNI_ATTR("c_str, not_null") const char* fmt, va_list args) noexcept = 0;

    /** Set the output location of the serializer data to be a specified file path.
     * Doesn't actually do anything with it until data is being written though.
     * Recognizes the special file paths "cout", "stdout", "cerr", and "stderr" as the standard output streams.
     *
     * @param[in] filePath New location of the output file
     */
    virtual void setOutputToFilePath_abi(OMNI_ATTR("c_str, not_null") const char* filePath) noexcept = 0;

    /** Set the output location of the serializer data to be a local string.
     * No check is made to ensure that the string size doesn't get too large so when in doubt use a file path.
     */
    virtual void setOutputToString_abi() noexcept = 0;

    /** Get the current location of the output data.
     *
     * @returns Current file path where the output is going. nullptr means the output is going to a string.
     */
    virtual const char* getOutputLocation_abi() noexcept = 0;

    /** Get the current output as a string.
     *
     * @returns The output that has been sent to the serializer. If the output is being sent to a file path then read
     * the file at that path and return the contents of the file. If the output is being sent to stdout or stderr
     * then nothing is returned as that output is unavailable after flushing.
     */
    virtual const char* asString_abi() noexcept = 0;

    /** Clear the contents of the serializer output, either emptying the file or clearing the string, depending on
     * where the current output is directed.
     */
    virtual void clear_abi() noexcept = 0;
};

} // namespace inspect
} // namespace omni

#include "IInspectSerializer.gen.h"
