// SPDX-FileCopyrightText: Copyright (c) 2019-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#pragma once

#include "../Framework.h"
#include "../settings/ISettings.h"
#include "../settings/SettingsUtils.h"
#include "ILogging.h"
#include "Log.h"
#include "StandardLogger.h"

namespace carb
{
namespace logging
{

/**
 * Converts a string to its equivalent OutputStream value.
 * @param[in] name The case-insensitive name of an output stream value.
 *
 * @returns This returns OutputStream::eStderr, if name is "stderr".
 * @reutrns This returns OutputStream::eDefault for any other name.
 */
inline OutputStream stringToOutputStream(const char* name)
{
    static constexpr struct
    {
        const char* name;
        OutputStream value;
    } kMappings[] = { { "stderr", OutputStream::eStderr } };

    for (size_t i = 0; i < CARB_COUNTOF(kMappings); i++)
    {
#if CARB_PLATFORM_WINDOWS
        if (_stricmp(kMappings[i].name, name) == 0)
#else
        if (strcasecmp(kMappings[i].name, name) == 0)
#endif
            return kMappings[i].value;
    }

    return OutputStream::eDefault;
}

/**
 * Configures global logging plugin with values from the config plugin values. Global logging
 * configuration specifies behavior for any loggers registered later, and doesn't dictate
 * neither how exactly any specific logger should operate, nor how the output will look like.
 *
 * Supported config fields:
 * - "level": string log level value, available options: "verbose"|"info"|"warning"|"error"|"fatal"
 * - "enabled": boolean value, enable or disable logging
 *
 * These values could be specified either per-source, in the source collection ("/log/sources/"),
 * for example, <source> level should be specified as "/log/sources/<source>/level", or globally,
 * as "/log/level". Similar pattern applies to "enabled" property.
 */
inline void configureLogging(settings::ISettings* settings)
{
    Framework* f = getFramework();
    logging::ILogging* logging = f->acquireInterface<logging::ILogging>();

    if (settings == nullptr)
        return;

    if (logging)
    {
        const char* kLogLevel = "/log/level";
        const char* kLogEnabled = "/log/enabled";
        const char* kLogAsync = "/log/async";

        auto* dictInterface = f->tryAcquireInterface<carb::dictionary::IDictionary>();

        // setting defaults
        settings->setDefaultString(kLogLevel, "Warning");
        settings->setDefaultBool(kLogEnabled, true);
        settings->setDefaultBool(kLogAsync, false);

        // thread safety for the getStringBuffer() and getSettingsDictionary() calls
        carb::settings::ScopedRead lock;

        // The first order of business is to set logging according to config (this can be from file or command line):
        const int32_t logLevel = logging::stringToLevel(settings->getStringBuffer(kLogLevel));
        logging->setLevelThreshold(logLevel);

        const bool logEnabled = settings->getAsBool(kLogEnabled);
        logging->setLogEnabled(logEnabled);

        logging->setLogAsync(settings->getAsBool(kLogAsync));

        // Read config for source-specific setting overrides

        // First, read the sources collection
        const char* kLogSourcesKey = "/log/sources";

        const carb::dictionary::Item* logSources = settings->getSettingsDictionary(kLogSourcesKey);

        if (logSources != nullptr && dictInterface != nullptr)
        {
            // Traverse the sources collection to set per-source overrides
            for (size_t i = 0, totalChildren = dictInterface->getItemChildCount(logSources); i < totalChildren; ++i)
            {
                const carb::dictionary::Item* curSource = dictInterface->getItemChildByIndex(logSources, i);
                if (curSource == nullptr)
                {
                    CARB_LOG_ERROR("Null log source present in the configuration.");
                    continue;
                }

                const char* curSourceName = dictInterface->getItemName(curSource);
                if (curSourceName == nullptr)
                {
                    CARB_LOG_ERROR("Log source with no name present in the configuration.");
                    continue;
                }

                // Read the source level setting
                const carb::dictionary::Item* curLogLevel = dictInterface->getItem(curSource, "level");
                if (curLogLevel != nullptr)
                {
                    logging->setLevelThresholdForSource(
                        curSourceName, logging::LogSettingBehavior::eOverride,
                        logging::stringToLevel(dictInterface->getStringBuffer(curLogLevel)));
                }

                // Read the source enabled setting
                const carb::dictionary::Item* curLogEnabled = dictInterface->getItem(curSource, "enabled");
                if (curLogEnabled != nullptr)
                {
                    const bool isCurLogEnabled =
                        dictInterface->isAccessibleAs(dictionary::ItemType::eBool, curLogEnabled) ?
                            dictInterface->getAsBool(curLogEnabled) :
                            logEnabled;
                    logging->setLogEnabledForSource(
                        curSourceName, logging::LogSettingBehavior::eOverride, isCurLogEnabled);
                }
            }
        }

#if CARB_VERSION_ATLEAST(carb_logging_ILogging, 1, 4)
        const char* kLogExtraFieldsKey = "/log/extraFields";

        // next check if there are any extra fields that need to be added to log messages.
        // Note that this only makes sense to add a set of global extra fields from this
        // setting.
        const carb::dictionary::Item* extraFields = settings->getSettingsDictionary(kLogExtraFieldsKey);

        if (extraFields != nullptr && dictInterface != nullptr)
        {
            carb::settings::ScopedRead readLock;

            // walk the item's children and add extra fields for each one.
            for (size_t i = 0, totalChildren = dictInterface->getItemChildCount(extraFields); i < totalChildren; i++)
            {
                // get the next extra field entry in the branch.
                const carb::dictionary::Item* item = dictInterface->getItemChildByIndex(extraFields, i);
                if (item == nullptr)
                {
                    CARB_LOG_ERROR("Null extra field present in the configuration.");
                    continue;
                }

                // get the item's name to use as the extra field's key name.
                const char* name = dictInterface->getItemName(item);
                if (name == nullptr)
                {
                    CARB_LOG_ERROR("extra field with no name present in the configuration.");
                    continue;
                }

                const char* value = dictInterface->getStringBuffer(item);
                if (value == nullptr)
                {
                    CARB_LOG_WARN("extra field '%s' does not have a value.", name);
                    continue;
                }

                logging->addExtraField(name, value, fExtraFieldFlagGlobal);
            }
        }
#endif
    }
}

// example-begin Configure StandardLogger
/**
 * Configures default logger with values from the config plugin values. Default logger configuration
 * specifies where to output the log stream and how the output will look.
 *
 * Further instructions on the meaning of fields is available from StandardLogger.h
 */
inline void configureDefaultLogger(settings::ISettings* settings)
{
    Framework* f = getFramework();
    logging::ILogging* logging = f->acquireInterface<logging::ILogging>();

    if (settings == nullptr)
        return;

    if (logging)
    {
        // Config settings for default logger
        auto* logger = logging->getDefaultLogger();

        // setting defaults

        const char* kFilePath = "/log/file";
        const char* kFileFlushLevelPath = "/log/fileFlushLevel";
        const char* kFlushStandardStreamOutputPath = "/log/flushStandardStreamOutput";
        const char* kEnableStandardStreamOutputPath = "/log/enableStandardStreamOutput";
        const char* kEnableDebugConsoleOutputPath = "/log/enableDebugConsoleOutput";
        const char* kEnableColorOutputPath = "/log/enableColorOutput";
        const char* kProcessGroupIdPath = "/log/processGroupId";
        const char* kIncludeSourcePath = "/log/includeSource";
        const char* kIncludeChannelPath = "/log/includeChannel";
        const char* kIncludeFilenamePath = "/log/includeFilename";
        const char* kIncludeLineNumberPath = "/log/includeLineNumber";
        const char* kIncludeFunctionNamePath = "/log/includeFunctionName";
        const char* kIncludeTimeStampPath = "/log/includeTimeStamp";
        const char* kIncludeThreadIdPath = "/log/includeThreadId";
        const char* kSetElapsedTimeUnitsPath = "/log/setElapsedTimeUnits";
        const char* kIncludeProcessIdPath = "/log/includeProcessId";
        const char* kIncludeTraceIdPath = "/log/includeTraceId";
        const char* kLogOutputStream = "/log/outputStream";
        const char* kOutputStreamLevelThreshold = "/log/outputStreamLevel";
        const char* kDebugConsoleLevelThreshold = "/log/debugConsoleLevel";
        const char* kFileOutputLevelThreshold = "/log/fileLogLevel";
        const char* kDetailLogPath = "/log/detail";
        const char* kFullDetailLogPath = "/log/fullDetail";
        const char* kFileAppend = "/log/fileAppend";
        const char* kForceAnsiColor = "/log/forceAnsiColor";

        settings->setDefaultString(kFileFlushLevelPath, "verbose");
        settings->setDefaultBool(kFlushStandardStreamOutputPath, false);

        settings->setDefaultBool(kEnableStandardStreamOutputPath, true);
        settings->setDefaultBool(kEnableDebugConsoleOutputPath, true);
        settings->setDefaultBool(kEnableColorOutputPath, true);
        settings->setDefaultInt(kProcessGroupIdPath, 0);

        settings->setDefaultBool(kIncludeSourcePath, true);
        settings->setDefaultBool(kIncludeChannelPath, true);
        settings->setDefaultBool(kIncludeFilenamePath, false);
        settings->setDefaultBool(kIncludeLineNumberPath, false);
        settings->setDefaultBool(kIncludeFunctionNamePath, false);
        settings->setDefaultBool(kIncludeTimeStampPath, false);
        settings->setDefaultBool(kIncludeThreadIdPath, false);
        settings->setDefaultBool(kIncludeProcessIdPath, false);
        settings->setDefaultBool(kIncludeTraceIdPath, false);
        settings->setDefaultBool(kDetailLogPath, false);
        settings->setDefaultBool(kFullDetailLogPath, false);
        settings->setDefaultBool(kForceAnsiColor, false);

        settings->setDefaultString(kOutputStreamLevelThreshold, "verbose");
        settings->setDefaultString(kDebugConsoleLevelThreshold, "verbose");
        settings->setDefaultString(kFileOutputLevelThreshold, "verbose");

#if CARB_VERSION_ATLEAST(carb_logging_ILogging, 1, 1)
#    define CARBLOCAL_LOGGER
#else
#    define CARBLOCAL_LOGGER logger,
#endif

        // lock settings to access strings safely
        settings::ScopedRead readLock;

        // getting values from the settings
        logger->setStandardStreamOutput(CARBLOCAL_LOGGER settings->getAsBool(kEnableStandardStreamOutputPath));
        logger->setDebugConsoleOutput(CARBLOCAL_LOGGER settings->getAsBool(kEnableDebugConsoleOutputPath));

        LogFileConfiguration config{};
        settings->setDefaultBool(kFileAppend, config.append);
        config.append = settings->getAsBool(kFileAppend);

        logger->setFileConfiguration(CARBLOCAL_LOGGER settings->getStringBuffer(kFilePath), &config);
        logger->setFileOuputFlushLevel(
            CARBLOCAL_LOGGER logging::stringToLevel(settings->getStringBuffer(kFileFlushLevelPath)));
        logger->setFlushStandardStreamOutput(CARBLOCAL_LOGGER settings->getAsBool(kFlushStandardStreamOutputPath));

        logger->setForceAnsiColor(CARBLOCAL_LOGGER settings->getAsBool(kForceAnsiColor));
        logger->setColorOutputIncluded(CARBLOCAL_LOGGER settings->getAsBool(kEnableColorOutputPath));
        logger->setMultiProcessGroupId(CARBLOCAL_LOGGER settings->getAsInt(kProcessGroupIdPath));

        bool channel = settings->getAsBool(kIncludeSourcePath) && settings->getAsBool(kIncludeChannelPath);

        // if this is set, it enabled everything
        bool fullDetail = settings->getAsBool(kFullDetailLogPath);

        // if this is set, it enables everything except file name and PID
        bool detail = fullDetail || settings->getAsBool(kDetailLogPath);
        logger->setSourceIncluded(CARBLOCAL_LOGGER detail || channel);
        logger->setFilenameIncluded(CARBLOCAL_LOGGER fullDetail || settings->getAsBool(kIncludeFilenamePath));
        logger->setLineNumberIncluded(CARBLOCAL_LOGGER detail || settings->getAsBool(kIncludeLineNumberPath));
        logger->setFunctionNameIncluded(CARBLOCAL_LOGGER detail || settings->getAsBool(kIncludeFunctionNamePath));
        logger->setTimestampIncluded(CARBLOCAL_LOGGER detail || settings->getAsBool(kIncludeTimeStampPath));
        logger->setThreadIdIncluded(CARBLOCAL_LOGGER detail || settings->getAsBool(kIncludeThreadIdPath));
        logger->setElapsedTimeUnits(CARBLOCAL_LOGGER settings->getStringBuffer(kSetElapsedTimeUnitsPath));
        logger->setProcessIdIncluded(CARBLOCAL_LOGGER fullDetail || settings->getAsBool(kIncludeProcessIdPath));

#if CARB_VERSION_ATLEAST(carb_logging_ILogging, 1, 3)
        bool includeTraceparentId = settings->getAsBool(kIncludeTraceIdPath);

        includeTraceparentId = includeTraceparentId || fullDetail;
        logger->setTraceIdIncluded(CARBLOCAL_LOGGER includeTraceparentId);

        // the traceparent ID is being included in the log messages => make sure the thread ID is
        //   also being printed so that there is a way to differentiate log messages from
        //   different threads.
        if (includeTraceparentId)
        {
            logger->setThreadIdIncluded(true);
        }
#endif

#if CARB_VERSION_ATLEAST(carb_logging_ILogging, 1, 5)
        const char* kUtcTimestampsPath = "/log/utcTimestamp";
        const char* kMicrosecondTimestampsPath = "/log/microsecondTimestamp";

        settings->setDefaultBool(kUtcTimestampsPath, true);
        settings->setDefaultBool(kMicrosecondTimestampsPath, false);

        logger->setUtcTimestamps(CARBLOCAL_LOGGER settings->getAsBool(kUtcTimestampsPath));
        logger->setMicrosecondTimestamp(CARBLOCAL_LOGGER settings->getAsBool(kMicrosecondTimestampsPath));
#endif

        if (auto buffer = settings->getStringBuffer(kLogOutputStream))
        {
            logger->setOutputStream(CARBLOCAL_LOGGER stringToOutputStream(buffer));
        }

        logger->setStandardStreamOutputLevelThreshold(
            CARBLOCAL_LOGGER logging::stringToLevel(settings->getStringBuffer(kOutputStreamLevelThreshold)));
        logger->setDebugConsoleOutputLevelThreshold(
            CARBLOCAL_LOGGER logging::stringToLevel(settings->getStringBuffer(kDebugConsoleLevelThreshold)));
        logger->setFileOutputLevelThreshold(
            CARBLOCAL_LOGGER logging::stringToLevel(settings->getStringBuffer(kFileOutputLevelThreshold)));
    }

#undef CARBLOCAL_LOGGER
}
// example-end
} // namespace logging
} // namespace carb
