// SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#pragma once

#include <carb/dictionary/IDictionary.h>

#include <omni/sensors/net/IChannel.h>
#include <omni/sensors/net/IServer.h>

namespace omni::sensors::net
{

OMNI_DECLARE_INTERFACE(INetworkBackend);

/**
 * An interface to a network backend that provides channel-based networking
 *
 * @note used by the INetworkFactory to create channels supported by that backend
 */
class INetworkBackend_abi : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.sensors.net.INetworkBackend")>
{
protected:
    /**
     * Get the name of the backend (to be matched to the description)
     * @return backend name
     */
    virtual const char* getName_abi() noexcept = 0;

    /**
     * Create a networking channel according to the description
     * @param description the backend-specific parameters for creating a specific channel
     * @return a channel object pointer if successful, empty/nullptr otherwise
     *
     * @note the caller owns the channel
     */
    OMNI_ATTR("no_py") virtual IChannel* makeChannel_abi(const carb::dictionary::Item* description) noexcept = 0;

    /**
     * Create a networking server according to the description
     * @param description the backend-specific parameters for creating a specific server
     * @return a server object pointer if successful, empty/nullptr otherwise
     *
     * @note the caller owns the server
     */
    OMNI_ATTR("no_py") virtual IServer* makeServer_abi(const carb::dictionary::Item* description) noexcept = 0;
};

using INetworkBackendPtr = omni::core::ObjectPtr<INetworkBackend>;

} // namespace omni::sensors::net

#include "INetworkBackend.gen.h"
