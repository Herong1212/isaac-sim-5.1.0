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
#include <omni/sensors/net/IBufferCapsule.h>

#include <utility>

namespace omni::sensors::net
{

OMNI_DECLARE_INTERFACE(IChannel);
OMNI_DECLARE_INTERFACE(IReceptionConsumer);

enum class EndpointType : uint16_t
{
    eNone,
    //! A custom endpoint, each protocol defines what this means.
    eCustom,
    //! A CAN endpoint.
    eCan,
    //! An IPv4 address
    eIp,
    //! A realm endpoint
    eRealm,
};

struct IP4Endpoint
{
    OMNI_ATTR("no_py") char addr[16];
    uint16_t port;
};
using CANFrameID = uint32_t;
using CustomEndpoint = uint8_t[16];

struct RealmEndpoint
{
    int64_t frameId;
};

struct Endpoint
{
    int64_t egressTimestamp;
    EndpointType type;
    union
    {
        IP4Endpoint ip;
        CANFrameID can;
        OMNI_ATTR("no_py") CustomEndpoint custom;
        OMNI_ATTR("no_py") RealmEndpoint realm;
    };
};

class IReceptionConsumer_abi
    : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.sensors.net.IReceptionConsumer")>
{
protected:
    OMNI_ATTR("no_py")
    virtual void onReceive_abi(IBufferCapsule* bufferCapsule,
                               OMNI_ATTR("in, not_null") Endpoint const* endPoint) noexcept = 0;
};

/**
 * Channel interface for sending/receiving data over different kinds of networks
 *
 * @note Create a channel according to a description using the network factory. See @ref INetworkFactory
 */
class IChannel_abi : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.sensors.net.IChannel")>
{
protected:
    /**
     * Check if the channel is connected/ready for sending and receiving
     * @return true if the channel is connected/ready
     * @note call this before sending or to check if a connection is dead to release the channel
     */
    virtual bool isConnected_abi() noexcept = 0;

    /**
     * Send the inBuffer on the channel according to the channel implementation
     * @param inBuffer the buffer capsule that has the buffer to be sent
     * @param endpoint the sender address/id or (default) eNone if the destination is configured
     * @return true if the operation is successful, false otherwise
     */
    OMNI_ATTR("no_py")
    virtual bool send_abi(IBufferCapsule* inBuffer, OMNI_ATTR("in") Endpoint const* destination) noexcept = 0;

    /**
     * Register a consumer that will be called when data is received on the channel
     * @param consumer The consumer class to be used when making a callback. See @ref IChannel::IReceptionConsumer
     */

    virtual OMNI_ATTR("no_py, consumer=onReceive_abi") void addReceptionConsumer_abi(
        OMNI_ATTR("not_null") IReceptionConsumer* consumer) noexcept = 0;

    /**
     * Unregister a previously registered consumer
     * @param consumer The previously registered consumer on this channel
     */
    virtual void removeReceptionConsumer_abi(IReceptionConsumer* consumer) noexcept = 0;
};

using IChannelPtr = omni::core::ObjectPtr<IChannel>;
using IReceptionConsumerPtr = omni::core::ObjectPtr<IReceptionConsumer>;

} // namespace omni::sensors::net

#include "IChannel.gen.h"

OMNI_DEFINE_INTERFACE_API(omni::sensors::net::IChannel)
#ifdef CLANG_FORMAT /* Fix clang format bug. */
class omni::sensors::net::IChannel
#endif
{
public:
    bool send(omni::core::ObjectParam<omni::sensors::net::IBufferCapsule> inBuffer) noexcept
    {
        omni::sensors::net::Endpoint dummy{};
        return send_abi(inBuffer.get(), &dummy);
    }
    bool send(omni::core::ObjectParam<omni::sensors::net::IBufferCapsule> inBuffer, omni::sensors::net::Endpoint const* destination) noexcept
    {
        return send_abi(inBuffer.get(), destination);
    }
    bool send(omni::core::ObjectParam<omni::sensors::net::IBufferCapsule> inBuffer, omni::sensors::net::Endpoint const& destination) noexcept
    {
        return send_abi(inBuffer.get(), &destination);
    }
};
