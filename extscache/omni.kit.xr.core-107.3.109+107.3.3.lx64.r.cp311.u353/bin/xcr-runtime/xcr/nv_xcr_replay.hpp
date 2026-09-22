// SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
/*!
 * @file
 * @brief Public header containing API for XCR Replay OpenXR runtime
 * @author Rafal Karp <rkarp@nvidia.com>
 * @ingroup xcr
 */

#pragma once

#include "nv_xcr_data.hpp"

#ifdef _WIN32
#define XCRAPI_PTR __stdcall
#else
#define XCRAPI_PTR
#endif

#ifdef __cplusplus
extern "C" {
#endif

// Define a type for the replay playback function
typedef void (*ReplayPlaybackCompleteCallback)();

typedef XCRResult(XCRAPI_PTR *PFN_xcrStartReplayService)(const char *path);
typedef XCRResult(XCRAPI_PTR *PFN_xcrStartReplayServiceWithConfig)(const char *path,
                                                                   const XCRReplayServiceMainConfig &mainInfoConfig);
typedef XCRResult(XCRAPI_PTR *PFN_xcrStopReplayServiceImmediately)(void);
typedef XCRResult(XCRAPI_PTR *PFN_xcrStopReplayServiceAfterReplayPlayback)(void);
typedef XCRResult(XCRAPI_PTR *PFN_xcrSetReplayFile)(const char *path);
typedef XCRResult(XCRAPI_PTR *PFN_xcrSetReplayTimestamp)(double timestamp);
typedef XCRResult(XCRAPI_PTR *PFN_xcrGetReplayFrameTimestamp)(uint32_t frameIndex, double *timestamp);
typedef XCRResult(XCRAPI_PTR *PFN_xcrSetReplayFrame)(uint32_t frameIndex);
typedef XCRResult(XCRAPI_PTR *PFN_xcrGetReplayFrameCount)(uint32_t *outFrameCount);
typedef XCRResult(XCRAPI_PTR *PFN_xcrGetLastReplayedTimestamp)(double *timestamp);
typedef XCRResult(XCRAPI_PTR *PFN_xcrGetReplayInteractionProfile)(size_t *outInteractionProfileSize,
                                                                  char *outInteractionProfile);
typedef XCRResult(XCRAPI_PTR *PFN_xcrPlayReplay)(void);
typedef XCRResult(XCRAPI_PTR *PFN_xcrStopReplay)(void);
typedef XCRResult(XCRAPI_PTR *PFN_xcrSetReplayPlaybackCompleteCallback)(ReplayPlaybackCompleteCallback callback);

/*!
 * Starts running the XCR Replay service (in separated thread). Initialize XCR service with given recording. Interaction
 * profile will be loaded from recording. Replay does not play automatically.
 */
XCR_REPLAY_API XCRResult
startReplayService(const char *path);

/*!
 * Starts running the XCR Replay service (in separated thread). Initialize XCR service with given recording and custom
 * configuration (can contain custom resolution or interaction profile). Replay does not play automatically.
 */
XCR_REPLAY_API XCRResult
startReplayServiceWithConfig(const char *path, const XCRReplayServiceMainConfig &mainInfoConfig);

/*!
 * Stops XCR Replay service. This call will wait (not return) till Monado service will stop.
 */
XCR_REPLAY_API XCRResult
stopReplayServiceImmediately(void);

/*!
 * Stops XCR Replay service after current playback ends. This call does not return immediately, just after playback
 * ends.
 */
XCR_REPLAY_API XCRResult
stopReplayServiceAfterReplayPlayback(void);

/*!
 * Sets path to recording file which will be replayed.
 * Needs to be for the same OpenXR Interaction Profile as current XCR Replay service was instanced with.
 */
XCR_REPLAY_API XCRResult
setReplayFile(const char *path);

/*!
 * Sets custom timestamp of the replay, value is a timestamp in seconds and should be positive.
 */
XCR_REPLAY_API XCRResult
setReplayTimestamp(double timestamp);

/*!
 * Gets count of all frames in current replay.
 */
XCR_REPLAY_API XCRResult
getReplayFrameCount(uint32_t *outFrameCount);

/*!
 * Sets concrete frame of the replay.
 */
XCR_REPLAY_API XCRResult
setReplayFrame(uint32_t frameIndex);

/*!
 * Gets relative timestamp (in seconds) when given frame was captured.
 */
XCR_REPLAY_API XCRResult
getReplayFrameTimestamp(uint32_t frameIndex, double *timestamp);

/*!
 * Gets timestamp (in seconds) of the most recent replayed moment.
 */
XCR_REPLAY_API XCRResult
getLastReplayedTimestamp(double *timestamp);

/*!
 * Gets current interaction profile.
 */
XCR_REPLAY_API XCRResult
getReplayInteractionProfile(size_t *outInteractionProfileSize, char *outInteractionProfile);

/*!
 * Starts given replay.
 */
XCR_REPLAY_API XCRResult
playReplay(void);

/*!
 * Stops given replay, it will reset time to 0 (beginning of replay).
 */
XCR_REPLAY_API XCRResult
stopReplay(void);

/*!
 * Sets the captured replay playing complete callback.
 */
XCR_REPLAY_API XCRResult
setReplayPlaybackCompleteCallback(ReplayPlaybackCompleteCallback callback);

#ifdef __cplusplus
}
#endif
