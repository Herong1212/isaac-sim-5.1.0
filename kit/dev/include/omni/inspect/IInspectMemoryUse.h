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

OMNI_DECLARE_INTERFACE(IInspectMemoryUse);

//! Base class for object inspection requests.
class IInspectMemoryUse_abi
    : public omni::Inherits<omni::inspect::IInspector, OMNI_TYPE_ID("omni.inspect.IInspectMemoryUse")>
{
protected:
    /** Add a block of used memory
     * Returns false if the memory was not recorded (e.g. because it was already recorded)
     *
     * @param[in] ptr Pointer to the memory location being logged as in-use
     * @param[in] bytesUsed Number of bytes in use at that location
     */
    virtual bool useMemory_abi(OMNI_ATTR("in, not_null") const void* ptr, size_t bytesUsed) noexcept = 0;

    /** Reset the memory usage data to a zero state
     */
    virtual void reset_abi() noexcept = 0;

    /** @returns the total number of bytes of memory used since creation or the last call to reset().
     */
    virtual size_t totalUsed_abi() noexcept = 0;
};

} // namespace inspect
} // namespace oni

#include "IInspectMemoryUse.gen.h"
