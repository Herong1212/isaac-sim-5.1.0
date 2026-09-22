// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Framework.h>
#include <carb/datasource/DataSourceUtils.h>
#include <carb/datasource/IDataSource.h>
#include <carb/filesystem/IFileSystem.h>
#include <carb/logging/Log.h>

#include <vector>

namespace omni
{
namespace kit
{

/** Obtain a list of datasources for the local file system.
 *  @returns A vector of the local filesystem connections.
 *           This vector contains pairs where the first member is the first
 *           character of the filesystem name (on windows, this is the upper
 *           case DOS drive label; on Linux, this is '/') and the second member
 *           is the connection to that filesystem.
 *           None of the connections in the returned vector will be nullptr.
 *
 *  @remarks This function is used to workaround a limitation with the datasource
 *           system that prevents DOS paths from being used, so each separate DOS
 *           drive needs to be registered as a separate connection.
 *           This function will be removed eventually when this deficiency is fixed.
 */
inline std::vector<std::pair<char, carb::datasource::Connection*>> getFilesystemConnections()
{
    carb::filesystem::IFileSystem* fs = carb::getFramework()->acquireInterface<carb::filesystem::IFileSystem>();
    carb::datasource::IDataSource* dataSource =
        carb::getFramework()->acquireInterface<carb::datasource::IDataSource>("carb.datasource-omniclient.plugin");
    std::vector<std::pair<char, carb::datasource::Connection*>> vec;

    if (fs == nullptr || dataSource == nullptr)
        return vec;

#if CARB_PLATFORM_WINDOWS

    for (char drive = 'A'; drive <= 'Z'; drive++)
    {
        std::string drivePath = std::string(1, drive) + ":";
        if (fs->exists(drivePath.c_str()))
        {
            carb::datasource::Connection* connection =
                carb::datasource::connectAndWait(carb::datasource::ConnectionDesc{ drivePath.c_str() }, dataSource);
            if (connection == nullptr)
            {
                CARB_LOG_ERROR("failed to get connection for drive %c", drive);
                continue;
            }

            vec.push_back(std::make_pair(drive, connection));
        }
    }

#else
    // Just add the root of the filesystem
    carb::datasource::Connection* connection =
        carb::datasource::connectAndWait(carb::datasource::ConnectionDesc{ "/" }, dataSource);
    if (connection == nullptr)
        CARB_LOG_ERROR("failed to get connection for the filesystem root");
    else
        vec.push_back(std::make_pair('/', connection));
#endif

    return vec;
}
}
}
