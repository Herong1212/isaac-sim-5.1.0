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
#include <omni/sensors/net/INetworkFactory.h>
#include <rtx/rtsensor/RtxSensorModel.h>

#include <cstdint>
#include <memory>
#include <vector>

namespace omni::sensors::nv::debugger
{

#pragma pack(push, 1)

enum class DebugRtxSensorBufferType : uint32_t
{
    EMPTY = 0,
    OPENTRACE,
    BATCHBEGIN,
    BATCHBEGINENTRY,
    BATCHEND,
    BATCHENDENTRY,
    CLOSETRACE,
};

enum class DebugBatchEntryType : uint32_t
{
    NONE = 0,
    ISVALID,
    FIRINGFLAGS,
    FIRETIMENS,
    FIRINGID,
    DIRECTION,
    ORIGIN,

    MATERIALID,
    RETURNFLAGS,
    DISTANCE,
    HITPT,
    NORMAL,
};

struct DebugRtxSensorBuffer
{
    DebugRtxSensorBufferType bufferType{ 0 };
    uint32_t batchId{ 0 };
    uint64_t startTimeNs{ 0 };
    uint64_t endTimeNs{ 0 };
    uint32_t maxRaysPerBatch{ 0 };
    uint32_t maxBatches{ 0 };
    DebugBatchEntryType entryType{ DebugBatchEntryType::NONE };
    void* data{ nullptr };
};

struct DebugRay
{
    // firings
    uint32_t isValid;
    uint32_t firingFlags;
    uint64_t fireTimeNs;
    uint32_t firingFiringId;
    float originM[3];
    float direction[3];

    // returns
    uint32_t objectId;
    uint32_t materialId;
    uint32_t returnFlags;
    uint32_t returnFiringId;
    float distance;
    float hitPt[3];
    float normal[3];
    float velocity[3];
    /*
    float diffuseReflectance[3];
    float specularReflectance[3];
    float shadingNormal[3];
    float indexOfRefraction;
    float roughness;
    */
    float vertices[3][3];
    float vertexNormals[3][3];
    // float barycentrics[3];
};

struct DebugAsyncBuffer
{
    void* instPtr;
    omni::core::ObjectPtr<omni::sensors::net::IBufferCapsule> capsule;
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


    void prepTrace(uint32_t* maxBatches, bool motionBvh, const void* signalsBuffer, uint64_t signalsSize)
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

        // track batchId
        m_currentBatchId = 0;

        // only capture frame if we gather the cached structs to have access to the device pointers
        if (m_cachedStructsValid)
        {
            m_captureFrame = true;

            // send out the current motion information
            size_t debugBufferSize = sizeof(DebugRtxSensorBuffer) + sizeof(rtx::rtxsensor::RtxSensorMotion);

            DebugAsyncBuffer* asyncBuffer = prepareAsyncBuffer(debugBufferSize);
            DebugRtxSensorBuffer* debugBuffer = reinterpret_cast<DebugRtxSensorBuffer*>(asyncBuffer->capsule->data());

            debugBuffer->bufferType = DebugRtxSensorBufferType::OPENTRACE;
            debugBuffer->startTimeNs = startTimeNs;
            debugBuffer->endTimeNs = endTimeNs;
            debugBuffer->batchId = m_currentBatchId;
            debugBuffer->maxRaysPerBatch = m_maxFirings;
            debugBuffer->maxBatches = m_maxBatches;
            memcpy((void*)&debugBuffer->data, motion, sizeof(rtx::rtxsensor::RtxSensorMotion));

            asyncSendBuffer(asyncBuffer);
        }
    }

    void sendSoAEntry(DebugRtxSensorBufferType bufferType, void* cudaPtr, DebugBatchEntryType entryType, size_t size)
    {
        size_t debugBufferSize = sizeof(DebugRtxSensorBuffer) + size * m_maxFirings;

        DebugAsyncBuffer* asyncBuffer = prepareAsyncBuffer(debugBufferSize);
        DebugRtxSensorBuffer* debugBuffer = reinterpret_cast<DebugRtxSensorBuffer*>(asyncBuffer->capsule->data());

        debugBuffer->bufferType = bufferType;
        debugBuffer->startTimeNs = m_currentTraceTimestamp;
        debugBuffer->batchId = m_currentBatchId;
        debugBuffer->entryType = entryType;
        // carb::extras::copyStringSafe(debugBuffer->name, sizeof(debugBuffer->name), name);

        // printf("sendSoAEntry: %s, %p, %p, %zu, %p\n", name, &debugBuffer->data, cudaPtr, size * m_maxFirings,
        // m_cudaStream);

        // printf("sendSoAEntry: %s, \n", name, &debugBuffer->data, cudaPtr, size * m_maxFirings, m_cudaStream);

        CUDA_CALL(cudaMemcpyAsync(
            (void*)&debugBuffer->data, cudaPtr, size * m_maxFirings, cudaMemcpyDeviceToHost, m_cudaStream));

        asyncSendBuffer(asyncBuffer);
    }

    void batchBegin(rtx::rtxsensor::RtxSensorFiringSOA_v10* firings)
    {
        CUDA_CALL(cudaMemcpyAsync((void*)&m_cachedFirings, firings, sizeof(rtx::rtxsensor::RtxSensorFiringSOA_v10),
                                  cudaMemcpyDeviceToHost, m_cudaStream));
        m_cachedStructsValid = true;

        if (m_captureFrame)
        {
            size_t debugBufferSize = sizeof(DebugRtxSensorBuffer) + sizeof(rtx::rtxsensor::RtxSensorFiringSOA_v10);

            DebugAsyncBuffer* asyncBuffer = prepareAsyncBuffer(debugBufferSize);
            DebugRtxSensorBuffer* debugBuffer = reinterpret_cast<DebugRtxSensorBuffer*>(asyncBuffer->capsule->data());

            debugBuffer->bufferType = DebugRtxSensorBufferType::BATCHBEGIN;
            debugBuffer->startTimeNs = m_currentTraceTimestamp;
            debugBuffer->batchId = m_currentBatchId;

            CUDA_CALL(cudaMemcpyAsync((void*)&debugBuffer->data, firings, sizeof(rtx::rtxsensor::RtxSensorFiringSOA_v10),
                                      cudaMemcpyDeviceToHost, m_cudaStream));

            asyncSendBuffer(asyncBuffer);

            sendSoAEntry(DebugRtxSensorBufferType::BATCHBEGINENTRY, m_cachedFirings.isValid,
                         DebugBatchEntryType::ISVALID, sizeof(uint32_t));
            sendSoAEntry(DebugRtxSensorBufferType::BATCHBEGINENTRY, m_cachedFirings.flags,
                         DebugBatchEntryType::FIRINGFLAGS, sizeof(uint32_t));
            sendSoAEntry(DebugRtxSensorBufferType::BATCHBEGINENTRY, m_cachedFirings.fireTimeNs,
                         DebugBatchEntryType::FIRETIMENS, sizeof(uint64_t));
            sendSoAEntry(DebugRtxSensorBufferType::BATCHBEGINENTRY, m_cachedFirings.firingId,
                         DebugBatchEntryType::FIRINGID, sizeof(uint32_t));
            sendSoAEntry(DebugRtxSensorBufferType::BATCHBEGINENTRY, m_cachedFirings.direction,
                         DebugBatchEntryType::DIRECTION, sizeof(float) * 3);
            sendSoAEntry(DebugRtxSensorBufferType::BATCHBEGINENTRY, m_cachedFirings.origin, DebugBatchEntryType::ORIGIN,
                         sizeof(float) * 3);
        }
    }


    void batchEnd(const rtx::rtxsensor::RtxSensorReturnSOA_v10* returns)
    {
        CUDA_CALL(cudaMemcpyAsync((void*)&m_cachedReturns, returns, sizeof(rtx::rtxsensor::RtxSensorReturnSOA_v10),
                                  cudaMemcpyDeviceToHost, m_cudaStream));

        if (m_captureFrame)
        {
            size_t debugBufferSize = sizeof(DebugRtxSensorBuffer) + sizeof(rtx::rtxsensor::RtxSensorReturnSOA_v10);

            DebugAsyncBuffer* asyncBuffer = prepareAsyncBuffer(debugBufferSize);
            DebugRtxSensorBuffer* debugBuffer = reinterpret_cast<DebugRtxSensorBuffer*>(asyncBuffer->capsule->data());

            debugBuffer->bufferType = DebugRtxSensorBufferType::BATCHEND;
            debugBuffer->startTimeNs = m_currentTraceTimestamp;
            debugBuffer->batchId = m_currentBatchId;

            CUDA_CALL(cudaMemcpyAsync((void*)&debugBuffer->data, returns, sizeof(rtx::rtxsensor::RtxSensorReturnSOA_v10),
                                      cudaMemcpyDeviceToHost, m_cudaStream));

            asyncSendBuffer(asyncBuffer);

            sendSoAEntry(DebugRtxSensorBufferType::BATCHENDENTRY, m_cachedReturns.materialId,
                         DebugBatchEntryType::MATERIALID, sizeof(uint32_t));
            sendSoAEntry(DebugRtxSensorBufferType::BATCHENDENTRY, m_cachedReturns.flags,
                         DebugBatchEntryType::RETURNFLAGS, sizeof(uint32_t));
            sendSoAEntry(DebugRtxSensorBufferType::BATCHENDENTRY, m_cachedReturns.distance,
                         DebugBatchEntryType::DISTANCE, sizeof(float));
            sendSoAEntry(DebugRtxSensorBufferType::BATCHENDENTRY, m_cachedReturns.hitPt, DebugBatchEntryType::HITPT,
                         sizeof(float) * 3);
            sendSoAEntry(DebugRtxSensorBufferType::BATCHENDENTRY, m_cachedReturns.normal, DebugBatchEntryType::NORMAL,
                         sizeof(float) * 3);
        }

        // update batchId after sending out
        m_currentBatchId++;
    }


    void closeTrace(void* outData, size_t* outLength, void* outputMetadata, size_t* metadataSize)
    {
        if (m_captureFrame)
        {
            // send out close trace
            size_t debugBufferSize = sizeof(DebugRtxSensorBuffer) + 512;

            DebugAsyncBuffer* asyncBuffer = prepareAsyncBuffer(debugBufferSize);
            DebugRtxSensorBuffer* debugBuffer = reinterpret_cast<DebugRtxSensorBuffer*>(asyncBuffer->capsule->data());

            debugBuffer->bufferType = DebugRtxSensorBufferType::CLOSETRACE;
            debugBuffer->startTimeNs = m_currentTraceTimestamp;

            asyncSendBuffer(asyncBuffer);
        }
    }


private:
    void setupChannel()
    {
        auto networkFactory = omni::core::createType<omni::sensors::net::INetworkFactory>();
        auto dict = carb::getCachedInterface<carb::dictionary::IDictionary>();

        // realm channel setup
        // TODO: deterministic realm required!

        carb::dictionary::Item* descItem = nullptr;
        descItem = dict->createItem(nullptr, "__channel_desc", carb::dictionary::ItemType::eDictionary);
        dict->makeAtPath(descItem, "backend", "net_realm");
        dict->makeAtPath(descItem, "type", "REALM");
        dict->makeAtPath(descItem, "key", "sensor_debugger_v10_raw");
        dict->makeBoolAtPath(descItem, "sending", true);
        dict->makeInt64AtPath(descItem, "remoteProcessIdx", 0);

        m_debugTopic = networkFactory->makeChannel(descItem);

        std::cout << "Sensor debugger for RtxSensor10 set up connection realm channel!" << std::endl;
    }


    DebugAsyncBuffer* prepareAsyncBuffer(size_t debugBufferSize)
    {
        m_networkFactory = omni::core::createType<omni::sensors::net::INetworkFactory>();

        DebugAsyncBuffer* asyncBuffer = new DebugAsyncBuffer;
        asyncBuffer->instPtr = (void*)this;
        asyncBuffer->capsule = m_networkFactory->makeCapsule(debugBufferSize);

        DebugRtxSensorBuffer* debugBuffer = reinterpret_cast<DebugRtxSensorBuffer*>(asyncBuffer->capsule->data());
        debugBuffer->startTimeNs = m_currentTraceTimestamp;

        return asyncBuffer;
    }


    void asyncSendBuffer(DebugAsyncBuffer* asyncBuffer)
    {
        cudaLaunchHostFunc(
            m_cudaStream,
            [](void* usrData)
            {
                DebugAsyncBuffer* asyncBuffer = reinterpret_cast<DebugAsyncBuffer*>(usrData);
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


    omni::sensors::net::INetworkFactoryPtr m_networkFactory;
    carb::tasking::ITasking* m_tasking;
    carb::tasking::SharedFuture<void> m_sendTask;
    omni::sensors::net::IChannelPtr m_debugTopic = nullptr;

    int32_t m_cudaDevice;
    cudaStream_t m_cudaStream;
    uint32_t m_maxBatches{ 0 };
    uint32_t m_maxFirings{ 0 };
    int64_t m_currentTraceTimestamp = 0;
    uint32_t m_currentBatchId = 0;

    // cache the device side structs
    bool m_captureFrame{ false };
    bool m_cachedStructsValid{ false };
    rtx::rtxsensor::RtxSensorFiringSOA_v10 m_cachedFirings;
    rtx::rtxsensor::RtxSensorReturnSOA_v10 m_cachedReturns;
};


} // namespace omni::sensors::nv::debugger
