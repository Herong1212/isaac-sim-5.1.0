// Copyright (c) 2021-2021 NVIDIA CORPORATION.  All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

// std
#include <type_traits>

// libraries
#include <carb/cpp/Bit.h>

namespace omni
{
namespace fabric
{

enum class DeviceType
{
    eCpu,
    eCuda,
    eCount
};

enum class FabricOptions : uint32_t
{
    eDefault = 0,
    eEnableCuda = 1,
};

// Operators for combining FabricOptions
constexpr enum FabricOptions operator|(const enum FabricOptions a, const enum FabricOptions b)
{
    return (enum FabricOptions)(uint32_t(a) | uint32_t(b));
}
constexpr enum FabricOptions operator&(const enum FabricOptions a, const enum FabricOptions b)
{
    return (enum FabricOptions)(uint32_t(a) & uint32_t(b));
}

/**
 * @enum PtrToPtrKind
 *
 * @details When getting an array-valued attribute for GPU access, you can
 *          optionally use this enum to ask for a GPU pointer to the GPU data
 *          pointer (eGpuPtrToGpuPtr), or a CPU pointer to the GPU data
 *          pointer (eCpuPtrToGpuPtr).
 *          The advantage of using eCpuPtrToGpuPtr is that you can dereference
 *          the returned pointer on the CPU, and pass the GPU data pointer as
 *          a CUDA kernel parameter.
 *          The advantage of using eGpuPtrToGpuPtr is that it makes it easier
 *          to extend kernels to operate on arrays of arrays later. Also it
 *          allows us to support allocation and resizing of array-valued
 *          attributes on the GPU in the future.
 *
 *          PtrToPtrKind is not a parameter of methods returning arrays of
 *          arrays, for example getArrayGPU(). This is because there is no way
 *          to pass a variable length array of GPU pointers to a kernel using
 *          its CPU launch parameters. So GPU arrays of arrays always have to
 *          be passed to kernels as a GPU pointer to an array of GPU pointers.
 */
enum class PtrToPtrKind : uint8_t
{
    eNotApplicable = 0,
    eGpuPtrToGpuPtr = 0, // eGpuPtrToGpuPtr == eNotApplicable for backward compatibility
    eCpuPtrToGpuPtr,

    eCount
};
static_assert(uint8_t(PtrToPtrKind::eCount) == 2,
              "Invalid number of enum values. This enum is treated as a boolean.");

// TODO: This has been repackaged to behave (mostly) like an enum from the outside.
// If we're happy packaging together the device type and the device id then usage of
// ValidMirrors could be refactored to simplify this struct
struct ValidMirrors
{
    enum ValidMirrorDeviceType
    {
        eNone = 0,
        eCPU = 1,
        eCudaGPU = 2,
        eGfxGPU /* c++17 [[deprecated]] */ = 4 // D3dVk removed in 105.1
    };
    ValidMirrors() {}
    ValidMirrors(ValidMirrorDeviceType validMirrorDeviceType) : validMirror(validMirrorDeviceType) {}
    ValidMirrors operator=(ValidMirrorDeviceType _validMirror) { return ValidMirrors(_validMirror); }
    bool operator==(ValidMirrors::ValidMirrorDeviceType rhs) { return validMirror == rhs; }
    bool operator!=(ValidMirrors::ValidMirrorDeviceType rhs) { return validMirror != rhs; }
    bool operator&(const ValidMirrors::ValidMirrorDeviceType& rhs) { return validMirror & rhs; }
    ValidMirrors operator|=(const ValidMirrors::ValidMirrorDeviceType& rhs)
    {
        validMirror = (ValidMirrorDeviceType)(validMirror | rhs);
        return *this;
    }
    ValidMirrors operator|(const ValidMirrors::ValidMirrorDeviceType& rhs)
    {
        ValidMirrors retval;
        retval.validMirror = (ValidMirrorDeviceType)(validMirror | rhs);
        retval.validDevices = validDevices;
        return retval;
    }
    int GetFirstValidDeviceId()
    {
        return carb::cpp::countr_zero(validDevices);
    }
    ValidMirrorDeviceType validMirror = ValidMirrorDeviceType::eNone;
    uint64_t validDevices = 0;
};

constexpr enum ValidMirrors::ValidMirrorDeviceType operator|(const ValidMirrors &a, const ValidMirrors &b)
{
    return (enum ValidMirrors::ValidMirrorDeviceType)(uint32_t(a.validMirror) | uint32_t(b.validMirror));
}
constexpr enum ValidMirrors::ValidMirrorDeviceType operator&(const ValidMirrors &a, const ValidMirrors &b)
{
    return (enum ValidMirrors::ValidMirrorDeviceType)(uint32_t(a.validMirror) & uint32_t(b.validMirror));
}

static_assert(std::is_standard_layout<ValidMirrors>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

enum class GpuComputeType
{
    eAuto = -1,
    eNone = 0,
    eCuda = 1,
};

enum struct SerializationOption
{
    eConnectivity_None = 0,
    eConnectivity_Full = 1,
    eConnectivity_Default = eConnectivity_Full,

    eEncoding_Local = 2, // example: paths and tokens are encoded as raw pathc and tokenc values
    eEncoding_Global = 3, // example: paths and tokens are encoded as strings
    eEncoding_Default = eEncoding_Global,

    eThreading_Enabled = 4, // Enable multithreading in a process of serialization and deserialization
    eThreading_Disabled = 5, // Disable multithreading in a process of serialization and deserialization
    eThreading_Default = eThreading_Enabled,

    eCount = 6 // reserved
};

enum WriteType
{
    eModify,   //!< Read/Write access
    eOverwrite //!< Initial value won't be read, but may be overwritten and
               //!< then may be read. Knowing that data is about to be
               //!< overwritten allows Fabric to perform optimizations. For
               //!< example, if data is valid on CPU then requested on GPU
               //!< with eOverwrite, Fabric doesn't have to copy the data
               //!< from CPU to GPU because it knows the GPU is about to
               //!< overwrite it.
};

enum CreatePrimOptions : int
{
    eOnlyNewPrims = 0,
    eProcessExistingPrims = 1 << 0,
    ePreserveExistingAttributes = 1 << 1,
};

} // namespace fabric
} // namespace omni
