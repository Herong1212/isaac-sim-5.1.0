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

#include <omni/sensors/net/utils/ChannelUtils.h>

namespace omni::sensors::net::utils
{

// ChannelConsumerAdaptor

ChannelConsumerAdaptor::ChannelConsumerAdaptor(net::IChannelPtr channel) : m_channel{ std::move(channel) }
{
    m_channelConsumer = m_channel->addReceptionConsumer(
        [this](net::IBufferCapsule* capsule, const net::Endpoint* endpoint)
        {
            CARB_CHECK(endpoint, "endpoint should never be nullptr");

            ChannelQueueData data;

            data.capsule = omni::core::borrow(capsule);
            data.endpoint = *endpoint;

            m_queue.emplace(data);
        });
}

ChannelConsumerAdaptor::~ChannelConsumerAdaptor()
{
    m_channel->removeReceptionConsumer(m_channelConsumer);
}

bool ChannelConsumerAdaptor::send(net::IBufferCapsulePtr capsule, const Endpoint* endpoint)
{
    return m_channel->send(capsule, endpoint);
}

carb::cpp::optional<ChannelConsumerAdaptor::ChannelQueueData> ChannelConsumerAdaptor::tryPop()
{
    return m_queue.tryPop();
}


void ChannelConsumerAdaptor::consume(const ConsumerFunctionType& f)
{
    m_queue.consume([&f](const ChannelQueueData& data) { f(data.capsule, data.endpoint); });
}


// StreamAssemblerAdaptor


StreamAssemblerAdaptor::StreamAssemblerAdaptor(IChannelPtr channel, size_t headerSize)
    : m_channel{ channel }, m_headerSize{ headerSize }, m_started{ false }
{
    CARB_CHECK(headerSize > 0ULL, "header must have a size");

    m_networkFactory = omni::core::createType<net::INetworkFactory>();
}

StreamAssemblerAdaptor::~StreamAssemblerAdaptor()
{
    stop();
}

void StreamAssemblerAdaptor::setHeaderCallback(HeaderCallbackType callback)
{
    CARB_CHECK(!m_started, "already started");
    CARB_CHECK(callback, "invalid callback");

    m_headerCallback = callback;
}


void StreamAssemblerAdaptor::setBufferCallback(BufferCallbackType callback)
{
    CARB_CHECK(!m_started, "already started");
    CARB_CHECK(callback, "invalid callback");

    m_bufferCallback = callback;
}

void StreamAssemblerAdaptor::start()
{
    CARB_CHECK(!m_started, "already started");
    CARB_CHECK(m_headerCallback, "no callback set for the header");

    m_state = State::Header;
    m_headerCapsule = m_networkFactory->makeCapsule(m_headerSize);
    m_remaining = m_headerSize;
    m_currentOffset = 0;

    m_channelHandler = m_channel->addReceptionConsumer(
        [this](IBufferCapsule* capsule, Endpoint const* endPoint)
        {
            const uint8_t* capsuleBase = capsule->as<const uint8_t*>();
            size_t capsuleOffset = 0ULL;

            while (capsuleOffset != capsule->size())
            {
                const size_t toCopy = std::min(m_remaining, capsule->size() - capsuleOffset);
                m_remaining -= toCopy;

                auto currentCapsule = m_state == State::Header ? m_headerCapsule : m_bufferCapsule;
                uint8_t* currentBase = currentCapsule->as<uint8_t*>();

                ::memcpy(currentBase + m_currentOffset, capsuleBase + capsuleOffset, toCopy);

                m_currentOffset += toCopy;
                capsuleOffset += toCopy;

                if (m_remaining == 0ULL)
                {
                    m_currentOffset = 0ULL;

                    if (m_state == State::Header)
                    {
                        m_remaining = m_headerCallback(m_headerCapsule);

                        if (m_remaining > 0ULL)
                        {
                            m_state = State::Buffer;
                            m_bufferCapsule = m_networkFactory->makeCapsule(m_remaining);
                            CARB_CHECK(m_bufferCallback, "no callback set for the buffer");
                        }
                        else
                        {
                            m_state = State::Header;
                            m_headerCapsule = m_networkFactory->makeCapsule(m_headerSize);
                            m_remaining = m_headerSize;
                        }
                    }
                    else
                    {
                        m_bufferCallback(std::move(m_headerCapsule), std::move(m_bufferCapsule));

                        m_state = State::Header;
                        m_remaining = m_headerSize;

                        m_headerCapsule = m_networkFactory->makeCapsule(m_headerSize);
                    }
                }
            }
        });

    m_started = true;
}


void StreamAssemblerAdaptor::stop()
{
    if (m_started)
    {
        m_started = false;
        m_channel->removeReceptionConsumer(m_channelHandler);
    }
}

bool StreamAssemblerAdaptor::send(net::IBufferCapsulePtr capsule, const Endpoint* endpoint)
{
    return m_channel->send(capsule, endpoint);
}


} // namespace omni::sensors::net::utils
