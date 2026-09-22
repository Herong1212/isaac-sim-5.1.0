// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#pragma once

#include <carb/tasking/ITasking.h>

#include <omni/core/IObject.h>
#include <omni/core/ITypeFactory.h>
#include <omni/drivesim/net/INetworkFactory.h>

#include <cstdint>
#include <memory>
#include <vector>

namespace omni
{
namespace sensors
{

#pragma pack(push, 1)

enum class DebugRtxSensorBufferType : uint32_t
{
    EMPTY = 0,
    OPENTRACE = 1,
    BATCHBEGIN = 2,
    BATCHEND = 3,
    CLOSETRACE = 4
};

struct DebugRtxSensorBuffer
{
    DebugRtxSensorBufferType bufferType{ 0 };
    int32_t _pad;
    int64_t startTimeNs;
    int64_t endTimeNs;
    void* data{ nullptr };
};

struct DebugAsyncBuffer
{
    void* instPtr;
    omni::core::ObjectPtr<omni::drivesim::net::IBufferCapsule> capsule;
};

#pragma pack(pop)


class RTXSensorDebugger
{
public:
    RTXSensorDebugger()
    {
        m_tasking = carb::getCachedInterface<carb::tasking::ITasking>();

        // make sure channel is up
        setupChannel();
    }


    void setCudaDevice(int32_t cudaDevice)
    {
        m_cudaDevice = cudaDevice;
    }


    void setCudaStream(rtx::rtxsensor::RtxSensorCudaStream_t cudaStream)
    {
        m_cudaStream = reinterpret_cast<cudaStream_t>(cudaStream);
    }


    void getModelRequirements(rtx::rtxsensor::RtxSensorRequirements* result)
    {
        m_maxFirings = result->maxRaysPerBatch;
    }


    void prepTrace(uint32_t* maxBatches, const void* signalsBuffer, uint64_t signalsSize)
    {
        m_maxBatches = *maxBatches;
    }


    void openTrace(int64_t startTimeNs,
                   int64_t endTimeNs,
                   const rtx::rtxsensor::RtxSensorMotion* motion,
                   void* perFrameBuffer,
                   uint64_t perFrameBufferSize)
    {
        // store current timestamp as unique identifier for trace
        m_currentTraceTimestamp = startTimeNs;

        // send out the current motion information
        size_t debugBufferSize = sizeof(omni::sensors::DebugRtxSensorBuffer) + sizeof(rtx::rtxsensor::RtxSensorMotion);

        omni::sensors::DebugAsyncBuffer* asyncBuffer = prepareAsyncBuffer(debugBufferSize);
        omni::sensors::DebugRtxSensorBuffer* debugBuffer =
            reinterpret_cast<DebugRtxSensorBuffer*>(asyncBuffer->capsule->data());

        debugBuffer->bufferType = omni::sensors::DebugRtxSensorBufferType::OPENTRACE;
        debugBuffer->startTimeNs = startTimeNs;
        debugBuffer->endTimeNs = endTimeNs;
        memcpy((void*)&debugBuffer->data, motion, sizeof(rtx::rtxsensor::RtxSensorMotion));

        asyncSendBuffer(asyncBuffer);
    }


    void batchBegin(rtx::rtxsensor::RtxSensorFiring* firings)
    {
        // send out the current firings
        size_t debugBufferSize =
            sizeof(omni::sensors::DebugRtxSensorBuffer) + sizeof(rtx::rtxsensor::RtxSensorFiring) * m_maxFirings;

        omni::sensors::DebugAsyncBuffer* asyncBuffer = prepareAsyncBuffer(debugBufferSize);
        omni::sensors::DebugRtxSensorBuffer* debugBuffer =
            reinterpret_cast<DebugRtxSensorBuffer*>(asyncBuffer->capsule->data());

        debugBuffer->bufferType = omni::sensors::DebugRtxSensorBufferType::BATCHBEGIN;
        CUDA_CALL(cudaMemcpyAsync((void*)&debugBuffer->data, firings,
                                  sizeof(rtx::rtxsensor::RtxSensorFiring) * m_maxFirings, cudaMemcpyDeviceToHost,
                                  m_cudaStream));

        asyncSendBuffer(asyncBuffer);
    }


    void batchEnd(const rtx::rtxsensor::RtxSensorReturn* returns)
    {
        // send out the current returns
        size_t debugBufferSize =
            sizeof(omni::sensors::DebugRtxSensorBuffer) + sizeof(rtx::rtxsensor::RtxSensorReturn) * m_maxFirings;

        omni::sensors::DebugAsyncBuffer* asyncBuffer = prepareAsyncBuffer(debugBufferSize);
        omni::sensors::DebugRtxSensorBuffer* debugBuffer =
            reinterpret_cast<DebugRtxSensorBuffer*>(asyncBuffer->capsule->data());

        debugBuffer->bufferType = omni::sensors::DebugRtxSensorBufferType::BATCHEND;
        CUDA_CALL(cudaMemcpyAsync((void*)&debugBuffer->data, returns,
                                  sizeof(rtx::rtxsensor::RtxSensorReturn) * m_maxFirings, cudaMemcpyDeviceToHost,
                                  m_cudaStream));

        asyncSendBuffer(asyncBuffer);
    }


    void closeTrace(void* outData, size_t* outLength, void* outputMetadata, size_t* metadataSize)
    {
        // send out close trace
        size_t debugBufferSize = sizeof(omni::sensors::DebugRtxSensorBuffer) + 512;

        omni::sensors::DebugAsyncBuffer* asyncBuffer = prepareAsyncBuffer(debugBufferSize);
        omni::sensors::DebugRtxSensorBuffer* debugBuffer =
            reinterpret_cast<DebugRtxSensorBuffer*>(asyncBuffer->capsule->data());

        debugBuffer->bufferType = omni::sensors::DebugRtxSensorBufferType::CLOSETRACE;

        asyncSendBuffer(asyncBuffer);
    }


private:
    void setupChannel()
    {
        auto networkFactory = omni::core::createType<omni::drivesim::net::INetworkFactory>();
        auto dict = carb::getCachedInterface<carb::dictionary::IDictionary>();
        // create an item
        auto item = dict->createItem(nullptr, "item", carb::dictionary::ItemType::eDictionary);

        auto backend = dict->createItem(item, "backend", carb::dictionary::ItemType::eDictionary);
        dict->setString(backend, "net_topic");
        auto netType = dict->createItem(item, "type", carb::dictionary::ItemType::eDictionary);
        dict->setString(netType, "TOPIC");
        auto remoteIP = dict->createItem(item, "topic", carb::dictionary::ItemType::eDictionary);
        dict->setString(remoteIP, "sensor_debugger_raw_batch");

        // realm channel setup
        // TODO: deterministic realm required!
        /*
        auto backend = dict->createItem(item, "backend", carb::dictionary::ItemType::eDictionary);
        dict->setString(backend, "net_realm");
        auto netType = dict->createItem(item, "type", carb::dictionary::ItemType::eDictionary);
        dict->setString(netType, "REALM");
        auto remoteIP = dict->createItem(item, "key", carb::dictionary::ItemType::eDictionary);
        dict->setString(remoteIP, "sensor_debugger_raw_batch");
        dict->makeBoolAtPath(item, "sending", true);
        dict->makeInt64AtPath(item, "remoteProcessIdx", 0);
        */
        m_debugTopic = networkFactory->makeChannel(item);


        std::cout << "LidarRotary set up connection to debug channel!" << std::endl;
    }


    omni::sensors::DebugAsyncBuffer* prepareAsyncBuffer(size_t debugBufferSize)
    {
        m_networkFactory = omni::core::createType<omni::drivesim::net::INetworkFactory>();

        omni::sensors::DebugAsyncBuffer* asyncBuffer = new omni::sensors::DebugAsyncBuffer;
        asyncBuffer->instPtr = (void*)this;
        asyncBuffer->capsule = m_networkFactory->makeCapsule(debugBufferSize);

        omni::sensors::DebugRtxSensorBuffer* debugBuffer =
            reinterpret_cast<DebugRtxSensorBuffer*>(asyncBuffer->capsule->data());
        debugBuffer->startTimeNs = m_currentTraceTimestamp;

        return asyncBuffer;
    }


    void asyncSendBuffer(DebugAsyncBuffer* asyncBuffer)
    {
        cudaLaunchHostFunc(
            m_cudaStream,
            [](void* usrData)
            {
                omni::sensors::DebugAsyncBuffer* asyncBuffer =
                    reinterpret_cast<omni::sensors::DebugAsyncBuffer*>(usrData);
                RTXSensorDebugger* handle = reinterpret_cast<RTXSensorDebugger*>(asyncBuffer->instPtr);

                // NOTE: not using carb tasking also works not but sure of the drawbacks (sending from
                // wrong thread?)
                /*
                handle->m_debugTopic->send(std::move(asyncBuffer->capsule));
                free(asyncBuffer);
                */

                // NOTE: to make sure we receive the capsules in order we use the subtasks mechanic
                //       if some task is still running, we add a subtask behind it
                if (handle->m_sendTask.valid())
                {
                    handle->m_sendTask =
                        handle->m_tasking->addSubTask(handle->m_sendTask, carb::tasking::Priority::eHigh, {},
                                                      [handle, asyncBuffer]()
                                                      {
                                                          handle->m_debugTopic->send(std::move(asyncBuffer->capsule));
                                                          delete asyncBuffer;
                                                      });
                }
                else
                {
                    handle->m_sendTask =
                        handle->m_tasking->addTask(carb::tasking::Priority::eHigh, {},
                                                   [handle, asyncBuffer]()
                                                   {
                                                       handle->m_debugTopic->send(std::move(asyncBuffer->capsule));
                                                       delete asyncBuffer;
                                                   });
                }
            },
            asyncBuffer);
    }


    omni::drivesim::net::INetworkFactoryPtr m_networkFactory;
    carb::tasking::ITasking* m_tasking;
    carb::tasking::SharedFuture<void> m_sendTask;
    omni::drivesim::net::IChannelPtr m_debugTopic = nullptr;

    int32_t m_cudaDevice;
    cudaStream_t m_cudaStream;
    uint32_t m_maxBatches{ 0 };
    uint32_t m_maxFirings{ 0 };
    int64_t m_currentTraceTimestamp = 0;
};


} // namespace sensors
} // namespace omni
