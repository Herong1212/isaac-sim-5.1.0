// SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
/*!
 * @file
 * @brief Types used across XCR API.
 * @author Rafal Karp <rkarp@nvidia.com>
 * @ingroup xcr
 */

#pragma once

// Define cross-platform import/export macros
#ifdef _WIN32
#ifdef BUILDING_XCR_REPLAY
#define XCR_REPLAY_API __declspec(dllexport)
#else
#define XCR_REPLAY_API __declspec(dllimport)
#endif
#else // Linux or other platforms
#ifdef BUILDING_XCR_REPLAY
#define XCR_REPLAY_API __attribute__((visibility("default")))
#else
#define XCR_REPLAY_API
#endif
#endif

#ifdef __cplusplus
extern "C" {
#endif

#define XCR_SUCCESS(result) ((result) == xcrResult_Success)

/*!
 * Enumeration for return codes.
 */
typedef enum
{
	xcrResult_Success = 0x0000, /*!< The operation succeeded */

	// General errors
	xcrResult_Error_Group_General = 0x0100,         /*!< Base value for general errors */
	xcrResult_Error_Unknown = 0x0101,               /*!< Unknown error occurred */
	xcrResult_Error_FilePathInvalid = 0x0102,       /*!< Invalid file path provided */
	xcrResult_Error_FileFormatInvalid = 0x0103,     /*!< Invalid file format provided */
	xcrResult_Error_MemoryAllocationError = 0x0104, /*!< Issue related to memory allocation */
	xcrResult_Error_InvalidArgument = 0x0105,       /*!< Invalid argument */

	// Service-related errors
	xcrResult_Error_Group_Service = 0x0200,          /*!< Base value for service-related errors */
	xcrResult_Error_ServiceAlreadyRunning = 0x0201,  /*!< Service is already running */
	xcrResult_Error_ServiceNotRunning = 0x0202,      /*!< Service is not running */
	xcrResult_Error_ServiceStartUpTimedOut = 0x0203, /*!< Service timed out on the start up */

	// Replay-related errors
	xcrResult_Error_Group_Replay = 0x0300,                  /*!< Base value for replay-related errors */
	xcrResult_Error_ReplayAlreadyPlaying = 0x0301,          /*!< Replay is already playing */
	xcrResult_Error_ReplayAlreadyPaused = 0x0302,           /*!< Replay is already paused */
	xcrResult_Error_ReplayFilePathNotSet = 0x0303,          /*!< Replay file path has not been set */
	xcrResult_Error_ReplayFileContainEmptyCapture = 0x0304, /*!< Replay file contain 0 tracked records */
	xcrResult_Error_ReplayTimestampNegative = 0x0305,       /*!< Replay timestamp is negative */
	xcrResult_Error_ReplayInteractionProfileDiffers =
	    0x0306, /*!< Replay Interaction Profile is different than the one service was initialized with */
	xcrResult_Error_ReplayFrameIndexOutOfBounds =
	    0x0307, /*!< Replay frame index is greater than size of all captured frames */
	xcrResult_Error_ReplayInteractionProfileInvalid = 0x0308, /*!< Replay Interaction Profile is not valid */
	xcrResult_Error_ReplayResolutionInvalid = 0x0309          /*!< Replay recommended resolution is not valid */
} XCRResult;


#define XCR_DEFAULT_MIN_RESOLUTION_WIDTH 1280
#define XCR_DEFAULT_MIN_RESOLUTION_HEIGHT 720
#define XCR_DEFAULT_INTERACTION_PROFILE nullptr

typedef struct XCRReplayServiceMainConfig
{
	const char *overriddenInteractionProfile =
	    XCR_DEFAULT_INTERACTION_PROFILE; // Interaction profile to override profile from the recording
	uint32_t resolutionWidth = XCR_DEFAULT_MIN_RESOLUTION_WIDTH;   // Recommended runtime resolution width
	uint32_t resolutionHeight = XCR_DEFAULT_MIN_RESOLUTION_HEIGHT; // Recommended runtime resolution height
	bool showWindow = false;                                       // Flag to control window visibility
} XCRReplayServiceMainConfig;


#define INTERACTION_PROFILE_EXT_HAND_INTERACTION "/interaction_profiles/ext/hand_interaction_ext"
#define INTERACTION_PROFILE_KHR_SIMPLE_CONTROLLER "/interaction_profiles/khr/simple_controller"
#define INTERACTION_PROFILE_GOOGLE_DAYDREAM_CONTROLLER "/interaction_profiles/google/daydream_controller"
#define INTERACTION_PROFILE_HTC_VIVE_CONTROLLER "/interaction_profiles/htc/vive_controller"
#define INTERACTION_PROFILE_HTC_VIVE_PRO "/interaction_profiles/htc/vive_pro"
#define INTERACTION_PROFILE_MICROSOFT_MOTION_CONTROLLER "/interaction_profiles/microsoft/motion_controller"
#define INTERACTION_PROFILE_MICROSOFT_XBOX_CONTROLLER "/interaction_profiles/microsoft/xbox_controller"
#define INTERACTION_PROFILE_OCULUS_GO_CONTROLLER "/interaction_profiles/oculus/go_controller"
#define INTERACTION_PROFILE_OCULUS_TOUCH_CONTROLLER "/interaction_profiles/oculus/touch_controller"
#define INTERACTION_PROFILE_META_TOUCH_CONTROLLER_RIFT_CV1 "/interaction_profiles/meta/touch_controller_rift_cv1"
#define INTERACTION_PROFILE_META_TOUCH_CONTROLLER_QUEST_1_RIFT_S                                                       \
	"/interaction_profiles/meta/touch_controller_quest_1_rift_s"
#define INTERACTION_PROFILE_META_TOUCH_CONTROLLER_QUEST_2 "/interaction_profiles/meta/touch_controller_quest_2"
#define INTERACTION_PROFILE_VALVE_INDEX_CONTROLLER "/interaction_profiles/valve/index_controller"
#define INTERACTION_PROFILE_HP_MIXED_REALITY_CONTROLLER "/interaction_profiles/hp/mixed_reality_controller"
#define INTERACTION_PROFILE_SAMSUNG_ODYSSEY_CONTROLLER "/interaction_profiles/samsung/odyssey_controller"
#define INTERACTION_PROFILE_ML_ML2_CONTROLLER "/interaction_profiles/ml/ml2_controller"
#define INTERACTION_PROFILE_MICROSOFT_HAND_INTERACTION "/interaction_profiles/microsoft/hand_interaction"
#define INTERACTION_PROFILE_MNDX_BALL_ON_A_STICK_CONTROLLER "/interaction_profiles/mndx/ball_on_a_stick_controller"
#define INTERACTION_PROFILE_MNDX_HYDRA "/interaction_profiles/mndx/hydra"
#define INTERACTION_PROFILE_EXT_EYE_GAZE_INTERACTION "/interaction_profiles/ext/eye_gaze_interaction"
#define INTERACTION_PROFILE_HTC_VIVE_TRACKER_HTCX "/interaction_profiles/htc/vive_tracker_htcx"
#define INTERACTION_PROFILE_OPPO_MR_CONTROLLER_OPPO "/interaction_profiles/oppo/mr_controller_oppo"
#define INTERACTION_PROFILE_BYTEDANCE_PICO_NEO3_CONTROLLER "/interaction_profiles/bytedance/pico_neo3_controller"
#define INTERACTION_PROFILE_BYTEDANCE_PICO4_CONTROLLER "/interaction_profiles/bytedance/pico4_controller"
#define INTERACTION_PROFILE_BYTEDANCE_PICO_G3_CONTROLLER "/interaction_profiles/bytedance/pico_g3_controller"
#define INTERACTION_PROFILE_HTC_VIVE_COSMOS_CONTROLLER "/interaction_profiles/htc/vive_cosmos_controller"
#define INTERACTION_PROFILE_HTC_VIVE_FOCUS3_CONTROLLER "/interaction_profiles/htc/vive_focus3_controller"
#define INTERACTION_PROFILE_META_TOUCH_PRO_CONTROLLER "/interaction_profiles/meta/touch_pro_controller"
#define INTERACTION_PROFILE_META_TOUCH_PLUS_CONTROLLER "/interaction_profiles/meta/touch_plus_controller"
#define INTERACTION_PROFILE_META_TOUCH_CONTROLLER_PLUS "/interaction_profiles/meta/touch_controller_plus"
#define INTERACTION_PROFILE_FACEBOOK_TOUCH_CONTROLLER_PRO "/interaction_profiles/facebook/touch_controller_pro"

#ifdef __cplusplus
}
#endif
