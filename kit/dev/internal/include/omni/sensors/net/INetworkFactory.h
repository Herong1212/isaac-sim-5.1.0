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
#include <omni/sensors/net/INetworkBackend.h>
#include <omni/sensors/net/IServer.h>

namespace omni::sensors::net
{

OMNI_DECLARE_INTERFACE(INetworkFactory);

class INetworkFactory_abi : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.sensors.net.INetworkFactory")>
{
protected:
    /**
     * Create a buffer capsule for use with net::IChannel
     * @param size capsule length in bytes
     * @return a buffer capsule that is (at least) the requested bytes
     *
     * @note the caller owns the server
     */
    OMNI_ATTR("no_py") virtual IBufferCapsule* makeCapsule_abi(size_t size) noexcept = 0;

    /**
     * Create a networking channel using the backend selected in the description
     * @param description a dictionary that has a "backend" param naming the backend that will
     * create and service the channel along with a list of backend-specific parameters
     * @return a channel object pointer if successful, empty/nullptr otherwise
     *
     * @note the caller owns the channel
     */
    OMNI_ATTR("no_py") virtual IChannel* makeChannel_abi(const carb::dictionary::Item* description) noexcept = 0;

    /**
     * Create a networking server using the backend selected in the description
     * @param description a dictionary that has a "backend" param naming the backend that will
     * create and service the server along with a list of backend-specific parameters
     * @return a server object pointer if successful, empty/nullptr otherwise
     *
     * @note the caller owns the server
     */
    OMNI_ATTR("no_py") virtual IServer* makeServer_abi(const carb::dictionary::Item* description) noexcept = 0;

    /**
     * Get the backend associated with the @ref description
     * @param description A description of the backend to get.
     * @returns The backend, if it exists, nullptr otherwise.
     *
     * @note This function is useful when needed to access the backend directly, for example it may expose additional
     * interfaces.
     */
    OMNI_ATTR("no_py") virtual INetworkBackend* getBackend_abi(const carb::dictionary::Item* description) noexcept = 0;
};

using INetworkFactoryPtr = omni::core::ObjectPtr<INetworkFactory>;

} // namespace omni::sensors::net

#include "INetworkFactory.gen.h"

OMNI_DEFINE_INTERFACE_API(omni::sensors::net::INetworkFactory)
#ifdef CLANG_FORMAT /* Fix clang format bug. */
class omni::sensors::net::INetworkFactory
#endif
{
public:
    using omni::core::Generated<omni::sensors::net::INetworkFactory_abi>::makeCapsule;

    template <typename T>
    static constexpr bool kIsOverAligned = (alignof(T) > alignof(std::max_align_t));

    /**
     * Makes a capsule that fits a type T
     * @tparam T type
     * @return a buffer capsule owning a buffer big enough for T
     */
    template <typename T>
    omni::sensors::net::IBufferCapsulePtr makeCapsule()
    {
        static_assert(!kIsOverAligned<T>, "cannot make capsules for over-aligned structures");

        return makeCapsule(sizeof(T));
    }

    /**
     * Makes a capsule that fits a type T, and fills it.
     *
     * This function uses emplace sematics.
     *
     * @tparam T The type to construct into the capsule.
     * @tparam Args the type of the arguments to pass in.
     * @param args The arguments to forward to the constructor.
     * @return a buffer capsule containing the data.
     */
    template <typename T, typename... Args>
    omni::sensors::net::IBufferCapsulePtr emplaceCapsule(Args&&... args)
    {
        static_assert(!kIsOverAligned<T>, "cannot emplace capsules for over-aligned structures");
        static_assert(
            std::is_trivially_destructible_v<T>, "cannot emplace capsules for non-trivially destructable types");

        auto capsule = makeCapsule(sizeof(T));

        // NOTE: MHAIBA - fall back to uniform initialization
        // when there's no direct constructor. This is handy with PODs
        if constexpr (std::is_constructible_v<T, Args...>)
            new (capsule->data()) T(std::forward<Args>(args)...);
        else
            new (capsule->data()) T{ std::forward<Args>(args)... };

        return capsule;
    }
};
