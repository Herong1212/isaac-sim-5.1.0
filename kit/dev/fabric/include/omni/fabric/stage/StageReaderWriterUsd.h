// Copyright (c) 2020-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/fabric/stage/StageReaderWriter.h>

#include <pxr/base/tf/token.h>
#include <pxr/usd/sdf/path.h>


namespace omni
{
namespace fabric
{

class StageReaderWriterUsd : StageReaderWriter
{
public:
    /**
     * @brief Register a token with the ObjectDirectory, which will store a counted ref which is released at destruction
     * @return the TokenC for the TfToken, for storage in Fabric attribute memory
     */
    static TokenC registerToken(const StageReaderWriter& stage, const PXR_NS::TfToken& token);

    /**
     * @brief Register tokens with the ObjectDirectory, which will store a counted ref which is released at destruction
     */
    static void registerTokens(const StageReaderWriter& stage, const gsl::span<const PXR_NS::TfToken>& tokens);

    /**
     * @brief Register a path with the ObjectDirectory, which will store a counted ref which is released at destruction
     * @return the PathC for the SdfPath, for storage in Fabric attribute memory
     */
    static PathC registerPath(const StageReaderWriter& stage, const PXR_NS::SdfPath& path);

    /**
     * @brief Register paths with the ObjectDirectory, which will store a counted ref which is released at destruction
     */
    static void registerPaths(const StageReaderWriter& stage, const gsl::span<const PXR_NS::SdfPath>& paths);
    };

} // namespace fabric
} // namespace omni

#include <omni/fabric/stage/impl/StageReaderWriterUsd.inl>
