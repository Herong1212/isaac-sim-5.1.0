// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

// clang-format off
#include "UsdPCH.h"
// clang-format on

#include <OgnOnObjectChangeDatabase.h>

#include "ActionNodeCommon.h"

#include <omni/graph/action/IActionGraph.h>
#include <omni/fabric/FabricUSD.h>
#include <omni/graph/core/ArrayWrapper.h>
// clang-format off
#include <omni/usd/UsdContext.h>
// clang-format on

#include <mutex>

namespace omni
{
namespace graph
{
namespace action
{

using namespace omni::graph::core;

// The idea here is that each node instance will register as a notice listener when it's compute is called if the path
// input has changed, or they haven't registered before. The watched path needs to be verified every compute because
// input could be changing at any point. The listener must always be revoked in `release`. Any changes since the last
// compute() will trigger the output execution.
//
class UsdNoticeListener;

using UsdNoticeListenerRefPtr = pxr::TfRefPtr<UsdNoticeListener>;
using UsdNoticeListenerWeakPtr = pxr::TfWeakPtr<UsdNoticeListener>;

// Derive from Ref and Weak bases so that we don't crash during `release` (and we delete the listener) from a
// different thread than the notices are being sent on. Instead we just decref the listener so that the internal
// weak pointer will keep it alive until notice sending is completed
class UsdNoticeListener : public pxr::TfRefBase, public pxr::TfWeakBase
{
public:
    enum class WatchType
    {
        eInvalid,
        ePrim,
        ePrimProperty
    };

    static UsdNoticeListenerRefPtr New(long stageId)
    {
        return pxr::TfCreateRefPtr(new UsdNoticeListener(stageId));
    }

    ~UsdNoticeListener()
    {
        pxr::TfNotice::Revoke(m_registerKey);
    }

    void registerForPath(pxr::SdfPath path, UsdNoticeListenerRefPtr ptr)
    {
        // Ensure our dirty flag isn't still set
        {
            const std::lock_guard<std::mutex> lock(m_noticeMutex);
            m_watchedPath = path;
            m_isDirty = false;
            m_noticedName = pxr::TfToken();
        }

        // If we are given an empty path we can revoke
        if (path.IsEmpty())
        {
            if (m_registerKey.IsValid())
                pxr::TfNotice::Revoke(m_registerKey);
            return;
        }

        // Determine if the path actually exists on the stage
        m_watchType = WatchType::eInvalid;

        if (path.IsPrimPath())
        {
            pxr::UsdPrim prim = m_stage->GetPrimAtPath(path);
            if (!prim)
                return;
            m_watchType = WatchType::ePrim;
        }
        else if (path.IsPrimPropertyPath())
        {
            pxr::UsdProperty prop = m_stage->GetPropertyAtPath(path);
            if (!prop)
                return;
            m_watchType = WatchType::ePrimProperty;
        }

        // Register ourselves
        if (!m_registerKey.IsValid())
            m_registerKey = pxr::TfNotice::Register(UsdNoticeListenerWeakPtr(ptr), &UsdNoticeListener::Handle);
    }

    void Handle(const class pxr::UsdNotice::ObjectsChanged& objectsChanged)
    {
        // If already dirty, don't worry about it
        if (m_isDirty)
            return;

        if (m_stage != objectsChanged.GetStage())
            return;

        switch (m_watchType)
        {
        case WatchType::ePrim:
        {
            pxr::UsdPrim prim = m_stage->GetPrimAtPath(m_watchedPath);
            if (prim)
            {
                for (const auto& path : objectsChanged.GetChangedInfoOnlyPaths())
                {
                    const pxr::SdfPath& changePath = path.GetPrimPath();
                    if (m_stage->GetPrimAtPath(changePath) == prim)
                    {
                        const std::lock_guard<std::mutex> lock(m_noticeMutex);
                        m_noticedName = path.GetNameToken();
                        m_isDirty = true;
                        break;
                    }
                }
            }
            break;
        }
        case WatchType::ePrimProperty:
        {
            pxr::UsdProperty prop = m_stage->GetPropertyAtPath(m_watchedPath);
            if (prop)
            {
                if (objectsChanged.AffectedObject(prop))
                {
                    const std::lock_guard<std::mutex> lock(m_noticeMutex);
                    m_noticedName = m_watchedPath.GetNameToken();
                    m_isDirty = true;
                }
            }
            break;
        }
        case WatchType::eInvalid:
            break;
        }
    }

    pxr::UsdStageRefPtr m_stage;
    pxr::TfNotice::Key m_registerKey;
    pxr::SdfPath m_watchedPath;
    WatchType m_watchType{ WatchType::eInvalid };
    bool m_isDirty{ false };
    pxr::TfToken m_noticedName;
    std::mutex m_noticeMutex;

private:
    UsdNoticeListener(long stageId)
    {
        m_stage = pxr::UsdUtilsStageCache::Get().Find(pxr::UsdStageCache::Id::FromLongInt(stageId));
        if (!m_stage)
        {
            CARB_LOG_ERROR("Could not find USD stage");
            return;
        }
    }
};

// ============================================================================


class OgnOnObjectChange
{
public:
    UsdNoticeListenerRefPtr m_listener{ nullptr };

    static bool compute(OgnOnObjectChangeDatabase& db)
    {
        if (checkNodeDisabledForOnlyPlay(db))
            return true;

        pxr::SdfPath watchedPath = toSdfPath(db.inputs.prim.firstOrDefault());
        if (!watchedPath.IsEmpty())
        {
            auto name = db.inputs.name();
            if (name != omni::fabric::kUninitializedToken)
            {
                auto nameToken = toTfToken(name);
                watchedPath = watchedPath.AppendProperty(nameToken);
            }
        }

        if (watchedPath.IsEmpty())
        {
            auto const& path = db.inputs.path();
            if (!pxr::SdfPath::IsValidPathString(path))
            {
                if (!path.empty())
                {
                    db.logError("Invalid path %s", path.data());
                    return false;
                }
            }
            else
                watchedPath = pxr::SdfPath(path);
        }

        auto& state = db.perInstanceState<OgnOnObjectChange>();

        auto processChange = [&]() -> pxr::TfToken
        {
            // Find the listener for this node, or create one if it doesn't exist
            if (!state.m_listener)
            {
                long stageId = db.abi_context().iContext->getStageId(db.abi_context());
                state.m_listener = UsdNoticeListener::New(stageId);
                state.m_listener->registerForPath(watchedPath, state.m_listener);
                return pxr::TfToken();
            }

            if (state.m_listener->m_watchedPath != watchedPath)
            {
                // re-register for the new path
                state.m_listener->registerForPath(watchedPath, state.m_listener);
                return pxr::TfToken();
            }

            {
                const std::lock_guard<std::mutex> lock(state.m_listener->m_noticeMutex);
                if (std::exchange(state.m_listener->m_isDirty, false))
                {
                    return state.m_listener->m_noticedName;
                }
            }
            return pxr::TfToken();
        };

        auto changed = processChange();
        if (!changed.IsEmpty())
        {
            auto iActionGraph = getInterface();
            iActionGraph->setExecutionEnabled(outputs::changed.token(), db.getInstanceIndex());
            db.outputs.propertyName() = omni::fabric::asInt(changed);
        }
        return true;
    }

    // ----------------------------------------------------------------------------

    static void release(const NodeObj& nodeObj)
    {
        auto& state = OgnOnObjectChangeDatabase::sSharedState<OgnOnObjectChange>(nodeObj);
        state.m_listener.Reset();
    }

    // ----------------------------------------------------------------------------

    static bool updateNodeVersion(const GraphContextObj& context, const NodeObj& nodeObj, int oldVersion, int newVersion)
    {
        if (oldVersion < newVersion)
        {
            if (oldVersion < 2)
            {
                // We added inputs:onlyPlayback default true - to maintain previous behavior we should set this to false
                const bool val{ false };
                nodeObj.iNode->createAttribute(nodeObj, "inputs:onlyPlayback", Type(BaseDataType::eBool), &val, nullptr,
                                               kAttributePortType_Input, kExtendedAttributeType_Regular, nullptr);
            }
            return true;
        }
        return false;
    }
};


REGISTER_OGN_NODE()
} // action
} // graph
} // omni
