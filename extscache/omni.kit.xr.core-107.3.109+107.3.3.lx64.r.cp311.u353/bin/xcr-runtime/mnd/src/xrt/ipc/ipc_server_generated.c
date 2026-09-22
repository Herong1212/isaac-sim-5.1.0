// Copyright 2020-2023, Collabora, Ltd.
// SPDX-License-Identifier: BSL-1.0
/*!
 * @file
 * @brief  Generated IPC server code.
 * @author Jakob Bornecrantz <jakob@collabora.com>
 * @ingroup ipc_server
 */

#include "xrt/xrt_limits.h"

#include "shared/ipc_protocol.h"
#include "shared/ipc_utils.h"

#include "server/ipc_server.h"

#include "ipc_server_generated.h"


xrt_result_t
ipc_dispatch(volatile struct ipc_client_state *ics, ipc_command_t *ipc_command)
{
	switch (*ipc_command) {
	case IPC_INSTANCE_GET_SHM_FD: {
		IPC_TRACE(ics->server, "Dispatching instance_get_shm_fd");

		struct ipc_result_reply reply = {0};
		xrt_shmem_handle_t handles[XRT_MAX_IPC_HANDLES] = {0};
		uint32_t handle_count = {0};


		reply.result = ipc_handle_instance_get_shm_fd(ics,
		                                              XRT_MAX_IPC_HANDLES,
		                                              handles,
		                                              &handle_count);

		xrt_result_t xret = ipc_send_handles_shmem((struct ipc_message_channel *)&ics->imc,
		                                           &reply,
		                                           sizeof(reply),
		                                           handles,
		                                           handle_count);
		return xret;
	}
	case IPC_INSTANCE_DESCRIBE_CLIENT: {
		IPC_TRACE(ics->server, "Dispatching instance_describe_client");

		struct ipc_instance_describe_client_msg *msg = (struct ipc_instance_describe_client_msg *)ipc_command;
		struct ipc_result_reply reply = {0};


		reply.result = ipc_handle_instance_describe_client(ics,
		                                                   &msg->desc);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_INSTANCE_IS_SYSTEM_AVAILABLE: {
		IPC_TRACE(ics->server, "Dispatching instance_is_system_available");

		struct ipc_instance_is_system_available_reply reply = {0};


		reply.result = ipc_handle_instance_is_system_available(ics,
		                                                       &reply.available);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SYSTEM_GET_PROPERTIES: {
		IPC_TRACE(ics->server, "Dispatching system_get_properties");

		struct ipc_system_get_properties_reply reply = {0};


		reply.result = ipc_handle_system_get_properties(ics,
		                                                &reply.properties);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SYSTEM_GET_CLIENT_INFO: {
		IPC_TRACE(ics->server, "Dispatching system_get_client_info");

		struct ipc_system_get_client_info_msg *msg = (struct ipc_system_get_client_info_msg *)ipc_command;
		struct ipc_system_get_client_info_reply reply = {0};


		reply.result = ipc_handle_system_get_client_info(ics,
		                                                 msg->id,
		                                                 &reply.ias);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SYSTEM_GET_CLIENTS: {
		IPC_TRACE(ics->server, "Dispatching system_get_clients");

		struct ipc_system_get_clients_reply reply = {0};


		reply.result = ipc_handle_system_get_clients(ics,
		                                             &reply.clients);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SYSTEM_SET_PRIMARY_CLIENT: {
		IPC_TRACE(ics->server, "Dispatching system_set_primary_client");

		struct ipc_system_set_primary_client_msg *msg = (struct ipc_system_set_primary_client_msg *)ipc_command;
		struct ipc_result_reply reply = {0};


		reply.result = ipc_handle_system_set_primary_client(ics,
		                                                    msg->id);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SYSTEM_SET_FOCUSED_CLIENT: {
		IPC_TRACE(ics->server, "Dispatching system_set_focused_client");

		struct ipc_system_set_focused_client_msg *msg = (struct ipc_system_set_focused_client_msg *)ipc_command;
		struct ipc_result_reply reply = {0};


		reply.result = ipc_handle_system_set_focused_client(ics,
		                                                    msg->id);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SYSTEM_TOGGLE_IO_CLIENT: {
		IPC_TRACE(ics->server, "Dispatching system_toggle_io_client");

		struct ipc_system_toggle_io_client_msg *msg = (struct ipc_system_toggle_io_client_msg *)ipc_command;
		struct ipc_result_reply reply = {0};


		reply.result = ipc_handle_system_toggle_io_client(ics,
		                                                  msg->id);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SYSTEM_TOGGLE_IO_DEVICE: {
		IPC_TRACE(ics->server, "Dispatching system_toggle_io_device");

		struct ipc_system_toggle_io_device_msg *msg = (struct ipc_system_toggle_io_device_msg *)ipc_command;
		struct ipc_result_reply reply = {0};


		reply.result = ipc_handle_system_toggle_io_device(ics,
		                                                  msg->id);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SYSTEM_OPAQUE_DATA_SEND: {
		IPC_TRACE(ics->server, "Dispatching system_opaque_data_send");

		struct ipc_system_opaque_data_send_msg *msg = (struct ipc_system_opaque_data_send_msg *)ipc_command;
		// No return arguments

		xrt_result_t xret = ipc_handle_system_opaque_data_send(ics,
		                                                       msg->length);

		return xret;
	}
	case IPC_SYSTEM_OPAQUE_DATA_RECEIVE: {
		IPC_TRACE(ics->server, "Dispatching system_opaque_data_receive");

		// No return arguments

		xrt_result_t xret = ipc_handle_system_opaque_data_receive(ics);

		return xret;
	}
	case IPC_SYSTEM_DEVICES_GET_ROLES: {
		IPC_TRACE(ics->server, "Dispatching system_devices_get_roles");

		struct ipc_system_devices_get_roles_reply reply = {0};


		reply.result = ipc_handle_system_devices_get_roles(ics,
		                                                   &reply.system_roles);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SYSTEM_DEVICES_BEGIN_FEATURE: {
		IPC_TRACE(ics->server, "Dispatching system_devices_begin_feature");

		struct ipc_system_devices_begin_feature_msg *msg = (struct ipc_system_devices_begin_feature_msg *)ipc_command;
		struct ipc_result_reply reply = {0};


		reply.result = ipc_handle_system_devices_begin_feature(ics,
		                                                       msg->type);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SYSTEM_DEVICES_END_FEATURE: {
		IPC_TRACE(ics->server, "Dispatching system_devices_end_feature");

		struct ipc_system_devices_end_feature_msg *msg = (struct ipc_system_devices_end_feature_msg *)ipc_command;
		struct ipc_result_reply reply = {0};


		reply.result = ipc_handle_system_devices_end_feature(ics,
		                                                     msg->type);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SYSTEM_COMPOSITOR_GET_INFO: {
		IPC_TRACE(ics->server, "Dispatching system_compositor_get_info");

		struct ipc_system_compositor_get_info_reply reply = {0};


		reply.result = ipc_handle_system_compositor_get_info(ics,
		                                                     &reply.info);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SESSION_CREATE: {
		IPC_TRACE(ics->server, "Dispatching session_create");

		struct ipc_session_create_msg *msg = (struct ipc_session_create_msg *)ipc_command;
		struct ipc_result_reply reply = {0};


		reply.result = ipc_handle_session_create(ics,
		                                         &msg->xsi,
		                                         msg->create_native_compositor);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SESSION_POLL_EVENTS: {
		IPC_TRACE(ics->server, "Dispatching session_poll_events");

		struct ipc_session_poll_events_reply reply = {0};


		reply.result = ipc_handle_session_poll_events(ics,
		                                              &reply.event);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SESSION_BEGIN: {
		IPC_TRACE(ics->server, "Dispatching session_begin");

		struct ipc_result_reply reply = {0};


		reply.result = ipc_handle_session_begin(ics);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SESSION_END: {
		IPC_TRACE(ics->server, "Dispatching session_end");

		struct ipc_result_reply reply = {0};


		reply.result = ipc_handle_session_end(ics);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SESSION_DESTROY: {
		IPC_TRACE(ics->server, "Dispatching session_destroy");

		struct ipc_result_reply reply = {0};


		reply.result = ipc_handle_session_destroy(ics);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SPACE_CREATE_SEMANTIC_IDS: {
		IPC_TRACE(ics->server, "Dispatching space_create_semantic_ids");

		struct ipc_space_create_semantic_ids_reply reply = {0};


		reply.result = ipc_handle_space_create_semantic_ids(ics,
		                                                    &reply.root_id,
		                                                    &reply.view_id,
		                                                    &reply.local_id,
		                                                    &reply.local_floor_id,
		                                                    &reply.stage_id,
		                                                    &reply.unbounded_id);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SPACE_CREATE_OFFSET: {
		IPC_TRACE(ics->server, "Dispatching space_create_offset");

		struct ipc_space_create_offset_msg *msg = (struct ipc_space_create_offset_msg *)ipc_command;
		struct ipc_space_create_offset_reply reply = {0};


		reply.result = ipc_handle_space_create_offset(ics,
		                                              msg->parent_id,
		                                              &msg->offset,
		                                              &reply.space_id);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SPACE_CREATE_POSE: {
		IPC_TRACE(ics->server, "Dispatching space_create_pose");

		struct ipc_space_create_pose_msg *msg = (struct ipc_space_create_pose_msg *)ipc_command;
		struct ipc_space_create_pose_reply reply = {0};


		reply.result = ipc_handle_space_create_pose(ics,
		                                            msg->xdev_id,
		                                            msg->name,
		                                            &reply.space_id);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SPACE_LOCATE_SPACE: {
		IPC_TRACE(ics->server, "Dispatching space_locate_space");

		struct ipc_space_locate_space_msg *msg = (struct ipc_space_locate_space_msg *)ipc_command;
		struct ipc_space_locate_space_reply reply = {0};


		reply.result = ipc_handle_space_locate_space(ics,
		                                             msg->base_space_id,
		                                             &msg->base_offset,
		                                             msg->at_timestamp,
		                                             msg->space_id,
		                                             &msg->offset,
		                                             &reply.relation);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SPACE_LOCATE_SPACES: {
		IPC_TRACE(ics->server, "Dispatching space_locate_spaces");

		struct ipc_space_locate_spaces_msg *msg = (struct ipc_space_locate_spaces_msg *)ipc_command;
		// No return arguments

		xrt_result_t xret = ipc_handle_space_locate_spaces(ics,
		                                                   msg->base_space_id,
		                                                   &msg->base_offset,
		                                                   msg->space_count,
		                                                   msg->at_timestamp);

		return xret;
	}
	case IPC_SPACE_LOCATE_DEVICE: {
		IPC_TRACE(ics->server, "Dispatching space_locate_device");

		struct ipc_space_locate_device_msg *msg = (struct ipc_space_locate_device_msg *)ipc_command;
		struct ipc_space_locate_device_reply reply = {0};


		reply.result = ipc_handle_space_locate_device(ics,
		                                              msg->base_space_id,
		                                              &msg->base_offset,
		                                              msg->at_timestamp,
		                                              msg->xdev_id,
		                                              &reply.relation);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SPACE_DESTROY: {
		IPC_TRACE(ics->server, "Dispatching space_destroy");

		struct ipc_space_destroy_msg *msg = (struct ipc_space_destroy_msg *)ipc_command;
		struct ipc_result_reply reply = {0};


		reply.result = ipc_handle_space_destroy(ics,
		                                        msg->space_id);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SPACE_MARK_REF_SPACE_IN_USE: {
		IPC_TRACE(ics->server, "Dispatching space_mark_ref_space_in_use");

		struct ipc_space_mark_ref_space_in_use_msg *msg = (struct ipc_space_mark_ref_space_in_use_msg *)ipc_command;
		struct ipc_result_reply reply = {0};


		reply.result = ipc_handle_space_mark_ref_space_in_use(ics,
		                                                      msg->type);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SPACE_UNMARK_REF_SPACE_IN_USE: {
		IPC_TRACE(ics->server, "Dispatching space_unmark_ref_space_in_use");

		struct ipc_space_unmark_ref_space_in_use_msg *msg = (struct ipc_space_unmark_ref_space_in_use_msg *)ipc_command;
		struct ipc_result_reply reply = {0};


		reply.result = ipc_handle_space_unmark_ref_space_in_use(ics,
		                                                        msg->type);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SPACE_RECENTER_LOCAL_SPACES: {
		IPC_TRACE(ics->server, "Dispatching space_recenter_local_spaces");

		struct ipc_result_reply reply = {0};


		reply.result = ipc_handle_space_recenter_local_spaces(ics);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SPACE_GET_TRACKING_ORIGIN_OFFSET: {
		IPC_TRACE(ics->server, "Dispatching space_get_tracking_origin_offset");

		struct ipc_space_get_tracking_origin_offset_msg *msg = (struct ipc_space_get_tracking_origin_offset_msg *)ipc_command;
		struct ipc_space_get_tracking_origin_offset_reply reply = {0};


		reply.result = ipc_handle_space_get_tracking_origin_offset(ics,
		                                                           msg->origin_id,
		                                                           &reply.offset);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SPACE_SET_TRACKING_ORIGIN_OFFSET: {
		IPC_TRACE(ics->server, "Dispatching space_set_tracking_origin_offset");

		struct ipc_space_set_tracking_origin_offset_msg *msg = (struct ipc_space_set_tracking_origin_offset_msg *)ipc_command;
		struct ipc_result_reply reply = {0};


		reply.result = ipc_handle_space_set_tracking_origin_offset(ics,
		                                                           msg->origin_id,
		                                                           &msg->offset);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SPACE_GET_REFERENCE_SPACE_OFFSET: {
		IPC_TRACE(ics->server, "Dispatching space_get_reference_space_offset");

		struct ipc_space_get_reference_space_offset_msg *msg = (struct ipc_space_get_reference_space_offset_msg *)ipc_command;
		struct ipc_space_get_reference_space_offset_reply reply = {0};


		reply.result = ipc_handle_space_get_reference_space_offset(ics,
		                                                           msg->type,
		                                                           &reply.offset);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SPACE_SET_REFERENCE_SPACE_OFFSET: {
		IPC_TRACE(ics->server, "Dispatching space_set_reference_space_offset");

		struct ipc_space_set_reference_space_offset_msg *msg = (struct ipc_space_set_reference_space_offset_msg *)ipc_command;
		struct ipc_result_reply reply = {0};


		reply.result = ipc_handle_space_set_reference_space_offset(ics,
		                                                           msg->type,
		                                                           &msg->offset);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_COMPOSITOR_GET_INFO: {
		IPC_TRACE(ics->server, "Dispatching compositor_get_info");

		struct ipc_compositor_get_info_reply reply = {0};


		reply.result = ipc_handle_compositor_get_info(ics,
		                                              &reply.info);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_COMPOSITOR_PREDICT_FRAME: {
		IPC_TRACE(ics->server, "Dispatching compositor_predict_frame");

		struct ipc_compositor_predict_frame_reply reply = {0};


		reply.result = ipc_handle_compositor_predict_frame(ics,
		                                                   &reply.frame_id,
		                                                   &reply.wake_up_time,
		                                                   &reply.predicted_display_time,
		                                                   &reply.predicted_display_period);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_COMPOSITOR_WAIT_WOKE: {
		IPC_TRACE(ics->server, "Dispatching compositor_wait_woke");

		struct ipc_compositor_wait_woke_msg *msg = (struct ipc_compositor_wait_woke_msg *)ipc_command;
		struct ipc_result_reply reply = {0};


		reply.result = ipc_handle_compositor_wait_woke(ics,
		                                               msg->frame_id);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_COMPOSITOR_BEGIN_FRAME: {
		IPC_TRACE(ics->server, "Dispatching compositor_begin_frame");

		struct ipc_compositor_begin_frame_msg *msg = (struct ipc_compositor_begin_frame_msg *)ipc_command;
		struct ipc_result_reply reply = {0};


		reply.result = ipc_handle_compositor_begin_frame(ics,
		                                                 msg->frame_id);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_COMPOSITOR_DISCARD_FRAME: {
		IPC_TRACE(ics->server, "Dispatching compositor_discard_frame");

		struct ipc_compositor_discard_frame_msg *msg = (struct ipc_compositor_discard_frame_msg *)ipc_command;
		struct ipc_result_reply reply = {0};


		reply.result = ipc_handle_compositor_discard_frame(ics,
		                                                   msg->frame_id);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_COMPOSITOR_LAYER_SYNC: {
		IPC_TRACE(ics->server, "Dispatching compositor_layer_sync");

		struct ipc_compositor_layer_sync_msg *msg = (struct ipc_compositor_layer_sync_msg *)ipc_command;
		struct ipc_compositor_layer_sync_reply reply = {0};
		struct ipc_result_reply _sync = {XRT_SUCCESS};
		xrt_graphics_sync_handle_t in_handles[XRT_MAX_IPC_HANDLES] = {0};
		struct ipc_command_msg _handle_msg = {0};

		if (msg->handle_count > XRT_MAX_IPC_HANDLES) {
			return XRT_ERROR_IPC_FAILURE;
		}

		xrt_result_t sync_result = ipc_send((struct ipc_message_channel *)&ics->imc,
		                                    &_sync,
		                                    sizeof(_sync));
		if (sync_result != XRT_SUCCESS) {
			return sync_result;
		}

		xrt_result_t receive_handle_result = ipc_receive_handles_graphics_sync((struct ipc_message_channel *)&ics->imc,
		                                                                       &_handle_msg,
		                                                                       sizeof(_handle_msg),
		                                                                       in_handles,
		                                                                       msg->handle_count);
		if (receive_handle_result != XRT_SUCCESS) {
			return receive_handle_result;
		}
		if (_handle_msg.cmd != IPC_COMPOSITOR_LAYER_SYNC) {
			return XRT_ERROR_IPC_FAILURE;
		}

		reply.result = ipc_handle_compositor_layer_sync(ics,
		                                                msg->slot_id,
		                                                &reply.free_slot_id,
		                                                &in_handles[0],
		                                                msg->handle_count);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_COMPOSITOR_LAYER_SYNC_WITH_SEMAPHORE: {
		IPC_TRACE(ics->server, "Dispatching compositor_layer_sync_with_semaphore");

		struct ipc_compositor_layer_sync_with_semaphore_msg *msg = (struct ipc_compositor_layer_sync_with_semaphore_msg *)ipc_command;
		struct ipc_compositor_layer_sync_with_semaphore_reply reply = {0};


		reply.result = ipc_handle_compositor_layer_sync_with_semaphore(ics,
		                                                               msg->slot_id,
		                                                               msg->semaphore_id,
		                                                               msg->semaphore_value,
		                                                               &reply.free_slot_id);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_COMPOSITOR_SET_PERFORMANCE_LEVEL: {
		IPC_TRACE(ics->server, "Dispatching compositor_set_performance_level");

		struct ipc_compositor_set_performance_level_msg *msg = (struct ipc_compositor_set_performance_level_msg *)ipc_command;
		struct ipc_result_reply reply = {0};


		reply.result = ipc_handle_compositor_set_performance_level(ics,
		                                                           msg->domain,
		                                                           msg->level);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_COMPOSITOR_SET_THREAD_HINT: {
		IPC_TRACE(ics->server, "Dispatching compositor_set_thread_hint");

		struct ipc_compositor_set_thread_hint_msg *msg = (struct ipc_compositor_set_thread_hint_msg *)ipc_command;
		struct ipc_result_reply reply = {0};


		reply.result = ipc_handle_compositor_set_thread_hint(ics,
		                                                     msg->hint,
		                                                     msg->thread_id);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_COMPOSITOR_GET_DISPLAY_REFRESH_RATE: {
		IPC_TRACE(ics->server, "Dispatching compositor_get_display_refresh_rate");

		struct ipc_compositor_get_display_refresh_rate_reply reply = {0};


		reply.result = ipc_handle_compositor_get_display_refresh_rate(ics,
		                                                              &reply.out_display_refresh_rate_hz);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_COMPOSITOR_REQUEST_DISPLAY_REFRESH_RATE: {
		IPC_TRACE(ics->server, "Dispatching compositor_request_display_refresh_rate");

		struct ipc_compositor_request_display_refresh_rate_msg *msg = (struct ipc_compositor_request_display_refresh_rate_msg *)ipc_command;
		struct ipc_result_reply reply = {0};


		reply.result = ipc_handle_compositor_request_display_refresh_rate(ics,
		                                                                  msg->display_refresh_rate_hz);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_COMPOSITOR_GET_REFERENCE_BOUNDS_RECT: {
		IPC_TRACE(ics->server, "Dispatching compositor_get_reference_bounds_rect");

		struct ipc_compositor_get_reference_bounds_rect_msg *msg = (struct ipc_compositor_get_reference_bounds_rect_msg *)ipc_command;
		struct ipc_compositor_get_reference_bounds_rect_reply reply = {0};


		reply.result = ipc_handle_compositor_get_reference_bounds_rect(ics,
		                                                               msg->reference_space_type,
		                                                               &reply.bounds);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SWAPCHAIN_GET_PROPERTIES: {
		IPC_TRACE(ics->server, "Dispatching swapchain_get_properties");

		struct ipc_swapchain_get_properties_msg *msg = (struct ipc_swapchain_get_properties_msg *)ipc_command;
		struct ipc_swapchain_get_properties_reply reply = {0};


		reply.result = ipc_handle_swapchain_get_properties(ics,
		                                                   &msg->info,
		                                                   &reply.xsccp);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SWAPCHAIN_CREATE: {
		IPC_TRACE(ics->server, "Dispatching swapchain_create");

		struct ipc_swapchain_create_msg *msg = (struct ipc_swapchain_create_msg *)ipc_command;
		struct ipc_swapchain_create_reply reply = {0};
		xrt_graphics_buffer_handle_t handles[XRT_MAX_IPC_HANDLES] = {0};
		uint32_t handle_count = {0};


		reply.result = ipc_handle_swapchain_create(ics,
		                                           &msg->info,
		                                           &reply.id,
		                                           &reply.image_count,
		                                           &reply.size,
		                                           &reply.use_dedicated_allocation,
		                                           XRT_MAX_IPC_HANDLES,
		                                           handles,
		                                           &handle_count);

		xrt_result_t xret = ipc_send_handles_graphics_buffer((struct ipc_message_channel *)&ics->imc,
		                                                     &reply,
		                                                     sizeof(reply),
		                                                     handles,
		                                                     handle_count);
		return xret;
	}
	case IPC_COMPOSITOR_CREATE_PASSTHROUGH: {
		IPC_TRACE(ics->server, "Dispatching compositor_create_passthrough");

		struct ipc_compositor_create_passthrough_msg *msg = (struct ipc_compositor_create_passthrough_msg *)ipc_command;
		struct ipc_result_reply reply = {0};


		reply.result = ipc_handle_compositor_create_passthrough(ics,
		                                                        &msg->info);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_COMPOSITOR_CREATE_PASSTHROUGH_LAYER: {
		IPC_TRACE(ics->server, "Dispatching compositor_create_passthrough_layer");

		struct ipc_compositor_create_passthrough_layer_msg *msg = (struct ipc_compositor_create_passthrough_layer_msg *)ipc_command;
		struct ipc_result_reply reply = {0};


		reply.result = ipc_handle_compositor_create_passthrough_layer(ics,
		                                                              &msg->info);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_COMPOSITOR_DESTROY_PASSTHROUGH: {
		IPC_TRACE(ics->server, "Dispatching compositor_destroy_passthrough");

		struct ipc_result_reply reply = {0};


		reply.result = ipc_handle_compositor_destroy_passthrough(ics);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SWAPCHAIN_IMPORT: {
		IPC_TRACE(ics->server, "Dispatching swapchain_import");

		struct ipc_swapchain_import_msg *msg = (struct ipc_swapchain_import_msg *)ipc_command;
		struct ipc_swapchain_import_reply reply = {0};
		struct ipc_result_reply _sync = {XRT_SUCCESS};
		xrt_graphics_buffer_handle_t in_handles[XRT_MAX_IPC_HANDLES] = {0};
		struct ipc_command_msg _handle_msg = {0};

		if (msg->handle_count > XRT_MAX_IPC_HANDLES) {
			return XRT_ERROR_IPC_FAILURE;
		}

		xrt_result_t sync_result = ipc_send((struct ipc_message_channel *)&ics->imc,
		                                    &_sync,
		                                    sizeof(_sync));
		if (sync_result != XRT_SUCCESS) {
			return sync_result;
		}

		xrt_result_t receive_handle_result = ipc_receive_handles_graphics_buffer((struct ipc_message_channel *)&ics->imc,
		                                                                         &_handle_msg,
		                                                                         sizeof(_handle_msg),
		                                                                         in_handles,
		                                                                         msg->handle_count);
		if (receive_handle_result != XRT_SUCCESS) {
			return receive_handle_result;
		}
		if (_handle_msg.cmd != IPC_SWAPCHAIN_IMPORT) {
			return XRT_ERROR_IPC_FAILURE;
		}

		reply.result = ipc_handle_swapchain_import(ics,
		                                           &msg->info,
		                                           &msg->args,
		                                           &reply.id,
		                                           &in_handles[0],
		                                           msg->handle_count);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SWAPCHAIN_WAIT_IMAGE: {
		IPC_TRACE(ics->server, "Dispatching swapchain_wait_image");

		struct ipc_swapchain_wait_image_msg *msg = (struct ipc_swapchain_wait_image_msg *)ipc_command;
		struct ipc_result_reply reply = {0};


		reply.result = ipc_handle_swapchain_wait_image(ics,
		                                               msg->id,
		                                               msg->timeout_ns,
		                                               msg->index);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SWAPCHAIN_ACQUIRE_IMAGE: {
		IPC_TRACE(ics->server, "Dispatching swapchain_acquire_image");

		struct ipc_swapchain_acquire_image_msg *msg = (struct ipc_swapchain_acquire_image_msg *)ipc_command;
		struct ipc_swapchain_acquire_image_reply reply = {0};


		reply.result = ipc_handle_swapchain_acquire_image(ics,
		                                                  msg->id,
		                                                  &reply.index);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SWAPCHAIN_RELEASE_IMAGE: {
		IPC_TRACE(ics->server, "Dispatching swapchain_release_image");

		struct ipc_swapchain_release_image_msg *msg = (struct ipc_swapchain_release_image_msg *)ipc_command;
		struct ipc_result_reply reply = {0};


		reply.result = ipc_handle_swapchain_release_image(ics,
		                                                  msg->id,
		                                                  msg->index);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_SWAPCHAIN_DESTROY: {
		IPC_TRACE(ics->server, "Dispatching swapchain_destroy");

		struct ipc_swapchain_destroy_msg *msg = (struct ipc_swapchain_destroy_msg *)ipc_command;
		struct ipc_result_reply reply = {0};


		reply.result = ipc_handle_swapchain_destroy(ics,
		                                            msg->id);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_COMPOSITOR_SEMAPHORE_CREATE: {
		IPC_TRACE(ics->server, "Dispatching compositor_semaphore_create");

		struct ipc_compositor_semaphore_create_reply reply = {0};
		xrt_graphics_sync_handle_t handles[XRT_MAX_IPC_HANDLES] = {0};
		uint32_t handle_count = {0};


		reply.result = ipc_handle_compositor_semaphore_create(ics,
		                                                      &reply.id,
		                                                      XRT_MAX_IPC_HANDLES,
		                                                      handles,
		                                                      &handle_count);

		xrt_result_t xret = ipc_send_handles_graphics_sync((struct ipc_message_channel *)&ics->imc,
		                                                   &reply,
		                                                   sizeof(reply),
		                                                   handles,
		                                                   handle_count);
		return xret;
	}
	case IPC_COMPOSITOR_SEMAPHORE_DESTROY: {
		IPC_TRACE(ics->server, "Dispatching compositor_semaphore_destroy");

		struct ipc_compositor_semaphore_destroy_msg *msg = (struct ipc_compositor_semaphore_destroy_msg *)ipc_command;
		struct ipc_result_reply reply = {0};


		reply.result = ipc_handle_compositor_semaphore_destroy(ics,
		                                                       msg->id);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_DEVICE_UPDATE_INPUT: {
		IPC_TRACE(ics->server, "Dispatching device_update_input");

		struct ipc_device_update_input_msg *msg = (struct ipc_device_update_input_msg *)ipc_command;
		struct ipc_result_reply reply = {0};


		reply.result = ipc_handle_device_update_input(ics,
		                                              msg->id);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_DEVICE_GET_TRACKED_POSE: {
		IPC_TRACE(ics->server, "Dispatching device_get_tracked_pose");

		struct ipc_device_get_tracked_pose_msg *msg = (struct ipc_device_get_tracked_pose_msg *)ipc_command;
		struct ipc_device_get_tracked_pose_reply reply = {0};


		reply.result = ipc_handle_device_get_tracked_pose(ics,
		                                                  msg->id,
		                                                  msg->name,
		                                                  msg->at_timestamp,
		                                                  &reply.relation);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_DEVICE_GET_HAND_TRACKING: {
		IPC_TRACE(ics->server, "Dispatching device_get_hand_tracking");

		struct ipc_device_get_hand_tracking_msg *msg = (struct ipc_device_get_hand_tracking_msg *)ipc_command;
		struct ipc_device_get_hand_tracking_reply reply = {0};


		reply.result = ipc_handle_device_get_hand_tracking(ics,
		                                                   msg->id,
		                                                   msg->name,
		                                                   msg->at_timestamp,
		                                                   &reply.value,
		                                                   &reply.timestamp);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_DEVICE_GET_VIEW_POSES: {
		IPC_TRACE(ics->server, "Dispatching device_get_view_poses");

		struct ipc_device_get_view_poses_msg *msg = (struct ipc_device_get_view_poses_msg *)ipc_command;
		// No return arguments

		xrt_result_t xret = ipc_handle_device_get_view_poses(ics,
		                                                     msg->id,
		                                                     &msg->fallback_eye_relation,
		                                                     msg->at_timestamp_ns,
		                                                     msg->view_count);

		return xret;
	}
	case IPC_DEVICE_GET_VIEW_POSES_2: {
		IPC_TRACE(ics->server, "Dispatching device_get_view_poses_2");

		struct ipc_device_get_view_poses_2_msg *msg = (struct ipc_device_get_view_poses_2_msg *)ipc_command;
		struct ipc_device_get_view_poses_2_reply reply = {0};


		reply.result = ipc_handle_device_get_view_poses_2(ics,
		                                                  msg->id,
		                                                  &msg->fallback_eye_relation,
		                                                  msg->at_timestamp_ns,
		                                                  msg->view_count,
		                                                  &reply.info);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_DEVICE_GET_PQW_STATE: {
		IPC_TRACE(ics->server, "Dispatching device_get_pqw_state");

		struct ipc_device_get_pqw_state_msg *msg = (struct ipc_device_get_pqw_state_msg *)ipc_command;
		struct ipc_device_get_pqw_state_reply reply = {0};


		reply.result = ipc_handle_device_get_pqw_state(ics,
		                                               msg->id,
		                                               msg->at_timestamp_ns,
		                                               msg->view_id,
		                                               &reply.info);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_DEVICE_GET_OVERRIDE_SCALING: {
		IPC_TRACE(ics->server, "Dispatching device_get_override_scaling");

		struct ipc_device_get_override_scaling_msg *msg = (struct ipc_device_get_override_scaling_msg *)ipc_command;
		struct ipc_device_get_override_scaling_reply reply = {0};


		reply.result = ipc_handle_device_get_override_scaling(ics,
		                                                      msg->id,
		                                                      msg->at_timestamp_ns,
		                                                      &reply.info);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_DEVICE_COMPUTE_DISTORTION: {
		IPC_TRACE(ics->server, "Dispatching device_compute_distortion");

		struct ipc_device_compute_distortion_msg *msg = (struct ipc_device_compute_distortion_msg *)ipc_command;
		struct ipc_device_compute_distortion_reply reply = {0};


		reply.result = ipc_handle_device_compute_distortion(ics,
		                                                    msg->id,
		                                                    msg->view,
		                                                    msg->u,
		                                                    msg->v,
		                                                    &reply.ret,
		                                                    &reply.triplet);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_DEVICE_SET_OUTPUT: {
		IPC_TRACE(ics->server, "Dispatching device_set_output");

		struct ipc_device_set_output_msg *msg = (struct ipc_device_set_output_msg *)ipc_command;
		struct ipc_result_reply reply = {0};


		reply.result = ipc_handle_device_set_output(ics,
		                                            msg->id,
		                                            msg->name,
		                                            &msg->value);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_DEVICE_GET_VISIBILITY_MASK: {
		IPC_TRACE(ics->server, "Dispatching device_get_visibility_mask");

		struct ipc_device_get_visibility_mask_msg *msg = (struct ipc_device_get_visibility_mask_msg *)ipc_command;
		// No return arguments

		xrt_result_t xret = ipc_handle_device_get_visibility_mask(ics,
		                                                          msg->id,
		                                                          msg->type,
		                                                          msg->view_index);

		return xret;
	}
	case IPC_DEVICE_IS_FORM_FACTOR_AVAILABLE: {
		IPC_TRACE(ics->server, "Dispatching device_is_form_factor_available");

		struct ipc_device_is_form_factor_available_msg *msg = (struct ipc_device_is_form_factor_available_msg *)ipc_command;
		struct ipc_device_is_form_factor_available_reply reply = {0};


		reply.result = ipc_handle_device_is_form_factor_available(ics,
		                                                          msg->id,
		                                                          msg->form_factor,
		                                                          &reply.available);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_DEVICE_GET_FACE_TRACKING: {
		IPC_TRACE(ics->server, "Dispatching device_get_face_tracking");

		struct ipc_device_get_face_tracking_msg *msg = (struct ipc_device_get_face_tracking_msg *)ipc_command;
		struct ipc_device_get_face_tracking_reply reply = {0};


		reply.result = ipc_handle_device_get_face_tracking(ics,
		                                                   msg->id,
		                                                   msg->facial_expression_type,
		                                                   msg->at_timestamp_ns,
		                                                   &reply.value);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_DEVICE_GET_BODY_SKELETON: {
		IPC_TRACE(ics->server, "Dispatching device_get_body_skeleton");

		struct ipc_device_get_body_skeleton_msg *msg = (struct ipc_device_get_body_skeleton_msg *)ipc_command;
		struct ipc_device_get_body_skeleton_reply reply = {0};


		reply.result = ipc_handle_device_get_body_skeleton(ics,
		                                                   msg->id,
		                                                   msg->body_tracking_type,
		                                                   &reply.value);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_DEVICE_GET_BODY_JOINTS: {
		IPC_TRACE(ics->server, "Dispatching device_get_body_joints");

		struct ipc_device_get_body_joints_msg *msg = (struct ipc_device_get_body_joints_msg *)ipc_command;
		struct ipc_device_get_body_joints_reply reply = {0};


		reply.result = ipc_handle_device_get_body_joints(ics,
		                                                 msg->id,
		                                                 msg->body_tracking_type,
		                                                 msg->desired_timestamp_ns,
		                                                 &reply.value);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	case IPC_DEVICE_GET_BATTERY_STATUS: {
		IPC_TRACE(ics->server, "Dispatching device_get_battery_status");

		struct ipc_device_get_battery_status_msg *msg = (struct ipc_device_get_battery_status_msg *)ipc_command;
		struct ipc_device_get_battery_status_reply reply = {0};


		reply.result = ipc_handle_device_get_battery_status(ics,
		                                                    msg->id,
		                                                    &reply.present,
		                                                    &reply.charging,
		                                                    &reply.charge);

		xrt_result_t xret = ipc_send((struct ipc_message_channel *)&ics->imc,
		                             &reply,
		                             sizeof(reply));
		return xret;
	}
	default:
		U_LOG_E("UNHANDLED IPC MESSAGE! %d", *ipc_command);
		return XRT_ERROR_IPC_FAILURE;
	}
}


size_t
ipc_command_size(const enum ipc_command cmd)
{
	switch (cmd) {
	case IPC_INSTANCE_GET_SHM_FD: return sizeof(enum ipc_command);
	case IPC_INSTANCE_DESCRIBE_CLIENT: return sizeof(struct ipc_instance_describe_client_msg);
	case IPC_INSTANCE_IS_SYSTEM_AVAILABLE: return sizeof(enum ipc_command);
	case IPC_SYSTEM_GET_PROPERTIES: return sizeof(enum ipc_command);
	case IPC_SYSTEM_GET_CLIENT_INFO: return sizeof(struct ipc_system_get_client_info_msg);
	case IPC_SYSTEM_GET_CLIENTS: return sizeof(enum ipc_command);
	case IPC_SYSTEM_SET_PRIMARY_CLIENT: return sizeof(struct ipc_system_set_primary_client_msg);
	case IPC_SYSTEM_SET_FOCUSED_CLIENT: return sizeof(struct ipc_system_set_focused_client_msg);
	case IPC_SYSTEM_TOGGLE_IO_CLIENT: return sizeof(struct ipc_system_toggle_io_client_msg);
	case IPC_SYSTEM_TOGGLE_IO_DEVICE: return sizeof(struct ipc_system_toggle_io_device_msg);
	case IPC_SYSTEM_OPAQUE_DATA_SEND: return sizeof(struct ipc_system_opaque_data_send_msg);
	case IPC_SYSTEM_OPAQUE_DATA_RECEIVE: return sizeof(enum ipc_command);
	case IPC_SYSTEM_DEVICES_GET_ROLES: return sizeof(enum ipc_command);
	case IPC_SYSTEM_DEVICES_BEGIN_FEATURE: return sizeof(struct ipc_system_devices_begin_feature_msg);
	case IPC_SYSTEM_DEVICES_END_FEATURE: return sizeof(struct ipc_system_devices_end_feature_msg);
	case IPC_SYSTEM_COMPOSITOR_GET_INFO: return sizeof(enum ipc_command);
	case IPC_SESSION_CREATE: return sizeof(struct ipc_session_create_msg);
	case IPC_SESSION_POLL_EVENTS: return sizeof(enum ipc_command);
	case IPC_SESSION_BEGIN: return sizeof(enum ipc_command);
	case IPC_SESSION_END: return sizeof(enum ipc_command);
	case IPC_SESSION_DESTROY: return sizeof(enum ipc_command);
	case IPC_SPACE_CREATE_SEMANTIC_IDS: return sizeof(enum ipc_command);
	case IPC_SPACE_CREATE_OFFSET: return sizeof(struct ipc_space_create_offset_msg);
	case IPC_SPACE_CREATE_POSE: return sizeof(struct ipc_space_create_pose_msg);
	case IPC_SPACE_LOCATE_SPACE: return sizeof(struct ipc_space_locate_space_msg);
	case IPC_SPACE_LOCATE_SPACES: return sizeof(struct ipc_space_locate_spaces_msg);
	case IPC_SPACE_LOCATE_DEVICE: return sizeof(struct ipc_space_locate_device_msg);
	case IPC_SPACE_DESTROY: return sizeof(struct ipc_space_destroy_msg);
	case IPC_SPACE_MARK_REF_SPACE_IN_USE: return sizeof(struct ipc_space_mark_ref_space_in_use_msg);
	case IPC_SPACE_UNMARK_REF_SPACE_IN_USE: return sizeof(struct ipc_space_unmark_ref_space_in_use_msg);
	case IPC_SPACE_RECENTER_LOCAL_SPACES: return sizeof(enum ipc_command);
	case IPC_SPACE_GET_TRACKING_ORIGIN_OFFSET: return sizeof(struct ipc_space_get_tracking_origin_offset_msg);
	case IPC_SPACE_SET_TRACKING_ORIGIN_OFFSET: return sizeof(struct ipc_space_set_tracking_origin_offset_msg);
	case IPC_SPACE_GET_REFERENCE_SPACE_OFFSET: return sizeof(struct ipc_space_get_reference_space_offset_msg);
	case IPC_SPACE_SET_REFERENCE_SPACE_OFFSET: return sizeof(struct ipc_space_set_reference_space_offset_msg);
	case IPC_COMPOSITOR_GET_INFO: return sizeof(enum ipc_command);
	case IPC_COMPOSITOR_PREDICT_FRAME: return sizeof(enum ipc_command);
	case IPC_COMPOSITOR_WAIT_WOKE: return sizeof(struct ipc_compositor_wait_woke_msg);
	case IPC_COMPOSITOR_BEGIN_FRAME: return sizeof(struct ipc_compositor_begin_frame_msg);
	case IPC_COMPOSITOR_DISCARD_FRAME: return sizeof(struct ipc_compositor_discard_frame_msg);
	case IPC_COMPOSITOR_LAYER_SYNC: return sizeof(struct ipc_compositor_layer_sync_msg);
	case IPC_COMPOSITOR_LAYER_SYNC_WITH_SEMAPHORE: return sizeof(struct ipc_compositor_layer_sync_with_semaphore_msg);
	case IPC_COMPOSITOR_SET_PERFORMANCE_LEVEL: return sizeof(struct ipc_compositor_set_performance_level_msg);
	case IPC_COMPOSITOR_SET_THREAD_HINT: return sizeof(struct ipc_compositor_set_thread_hint_msg);
	case IPC_COMPOSITOR_GET_DISPLAY_REFRESH_RATE: return sizeof(enum ipc_command);
	case IPC_COMPOSITOR_REQUEST_DISPLAY_REFRESH_RATE: return sizeof(struct ipc_compositor_request_display_refresh_rate_msg);
	case IPC_COMPOSITOR_GET_REFERENCE_BOUNDS_RECT: return sizeof(struct ipc_compositor_get_reference_bounds_rect_msg);
	case IPC_SWAPCHAIN_GET_PROPERTIES: return sizeof(struct ipc_swapchain_get_properties_msg);
	case IPC_SWAPCHAIN_CREATE: return sizeof(struct ipc_swapchain_create_msg);
	case IPC_COMPOSITOR_CREATE_PASSTHROUGH: return sizeof(struct ipc_compositor_create_passthrough_msg);
	case IPC_COMPOSITOR_CREATE_PASSTHROUGH_LAYER: return sizeof(struct ipc_compositor_create_passthrough_layer_msg);
	case IPC_COMPOSITOR_DESTROY_PASSTHROUGH: return sizeof(enum ipc_command);
	case IPC_SWAPCHAIN_IMPORT: return sizeof(struct ipc_swapchain_import_msg);
	case IPC_SWAPCHAIN_WAIT_IMAGE: return sizeof(struct ipc_swapchain_wait_image_msg);
	case IPC_SWAPCHAIN_ACQUIRE_IMAGE: return sizeof(struct ipc_swapchain_acquire_image_msg);
	case IPC_SWAPCHAIN_RELEASE_IMAGE: return sizeof(struct ipc_swapchain_release_image_msg);
	case IPC_SWAPCHAIN_DESTROY: return sizeof(struct ipc_swapchain_destroy_msg);
	case IPC_COMPOSITOR_SEMAPHORE_CREATE: return sizeof(enum ipc_command);
	case IPC_COMPOSITOR_SEMAPHORE_DESTROY: return sizeof(struct ipc_compositor_semaphore_destroy_msg);
	case IPC_DEVICE_UPDATE_INPUT: return sizeof(struct ipc_device_update_input_msg);
	case IPC_DEVICE_GET_TRACKED_POSE: return sizeof(struct ipc_device_get_tracked_pose_msg);
	case IPC_DEVICE_GET_HAND_TRACKING: return sizeof(struct ipc_device_get_hand_tracking_msg);
	case IPC_DEVICE_GET_VIEW_POSES: return sizeof(struct ipc_device_get_view_poses_msg);
	case IPC_DEVICE_GET_VIEW_POSES_2: return sizeof(struct ipc_device_get_view_poses_2_msg);
	case IPC_DEVICE_GET_PQW_STATE: return sizeof(struct ipc_device_get_pqw_state_msg);
	case IPC_DEVICE_GET_OVERRIDE_SCALING: return sizeof(struct ipc_device_get_override_scaling_msg);
	case IPC_DEVICE_COMPUTE_DISTORTION: return sizeof(struct ipc_device_compute_distortion_msg);
	case IPC_DEVICE_SET_OUTPUT: return sizeof(struct ipc_device_set_output_msg);
	case IPC_DEVICE_GET_VISIBILITY_MASK: return sizeof(struct ipc_device_get_visibility_mask_msg);
	case IPC_DEVICE_IS_FORM_FACTOR_AVAILABLE: return sizeof(struct ipc_device_is_form_factor_available_msg);
	case IPC_DEVICE_GET_FACE_TRACKING: return sizeof(struct ipc_device_get_face_tracking_msg);
	case IPC_DEVICE_GET_BODY_SKELETON: return sizeof(struct ipc_device_get_body_skeleton_msg);
	case IPC_DEVICE_GET_BODY_JOINTS: return sizeof(struct ipc_device_get_body_joints_msg);
	case IPC_DEVICE_GET_BATTERY_STATUS: return sizeof(struct ipc_device_get_battery_status_msg);
	default:
		U_LOG_E("UNHANDLED IPC COMMAND! %d", cmd);
		return 0;
	}
}

