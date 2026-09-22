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

#include <omni/core/IObject.h>
#include <omni/core/Types.h>
#include <omni/sensors/net/IChannel.h>

#include <utility>

namespace omni::sensors::net
{

OMNI_DECLARE_INTERFACE(IServer);
OMNI_DECLARE_INTERFACE(IConnectionConsumer);

class IConnectionConsumer_abi
    : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.sensors.net.IConnectionConsumer")>
{
protected:
    virtual OMNI_ATTR("no_py") void onConnect_abi(IChannel* channel,
                                                  OMNI_ATTR("in") Endpoint const* endPoint) noexcept = 0;
};

/**
 * Server interface for connection-based channels (eg. TCP and WebSocket servers)
 *
 * @note Create a server according to a description using the network factory. See @ref INetworkFactory
 */
class IServer_abi : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.sensors.net.IServer")>
{
protected:
    /**
     * Register a consumer that will be called when a new client connects to the server
     * @param consumer The consumer class to be used when making a callback. See @ref IChannel::IReceptionConsumer
     */
    virtual OMNI_ATTR("consumer=onConnect_abi") void addConnectionConsumer_abi(
        OMNI_ATTR("not_null") IConnectionConsumer* consumer) noexcept = 0;

    /**
     * Unregisters a previously registered handler
     * @param id handler id of a handler previously registered on this server
     */
    virtual void removeConnectionConsumer_abi(IConnectionConsumer* consumer) noexcept = 0;
};

using IServerPtr = omni::core::ObjectPtr<IServer>;
using IConnectionConsumerPtr = omni::core::ObjectPtr<IConnectionConsumer>;

} // namespace omni::sensors::net

#include "IServer.gen.h"
