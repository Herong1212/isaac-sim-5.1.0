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

#include <carb/InterfaceUtils.h>
#include <carb/container/LocklessQueue.h>
#include <carb/container/LocklessStack.h>
#include <carb/cpp/Optional.h>
#include <carb/logging/Log.h>

#include <omni/core/ITypeFactory.h>
#include <omni/sensors/net/IChannel.h>
#include <omni/sensors/net/INetworkFactory.h>
#include <omni/sensors/net/utils/LocklessQueueNI.h>

#include <functional>

namespace omni::sensors::net::utils
{

/**
 * A utility that facilitates queued reception from channels
 */
class ChannelConsumerAdaptor
{
public:
    struct ChannelQueueData
    {
        net::IBufferCapsulePtr capsule;
        net::Endpoint endpoint;
    };

    /**
     * Constructor
     * @param channel the channel to adapt
     */
    inline ChannelConsumerAdaptor(net::IChannelPtr channel);

    inline ~ChannelConsumerAdaptor();

    /**
     * Send a capsule on the wrapped channel. See @ref net::IChannel::send
     */
    inline bool send(net::IBufferCapsulePtr capsule, const Endpoint* endpoint);

    /**
     * Try popping an element from the receive queue
     * @returns an optional with value ChannelQueueData if there's something to pop, nullopt otherwise
     */
    inline carb::cpp::optional<ChannelQueueData> tryPop();

    using ConsumerFunctionType = std::function<void(net::IBufferCapsulePtr, const net::Endpoint&)>;

    /**
     * Consume all elements in the consumer queue, while applying function f to every element
     * @param f function-like object to apply to every element before it's destroyed
     */
    inline void consume(const ConsumerFunctionType& f);


private:
    net::IChannelPtr m_channel;
    omni::core::ObjectPtr<net::IReceptionConsumer> m_channelConsumer;

    utils::LocklessQueueNI<ChannelQueueData> m_queue;
};


/**
 * A utility that facilitates reception from streaming (eg. TCP) channels
 */
class StreamAssemblerAdaptor final
{
public:
    // (header buffer) -> expected payload size
    using HeaderCallbackType = std::function<size_t(IBufferCapsulePtr)>;

    // (header buffer, payload buffer) -> void
    using BufferCallbackType = std::function<void(IBufferCapsulePtr, IBufferCapsulePtr)>;


    /**
     * Constructor
     * @param channel the streaming channel that we will be receiving from
     * @param headerSize size of the header of every received frame
     * @note the header can be the only thing that is received (eg. in the case of known static size frames)
     */
    inline StreamAssemblerAdaptor(IChannelPtr channel, size_t headerSize);

    inline ~StreamAssemblerAdaptor();

    /**
     * Set a func that is called when the header is received
     * @param callback a function that will be called to process the header and calculate expected buffer size to follow
     * @note callback returns the size of the expected buffer size to follow or 0 if a new header is expected
     * @note this callback can also be used to verify a magic number if applicable
     */
    inline void setHeaderCallback(HeaderCallbackType callback);

    /**
     * Set a func that is called when the expected buffer (payload) is received
     * @param callback a function that will be called to process the header and full assembled buffer (payload)
     * @note the callback owns the buffer capsules
     * @note the callback is optional in case the header callback always returns 0 (static frame sizes)
     */
    inline void setBufferCallback(BufferCallbackType callback);

    /**
     * Start the reception/assembly chain
     */
    inline void start();

    /**
     * Stop the reception/assembly chain
     * @note callbacks will not be called *after* this function returns
     */
    inline void stop();

    /**
     * Send a capsule on the wrapped channel. See @ref net::IChannel::send
     */
    inline bool send(net::IBufferCapsulePtr capsule, const Endpoint* endpoint);

private:
    IChannelPtr m_channel;
    omni::core::ObjectPtr<IReceptionConsumer> m_channelHandler;
    omni::core::ObjectPtr<INetworkFactory> m_networkFactory;

    const size_t m_headerSize;
    size_t m_remaining;
    size_t m_currentOffset;

    HeaderCallbackType m_headerCallback;
    BufferCallbackType m_bufferCallback;

    bool m_started;

    IBufferCapsulePtr m_headerCapsule;
    IBufferCapsulePtr m_bufferCapsule;

    enum class State : uint8_t
    {
        Header,
        Buffer
    } m_state;
};


} // namespace omni::sensors::net::utils

#include <omni/sensors/net/utils/ChannelUtilsImpl.inl>
