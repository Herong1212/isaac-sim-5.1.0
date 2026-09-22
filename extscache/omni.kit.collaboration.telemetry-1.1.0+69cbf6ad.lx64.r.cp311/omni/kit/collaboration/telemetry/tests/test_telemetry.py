# Copyright (c) 2022, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import omni.kit.test
import omni.kit.test.teamcity
import omni.structuredlog
import carb.settings
import tempfile
import pathlib
import time
import io
import os
import sys
import json
import datetime
import psutil
import carb
import carb.tokens

import omni.kit.collaboration.telemetry


class TestCollaborationTelemetry(omni.kit.test.AsyncTestCase):  # pragma: no cover
    def setUp(self):
        self._structured_log_settings = omni.structuredlog.IStructuredLogSettings()
        self._control = omni.structuredlog.IStructuredLogControl()
        self._settings = carb.settings.get_settings_interface()
        self.assertIsNotNone(self._control)
        self.assertIsNotNone(self._settings)
        self.assertIsNotNone(self._structured_log_settings)

        # failed to retrieve the IStructuredLogSettings object => fail
        if self._structured_log_settings == None or self._control == None or self._settings == None:
            return

        # make sure to flush the structured log queue now since we're going to be changing the
        # log output path and default log name for this test.  This will ensure that any pending
        # events are flushed to their appropriate log files first.
        self._control.stop()

        # set the log directory and name.
        self._temp_dir = tempfile.TemporaryDirectory()
        self._log_file_name = "omni.kit.collaboration.test.log"
        self._old_log_name = self._structured_log_settings.log_default_name
        self._old_log_path = self._structured_log_settings.log_output_path
        self._structured_log_settings.log_default_name = self._log_file_name
        self._structured_log_settings.log_output_path = self._temp_dir.name

        # piece together the expected name of the log file we'll be watching.
        self._log_path = pathlib.Path(self._temp_dir.name).joinpath(self._log_file_name)

        self.assertEqual(pathlib.Path(self._structured_log_settings.log_default_name), self._log_path)
        self.assertEqual(pathlib.Path(self._structured_log_settings.log_output_path), pathlib.Path(self._temp_dir.name))

    def tearDown(self):
        # nothing to clean up => fail.
        if self._structured_log_settings == None:
            return;

        self._structured_log_settings.log_output_path = self._old_log_path
        self._structured_log_settings.log_default_name = self._old_log_name

        # explicitly clean up the temporary dir.  Note that we need to explicitly clean it up
        # since it can throw an exception on Windows if a file or folder is still locked.  The
        # support for internally ignoring these exceptions isn't added until `tempfile` v3.10
        # and we're using an older version of the package here.
        try:
            self._temp_dir.cleanup()
        except:
            pass

        # explicitly clean up all of our objects so we're not relying on the python GC.
        self._structured_log_settings = None
        self._control = None
        self._settings = None
        self._temp_dir = None
        self._log_file_name = None
        self._old_log_name = None
        self._old_log_path = None
        self._log_path = None

    def _read_log_lines(self, filename, expected_types, session = None, time_delta = -1, log_time_range = 900):
        """
        Reads the events from the expected log file location.  Each log message line is parsed as
        a JSON blob.  The 'data' property of each message is parsed into a dictionary and a list
        of these parsed dictionaries are returned.  The log's header JSON object will also be
        parsed and verified.  The verification includes checking that the log's creation timestamp
        is recent.

        Parameters:
            filename:       The name of the log file to process for events.  This may not be
                            `None`.
            expected_types: A list of event type names that are to be expected in the log file.
                            If an event is found that does not match one of the events in this
                            list, a test will fail.
            session:        An optional session ID string to match to each event.  An event will
                            only be included in the output if its session ID matches this one.
                            This may be `None` or "0" to ignore the session ID matching.  If this
                            is set to "0", the session ID from each event will be added to each
                            event in the output list so that further filtering can occur.
            time_delta:     An optional time delta in seconds used to further filter events from
                            the log file.  Only events that were logged after a point that is
                            this many seconds earlier than the call time will be included in the
                            output.  This may be negative to disable filtering out older events.
            log_time_range: The maximum number of seconds old that the log's creation timestamp
                            in its header may be.  This test may be disabled by settings this
                            value to 0.  If non-zero, this should be set to an absurd range
                            versus the ideal case so that running on slow machines doesn't cause
                            this test to unexpectedly fail.  This defaults to 900s (15m).

        Returns:
            A list of parsed events.  Each event in the list will be a dictionary of the
            properties parsed from that event's 'data' property.  Note that each returned
            event in this list will have had its 'type' and 'session' properties copied
            into it under the property names 'cloudEventsEventType' and 'cloudEventsSessionId'.
            These can be used by the caller to further filter and categorize the events.
        """
        if not os.path.isfile(filename):
            print("failed to find the log file '" + str(filename) + "'.")
            return []

        events = []
        lines = []
        header = {}
        with open(filename, "r") as f:
            lines = f.readlines()

        if time_delta >= 0:
            timestamp = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds = time_delta)

        # walk through all the lines in the file except the first one (the log header).
        for i in range(1, len(lines)):
            line = lines[i]
            try:
                event = json.loads(line)
                self.assertTrue(event["type"] in expected_types)
                msg_time = datetime.datetime.strptime(event["time"], "%Y-%m-%dT%H:%M:%S.%f%z")

                # always add the 'type' and 'session' properties to the output event.  Since the
                # "type" and "session" property names are rather generic and could legitimately
                # be part of the "data" property, we'll rename them to something less generic
                # that the caller can consume.
                event["data"]["cloudEventsEventType"] = event["type"]
                event["data"]["cloudEventsSessionId"] = event["session"]

                if (session == None or session == "0" or event["session"] == session) and (time_delta < 0 or msg_time >= timestamp):
                    events.append(event["data"])

            except json.decoder.JSONDecodeError as e:
                print("failed to parse the line '" + line + "' as JSON {reason = '" + str(e) + "'}")
                pass
            except Exception as e:
                print("error processing the line '" + line + "' as JSON {error = '" + str(e) + "'}")
                raise


        # ****** parse and verify the header line ******
        try:
            header = json.loads(lines[0])
        except json.decoder.JSONDecodeError as e:
            print("failed to parse the header '" + lines[0] + "' as JSON {reason = '" + str(e) + "'}")
            self.assertFalse(True)
        except Exception as e:
            print("error processing the header '" + lines[0] + "' as JSON {error = '" + str(e) + "'}")
            self.assertFalse(True)

        self.assertEqual(header["source"], "omni.structuredlog")
        self.assertIsNotNone(header["version"])

        # make sure the log was created recently.
        if log_time_range > 0:
            timestamp = datetime.datetime.strptime(header["time"], "%Y-%m-%dT%H:%M:%S.%f%z")
            time_diff = datetime.datetime.now(datetime.timezone.utc) - timestamp

            self.assertLess(time_diff.total_seconds(), log_time_range)

        return events

    def _is_event_present(self, events, properties):
        """
        Verifies that all keys in `properties` both exist and have the same values in a
        single event in `events`.

        Parameters:
            events: The set of events that were read from the log file.  These are
                    expected to have been parsed into dictionary objects from the
                    original JSON 'data' property of each event.
            properties: The set of properties to verify are present and match at least
                    one of the events in the log.  All properties must match to a single
                    event in order for this to succeed.

        Returns:
            `True` if all the requested keys match in a single event.
            `False` if no event containing all properties is found.
        """

        # go through each event in the log file and check if it has all the required properties.
        for i in range(len(events)):
            event = events[i]
            matches = True

            # go through each of the required properties and verify they are all present and
            # have the expected value.
            for key, value in properties.items():
                if not key in event:
                    continue

                if event[key] != value:
                    matches = False
                    break

            if matches:
                return True

        return False

    def test_live_edit_events(self):
        """
        Tests sending Schema_omni_kit_collaboration_1_0 events.  Note that since this extension
        is purely a bindings module, no coverage information will be generated unfortunately.
        This does however test the functionality of the bindings module.
        """

        # get the schema object and create the data object that is required to send the event.
        self._telemetry = omni.kit.collaboration.telemetry.Schema_omni_kit_collaboration_1_0()
        event = omni.kit.collaboration.telemetry.Struct_liveEdit_liveEdit()
        self.assertIsNotNone(self._telemetry)
        self.assertIsNotNone(event)

        # send some test events.
        event.id = "purple monkey dishwasher"
        event.action = "join"
        self._telemetry.liveEdit_sendEvent("fudgesicle", event)

        event.id = "spatula lampshade"
        event.action = "leave"
        self._telemetry.liveEdit_sendEvent("peanut butter parfait", event)

        # make sure all the messages are flushed to disk.
        self._control.stop()

        # read the log and verify that all the expected messages are present.
        events = self._read_log_lines(self._log_path,
                                      [
                                          "com.nvidia.omni.kit.collaboration.liveEdit",
                                      ])

        # verify the ordered parameters events.
        self.assertTrue(self._is_event_present(events, {"cloud_link_id" : "fudgesicle", "event" : { "id": "purple monkey dishwasher", "action": "join"}, "event": "live-edit"}))
        self.assertTrue(self._is_event_present(events, {"cloud_link_id" : "peanut butter parfait", "event" : { "id": "spatula lampshade", "action": "leave"}, "event": "live-edit"}))

        # clean up.
        self._telemetry = None
        event = None
