// Copyright 2020-2022, Collabora, Ltd.
// SPDX-License-Identifier: BSL-1.0
/*!
 * @file
 * @brief  Generated bindings data header.
 * @author Jakob Bornecrantz <jakob@collabora.com>
 * @author Christoph Haag <christoph.haag@collabora.com>
 * @author Korcan Hussein <korcan.hussein@collabora.com>
 * @ingroup oxr_api
 */

#pragma once

#include <stddef.h>

#include "xrt/xrt_defines.h"


#ifdef __cplusplus
extern "C" {
#endif

typedef uint64_t XrPath; // OpenXR typedef
typedef uint64_t XrVersion; // OpenXR typedef

struct oxr_extension_status;

#define OXR_BINDINGS_PROFILE_TEMPLATE_COUNT 31

struct oxr_bindings_path_cache_element {
    //! Pointer to XrPath
    XrPath *path_cache;
    //! Pointer to char*
    const char **path_cache_name;
};

struct oxr_bindings_path_cache {
    // wrapped in a struct solely to reduce the C pointer soup
    struct oxr_bindings_path_cache_element path_cache[OXR_BINDINGS_PROFILE_TEMPLATE_COUNT];
};

void oxr_get_interaction_profile_path_cache(const struct oxr_bindings_path_cache **out_path_cache);

// clang-format off

bool
oxr_verify_bytedance_pico4_controller_subpath(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_bytedance_pico4_controller_dpad_path(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_bytedance_pico4_controller_dpad_emulator(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

void
oxr_verify_bytedance_pico4_controller_ext(const struct oxr_extension_status *extensions, XrVersion openxr_version, bool *out_supported, bool *out_enabled);

bool
oxr_verify_bytedance_pico_g3_controller_subpath(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_bytedance_pico_g3_controller_dpad_path(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_bytedance_pico_g3_controller_dpad_emulator(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

void
oxr_verify_bytedance_pico_g3_controller_ext(const struct oxr_extension_status *extensions, XrVersion openxr_version, bool *out_supported, bool *out_enabled);

bool
oxr_verify_bytedance_pico_neo3_controller_subpath(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_bytedance_pico_neo3_controller_dpad_path(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_bytedance_pico_neo3_controller_dpad_emulator(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

void
oxr_verify_bytedance_pico_neo3_controller_ext(const struct oxr_extension_status *extensions, XrVersion openxr_version, bool *out_supported, bool *out_enabled);

bool
oxr_verify_ext_eye_gaze_interaction_subpath(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_ext_eye_gaze_interaction_dpad_path(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_ext_eye_gaze_interaction_dpad_emulator(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

void
oxr_verify_ext_eye_gaze_interaction_ext(const struct oxr_extension_status *extensions, XrVersion openxr_version, bool *out_supported, bool *out_enabled);

bool
oxr_verify_ext_hand_interaction_ext_subpath(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_ext_hand_interaction_ext_dpad_path(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_ext_hand_interaction_ext_dpad_emulator(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

void
oxr_verify_ext_hand_interaction_ext_ext(const struct oxr_extension_status *extensions, XrVersion openxr_version, bool *out_supported, bool *out_enabled);

bool
oxr_verify_facebook_touch_controller_pro_subpath(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_facebook_touch_controller_pro_dpad_path(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_facebook_touch_controller_pro_dpad_emulator(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

void
oxr_verify_facebook_touch_controller_pro_ext(const struct oxr_extension_status *extensions, XrVersion openxr_version, bool *out_supported, bool *out_enabled);

bool
oxr_verify_google_daydream_controller_subpath(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_google_daydream_controller_dpad_path(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_google_daydream_controller_dpad_emulator(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

void
oxr_verify_google_daydream_controller_ext(const struct oxr_extension_status *extensions, XrVersion openxr_version, bool *out_supported, bool *out_enabled);

bool
oxr_verify_hp_mixed_reality_controller_subpath(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_hp_mixed_reality_controller_dpad_path(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_hp_mixed_reality_controller_dpad_emulator(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

void
oxr_verify_hp_mixed_reality_controller_ext(const struct oxr_extension_status *extensions, XrVersion openxr_version, bool *out_supported, bool *out_enabled);

bool
oxr_verify_htc_vive_controller_subpath(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_htc_vive_controller_dpad_path(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_htc_vive_controller_dpad_emulator(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

void
oxr_verify_htc_vive_controller_ext(const struct oxr_extension_status *extensions, XrVersion openxr_version, bool *out_supported, bool *out_enabled);

bool
oxr_verify_htc_vive_cosmos_controller_subpath(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_htc_vive_cosmos_controller_dpad_path(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_htc_vive_cosmos_controller_dpad_emulator(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

void
oxr_verify_htc_vive_cosmos_controller_ext(const struct oxr_extension_status *extensions, XrVersion openxr_version, bool *out_supported, bool *out_enabled);

bool
oxr_verify_htc_vive_focus3_controller_subpath(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_htc_vive_focus3_controller_dpad_path(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_htc_vive_focus3_controller_dpad_emulator(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

void
oxr_verify_htc_vive_focus3_controller_ext(const struct oxr_extension_status *extensions, XrVersion openxr_version, bool *out_supported, bool *out_enabled);

bool
oxr_verify_htc_vive_pro_subpath(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_htc_vive_pro_dpad_path(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_htc_vive_pro_dpad_emulator(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

void
oxr_verify_htc_vive_pro_ext(const struct oxr_extension_status *extensions, XrVersion openxr_version, bool *out_supported, bool *out_enabled);

bool
oxr_verify_htc_vive_tracker_htcx_subpath(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_htc_vive_tracker_htcx_dpad_path(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_htc_vive_tracker_htcx_dpad_emulator(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

void
oxr_verify_htc_vive_tracker_htcx_ext(const struct oxr_extension_status *extensions, XrVersion openxr_version, bool *out_supported, bool *out_enabled);

bool
oxr_verify_khr_simple_controller_subpath(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_khr_simple_controller_dpad_path(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_khr_simple_controller_dpad_emulator(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

void
oxr_verify_khr_simple_controller_ext(const struct oxr_extension_status *extensions, XrVersion openxr_version, bool *out_supported, bool *out_enabled);

bool
oxr_verify_meta_touch_controller_plus_subpath(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_meta_touch_controller_plus_dpad_path(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_meta_touch_controller_plus_dpad_emulator(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

void
oxr_verify_meta_touch_controller_plus_ext(const struct oxr_extension_status *extensions, XrVersion openxr_version, bool *out_supported, bool *out_enabled);

bool
oxr_verify_meta_touch_controller_quest_1_rift_s_subpath(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_meta_touch_controller_quest_1_rift_s_dpad_path(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_meta_touch_controller_quest_1_rift_s_dpad_emulator(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

void
oxr_verify_meta_touch_controller_quest_1_rift_s_ext(const struct oxr_extension_status *extensions, XrVersion openxr_version, bool *out_supported, bool *out_enabled);

bool
oxr_verify_meta_touch_controller_quest_2_subpath(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_meta_touch_controller_quest_2_dpad_path(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_meta_touch_controller_quest_2_dpad_emulator(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

void
oxr_verify_meta_touch_controller_quest_2_ext(const struct oxr_extension_status *extensions, XrVersion openxr_version, bool *out_supported, bool *out_enabled);

bool
oxr_verify_meta_touch_controller_rift_cv1_subpath(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_meta_touch_controller_rift_cv1_dpad_path(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_meta_touch_controller_rift_cv1_dpad_emulator(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

void
oxr_verify_meta_touch_controller_rift_cv1_ext(const struct oxr_extension_status *extensions, XrVersion openxr_version, bool *out_supported, bool *out_enabled);

bool
oxr_verify_meta_touch_plus_controller_subpath(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_meta_touch_plus_controller_dpad_path(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_meta_touch_plus_controller_dpad_emulator(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

void
oxr_verify_meta_touch_plus_controller_ext(const struct oxr_extension_status *extensions, XrVersion openxr_version, bool *out_supported, bool *out_enabled);

bool
oxr_verify_meta_touch_pro_controller_subpath(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_meta_touch_pro_controller_dpad_path(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_meta_touch_pro_controller_dpad_emulator(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

void
oxr_verify_meta_touch_pro_controller_ext(const struct oxr_extension_status *extensions, XrVersion openxr_version, bool *out_supported, bool *out_enabled);

bool
oxr_verify_microsoft_hand_interaction_subpath(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_microsoft_hand_interaction_dpad_path(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_microsoft_hand_interaction_dpad_emulator(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

void
oxr_verify_microsoft_hand_interaction_ext(const struct oxr_extension_status *extensions, XrVersion openxr_version, bool *out_supported, bool *out_enabled);

bool
oxr_verify_microsoft_motion_controller_subpath(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_microsoft_motion_controller_dpad_path(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_microsoft_motion_controller_dpad_emulator(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

void
oxr_verify_microsoft_motion_controller_ext(const struct oxr_extension_status *extensions, XrVersion openxr_version, bool *out_supported, bool *out_enabled);

bool
oxr_verify_microsoft_xbox_controller_subpath(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_microsoft_xbox_controller_dpad_path(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_microsoft_xbox_controller_dpad_emulator(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

void
oxr_verify_microsoft_xbox_controller_ext(const struct oxr_extension_status *extensions, XrVersion openxr_version, bool *out_supported, bool *out_enabled);

bool
oxr_verify_ml_ml2_controller_subpath(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_ml_ml2_controller_dpad_path(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_ml_ml2_controller_dpad_emulator(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

void
oxr_verify_ml_ml2_controller_ext(const struct oxr_extension_status *extensions, XrVersion openxr_version, bool *out_supported, bool *out_enabled);

bool
oxr_verify_mndx_ball_on_a_stick_controller_subpath(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_mndx_ball_on_a_stick_controller_dpad_path(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_mndx_ball_on_a_stick_controller_dpad_emulator(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

void
oxr_verify_mndx_ball_on_a_stick_controller_ext(const struct oxr_extension_status *extensions, XrVersion openxr_version, bool *out_supported, bool *out_enabled);

bool
oxr_verify_mndx_hydra_subpath(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_mndx_hydra_dpad_path(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_mndx_hydra_dpad_emulator(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

void
oxr_verify_mndx_hydra_ext(const struct oxr_extension_status *extensions, XrVersion openxr_version, bool *out_supported, bool *out_enabled);

bool
oxr_verify_oculus_go_controller_subpath(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_oculus_go_controller_dpad_path(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_oculus_go_controller_dpad_emulator(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

void
oxr_verify_oculus_go_controller_ext(const struct oxr_extension_status *extensions, XrVersion openxr_version, bool *out_supported, bool *out_enabled);

bool
oxr_verify_oculus_touch_controller_subpath(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_oculus_touch_controller_dpad_path(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_oculus_touch_controller_dpad_emulator(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

void
oxr_verify_oculus_touch_controller_ext(const struct oxr_extension_status *extensions, XrVersion openxr_version, bool *out_supported, bool *out_enabled);

bool
oxr_verify_oppo_mr_controller_oppo_subpath(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_oppo_mr_controller_oppo_dpad_path(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_oppo_mr_controller_oppo_dpad_emulator(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

void
oxr_verify_oppo_mr_controller_oppo_ext(const struct oxr_extension_status *extensions, XrVersion openxr_version, bool *out_supported, bool *out_enabled);

bool
oxr_verify_samsung_odyssey_controller_subpath(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_samsung_odyssey_controller_dpad_path(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_samsung_odyssey_controller_dpad_emulator(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

void
oxr_verify_samsung_odyssey_controller_ext(const struct oxr_extension_status *extensions, XrVersion openxr_version, bool *out_supported, bool *out_enabled);

bool
oxr_verify_valve_index_controller_subpath(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_valve_index_controller_dpad_path(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

bool
oxr_verify_valve_index_controller_dpad_emulator(const struct oxr_extension_status *extensions, XrVersion openxr_major_minor, const char *str, size_t length);

void
oxr_verify_valve_index_controller_ext(const struct oxr_extension_status *extensions, XrVersion openxr_version, bool *out_supported, bool *out_enabled);

#define PATHS_PER_BINDING_TEMPLATE 16

enum oxr_dpad_binding_point
{
	OXR_DPAD_BINDING_POINT_NONE,
	OXR_DPAD_BINDING_POINT_UP,
	OXR_DPAD_BINDING_POINT_DOWN,
	OXR_DPAD_BINDING_POINT_LEFT,
	OXR_DPAD_BINDING_POINT_RIGHT,
};

struct dpad_emulation
{
	const char *subaction_path;
	const char *paths[PATHS_PER_BINDING_TEMPLATE];
	enum xrt_input_name position;
	enum xrt_input_name activate; // Can be zero
};

struct binding_template
{
	const char *subaction_path;
	const char *steamvr_path;
	const char *localized_name;
	const char *paths[PATHS_PER_BINDING_TEMPLATE];
	enum xrt_input_name input;
	enum xrt_input_name dpad_activate;
	enum xrt_output_name output;
};

typedef bool (*path_verify_fn_t)(const struct oxr_extension_status *extensions, XrVersion openxr_version, const char *, size_t);
typedef void (*ext_verify_fn_t)(const struct oxr_extension_status *extensions, XrVersion openxr_version, bool *out_supported, bool *out_enabled);

struct profile_template
{
	enum xrt_device_name name;
	const char *path;
	const char *localized_name;
	const char *steamvr_input_profile_path;
	const char *steamvr_controller_type;
	struct binding_template *bindings;
	size_t binding_count;
	struct dpad_emulation *dpads;
	size_t dpad_count;
	struct {
		struct {
			uint32_t major;
			uint32_t minor;
		} promoted;
	} openxr_version;
	// Only valid after path cache entries are initialized via oxr_get_interaction_profile_path_cache.
	XrPath path_cache;

	path_verify_fn_t subpath_fn;
	path_verify_fn_t dpad_path_fn;
	path_verify_fn_t dpad_emulator_fn;
	ext_verify_fn_t ext_verify_fn;
	const char *extension_name;
};

extern struct profile_template profile_templates[OXR_BINDINGS_PROFILE_TEMPLATE_COUNT];

const char *
xrt_input_name_string(enum xrt_input_name input);

enum xrt_input_name
xrt_input_name_enum(const char *input);

const char *
xrt_output_name_string(enum xrt_output_name output);

enum xrt_output_name
xrt_output_name_enum(const char *output);


// clang-format on

#ifdef __cplusplus
}
#endif
