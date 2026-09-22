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
#include <carb/dictionary/IDictionary.h>

#include <omni/core/IObject.h>
#include <omni/sensors/net/IChannel.h>
#include <omni/sensors/net/IServer.h>

namespace omni
{
namespace sensors
{
namespace net
{

constexpr char kInterfaceName_INetworkDecorator[] = "omni.sensors.net.INetworkDecorator";
constexpr char kPluginName_NetworkDataRecorder[] = "omni.sensors.net.INetworkDecorator-datarecorder";
constexpr char kSettingPathNetworkDecorators[] = "/exts/omni.sensors.net/decorators";

// added for backward compatibility, will be removed in future releases
constexpr char kSettingPathNetworkDecorators_Deprecated[] = "/exts/omni.drivesim.net/decorators";

OMNI_DECLARE_INTERFACE(INetworkDecorator);

using INetworkDecoratorPtr = omni::core::ObjectPtr<INetworkDecorator>;

/**
 * An interface to a network channel and server decorator factory.
 */
class INetworkDecorator_abi
    : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID(kInterfaceName_INetworkDecorator)>
{
protected:
    /**
     * Create a network channel decorator
     *
     * @note If a decorator is created, it will manage the channel.
     *
     * @param channelDesc network channel description as defined in INetworkFactory.
     * @param channel the network channel to be decorated.
     * @return a decorated channel if successful, the original channel otherwise.
     */
    OMNI_ATTR("no_py")
    virtual IChannel* decorateChannel_abi(OMNI_ATTR("not_null") const carb::dictionary::Item* channelDesc,
                                          OMNI_ATTR("not_null") IChannel* channel) noexcept = 0;

    /**
     * Create a network server decorator
     *
     * @note If a decorator is created, it will manage the server.
     *
     * @param serverDesc network server description as defined in INetworkFactory.
     * @param server the network server to be decorated.
     * @return a decorated server if successful, the original server otherwise.
     */
    OMNI_ATTR("no_py")
    virtual IServer* decorateServer_abi(OMNI_ATTR("not_null") const carb::dictionary::Item* serverDesc,
                                        OMNI_ATTR("not_null") IServer* server) noexcept = 0;
};

using INetworkDecoratorPtr = omni::core::ObjectPtr<INetworkDecorator>;

/**
 * Creates an instance of the native recorder.
 * @return the native recorder instance
 */
inline omni::core::ObjectPtr<INetworkDecorator> createNativeRecorder()
{
    return omni::core::createType<INetworkDecorator>(omni::core::typeId(kPluginName_NetworkDataRecorder));
}

} // namespace net
} // namespace sensors
} // namespace omni

#include "INetworkDecorator.gen.h"
