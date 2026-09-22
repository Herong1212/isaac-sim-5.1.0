// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.

#pragma once

#include <atomic>
#include <thread>

namespace omni
{
    namespace utils
    {
        enum class OperationResult : uint32_t
        {
            SUCCESS = 0, // Operation completed successfully - out parameters are written to
            FAILURE = 1, // Operation failed
            OVERFLOW_ERROR = 2, // Overflow based on parameters occurred 
            INVALIDHANDLE_ERROR = 3, // The handle passed to the operation wasn't valid (anymore)
            NOPROCESSOR_ERROR = 4, // No processor was found for this request
            NOTFOUND_ERROR = 5, // The handle wasn't found
            NOTBUILT_ERROR = 6, // The build-request wasn't build yet
            INVALIDMETADATA_ERROR = 7, // The build result wasn't the expected metadata
            OUTOFMEMORY_ERROR = 8, // Out of memory occurred
            TIMEOUT_ERROR = 9, // Timeout occurred
            DATAVALIDATION_ERROR = 10, // Validation of data failed: required external data wasn't found
            NOT_SUPPORTED = 11, // Operation or feature set not supported
            CIRCULAR_DEPENDENCY = 12, // Operation failed due to a circular dependency
            ALREADY_IN_PROCESS = 13, // Operation is already in process
            TRANSIENT_FAILURE = 14, // A transient failure happened during the operation (the operation will likely succeed if retried)
            CANCELLED = 15, // The opearation was cancelled before succeeding
            INTERNAL = 0xffff, // Internal reserved value
        };

        inline const char *getOperationResultStr(OperationResult operationResult)
        {
            static const char* str[] = {
                "SUCCESS",
                "FAILURE",
                "OVERFLOW_ERROR",
                "INVALIDHANDLE_ERROR",
                "NOPROCESSOR_ERROR",
                "NOTFOUND_ERROR",
                "NOTBUILT_ERROR",
                "INVALIDMETADATA_ERROR",
                "OUTOFMEMORY_ERROR",
                "TIMEOUT_ERROR",
                "DATAVALIDATION_ERROR",
                "NOT_SUPPORTED",
                "CIRCULAR_DEPENDENCY",
                "ALREADY_IN_PROCESS",
                "TRANSIENT_FAILURE",
                "CANCELLED"
            };
            uint32_t index = uint32_t(operationResult);
            return (index <= uint32_t(OperationResult::TRANSIENT_FAILURE)) ? str[index] : "INTERNAL";
        }
    }
} // namespace omni
