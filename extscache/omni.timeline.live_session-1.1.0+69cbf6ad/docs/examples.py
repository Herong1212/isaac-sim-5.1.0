# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#


# This file shows API usage examples for omni.timeline.live_session

import omni.kit.usd.layers as layers
import omni.timeline.live_session
import omni.usd


class Examples:
    # Example: Watch for connection to live session, then register to presenter changed event and react to it
    def example_presenter_changed_watcher(self):
        usd_context_name: str = ""
        self.usd_context = omni.usd.get_context(usd_context_name)
        live_syncing = layers.get_live_syncing(self.usd_context)
        self.layers = layers.get_layers(self.usd_context)

        self.layers_event_subscription = self.layers.get_event_stream().create_subscription_to_pop(
            self._on_layers_event, name="my_example_sub"
        )
        # Make sure to set self.layers_event_subscription to None somewhere, omitted from the example

    # When a live session is joined, register callback for presenter changed events
    def _on_layers_event(self, event):
        payload = layers.get_layer_event_payload(event)
        if not payload:
            return

        # Only events from root layer session are handled.
        if payload.event_type == layers.LayerEventType.LIVE_SESSION_STATE_CHANGED:
            if not payload.is_layer_influenced(self.usd_context.get_stage_url()):
                return

            # Get the timeline session and register our own callback for presenter changed
            self.timeline_session = omni.timeline.live_session.get_timeline_session()
            if self.timeline_session is not None:
                self.timeline_session.add_presenter_changed_fn(self._on_presenter_changed)
                # Make sure to call session.remove_presenter_changed_fn somewhere, this is omitted here

    # Our callback that is called by the timeline sync extension when the presenter is changed. We get the new user.
    def _on_presenter_changed(self, user: layers.LiveSessionUser):
        print(f'The new Timeline Presenter is {user.user_name}')
        if self.timeline_session.am_i_presenter():
            print('I am the Timeline Presenter!')
        else:
            print('I am a Timeline Listener.')

    # Example: Turn the timeline sync on or off.
    #   For Listeners turning off stops receiving updates and gives them back the ability to control their own timeline.
    #   For the Presenter turning off stops sending updates to Listeners.
    def example_toggle_sync(self):
        timeline_session = omni.timeline.live_session.get_timeline_session()
        if timeline_session is not None:
            syncing = timeline_session.is_sync_enabled()
            if syncing:
                print('Timeline sync is enabled, turning it off')
            else:
                print('Timeline sync is disabled, turning it on')
            timeline_session.enable_sync(not syncing)

    # Example: Subscribe to changes in timeline sync (enabled/disabled)
    def example_enable_sync_changed(self):
        timeline_session = omni.timeline.live_session.get_timeline_session()
        if timeline_session is not None:
            timeline_session.add_enable_sync_changed_fn(self._on_enable_sync_changed)
            # Make sure to call session.remove_enable_sync_changed_fn somewhere, this is omitted here

    def _on_enable_sync_changed(self, enabled: bool):
        print(f'Timeline synchronization was {"enabled" if enabled else "disabled"}')

    # Example: Query the estimated latency from the timeline session
    def example_query_latency(self):
        timeline_session = omni.timeline.live_session.get_timeline_session()
        if timeline_session is not None:
            latency = timeline_session.role.get_latency_estimate()
            print(f'The estimated latency from the Timeline Presenter is {latency}')

    # Example: Register to control request received event
    def example_control_requests(self):
        timeline_session = omni.timeline.live_session.get_timeline_session()
        if timeline_session is not None:
            timeline_session.add_control_request_changed_fn(self._on_control_requests_changed)
            # Make sure to call session.remove_control_request_changed_fn somewhere, this is omitted here

    # Our callback that is called by the timeline sync extension when a user sends or withdraws control request.
    def _on_control_requests_changed(self, user: layers.LiveSessionUser, wants_control: bool):
        if wants_control:
            print(f'User {user.user_name} requested to control the Timeline')
        else:
            print(f'User {user.user_name} withdrew the request to control the Timeline')

        # Print all users who have requested control
        timeline_session = omni.timeline.live_session.get_timeline_session()
        if timeline_session is not None:
            all_users = timeline_session.get_request_controls()
            if len(all_users) == 0:
                print('There are no requests to control the Timeline')
            else:
                print('List of users requested to control the Timeline:')
                for request_user in all_users:
                    print(f'\t{request_user.user_name}')
