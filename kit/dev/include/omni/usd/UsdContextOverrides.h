// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include <omni/core/IObject.h>
#include <omni/core/OmniAttr.h>

namespace omni
{
namespace usd
{

OMNI_DECLARE_INTERFACE(IUsdContextSchedulingOverride);

class IUsdContextSchedulingOverride_abi
    : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.usd.IUsdContextSchedulingOverride")>
{
protected:
    /**
     * Function to run before scheduling the next round of renders
     *
     * @param elapsedTime     time since the call was called last time
     * @param asyncRendering  whether async rendering was enabled
     *
     * @return whether pre render scheduling function succeeded
     */
    virtual void preScheduleRender_abi(float elapsedTime, bool asyncRendering) noexcept = 0;

    /**
     * Function to run after scheduling and before usd lock is grabbed again.
     */
    virtual void postRenderScheduledGate_abi() noexcept = 0;

    /**
     * Function to run after scheduling when main thread has usd lock again.
     */
    virtual void postRenderUsdLockAcquired_abi() noexcept = 0;

};
}
}

template <>
class omni::core::Generated<omni::usd::IUsdContextSchedulingOverride_abi>
    : public omni::usd::IUsdContextSchedulingOverride_abi
{
public:
    /**
     * Function to run before scheduling the next round of renders
     *
     * @param elapsedTime     time since the call was called last time
     * @param asyncRendering  whether async rendering was enabled
     *
     * @return whether pre render scheduling function succeeded
     */
    inline void preScheduleRender(float elapsedTime, bool asyncRendering)
    {
        preScheduleRender_abi(elapsedTime, asyncRendering);
    }

    /**
     * Function to run after scheduling and before usd lock is grabbed again.
     */
    inline void postRenderScheduledGate()
    {
        postRenderScheduledGate_abi();
    }

    /**
     * Function to run after scheduling when main thread has usd lock again.
     */
    inline void postRenderUsdLockAcquired()
    {
        postRenderUsdLockAcquired_abi();
    }
};

namespace omni
{
namespace usd
{
using UsdContextSchedulingOverridePtr = omni::core::ObjectPtr<omni::usd::IUsdContextSchedulingOverride>;
}
}
