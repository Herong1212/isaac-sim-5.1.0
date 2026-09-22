// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
#include <carb/settings/ISettings.h>
#include <carb/tasking/TaskingUtils.h>

#include <omni/sensors/Settings.h>

#include <chrono>


struct SyncData
{
    // All data is protected by the mutex.
    std::mutex mutex;
    std::condition_variable cv;

    bool ready{ true };
    bool connected{ false };

    using Clock = std::chrono::steady_clock;
};

inline std::chrono::nanoseconds computeSyncDataWaitTime()
{
    using namespace std::chrono;
    using namespace carb::settings;
    using namespace carb::dictionary;

    ISettings* settings = carb::getCachedInterface<ISettings>();

    // Don't use defaults as they require common code.
    double syncDataWait = 5.0;
    if (settings->isAccessibleAs(ItemType::eFloat, omni::sensors::nv::kSyncDataWait))
    {
        syncDataWait = settings->get<double>(omni::sensors::nv::kSyncDataWait);
    }

    if (settings->isAccessibleAs(ItemType::eFloat, omni::sensors::nv::kSyncDataScale))
    {
        syncDataWait *= settings->getAsFloat64(omni::sensors::nv::kSyncDataScale);
    }

    double maxSyncDataWait = 5.0;
    if (settings->isAccessibleAs(ItemType::eFloat, omni::sensors::nv::kMaxSyncDataWait))
    {
        maxSyncDataWait = settings->getAsFloat64(omni::sensors::nv::kMaxSyncDataWait);
    }

    if (maxSyncDataWait < syncDataWait)
    {
        syncDataWait = maxSyncDataWait;
    }
    return nanoseconds(static_cast<int64_t>(syncDataWait * 1.0e9));
}

inline void procFinished(SyncData* syncData, const bool checkConnection = false)
{
    if (syncData)
    {
        std::lock_guard lk(syncData->mutex);
        if (!(checkConnection && syncData->connected))
        {
            syncData->ready = true;
            syncData->cv.notify_all();
        }
    }
}

inline void nodeConnected(SyncData* syncData)
{
    if (syncData)
    {
        std::lock_guard lk(syncData->mutex);
        syncData->connected = true;
    }
}

inline void syncWait(SyncData* syncData)
{
    using namespace std::chrono;
    if (syncData)
    {
        nanoseconds waitTime = computeSyncDataWaitTime();
        auto endTime = SyncData::Clock::now() + waitTime;

        std::unique_lock lk(syncData->mutex);

        // There is a strange issue with ConditionVariableWrapper in how it gets the mutex, which is why the code
        // below has `operator carb::tasking::Mutex*()`
        if (!syncData->cv.wait_until(lk, endTime, [syncData]() { return syncData->ready; }))
        {
            CARB_LOG_WARN("Timeout in syncWait, waitTime = %f.", waitTime.count() * 1.0e-9);
        }
        syncData->ready = false;
    }
}

inline bool isReady(SyncData* syncData)
{
    bool result{ true };
    if (syncData)
    {
        std::lock_guard lk(syncData->mutex);
        result = syncData->ready;
    }
    return result;
}

inline void setReady(SyncData* syncData, bool value)
{
    if (syncData)
    {
        std::lock_guard lk(syncData->mutex);
        syncData->ready = value;
    }
}
