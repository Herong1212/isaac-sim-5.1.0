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

#include <omni/core/IObject.h>
#include <omni/core/Types.h>
#include <omni/sensors/net/IBufferCapsule.h>

namespace omni
{
namespace sensors
{
namespace net
{
OMNI_DECLARE_INTERFACE(IRealmBackend);

/**
 * REALM backend interface, allowing for the creation of buffer capsules managed by REALM.
 */
class IRealmBackend_abi : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.sensors.net.IRealmBackend")>
{
protected:
    /**
     * Create a Host buffer capsule for use with net::RealmChannel
     * @param size capsule length in bytes
     * @return a buffer capsule that is (at least) the requested bytes
     *
     */
    OMNI_ATTR("no_py") virtual IBufferCapsule* makeHostCapsule_abi(size_t size) noexcept = 0;

    /**
     * Create a CUDA buffer capsule for use with net::RealmChannel
     * @param size capsule length in bytes
     * @return a buffer capsule that is (at least) the requested bytes
     *
     */
    OMNI_ATTR("no_py") virtual IBufferCapsule* makeCUDACapsule_abi(size_t size, uint32_t cudaDeviceIdx) noexcept = 0;
};

using IRealmBackendPtr = omni::core::ObjectPtr<IRealmBackend>;


} // namespace net
} // namespace sensors
} // namespace omni

#include "IRealmBackend.gen.h"
