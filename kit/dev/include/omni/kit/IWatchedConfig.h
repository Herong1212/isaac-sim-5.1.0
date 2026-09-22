// Copyright (c) 2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/InterfaceUtils.h>


namespace omni
{
namespace kit
{

/** Setting path to enable the watched settings file and provide its path.  This is expected to
 *  be a string setting that contains the relative or absolute path to the settings file to
 *  monitor for changes.  When a relative path is used, it is assumed to be relative to the
 *  process' current working directory at the time this setting is processed.  The file does
 *  not need to exist when enabled, but the directory it is named in must exist.  If the file
 *  is created or modified at a later time, it will be loaded and merged into the settings
 *  registry for the active process.  The filename must have either a '.json' or '.toml' file
 *  extension so it can be determined how to load it.  If the @ref kWatchedConfigDurationSetting
 *  setting also specifies a positive non-zero value, the newly loaded settings will automatically
 *  be restored to their original values once the given duration expires.  If no duration is
 *  specified or it is zero or negative, the settings changes will persist for the remainder
 *  of the process' lifetime.  If this filename points to a path that already exists as a
 *  directory or the directory containing the named file does not exist, this setting will
 *  be ignored.  This defaults to an empty string (ie: disabled).
 *
 *  @note It is suggested that this named file be located in a directory that is seldomly
 *        modified or contains few files.  Having it be in a directory that changes a lot
 *        or has a lot of files could result in extra unnecessary work and checks on changes
 *        to other uninteresting files.
 */
constexpr char kWatchedConfigFileSetting[] = "/app/watchedConfigFile";

/** Setting path to specify a duration in seconds for which any dynamically loaded settings will
 *  persist for.  If this value is 0 or negative, any loaded settings will persist for the
 *  remainder of the process' lifetime.  When a positive value is used and this duration has
 *  expired, the original settings will be restored immediately.  This setting may be modified
 *  inside the watched settings file itself but will only take effect for the duration of that
 *  one loaded change.  If a positive value is used in the settings file, the original value
 *  will be restored once the settings are restored.  This defaults to 0 (ie: settings always
 *  persist in the process).
 */
constexpr char kWatchedConfigDurationSetting[] = "/app/watchedConfigDurationSeconds";


/** Base type for flags used in various functions in the `IWatchedConfig` interface. */
using WatchedConfigFlags = uint32_t;

/** Flag to indicate that a restore dictionary should be created before merging any new settings.
 *  When not used, the newly requested settings changes will be merged and replace any previous
 *  values persistently.
 */
constexpr WatchedConfigFlags fWatchedConfigFlagSaveState = 0x01;

/** Flag to indicate that changes should be tracked on the requested file.  If this flag is not
 *  used, only the immediate load request will be handled (if any).
 */
constexpr WatchedConfigFlags fWatchedConfigFlagTrackChanges = 0x02;

/** Flag to indicate that change tracking on the current file should be stopped.  This flag will
 *  essentially have no effect if used with @ref fWatchedConfigFlagTrackChanges since the new
 *  tracking task will still be queued after stopping the current task.  This flag may be used
 *  whether or not a new filename is provided.
 */
constexpr WatchedConfigFlags fWatchedConfigFlagStopTracking = 0x04;


/** Possible watched settings file actions that can be notified of through the callbacks.  These
 *  callbacks can be registered using omni::kit::IWatchedConfig::addWatchedConfigCallback().
 *  These callbacks are useful as a way of having a caller trigger a local settings reload when
 *  the watched settings file is loaded into the settings registry.
 */
enum class WatchedConfigAction
{
    /** The contents of a settings file was loaded and merged into the settings registry.  This
     *  may have been from a file change being detected on a tracked settings file or from an
     *  explicit request to load a specific settings file.  Any modified settings will already
     *  be present in the settings registry during the callback.
     */
    eMerged,

    /** A restore dictionary has been merged to the settings registry.  This may be the result of
     *  the active time for the settings that were loaded from the watched settings file expired,
     *  or due to an explicit request to restore the previous config.
     *
     *  @note Any settings that were added by the settings file that were _not_ already present in
     *        the settings registry will not be removed when the original settings are restored.
     *        This is done intentionally since a new setting created by the watched or loaded
     *        settings file could race with another plugin or extension adding or setting a
     *        default value for it.  If restoring the original settings also meant deleting that
     *        new setting, that other plugin or extension could find its expected setting missing
     *        and misbehave.
     */
    eRestored,

    /** The filename for the watched config file has changed.  The previous change subscription
     *  was removed and a new file change subscription will have been created.
     */
    eWatchChanged,

    /** An attempt to load the watched config file failed for some reason.  The settings were
     *  not loaded and the operation was cancelled.  Future attempts may be successful still.
     *  This failure usually occurs due to syntax errors in the settings file.
     */
    eLoadFailed,

    /** The watched settings file is shutting down its watch.  No more callbacks will be received
     *  after this point and any registered callbacks will be automatically removed.
     */
    eShutdown,
};

/** Callback function prototype for watched settings file change notifications.
 *
 *  @param[in] action   The action that occurred.
 *  @param[in] filename The name and path of the settings file that is being monitored for
 *                      changes.  This will always be an absolute path.
 *  @param[in] timeout  The current timeout value that will be used to determine when the current
 *                      settings will be restored.  This value will be passed the current value
 *                      for all callback actions.
 *  @param[in] userData Caller specific context value.  This is passed through unmodified from
 *                      when the callback was originally registered.  It is the callback's
 *                      responsibility to know how to properly access this value.
 *  @returns No return value.
 */
using OnWatchedConfigFileCallback = void (*)(WatchedConfigAction action,
                                             const char* filename,
                                             int64_t timeout,
                                             void* userData);


/** Interface to track and load changes to a single settings file.  When the file is created
 *  or modified, its contents will be merged into the settings registry, replacing any existing
 *  settings.  If a duration is also specified, the original settings will be restored after
 *  the duration expires.  Once set, the filename being watched cannot be modified through the
 *  watched settings file itself.  Settings can also be explicitly loaded and restored if needed.
 *
 *  It is highly suggested that the named file be placed in a directory that is seldomly changed
 *  and contains few files.  Having the file be in a large directory could result in extra
 *  unnecessary file change notification churn.  All of these extra notifications would be
 *  ignored quickly if they do not match the watched file, but it is still extra work that could
 *  be otherwise avoided.
 *
 *  This feature is intended to be used as a debugging tool to allow new settings to be
 *  dynamically loaded to assist with debugging efforts.  This helper class will only
 *  automatically refresh the logging and structured logging settings.  It is up to other
 *  plugins and extensions to monitor for changes in their own settings in order to have
 *  their functionality refreshed.  For example, `carb.crashreporter-breakpad.plugin` does
 *  this and will automatically refresh any new settings that appear in its settings branch.
 *
 *  @note If the directory containing the watched settings file is deleted, this may stop working
 *        on some platforms.  It is the caller's or user's responsibility to ensure that the
 *        directory containing the watched file stays valid as long as a file in it is being
 *        tracked.
 *
 *  @note If new settings are added through the watched settings file, they will persist even
 *        after the previous settings have been restored.  It is the caller's or user's
 *        responsibility to know this and to not add new settings through the watched settings
 *        file unless it is intended that they persist.  This is done intentionally to avoid
 *        settings being inadvertently deleted if loading them from the watched file races with
 *        another extension or plugin setting defaults or values for them.
 *
 *  @note The named settings file will _not_ be loaded on process startup or when tracking on
 *        the file's changes is first enabled.  The file will only be loaded on startup if it
 *        is also specified on the command line with the `-m` option.  The file will only be
 *        loaded if it is created or modified on disk.  This allows for the file to already
 *        exist in the named location on startup without affecting app behavior.  If something
 *        modifies the file on disk however (even by a background process such as AV software),
 *        it will be loaded and potentially modify behavior unintentionally.  It is the user's
 *        responsibility that when enabled, this feature is used responsibly.
 *
 *  @note This interface is available from the `omni.kit.watched_config` extension.
 */
class IWatchedConfig
{
public:
    CARB_PLUGIN_INTERFACE("omni::kit::IWatchedConfig", 1, 0);

    /** Main entry point for new config file watching requests.
     *
     *  @param[in] filename     The path to the file to watch for changes to or to load and merge
     *                          immediately.  This file must have either a `.json` or `.toml`
     *                          extension so it can be determined how to properly load it.  This
     *                          file does not need to exist on disk when this call is made if the
     *                          @ref fWatchedConfigFlagTrackChanges flag is used, however the
     *                          directory that it is named in must exist on disk.  This may be
     *                          `nullptr` if the @ref fWatchedConfigFlagStopTracking flag is used.
     *  @param[in] timeoutSec   The number of seconds that loaded settings should persist for in
     *                          the process.  This may be 0 or negative to allow any loaded
     *                          settings to persist for the remainder of the process' lifetime.
     *                          Once this timeout expires, the previous values of all the affected
     *                          settings will be restored.  This value will only be used if the
     *                          @ref fWatchedConfigFlagSaveState flag is also used.
     *  @param[in] flags        Flags to control the behavior of this operation.  This may be
     *                          0 or any combination of the @ref WatchedConfigFlags flags.
     *  @returns `true` if the operation on the specified file was successfully setup.  Returns
     *           `false` if the operation failed for any reason.  In this case it can be assumed
     *           that no settings will be loaded from any file at runtime.
     *
     *  @note In most cases this should not need to be called directly.  The other helper
     *        should be used instead.
     */
    virtual bool loadConfigFileEx(const char* filename, int64_t timeoutSec, WatchedConfigFlags flags) = 0;

    /** Immediately loads and merges a config file.
     *
     *  @param[in] filename     The path to the file to load and merge immediately.  This file
     *                          must have either a `.json` or `.toml` extension so it can be
     *                          determined how to properly load it.  This file must exist on
     *                          disk when this call is made.  This may be a relative or absolute
     *                          path but may not be `nullptr`.
     *  @returns `true` if the file is successfully loaded and merged.  A callback will be
     *           performed with the @ref WatchedConfigAction::eMerged action before return in
     *           this case.  Returns `false` if the file could not be loaded or merged.
     */
    bool loadConfigFile(const char* filename)
    {
        return loadConfigFileEx(filename, 0, 0);
    }

    /** Immediately loads and merges a config file and creates a restore dictionary for later.
     *
     *  @param[in] filename     The path to the file to load and merge immediately.  This file
     *                          must have either a `.json` or `.toml` extension so it can be
     *                          determined how to properly load it.  This file must exist on
     *                          disk when this call is made.  This may be a relative or absolute
     *                          path but may not be `nullptr`.
     *  @param[in] timeoutSec   The amount of time in seconds that the merged settings should
     *                          exist for before being restored.  If this is zero or negative
     *                          the previous settings will not be automatically restored.  In
     *                          that case the restoreConfig() function must be used instead to
     *                          explicitly merge the restore dictionary.
     *  @returns `true` if the file is successfully loaded and merged.  A callback will be
     *           performed with the @ref WatchedConfigAction::eMerged action before return in
     *           this case.  Returns `false` if the file could not be loaded or merged.
     */
    bool loadConfigFileWithRestore(const char* filename, int64_t timeoutSec)
    {
        return loadConfigFileEx(filename, timeoutSec, fWatchedConfigFlagSaveState);
    }

    /** Starts watching for changes on a config file.
     *
     *  @param[in] filename     The path to the file to start a change watch on.  This file
     *                          must have either a `.json` or `.toml` extension so it can be
     *                          determined how to properly load it.  This file does not need to
     *                          exist on disk when registering it.  However, the directory it is
     *                          named in must exist.  This may be a relative or absolute path but
     *                          may not be `nullptr`.
     *  @returns `true` if the tracking task is successfully started.  The named file will not be
     *           loaded and merged into the settings registry unless a change is detected on it.
     *           This allows for the file to already exist on disk at app startup time without it
     *           affecting the app's behavior.  Returns `false` if the new watch task could not be
     *           started.
     */
    bool trackConfigFileChanges(const char* filename)
    {
        return loadConfigFileEx(filename, 0, fWatchedConfigFlagTrackChanges);
    }

    /** Starts watching for changes on a config file.
     *
     *  @param[in] filename     The path to the file to start a change watch on.  This file
     *                          must have either a `.json` or `.toml` extension so it can be
     *                          determined how to properly load it.  This file does not need to
     *                          exist on disk when registering it.  However, the directory it is
     *                          named in must exist.  This may be a relative or absolute path but
     *                          may not be `nullptr`.
     *  @param[in] timeoutSec   The amount of time in seconds that the merged settings should
     *                          exist for before being restored.  If this is zero or negative
     *                          the previous settings will not be automatically restored.  In
     *                          that case the restoreConfig() function must be used instead to
     *                          explicitly merge the restore dictionary.
     *  @returns `true` if the tracking task is successfully started.  The named file will not be
     *           loaded and merged into the settings registry unless a change is detected on it.
     *           This allows for the file to already exist on disk at app startup time without it
     *           affecting the app's behavior.  Returns `false` if the new watch task could not be
     *           started.
     */
    bool trackConfigFileChangesWithRestore(const char* filename, int64_t timeoutSec)
    {
        return loadConfigFileEx(filename, timeoutSec, fWatchedConfigFlagSaveState | fWatchedConfigFlagTrackChanges);
    }

    /** Stops the current tracking task if any.
     *
     *  @remarks This stops any current config file change tracking task.  If a settings restore
     *           task has already been queued to occur, it will still occur as scheduled, but no
     *           new changes to the named config file will occur.  The path to the currently
     *           tracked config file will also be cleared so getTrackedConfigFilePath() will
     *           return an empty string after this call.
     */
    void stopTrackingConfigFileChanges()
    {
        loadConfigFileEx(nullptr, 0, fWatchedConfigFlagStopTracking);
    }

    /** Immediately merges the pending restore dictionary (if any).
     *
     *  @param[in] flags    Flags to control the behavior of this operation.
     *  @returns `true` if a restore dictionary was pending and was successfully merged to the
     *           settings registry.  In this case, the restore dictionary will be destroyed after
     *           merging to the settings registry.  Returns `false` if no restore dictionary is
     *           pending.
     */
    virtual bool restoreConfig(WatchedConfigFlags flags) = 0;

    /** Checks if a settings restore dictionary is pending.
     *
     *  @returns `true` if a restore dictionary is pending.  Returns `false` otherwise.
     */
    virtual bool hasRestorePending() = 0;

    /** Retrieves the path of the current config file being tracked (if any).
     *
     *  @param[out] buffer  If not `nullptr` and the buffer is large enough, this receives the
     *                      path to the config file currently being tracked for changes.  If
     *                      no file is being tracked, this will receive an empty string.  This
     *                      may be `nullptr` if only the size of the required buffer is needed.
     *  @param[inout] len   On input this contains the maximum size of the buffer @p buffer
     *                      in characters including any space for a terminating null character.
     *                      On output this receives either the required size of the buffer in
     *                      characters including the null terminator (if @p buffer is `nullptr`),
     *                      or the total number of characters written to the buffer not
     *                      including the null terminator.
     *  @returns `true` if there is a current config file change tracking task and the full
     *           file path was successfully copied into the buffer @p buffer.  Returns `false`
     *           if the buffer is not large enough or there is no current tracking task.
     */
    virtual bool getTrackedConfigFilePath(char* buffer, size_t* len) = 0;

    /** Registers a callback function to be performed when the watched settings file changes.
     *
     *  @param[in] callback The callback function that will be performed when settings changes
     *                      are loaded or restored.  This may not be `nullptr`.
     *  @param[in] userData Caller specific context data that will be passed to each invocation
     *                      of the callback function.
     *  @returns No return value.
     *
     *  @remarks This registers a callback function that can be used to notify an interested
     *           party when settings from a watched settings file are detected and loaded or
     *           restored.  When this callback is no longer needed, it must be unregistered
     *           using removeWatchedConfigFileCallback() and the same arguments passed in here.
     *
     *  @thread_safety These callbacks may occur on multiple threads but will rarely if ever have
     *                 multiple simultaneous callbacks arriving on different threads.  Regardless,
     *                 callback owners should still protect access to internal resources inside
     *                 their callback implementations.
     */
    virtual void addWatchedConfigFileCallback(OnWatchedConfigFileCallback callback, void* userData) = 0;

    /** Unregisters a dynamic settings change callback function.
     *
     *  @param[in] callback The callback function that was to be performed when settings changes
     *                      are loaded or restored.  This may not be `nullptr`.  This must be the
     *                      same callback function that was previously passed to the call to
     *                      addSettingsChangeCallback() when the callback was originally
     *                      registered.
     *  @param[in] userData Caller specific context data that was to be passed to each invocation
     *                      of the callback function.  This must be the same context value that
     *                      was previously passed to addSettingsChangeCallback() when the callback
     *                      was originally registered.
     *  @returns No return value.
     *
     *  @remarks This unregisters a settings change callback function.  Any registered callback
     *           must be removed before its owning module is unloaded.
     */
    virtual void removeWatchedConfigFileCallback(OnWatchedConfigFileCallback callback, void* userData) = 0;
};

} // namespace kit
} // namespace omni
