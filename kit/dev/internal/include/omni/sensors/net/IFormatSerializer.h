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
#include <omni/sensors/net/IBufferCapsule.h>
#include <omni/sensors/net/IChannel.h>


namespace omni
{
namespace sensors
{
namespace net
{

OMNI_DECLARE_INTERFACE(IFormatSerializer);

using IFormatSerializerPtr = omni::core::ObjectPtr<IFormatSerializer>;

/**
 * An interface to a format serializer that serializes sensor network messages.
 */
class IFormatSerializer_abi : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.sensors.net.IFormatSerializer")>
{
protected:
    /**
     * Serialize network message.
     * @param capsule buffer containing network message payload.
     * @param endpoint network message endpoint information.
     */
    OMNI_ATTR("no_py")
    virtual void serialize_abi(OMNI_ATTR("not_null") IBufferCapsule* capsule,
                               OMNI_ATTR("in, not_null") const Endpoint* endpoint) noexcept = 0;
};


OMNI_DECLARE_INTERFACE(IFormatSerializerFactory);

using IFormatSerializerFactoryPtr = omni::core::ObjectPtr<IFormatSerializerFactory>;

/**
 * An interface to a format serializer factory.
 */
class IFormatSerializerFactory_abi
    : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.sensors.net.IFormatSerializerFactory")>
{
protected:
    /**
     * Create a format serializer according to description
     * @param channelDescription network channel description as defined in INetworkFactory.
     * @param outputPath A file or directory path (depending on implementation) in which to write the serialized data.
     * Parent dirs can be assumed to exist by the implementation.
     * @return a serializer object, if successful, nullptr otherwise.
     */
    OMNI_ATTR("no_py")
    virtual IFormatSerializer* makeSerializer_abi(OMNI_ATTR("not_null") const carb::dictionary::Item* channelDescription,
                                                  OMNI_ATTR("in, not_null") const char* outputPath) noexcept = 0;
};

} // namespace net
} // namespace sensors
} // namespace omni

#include "IFormatSerializer.gen.h"
