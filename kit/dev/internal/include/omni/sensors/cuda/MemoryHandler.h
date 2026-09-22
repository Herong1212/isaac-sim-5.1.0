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

#ifndef __CUDACC__
#    include <carb/InterfaceUtils.h>
#    include <carb/settings/ISettings.h>
#endif

#include <omni/sensors/cuda/CudaHelperDecl.h>
#include <omni/sensors/cuda/CudaHelperMem.h>
#include <omni/sensors/cuda/GpuMigrationHandler.h>
// this should be removed if syncData is deprecated
#include <omni/String.h>
#include <omni/sensors/SyncData.h>

#include <deque>
#include <iterator>
#include <map>
#include <vector>


namespace omni
{
namespace sensors
{
namespace cuda
{

struct BufferDesc
{
    size_t numElements{ 0LU };
    cuda::MemKind memKind;
    void* mirroredHostStruct{ nullptr };
    bool constant{ false };
    bool zeroInit{ false };
};

struct BufferEntry
{
    BufferDesc desc{};
    size_t sizeInBytes{ 0 };
    std::vector<void*> framePtrs;
};

struct HostFnUsrData
{
    void* usrData;
    cudaStream_t stream;
};

class MemoryHandler
{

public:
#ifndef __CUDACC__
    void init(const omni::string& model, const int deviceId, const cuda::GpuMigrationHandler::MigrationCbFn& cb = nullptr)
    {
        if (auto* iSettings = carb::getCachedInterface<carb::settings::ISettings>())
        {
            const std::string kSettingsFiF = "app/sensors/nv/" + std::string(model.c_str()) + "/framesInFlight";
            const std::string kSettingsGlobalFiF = "app/sensors/nv/all/framesInFlight";
            if (iSettings->isAccessibleAs(carb::dictionary::ItemType::eInt, kSettingsFiF.c_str()))
            {
                m_framesInFlight = static_cast<uint16_t>(iSettings->getAsInt(kSettingsFiF.c_str()));
            }
            else if (iSettings->isAccessibleAs(carb::dictionary::ItemType::eInt, kSettingsGlobalFiF.c_str()))
            {
                m_framesInFlight = static_cast<uint16_t>(iSettings->getAsInt(kSettingsGlobalFiF.c_str()));
            }
            else
            {
                m_framesInFlight = 3;
            }
        }
        // Activate sync wait if there only is one frame in flight
        if (m_framesInFlight == 1)
        {
            m_syncData = std::make_unique<SyncData>();
        }

        if (deviceId > -1)
        {
            m_migrationHandler.init(deviceId, cb);
        }
        m_deviceId = deviceId;
        m_initialized = true;
    }
#endif

    bool initialized() const noexcept
    {
        return m_initialized;
    }

    template <class T>
    uint16_t alloc(const BufferDesc& desc, const cudaStream_t stream = 0)
    {
        const uint16_t buffId{ static_cast<uint16_t>(m_datas.size()) };
        m_datas.emplace_back(BufferEntry());
        auto& el = m_datas[buffId];

        el.desc = desc;
        el.sizeInBytes = sizeof(T) * el.desc.numElements;

        // Frames on the GPU are guaranteed to be processed in sequence
        // GPU memory can therefore always be declared as constant
        if (el.desc.memKind == MemKind::GPU)
        {
            el.desc.constant = true;
        }

        uint16_t effectiveNumFrames{ m_framesInFlight };
        if (el.desc.constant || m_framesInFlight == 1)
        {
            el.desc.constant = true;
            effectiveNumFrames = 1;
        }

        el.framePtrs.resize(effectiveNumFrames);
        for (uint64_t frame = 0; frame < effectiveNumFrames; ++frame)
        {
            cuda::allocateBlob<T>((T**)&el.framePtrs[frame], el.desc.numElements, el.desc.memKind);
            if (el.desc.zeroInit)
            {
                cuda::setMem<T>((T*)el.framePtrs[frame], 0, el.desc.numElements,
                                desc.memKind != MemKind::GPU ? -1 : m_deviceId, stream);
            }
            if (el.desc.memKind == cuda::MemKind::GPU)
            {
                if (!el.desc.mirroredHostStruct)
                {
                    m_migrationHandler.registerDeviceData((void**)&el.framePtrs[frame], el.sizeInBytes);
                }
                else
                {
                    m_migrationHandler.registerMirroredData(
                        (void**)&el.framePtrs[frame], el.sizeInBytes, el.desc.mirroredHostStruct);
                }
            }
        }

        return buffId;
    }

    // Convenience operator
    void* operator()(const uint16_t ptrId, const cudaStream_t stream = 0)
    {
        return getDataPtr(ptrId, stream);
    }

    template <class T>
    T* getDataPtr(const uint16_t ptrId, const cudaStream_t stream = 0)
    {
        return reinterpret_cast<T*>(getDataPtr(ptrId, stream));
    }

    void* getDataPtr(const uint16_t ptrId, const cudaStream_t stream = 0)
    {
        void* result{ nullptr };

        if (validPtrId(ptrId))
        {
            auto& el = m_datas[ptrId];

            if (el.desc.constant)
            {
                result = el.framePtrs[0];
            }
            else
            {
                auto mapElement = m_streams.find(stream);
                if (mapElement != m_streams.end())
                {
                    result = el.framePtrs[mapElement->second];
                }
                else
                {
                    addNewStream(stream);
                    result = el.framePtrs[m_streams[stream]];
                }
            }
        }

        return result;
    }

    size_t getDataSize(const uint16_t ptrId) const
    {
        size_t result{ 0LU };
        if (validPtrId(ptrId))
        {
            result = m_datas[ptrId].sizeInBytes;
        }
        return result;
    }

    void setDevice(const int newDeviceId)
    {
        if (newDeviceId > -1)
        {
            if (!m_migrationHandler.initialized())
            {
                m_migrationHandler.init(newDeviceId);
            }
            m_migrationHandler.handleGpuMigration(newDeviceId);
            m_deviceId = newDeviceId;
        }
    }

    template <class T = void>
    void free(const uint16_t ptrId)
    {
        if (validPtrId(ptrId))
        {
            auto& el = m_datas[ptrId];
            for (auto& ptr : el.framePtrs)
            {
                if (ptr)
                {
                    cuda::freeBlob((T*)ptr, el.desc.memKind);
                    ptr = nullptr;
                }
            }
            el.sizeInBytes = 0;
            el.desc = {};
            el.framePtrs.clear();
            // the record in m_datas remain
        }
    }

    const BufferEntry& getBufferEntryForId(const uint16_t ptrId) const
    {
        return m_datas[ptrId];
    }


    void cpyMem(const uint16_t dstPtrId, const uint16_t srcPtrId, const cudaMemcpyKind kind, const cudaStream_t stream = 0)
    {
        void* srcPtr{ getDataPtr(srcPtrId, stream) };
        void* dstPtr{ getDataPtr(dstPtrId, stream) };
        const size_t sizeInBytes{ getDataSize(srcPtrId) };
        cpyMem(dstPtr, srcPtr, sizeInBytes, kind, stream);
    }

    void cpyMem(
        void* dstPtr, void* srcPtr, const size_t sizeInBytes, const cudaMemcpyKind kind, const cudaStream_t stream = 0)
    {
        cuda::cpyMem(dstPtr, srcPtr, sizeInBytes, kind, m_deviceId, stream);
    }


    ////// Sync wait methods -- if tripling of memory is not desired/applicable ///////////

#ifndef __CUDACC__
    void procFinished(const bool checkConnection = false)
    {
        ::procFinished(m_syncData.get(), checkConnection);
    }

    void nodeConnected()
    {
        ::nodeConnected(m_syncData.get());
    }

    void syncWait()
    {
        ::syncWait(m_syncData.get());
    }

    bool isReady()
    {
        bool result{ false };
        if (m_syncData)
        {
            result = ::isReady(m_syncData.get());
        }
        return result;
    }

    void setReady(const bool value)
    {
        ::setReady(m_syncData.get(), value);
    }
#endif

private:
    bool validPtrId(const uint16_t ptrId) const
    {
        bool result = true;
        if (ptrId >= m_datas.size() || m_datas[ptrId].framePtrs.empty())
        {
            result = false;
        }
        return result;
    }

    void addNewStream(const cudaStream_t stream = 0)
    {
        if (m_streams.size() >= m_framesInFlight)
        {
            const auto streamToChange = m_streamsToChange.front();
            m_streamsToChange.pop_front();

            auto entry = m_streams.find(streamToChange);
            if (entry != m_streams.end())
            {
                auto const value = entry->second;
                m_streams.erase(entry);
                m_streams.insert({ stream, value });
            }
            else
            {
                CARB_LOG_ERROR("tracked stream does not exist");
            }
        }
        else
        {
            m_streams.emplace(std::pair<cudaStream_t, uint16_t>(stream, (uint16_t)m_streams.size()));
        }
        m_streamsToChange.push_back(stream);
    }

    bool m_initialized{ false };
    std::vector<BufferEntry> m_datas;
    std::map<cudaStream_t, uint16_t> m_streams;
    int m_deviceId{ 0 };
    cuda::GpuMigrationHandler m_migrationHandler;
    // Only needed if tripling of memory is not desired/applicable
    std::unique_ptr<SyncData> m_syncData{ nullptr };
    std::deque<cudaStream_t> m_streamsToChange;
    uint16_t m_framesInFlight{ 0 };
};

} // namespace cuda
} // namespace sensors
} // namespace omni
