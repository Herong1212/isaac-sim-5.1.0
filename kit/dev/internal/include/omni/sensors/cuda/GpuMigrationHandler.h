// SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#pragma once

#include <carb/logging/Log.h>

#include <omni/sensors/cuda/CudaHelperDecl.h>

#include <cstdint>
#include <cuda_runtime.h>
#include <tuple>
#include <unordered_map>

namespace omni
{
namespace sensors
{
namespace cuda
{


/**
 * GpuMigrationHandler: Utility to handle migration of device data to different gpus
 * This utility can handle either just pointer to distinct device data or a device side struct with
 * pointers to device data.
 */
class GpuMigrationHandler
{
    /**
     * DeviceData: This struct contains all the necessary data to migrate registered device data
     * This is a private internal data structure.
     */
    struct DeviceData
    {
        /**
         * @brief Default constructor
         */
        DeviceData() = default;

        /**
         * @brief Constructor
         *
         * @param dPtr pointer to device data
         * @param userDPtrAddress address to the pointer
         * @param dataSize size of the device data
         */
        DeviceData(void* dPtr, void** userDPtrAddress, size_t dataSize)
            : devicePtr(dPtr), userDevicePtrAddress(userDPtrAddress), dataSize(dataSize)
        {
        }

        void* devicePtr; /**< pointer to device data */
        void** userDevicePtrAddress; /**< address to the pointer */
        size_t dataSize; /**< size of the device data */
    };

    /**
     * MirroredData: This struct is used for handling a device side struct containing pointer to device data
     * This is a private internal data structure.
     */
    struct MirroredData
    {
        /**
         * @brief Default constructor
         */
        MirroredData() = default;

        /**
         * @brief Constructor
         *
         * @param dPtr pointer to device struct
         * @param userDPtrAddress address to the device pointer
         * @param hostPtr pointer to host struct
         * @param dataSize size of the device data
         */
        MirroredData(void* dPtr, void** userDPtrAddress, void* hostPtr, size_t dataSize)
            : devicePtr(dPtr), userdevicePtrAddress(userDPtrAddress), hostPtr(hostPtr), dataSize(dataSize)
        {
        }

        void* devicePtr; /**< pointer to device struct */
        void** userdevicePtrAddress; /**< address to the device pointer */
        void* hostPtr; /**< pointer to host struct */
        size_t dataSize; /**< size of the device struct */
    };

    /**
     * @brief Internal typedefs for readability
     */
    using InternalDeviceDataStorage = std::unordered_map<int32_t, std::vector<DeviceData>>;
    using InternalMirroredDataStorage = std::unordered_map<int32_t, std::vector<MirroredData>>;


public:
    using MigrationCbFn = std::function<void(void* userData)>;
    /**
     * @brief Destructor, only the allocated memory during the migration is destructed. The original device memory has
     * to be freed by the user.
     */
    ~GpuMigrationHandler()
    {
        // Release all migrated device data
        for (auto& el : m_internalDeviceData)
        {
            if (el.first != m_currentDeviceId)
            {
                for (DeviceData& deviceData : el.second)
                {
                    if (deviceData.devicePtr)
                        CUDA_CALL(cudaFree(deviceData.devicePtr));
                }
            }
        }
        m_internalDeviceData.clear();

        // Release all migrated device data
        for (auto& el : m_internalMirroredData)
        {
            if (el.first != m_currentDeviceId)
            {
                for (MirroredData& mirroredData : el.second)
                {
                    if (mirroredData.devicePtr)
                        CUDA_CALL(cudaFree(mirroredData.devicePtr));
                }
            }
        }
        m_internalMirroredData.clear();
    }

    /**
     * @brief init, initializes the utility with the current deviceId and a callback function which potentially handles
     * the host side struct data
     *
     * @param dPtr pointer to device struct
     * @param userDPtrAddress address to the device pointer
     * @param hostPtr pointer to host struct
     * @param dataSize size of the device data
     */
    void init(const int deviceId, const MigrationCbFn& cb = nullptr)
    {
        m_migrationCbFn = cb;
        m_currentDeviceId = deviceId;
        m_internalDeviceData.emplace(deviceId, std::vector<DeviceData>());
        m_internalMirroredData.emplace(deviceId, std::vector<MirroredData>());
        CUDA_CALL(cudaSetDevice(m_currentDeviceId));
    }

    /**
     * @brief registerDeviceData, registers a pointer to device data
     *
     * @param devicePtrAddress address of the pointer
     * @param dataSize size of the device data
     */
    void registerDeviceData(void** devicePtrAddress, const size_t dataSize)
    {
        if (m_currentDeviceId > -1)
        {
            m_internalDeviceData[m_currentDeviceId].emplace_back(*devicePtrAddress, devicePtrAddress, dataSize);
        }
        else
        {
            CARB_LOG_WARN("Current device ID is not valid: %d, is the handler initialized?", m_currentDeviceId);
        }
    }

    /**
     * @brief registerMirroredData, registers a pointer to device struct which points to device pointers.
     * Therefore, the host and device pointers are needed
     *
     * @param devicePtrAddress address of the pointer to the device struct
     * @param dataSize size of the device data struct
     * @param hostPtr pointer to the host struct
     */
    void registerMirroredData(void** devicePtrAddress, const size_t dataSize, void* hostPtr)
    {
        if (m_currentDeviceId > -1)
        {
            m_internalMirroredData[m_currentDeviceId].emplace_back(
                *devicePtrAddress, devicePtrAddress, hostPtr, dataSize);
        }
        else
        {
            CARB_LOG_WARN("Current device ID is not valid: %d, is the handler initialized?", m_currentDeviceId);
        }
    }

    /**
     * @brief handleGpuMigration, potentially handles the gpu migration (if the cuda device is different than the saved
     * cuda device). The userData is used inside the stored callback function to set host-side data (only needed for
     * mirrored data).
     *
     * @param deviceId potentially new device id
     * @param userData input data blob for the callback function, optional
     */
    void handleGpuMigration(const int deviceId, void* userData = nullptr)
    {
        if (deviceId != m_currentDeviceId)
        {
            if (deviceId >= 0 && m_currentDeviceId >= 0)
            {
                if (m_canAccessPeer == -1)
                    CUDA_CALL(cudaDeviceCanAccessPeer(&m_canAccessPeer, m_currentDeviceId, deviceId));

                // optional user callback to keep the host current
                if (m_migrationCbFn)
                {
                    m_migrationCbFn(userData);
                }
                // Check if device has to be set
                {
                    int setDeviceId;
                    CUDA_CALL(cudaGetDevice(&setDeviceId));
                    if (setDeviceId != deviceId)
                    {
                        CUDA_CALL(cudaSetDevice(deviceId));
                    }
                }

                CARB_LOG_INFO("migrating from device %d to %d\n", m_currentDeviceId, deviceId);

                // Needs to be done first as these ptrs could be members of the host data struct
                handleDeviceGpuMigration(deviceId, m_internalDeviceData);

                handleMirroredGpuMigration(deviceId, m_internalMirroredData);

                // Set new current device id
                m_currentDeviceId = deviceId;
            }
            else
            {
                CARB_LOG_WARN("New device ID or currentDeviceId is not valid, is the handler initialized?: %d, %d",
                              deviceId, m_currentDeviceId);
            }
        }
    }


    /**
     * @brief initialized, returns if the utility object is initialized
     */
    bool initialized() const noexcept
    {
        return m_currentDeviceId > -1;
    }

    /**
     * @brief private helper functions
     */
private:
    void handleDeviceGpuMigration(const int deviceId, InternalDeviceDataStorage& internalData)
    {
        // Don't do anything if there is no registered data
        if (internalData.size() > 0)
        {
            auto it = internalData.find(deviceId);
            // Data already present in gpu
            if (it != internalData.end())
            {
                for (const auto& el : internalData[m_currentDeviceId])
                {
                    if (m_canAccessPeer == 1)
                    {
                        CUDA_CALL(cudaMemcpyPeer(
                            el.devicePtr, deviceId, *(el.userDevicePtrAddress), m_currentDeviceId, el.dataSize));
                    }
                    else
                    {
                        void* host = malloc(el.dataSize);
                        CUDA_CALL(cudaSetDevice(m_currentDeviceId));
                        CUDA_CALL(cudaMemcpy(host, *(el.userDevicePtrAddress), el.dataSize, cudaMemcpyDeviceToHost));
                        CUDA_CALL(cudaSetDevice(deviceId));
                        CUDA_CALL(cudaMemcpy(el.devicePtr, host, el.dataSize, cudaMemcpyHostToDevice));
                        free(host);
                    }
                    // Overwrite old ptr with new ptr
                    *(el.userDevicePtrAddress) = el.devicePtr;
                }
            }
            else // new device
            {
                // Copy from current device to new one
                std::vector<DeviceData> newData;
                for (const auto& el : internalData[m_currentDeviceId])
                {
                    // Allocate on new Gpu
                    void* newDPtr;
                    CUDA_CALL(cudaMalloc(&newDPtr, el.dataSize));
                    if (m_canAccessPeer == 1)
                    {
                        // Copy from old gpu to new gpu
                        CUDA_CALL(cudaMemcpyPeer(newDPtr, deviceId, el.devicePtr, m_currentDeviceId, el.dataSize));
                    }
                    else // Peer to peer not possible -> bridge over host memory
                    {
                        void* host = malloc(el.dataSize);
                        CUDA_CALL(cudaSetDevice(m_currentDeviceId));
                        CUDA_CALL(cudaMemcpy(host, el.devicePtr, el.dataSize, cudaMemcpyDeviceToHost));
                        CUDA_CALL(cudaSetDevice(deviceId));
                        CUDA_CALL(cudaMemcpy(newDPtr, host, el.dataSize, cudaMemcpyHostToDevice));
                        free(host);
                    }
                    // Overwrite old ptr with new ptr
                    *(el.userDevicePtrAddress) = newDPtr;
                    // Add to internal data structure
                    newData.emplace_back(newDPtr, el.userDevicePtrAddress, el.dataSize);
                }
                internalData.emplace(deviceId, newData);
            }
        }
    }

    // Copy host to device always needed as pointer values of host struct was changed
    void handleMirroredGpuMigration(const int deviceId, InternalMirroredDataStorage& internalData)
    {
        // Don't do anything if there is no registered data
        if (internalData.size() > 0)
        {
            auto it = internalData.find(deviceId);
            // Data already present in gpu
            if (it != internalData.end())
            {
                for (const auto& el : internalData[m_currentDeviceId])
                {
                    // Pointer changed --> copy from host needed
                    CUDA_CALL(cudaMemcpy(el.devicePtr, el.hostPtr, el.dataSize, cudaMemcpyHostToDevice));
                    // Overwrite old ptr with new ptr
                    *(el.userdevicePtrAddress) = el.devicePtr;
                }
            }
            else // new device
            {
                // Copy from current device to new one
                std::vector<MirroredData> newData;
                for (const auto& el : internalData[m_currentDeviceId])
                {
                    // Allocate on new Gpu
                    void* newDPtr;
                    CUDA_CALL(cudaMalloc(&newDPtr, el.dataSize));
                    // Copy from host to new gpu
                    CUDA_CALL(cudaMemcpy(newDPtr, el.hostPtr, el.dataSize, cudaMemcpyHostToDevice));
                    // Overwrite old device ptr with new device ptr
                    *(el.userdevicePtrAddress) = newDPtr;
                    // Add to internal data structure
                    newData.emplace_back(newDPtr, el.userdevicePtrAddress, el.hostPtr, el.dataSize);
                }
                internalData.emplace(deviceId, newData);
            }
        }
    }

private:
    int m_canAccessPeer{ -1 }; /**< peer to peer access available */
    int m_currentDeviceId{ -1 }; /**< current device id of the handled data */
    InternalDeviceDataStorage m_internalDeviceData; /**< internal device data */
    // Ptr to struct which holds to be moved ptr
    InternalMirroredDataStorage m_internalMirroredData; /**< internal mirrored data */

    MigrationCbFn m_migrationCbFn; /**< callback function, optional */
};

} // namespace cuda
} // namespace sensors
} // namespace omni
