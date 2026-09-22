// SPDX-FileCopyrightText: Copyright (c) 2019-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#pragma once

#include <carb/Types.h>

// Enum for possible XR errors

namespace omni
{
namespace kit
{
namespace xr
{


enum OMNI_ATTR("translate_to_exception=XR_THROW_IF_ERROR") class XRError : int32_t
{
    eSuccess = 0, // No error

    // === General errors ===
    eNotImplemented = 101, // A feature not yet ready
    eInternalError = 102, // Internal error
    eMemoryError = 103, // Memory error
    eTimeout = 104, // Timeout
    eCustomError = 105, // User defined error
    eSkipFrame = 106, // Skip this frame
    eInternalVulkanError = 107, // Internal Vulkan error
    eInternalUsdError = 109, // Internal Usd error
    eFailedToCreateTempDir = 110, // Failed to create temp directory
    eFailedToOpenWinRegistry = 111, // Failed to open windows registry key

    // === ABI errors ===
    eCastError = 201, // Cannot cast to a given type
    eWeakRefNullError = 202, // A null weak ref was attempted to be dereferenced

    // === Initialization errors ===
    eFailedToInitializeXRCore = 301, // XRCore failed to initialize
    eFailedToInitializeShader = 302, // Failed to initialize shader
    eFailedToInitializeSystem = 303, // Failed to initialize a system
    eFailedToInitializeSession = 304, // Failed to initialize a session

    eGpuFoundationNotInitialized = 305, // Gpu foundation is not initialized

    eFailedToFindGpuFoundation = 306, // Failed to find the gpu foundation
    eFailedToFindResourceManager = 307, // Failed to find the resource manager
    eFailedToFindRenderGraphBuilder = 308, // Failed to find the render graph builder
    eFailedToFindShaderDb = 309, // Failed to find the shader db
    eFailedToFindGpuFoundationDevices = 310, // Failed to find gpu foundation devices
    eFailedToFindGpuFoundationPlugins = 311, // Failed to get the foundation plugins
    eFailedToInitializeOpenXRSystem = 312, // Failed to initialize OpenXR related system
    eFailedToInitializeOpenVRSystem = 313, // Failed to initialize OpenVR related system
    eGraphicsIsNotVulkanNorDX12 = 314, // Graphics is not vulkan nor DX12

    // === XRSystem errors ===
    eExtensionFailedToInitialize = 401, // Failed to initialize the xr system extension
    eExtensionFailedToShutdown = 402, // Failed to shutdown xr system extension
    eFailedToActivateXRSystem = 403, // Failed to activate XR system
    eMultipleSessionsNotAllowed = 404, // System does not support multiple sessions
    eSystemCannotActivateAgain = 405, // A system is already activated and cannot handle multiple activations

    // === Testing errors ===
    eTestNotFound = 501, // Test not found
    eTestFailed = 502, // Test Failed

    // === Something is not valid ===
    eInvalidParameter = 601, // One of the given parameters is not valid
    eInvalidUsdPath = 602, // Usd path is not valid
    eInvalidManagedObject = 603, // Object is not managed by UsdLayer
    eInvalidManagedObjectType = 604, // Operation is not supported for this type of managed object
    eInvalidStage = 605, // Stage is invalid
    eInvalidUsdPrim = 606, // Usd prim is not valid
    eInvalidProfile = 607, // Profile given is not valid (try to initialize profile first)
    eInvalidDevice = 608, // Invalid device
    eInvalidBuffer = 609, // Invalid buffer
    eInvalidSystemName = 610, // System name is not valid
    eInvalidMatrix = 611, // Invalid matrix
    eUnsafeMatrix = 612, // Unsafe matrix
    eProfileDoesNotExist = 613, // Already existing profile does not exist
    eParameterIsNull = 614, // One of the given parameters is null, which is not expected
    eGivenPathExceeds260Characters = 615, // Given path exceeds 260 characters (limit on Windows)
    eInvalidKey = 616, // Invalid key was given
    eDuplicateKey = 617, // Key that was given is duplicate
    eNoUsdrtPrimFound = 618, // The prim was not found by the USDRT API
    eFabricHierarchyAttrFailed = 619, // Getting or setting a Fabric Hierarchy matrix did not succeed
    eInvalidTexture = 620, // Invalid texture
    eInvalidTime = 621, // Invalid time (OpenXR)


    // === raycast errors ===
    eRaycastSequenceDoesNotExist = 701, // Raycast sequence requested does not exist
    eRaycastQueryManagerDoesNotExist = 702, // Raycast query manager does not exist, raycast queries disabled
    eRaycastSequenceAdditionFailed = 703, // Raycast sequence addition failed

    // === resource errors ===
    ePrimAlreadyExists = 801, // Prim is already present
    eFailedToOpenFile = 802, // File could not be opened
    eFailedToCreateServer = 803, // Failed to create server
    eFailedToCreatePrim = 804, // Could not create Usd prim
    eFileNotFound = 805, // File not found
    eFailedToReadFile = 806, //  Failed to read file
    eFailedToCreateDirectoryOrFile = 807, // Failed to create directory/file
    eFileExceedsBuffer = 808, // Given file exceeds provided buffer
    eCannotParseAssetPath = 809, // Failed to parse a given asset path
    eAssetPackageDoesNotExist = 810, // Asset package does not exist
    eCannotParseAssetConfig = 811, // Failed to parse the asset configuration


    // === Gfx errors ===
    eUnknownAovType = 901, // Aov type is not known
    eUnknownAovFormat = 902, // Aov format is not known
    eUnsupportedGraphicsAPI = 903, // Graphics API is not supported
    eUnsupportedTextureFormat = 904, // Graphics texture format is not supported
    eFailedToAllocateBuffer = 905, // Failed to allocate buffer
    eInvalidTextureOffsetOrSize = 906, // Texture offset was incorrect
    eInvalidGpuFoundation = 907, // Gpu foundation was not initialized
    eFailedToCreateSemaphore = 908, // Failed to create a semaphore
    eFailedToCreateVulkanInstance = 909, // Failed to create new vulkan instance
    eFailedToCreateVulkanDevice = 910, // Failed to create new vulkan device
    eFailedToFindVulkanFunction = 911, // Failed tp locate a function
    eFailedToAllocateTexture = 912, // Failed to allocate texture
    eFailedToShareTexture = 913, // Failed to share texture
    eFailedOnSemaphoreHandlerImport = 914, // Failed to import semaphore handler

    // === component errors ===
    eReadOnlyObject = 1001, // Read-only Object
    eNotReadOnlyObject = 1002, // Not read-only Object
    eDuplicateComponentName = 1003, // Component name was duplicated
    eInvalidComponentName = 1004, // Component name is invalid
    eDuplicateInputName = 1005, // Input name was duplicated
    eInvalidInputName = 1006, // Input name is invalid

    // === input system ===
    eDuplicateGesture = 1101, // Gesture is defined twice
    eInvalidGesture = 1102, // Defined gesture is not valid
    eInvalidInteractionProfile = 1103, // Invalid input profile
    eInvalidActionMap = 1104, // Actionmap is not present
    eInvalidEventName = 1105, // Invalid event name
    eInvalidEventType = 1106, // Invalid event name

};

typedef OMNI_ATTR("translate_to_exception=XR_THROW_IF_ERROR") XRError XRResult;

} // namespace xr
} // namespace kit
} // namespace omni
