# Copyright (c) 2022, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import omni.kit.test
import omni.kit.test.teamcity
import omni.kit.telemetry
import omni.structuredlog
import omni.kit.app
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


class TestITelemetry(omni.kit.test.AsyncTestCase):  # pragma: no cover
    def setUp(self):
        self._structured_log_settings = omni.structuredlog.IStructuredLogSettings()
        self._control = omni.structuredlog.IStructuredLogControl()
        self._settings = carb.settings.get_settings_interface()
        self.assertIsNotNone(self._control)
        self.assertIsNotNone(self._settings)
        self.assertIsNotNone(self._structured_log_settings)

        # failed to retrieve the IStructuredLogSettings object => fail
        if self._structured_log_settings == None or self._control == None:
            return

        # print out the current timestamps and session ID to help with debugging test failures
        # post mortem.
        print("local time at test start is " + str(datetime.datetime.now()) + ", UTC time is " + str(datetime.datetime.now(datetime.timezone.utc)) + ".")
        print("current session ID is " + str(self._structured_log_settings.session_id) + ".")

        # make sure to flush the structured log queue now since we're going to be changing the
        # log output path and default log name for this test.  This will ensure that any pending
        # events are flushed to their appropriate log files first.
        self._control.stop()

        # set the log directory and name.
        self._temp_dir = tempfile.TemporaryDirectory()
        self._log_file_name = "omni.kit.telemetry.test.log"
        self._old_log_name = self._structured_log_settings.log_default_name
        self._old_log_path = self._structured_log_settings.log_output_path
        self._structured_log_settings.log_default_name = self._log_file_name
        self._structured_log_settings.log_output_path = self._temp_dir.name

        # piece together the expected name of the log and privacy files we'll be watching.
        self._log_path = pathlib.Path(self._temp_dir.name).joinpath(self._log_file_name)
        self._privacy_path = pathlib.Path(self._temp_dir.name).joinpath("privacy.toml")

        # put together the expected location for the system info logs.  Unfortunately these
        # logs are created and events added to them before this script gets a chance to modify
        # the log directory and log name.  We'll have to look at the original log location to
        # make sure that it output the system info events as expected.  Also, if the system
        # info logs are accumulating on the system, they may be rotated out over time.  If this
        # happens during the launch of the app on this run, it could split the messages belonging
        # to this session over two log files (presumably we won't be outputting more than 50MiB
        # of system info logs in a single run).  We'll make sure to run over each of the default
        # rotated log names to pull in as much information as possible.
        self._sysinfo_log_paths = [pathlib.Path(self._old_log_path).joinpath("omni.kit.sysinfo.2.log"),
                                   pathlib.Path(self._old_log_path).joinpath("omni.kit.sysinfo.1.log"),
                                   pathlib.Path(self._old_log_path).joinpath("omni.kit.sysinfo.log")]

        self._write_privacy_settings(self._privacy_path)
        self._settings.set_string("/structuredLog/privacySettingsFile", str(self._privacy_path))
        self._structured_log_settings.load_privacy_settings()

        self.assertEqual(pathlib.Path(self._structured_log_settings.log_default_name), self._log_path)
        self.assertEqual(pathlib.Path(self._structured_log_settings.log_output_path), pathlib.Path(self._temp_dir.name))

    def tearDown(self):
        # nothing to clean up => fail.
        if self._structured_log_settings == None:
            return;

        self._structured_log_settings.log_output_path = self._old_log_path
        self._structured_log_settings.log_default_name = self._old_log_name

        # restore the original privacy settings.
        self._settings.set_string("/structuredLog/privacySettingsFile", "")
        self._structured_log_settings.load_privacy_settings()

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
        self._privacy_path = None
        self._sysinfo_log_paths = None
        print("local time at test end is " + str(datetime.datetime.now()) + ", UTC time is " + str(datetime.datetime.now(datetime.timezone.utc)) + ".")

    def _write_privacy_settings(self, filename):
        with io.open(filename, "w") as fp:
            fp.write("[privacy]\n")
            fp.write("performance = true\n")
            fp.write("personalization = true\n")
            fp.write("usage = true\n")
            fp.write("userId = \"test-user@nvidia.com\"\n")
            fp.write("extraDiagnosticDataOptIn = \"externalBuilds\"\n")

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

    def test_itelemetry_generic_events(self):
        """
        Tests sending telemetry events with ITelemetry.send_generic_event().  This version of the
        helper function does not provide default values for the parameters.
        """
        # retrieve the ITelemetry object.
        self._telemetry = omni.kit.telemetry.ITelemetry()
        self.assertIsNotNone(self._telemetry)

        # send some test events with default ordered parameters.
        self._telemetry.send_generic_event("itelemetry_event3_1", 1.025, "apple", None, -1.1275, 5.5)
        self._telemetry.send_generic_event("itelemetry_event3_2", 4.25, None, "boo", 8.75, 14.12875)
        self._telemetry.send_generic_event("itelemetry_event3_3", 17.625, None, None, 1.25, 2.25)
        self._telemetry.send_generic_event("itelemetry_event3_4", 6.75, "orange", "muffin", 76.25, -83.25)

        # send some test events with default named parameters.
        # FIXME!! once python bindings from 'omni.bind' generate parameter names, these tests
        #         should be enabled to get some extra test coverage.  Currently python is
        #         expecting the parameters to be named "arg0", "arg1", etc.
        #self._telemetry.send_generic_event(eventType = "itelemetry_event4_1", duration = 11.025, data1 = "pear", data2 = None, value1 = -3.1275, value2 = 50.5)
        #self._telemetry.send_generic_event(value2 = 23.12875, data2 = "peach", data1 = None, value1 = 10.75, eventType = "itelemetry_event4_2", duration = 14.25)

        # make sure all the messages are flushed to disk.
        self._control.stop()

        # read the log and verify that all the expected messages are present.
        events = self._read_log_lines(self._log_path,
                                      [
                                          "com.nvidia.omni.kit.internal.generic",
                                          "com.nvidia.omni.kit.telemetry.startup",
                                          "com.nvidia.omni.kit.extension.startup"
                                      ])

        # verify the ordered parameters events.
        self.assertTrue(self._is_event_present(events, {"eventType" : "itelemetry_event3_1", "duration" : 1.025, "data1" : "apple", "data2" : "", "value1" : -1.1275, "value2" : 5.5}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "itelemetry_event3_2", "duration" : 4.25, "data1" : "", "data2" : "boo", "value1" : 8.75, "value2" : 14.12875}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "itelemetry_event3_3", "duration" : 17.625, "data1" : "", "data2" : "", "value1" : 1.25, "value2" : 2.25}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "itelemetry_event3_4", "duration" : 6.75, "data1" : "orange", "data2" : "muffin", "value1" : 76.25, "value2" : -83.25}))

        # verify the named parameters events.
        # FIXME!! once python bindings from 'omni.bind' generate parameter names, these tests
        #         should be enabled to get some extra test coverage.
        #self.assertTrue(self._is_event_present(events, {"eventType" : "itelemetry_event4_1", "duration" : 11.025, "data1" : "pear", "data2" : "", "value1" : -3.1275, "value2" : 50.5}))
        #self.assertTrue(self._is_event_present(events, {"eventType" : "itelemetry_event4_2", "duration" : 14.25, "data1" : "", "data2" : "peach", "value1" : 10.75, "value2" : 23.12875}))

        # clean up.
        self._telemetry = None

    def test_itelemetry_custom_events(self):
        """
        Tests sending telemetry events with ITelemetry.send_custom_event().  This version of the
        helper function provides default values for all parameters except the first 'eventType'.
        """
        # retrieve the ITelemetry object.
        self._telemetry = omni.kit.telemetry.ITelemetry()
        self.assertIsNotNone(self._telemetry)

        # send some test events with default ordered parameters.
        self._telemetry.send_custom_event("itelemetry_event")
        self._telemetry.send_custom_event("itelemetry_event_duration", 1.25)
        self._telemetry.send_custom_event("itelemetry_event_data1", 0, "some data1")
        self._telemetry.send_custom_event("itelemetry_event_data2", 0, None, "some data2")
        self._telemetry.send_custom_event("itelemetry_event_value1", 0, None, None, 3.14159)
        self._telemetry.send_custom_event("itelemetry_event_value2", 0, None, None, 0, 2.71828)

        # send some test events with default named parameters.
        self._telemetry.send_custom_event("itelemetry_event2")
        self._telemetry.send_custom_event("itelemetry_event2_duration", duration = 5.05)
        self._telemetry.send_custom_event("itelemetry_event2_data1", data1 = "some data1_2")
        self._telemetry.send_custom_event("itelemetry_event2_data2", data2 = "some data2_2")
        self._telemetry.send_custom_event("itelemetry_event2_value1", value1 = 1.75)
        self._telemetry.send_custom_event("itelemetry_event2_value2", value2 = -14.28)

        # make sure all the messages are flushed to disk.
        self._control.stop()

        # read the log and verify that all the expected messages are present.
        events = self._read_log_lines(self._log_path,
                                      [
                                          "com.nvidia.omni.kit.internal.generic",
                                          "com.nvidia.omni.kit.telemetry.startup",
                                          "com.nvidia.omni.kit.extension.startup"
                                      ])

        # verify the ordered parameters events.
        self.assertTrue(self._is_event_present(events, {"eventType" : "itelemetry_event", "duration" : 0, "data1" : "", "data2" : "", "value1" : 0, "value2" : 0}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "itelemetry_event_duration", "duration" : 1.25, "data1" : "", "data2" : "", "value1" : 0, "value2" : 0}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "itelemetry_event_data1", "duration" : 0, "data1" : "some data1", "data2" : "", "value1" : 0, "value2" : 0}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "itelemetry_event_data2", "duration" : 0, "data1" : "", "data2" : "some data2", "value1" : 0, "value2" : 0}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "itelemetry_event_value1", "duration" : 0, "data1" : "", "data2" : "", "value1" : 3.14159, "value2" : 0}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "itelemetry_event_value2", "duration" : 0, "data1" : "", "data2" : "", "value1" : 0, "value2" : 2.71828}))

        # verify the named parameters events.
        self.assertTrue(self._is_event_present(events, {"eventType" : "itelemetry_event2", "duration" : 0, "data1" : "", "data2" : "", "value1" : 0, "value2" : 0}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "itelemetry_event2_duration", "duration" : 5.05, "data1" : "", "data2" : "", "value1" : 0, "value2" : 0}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "itelemetry_event2_data1", "duration" : 0, "data1" : "some data1_2", "data2" : "", "value1" : 0, "value2" : 0}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "itelemetry_event2_data2", "duration" : 0, "data1" : "", "data2" : "some data2_2", "value1" : 0, "value2" : 0}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "itelemetry_event2_value1", "duration" : 0, "data1" : "", "data2" : "", "value1" : 1.75, "value2" : 0}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "itelemetry_event2_value2", "duration" : 0, "data1" : "", "data2" : "", "value1" : 0, "value2" : -14.28}))

        # clean up.
        self._telemetry = None

    def test_iapp_events(self):
        """
        Tests sending telemetry events with omni.kit.app.send_telemetry_event().  This version
        provides access to generic telemetry events to all systems through IApp.  These events
        will be a no-op if the `omni.kit.telemetry` extension is not loaded.
        """
        # send some test events with default ordered parameters.
        omni.kit.app.send_telemetry_event("iapp_event")
        omni.kit.app.send_telemetry_event("iapp_event_duration", -2.25)
        omni.kit.app.send_telemetry_event("iapp_event_data1", 0, "some app_data1")
        omni.kit.app.send_telemetry_event("iapp_event_data2", 0, None, "some app_data2")
        omni.kit.app.send_telemetry_event("iapp_event_value1", 0, None, None, 1.5)
        omni.kit.app.send_telemetry_event("iapp_event_value2", 0, None, None, 0, 75.5)

        # send some test events with default named parameters.
        omni.kit.app.send_telemetry_event("iapp_event2")
        omni.kit.app.send_telemetry_event("iapp_event2_duration", duration = 81.75)
        omni.kit.app.send_telemetry_event("iapp_event2_data1", data1 = "some app_data1_2")
        omni.kit.app.send_telemetry_event("iapp_event2_data2", data2 = "some app_data2_2")
        omni.kit.app.send_telemetry_event("iapp_event2_value1", value1 = -4.75)
        omni.kit.app.send_telemetry_event("iapp_event2_value2", value2 = 214.5)

        # make sure all the messages are flushed to disk.
        self._control.stop()

        # read the log and verify that all the expected messages are present.
        events = self._read_log_lines(self._log_path,
                                      [
                                          "com.nvidia.omni.kit.internal.generic",
                                          "com.nvidia.omni.kit.telemetry.startup",
                                          "com.nvidia.omni.kit.extension.startup"
                                      ])

        # verify the ordered parameters events.
        self.assertTrue(self._is_event_present(events, {"eventType" : "iapp_event", "duration" : 0, "data1" : "", "data2" : "", "value1" : 0, "value2" : 0}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "iapp_event_duration", "duration" : -2.25, "data1" : "", "data2" : "", "value1" : 0, "value2" : 0}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "iapp_event_data1", "duration" : 0, "data1" : "some app_data1", "data2" : "", "value1" : 0, "value2" : 0}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "iapp_event_data2", "duration" : 0, "data1" : "", "data2" : "some app_data2", "value1" : 0, "value2" : 0}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "iapp_event_value1", "duration" : 0, "data1" : "", "data2" : "", "value1" : 1.5, "value2" : 0}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "iapp_event_value2", "duration" : 0, "data1" : "", "data2" : "", "value1" : 0, "value2" : 75.5}))

        # verify the named parameters events.
        self.assertTrue(self._is_event_present(events, {"eventType" : "iapp_event2", "duration" : 0, "data1" : "", "data2" : "", "value1" : 0, "value2" : 0}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "iapp_event2_duration", "duration" : 81.75, "data1" : "", "data2" : "", "value1" : 0, "value2" : 0}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "iapp_event2_data1", "duration" : 0, "data1" : "some app_data1_2", "data2" : "", "value1" : 0, "value2" : 0}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "iapp_event2_data2", "duration" : 0, "data1" : "", "data2" : "some app_data2_2", "value1" : 0, "value2" : 0}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "iapp_event2_value1", "duration" : 0, "data1" : "", "data2" : "", "value1" : -4.75, "value2" : 0}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "iapp_event2_value2", "duration" : 0, "data1" : "", "data2" : "", "value1" : 0, "value2" : 214.5}))

    def test_transmitter_launch(self):
        """
        Tests that the telemetry transmitter app was successfully launched and is still running.
        This should always be the case in the default configuration.
        """
        transmitter_log = carb.tokens.get_tokens_interface().resolve("${omni_logs}/omni.telemetry.transmitter.log")
        transmitter_exited = False
        transmitter_old_log = False

        # wait for a little bit to allow the transmitter process to fully start up.  This usually
        # takes up to 1s.  We'll wait longer to account for slow machines.  Without waiting, this
        # test will only catch the first few lines of the transmitter's log and it may not have
        # exited yet.  Without checking for the log's early exit message first, this test could
        # get into a race condition with checking for the process still running versus the
        # transmitter process exiting.
        time.sleep(5)

        self.assertIsNotNone(transmitter_log)

        # wait for the log to appear for up to a minute.  This will also account for cases where
        # the transmitter takes a long time to download the schemas package or time out while
        # attempting to download the authentication token from the OV launcher (this failure is
        # expected but normally takes ~1s).
        for i in range(60):
            if os.path.isfile(transmitter_log):
                break

            time.sleep(1)

        # check the transmitter's test log first to see if it ran.  If it did run, it is possible
        # that it shutdown early if the local user hasn't given data consent or the 'privacy.toml'
        # file doesn't exist.  In this case we can check for the shutdown message and avoid
        # testing for the existence of the process later on.  For this test, all we're really
        # interested in is whether we can verify that this process at least attempted to launch
        # the transmitter process.
        self.assertTrue(os.path.isfile(transmitter_log))

        # get the log's modification time and make sure it's very recent.  If it's not recent,
        # that means the transmitter didn't run or wasn't launched by this process.  We'll
        # consider a modification time in the last 60s as being recent.
        log_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(transmitter_log))
        self.assertGreaterEqual(log_mtime, datetime.datetime.now() - datetime.timedelta(seconds = 60))

        lines = []
        with io.open(transmitter_log, "r") as f:
            lines = f.readlines()

        for line in lines:
            # check if the disabled consent message was printed to the log.  This means that the
            # transmitter exited early because either the user did not give consent to any of
            # the data categories or the 'privacy.toml' file is missing.  However, in this case
            # we did verify that the transmitter process did actually run.
            if "consent was disabled for all categories - exiting" in line:
                transmitter_exited = True

            # check if the transmitter exited naturally on its own.  This means that this log
            # belonged to an older instance of the transmitter that was launched by another
            # process.  This message should not be present in the log belonging to the transmitter
            # process that was launched by this process since the existence of this process itself
            # will keep the transmitter alive.
            if "all clients have exited - shutting down" in line:
                transmitter_old_log = True

        # make sure there wasn't a natural shutdown present in the log.  If this is found, that
        # means that log was created by a previous instances of the transmitter, not the one
        # that was launched by this process (since this process would hold the transmitter
        # open).
        self.assertFalse(transmitter_old_log)


        # the transmitter process has not exited yet according to its log => scan the running
        #   processes to make sure it's actually running.  Note that this is safe to do since
        #   this process itself will be keeping the transmitter from exiting now that we know
        #   it didn't exit early during its startup.
        if not transmitter_exited:
            transmitter_count = 0

            # walk the process list in the table and count how many transmitter processes are running.
            for proc in psutil.process_iter():
                try:
                    if "omni.telemetry.transmitter" in proc.name().lower():
                        print("found the running process '" + proc.name() + "' (" + str(proc.pid) + ").")
                        transmitter_count = transmitter_count + 1

                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                    print("invalid process found {e = '" + str(e) + "'}")
                    pass

            # make sure only a single telemetry transmitter is running.
            self.assertEqual(transmitter_count, 1)

    def test_log_redirection(self):
        """
        Tests that the log message redirection works as expected.
        """
        # save the original settings for all the log channels locally so we can restore
        # them later.
        logging_settings = self._settings.create_dictionary_from_settings("/telemetry/logging")

        def log_fatal(msg):
            """
            Helper function to provide functionality to the 'CARB_LOG_FATAL()' operation from
            python.  This isn't provided in the carb logging bindings because in theory we
            should never get into a situation where a fatal operation can be performed from
            the python side.  However, for the purposes of this test, we need to be able to
            produce fatal log messages.
            """
            file, lno, func, mod = carb._get_caller_info()
            carb.log(mod, carb.logging.LEVEL_FATAL, file, func, lno, msg)

        def get_function_name():
            """
            Retrieves the name of the calling function.
            """
            f = sys._getframe(1)
            if f is None or not hasattr(f, "f_code"):
                return "(unknown function)"

            return f.f_code.co_name

        # write some test log messages.
        carb.log_verbose("verbose log message 1") # should be missing in the log.
        carb.log_info("info log message 2")       # should be missing in the log.
        carb.log_warn("warn log message 3")       # should be missing in the log.
        carb.log_error("error log message 4")     # should be found in the log.
        log_fatal("fatal log message 5")          # should be found in the log.

        # adjust the settings and write more log messages.
        self._settings.destroy_item("/telemetry/logging/warnFilter")
        self._settings.destroy_item("/telemetry/logging/errorFilter")
        self._settings.destroy_item("/telemetry/logging/fatalFilter")
        carb.log_verbose("verbose log message 6") # should be missing in the log.
        carb.log_info("info log message 7")       # should be missing in the log.
        carb.log_warn("warn log message 8")       # should be found in the log.
        carb.log_error("error log message 9")     # should be found in the log.
        log_fatal("fatal log message 10")         # should be found in the log.

        # adjust the settings again and write more log messages.
        self._settings.set_string_array("/telemetry/logging/warnFilter", [".* message .*"])
        self._settings.set_string_array("/telemetry/logging/errorFilter", [".* log .*"])
        self._settings.set_string_array("/telemetry/logging/fatalFilter", [".*"])
        carb.log_verbose("verbose log message 11")    # should be missing in the log.
        carb.log_verbose("verbose apple muffin 11b")  # should be missing in the log.
        carb.log_info("info log message 12")          # should be missing in the log.
        carb.log_info("info apple muffin 12b")        # should be missing in the log.
        carb.log_warn("warn log message 13")          # should be missing in the log.
        carb.log_warn("warn apple muffin 13b")        # should be found in the log.
        carb.log_error("error log message 14")        # should be missing in the log.
        carb.log_error("error apple muffin 14b")      # should be found in the log.
        log_fatal("fatal log message 15")             # should be missing in the log.
        log_fatal("fatal apple muffin 15b")           # should be missing in the log.

        # flush the log queue and read the log file.
        self._control.stop()

        events = self._read_log_lines(self._log_path,
                                      [
                                          "omni.kit.logging.message",
                                          "com.nvidia.omni.kit.telemetry.startup",
                                          "com.nvidia.omni.kit.extension.startup"
                                      ])
        func_name = get_function_name()

        # verify that the expected log messages show up in the log.
        self.assertFalse(self._is_event_present(events, {"functionName" : func_name, "level" : "verbose", "message" : "verbose log message 1"}))
        self.assertFalse(self._is_event_present(events, {"functionName" : func_name, "level" : "info", "message" : "info log message 2"}))
        self.assertFalse(self._is_event_present(events, {"functionName" : func_name, "level" : "warn", "message" : "warn log message 3"}))
        self.assertTrue(self._is_event_present(events,  {"functionName" : func_name, "level" : "error", "message" : "error log message 4"}))
        self.assertTrue(self._is_event_present(events,  {"functionName" : func_name, "level" : "fatal", "message" : "fatal log message 5"}))

        self.assertFalse(self._is_event_present(events, {"functionName" : func_name, "level" : "verbose", "message" : "verbose log message 6"}))
        self.assertFalse(self._is_event_present(events, {"functionName" : func_name, "level" : "info", "message" : "info log message 7"}))
        self.assertTrue(self._is_event_present(events,  {"functionName" : func_name, "level" : "warn", "message" : "warn log message 8"}))
        self.assertTrue(self._is_event_present(events,  {"functionName" : func_name, "level" : "error", "message" : "error log message 9"}))
        self.assertTrue(self._is_event_present(events,  {"functionName" : func_name, "level" : "fatal", "message" : "fatal log message 10"}))

        self.assertFalse(self._is_event_present(events, {"functionName" : func_name, "level" : "verbose", "message" : "verbose log message 11"}))
        self.assertFalse(self._is_event_present(events, {"functionName" : func_name, "level" : "verbose", "message" : "verbose apple muffin 11b"}))
        self.assertFalse(self._is_event_present(events, {"functionName" : func_name, "level" : "info", "message" : "info log message 12"}))
        self.assertFalse(self._is_event_present(events, {"functionName" : func_name, "level" : "info", "message" : "info apple muffin 12b"}))
        self.assertFalse(self._is_event_present(events, {"functionName" : func_name, "level" : "warn", "message" : "warn log message 13"}))
        self.assertTrue(self._is_event_present(events,  {"functionName" : func_name, "level" : "warn", "message" : "warn apple muffin 13b"}))
        self.assertFalse(self._is_event_present(events, {"functionName" : func_name, "level" : "error", "message" : "error log message 14"}))
        self.assertTrue(self._is_event_present(events,  {"functionName" : func_name, "level" : "error", "message" : "error apple muffin 14b"}))
        self.assertFalse(self._is_event_present(events, {"functionName" : func_name, "level" : "fatal", "message" : "fatal log message 15"}))
        self.assertFalse(self._is_event_present(events, {"functionName" : func_name, "level" : "fatal", "message" : "fatal apple muffin 15b"}))


        # restore the original logging redirection settings.  Note that calling update() with
        # OVERWRITE doesn't actually overwrite array values.  It instead only replaces the items
        # in the array that are also present in the new array.  If the old array was longer, the
        # additional array items from the old value still exist after the update.  To work around
        # this and have 'replace' behaviour instead of just 'overwrite', we need to delete the
        # old array first.
        self._settings.destroy_item("/telemetry/logging/warnFilter")
        self._settings.destroy_item("/telemetry/logging/errorFilter")
        self._settings.destroy_item("/telemetry/logging/fatalFilter")
        self._settings.update("/telemetry/logging", logging_settings, "", carb.dictionary.UpdateAction.OVERWRITE)

    def test_sysinfo_messages(self):
        """
        Test whether the system info messages were written out when the 'omni.kit.telemetry'
        extension was loaded.  Note that this happens when the `omni.kit.telemetry` extension
        loads and would have happened long before this script started running so we unfortunately
        can't redirect its output to a new log or log directory.  However, we can find the log
        it did go to (in its original location) and verify that some new system info events
        were written into it in the last few seconds or minutes.
        """

        # on a system with attached (active) displays, we should expect 4 events - 'cpu', 'os',
        # 'display', and 'displayOverview'.  However, on headless systems (like some TC agents)
        # there may not be displays to speak of so we'll just ignore them.
        expected_count = 2

        # stop the queue to ensure all events are flushed to disk.
        self._control.stop()

        # make sure that at least one log message from a recent session was written to the
        # system info log.  Note that if the local user doesn't have its 'privacy.toml' file
        # present on disk or the user hasn't given consent for 'usage' data, the retrieved
        # session ID will be 0 and we won't be able to filter based on session ID.  This will
        # be the case on most or all test agent machines.  To work around this, we'll also
        # make sure to only grab the events from a recent period (several minutes in this case).
        for sysinfo_log_path in self._sysinfo_log_paths:
            # numbered log file doesn't exist => skip it.
            if not os.path.isfile(sysinfo_log_path):
                print("the log file '" + str(sysinfo_log_path) + "' doesn't exist.  Skipping it.")
                continue

            # publish the full log file to the TC artifacts.
            omni.kit.test.teamcity.teamcity_publish_image_artifact(sysinfo_log_path, "logs")
            events = self._read_log_lines(sysinfo_log_path,
                                          [
                                              "com.nvidia.omni.kit.sysinfo.cpu",
                                              "com.nvidia.omni.kit.sysinfo.os",
                                              "com.nvidia.omni.kit.sysinfo.display",
                                              "com.nvidia.omni.kit.sysinfo.displayOverview",
                                              "com.nvidia.omni.kit.sysinfo.gpu",
                                              "com.nvidia.omni.kit.sysinfo.gpuOverview"
                                          ],
                                          str(self._structured_log_settings.session_id),
                                          30 * 60, 0)

        # make sure at least one event was found.
        self.assertGreater(len(events), 0)

        # this local user is either missing their 'privacy.toml' file or did not give consent
        # for 'usage' data => count how many events appeared for each session ID in the list
        #   of recent events.  There should be at least four events for each run - 'cpu', 'os',
        #   'display', and 'displayOverview'.  Note that in render-less cases like these tests
        #   the GPU info will never be collected because the `gpu.foundation` plugin is never
        #   loaded.
        if "cloudEventsSessionId" in events[0]:
            session_counts = {}

            for event in events:
                if not event["cloudEventsSessionId"] in session_counts:
                    session_counts[event["cloudEventsSessionId"]] = 1
                else:
                    session_counts[event["cloudEventsSessionId"]] = session_counts[event["cloudEventsSessionId"]] + 1

            # make sure at least one group of events from sessions have matching messages for the
            # main events that always print (cpu, os, display, displayOverview).
            found = False
            for key, value in session_counts.items():
                if value >= expected_count:
                    found = True
                    break
                else:
                    print(f"only found {value} events from session {key}.")

            self.assertTrue(found)

        # make sure at least one matching message was found for the main events that always print
        # (cpu, os, display, displayOverview).
        else:
            self.assertGreaterEqual(len(events), expected_count)


        # verify that at least the 'cpu' and 'os' events are present for each session ID returned
        # in the event list.
        cpu_counts = {}
        os_counts = {}
        sessions = []

        for event in events:
            # the event name wasn't present (?!) => fail.
            self.assertTrue("cloudEventsEventType" in event)
            self.assertTrue("cloudEventsSessionId" in event)

            # add the session ID to a list so we can ensure each one had a CPU and OS entry.  Note
            # that if multiple sessions are found in the list, we'll reject the counts for the
            # first session since one or more of its events could have been filtered out by the
            # time delta check in _read_log_lines().
            if not event["cloudEventsSessionId"] in sessions:
                sessions.append(event["cloudEventsSessionId"])

            session_id = event["cloudEventsSessionId"]

            if event["cloudEventsEventType"] == "com.nvidia.omni.kit.sysinfo.cpu":
                if not session_id in cpu_counts:
                    cpu_counts[session_id] = 1
                else:
                    cpu_counts[session_id] = cpu_counts[session_id] + 1

            elif event["cloudEventsEventType"] == "com.nvidia.omni.kit.sysinfo.os":
                if not session_id in os_counts:
                    os_counts[session_id] = 1
                else:
                    os_counts[session_id] = os_counts[session_id] + 1

        # make sure at least one session ID was found.
        self.assertGreater(len(sessions), 0)

        # events from multiple sessions were found => reject the counts from the first session
        #   since some of its events may have been filtered by the time delta check.
        if len(sessions) > 1:
            print("trimming partial sessions.")
            for id in sessions:
                print("    {session = '" + str(id) +
                      "', cpu_counts = " + str(cpu_counts[id]) +
                      ", os_counts = " + str(os_counts[id]) + "}")

            session_id = sessions[0]
            self.assertTrue(session_id in cpu_counts)
            self.assertTrue(session_id in os_counts)

            sessions.pop(0)
            cpu_counts.pop(session_id)
            os_counts.pop(session_id)
            self.assertGreater(len(cpu_counts), 0)
            self.assertGreater(len(os_counts), 0)

        # make sure no mysterious extra sessions got into the counts somehow.
        self.assertEqual(len(sessions), len(cpu_counts))
        self.assertEqual(len(sessions), len(os_counts))

        # check that each known session has at least one 'cpu' and one 'os' event found for it.
        for session in sessions:
            self.assertTrue(session in cpu_counts)
            self.assertTrue(session in os_counts)
            self.assertGreater(cpu_counts[session], 0)
            self.assertGreater(os_counts[session], 0)

    def test_itelemetry2(self):
        """
        Tests the methods of the with ITelemetry2 interface.  This version of the
        helper function provides default values for all parameters except the first 'eventType'.
        """
        # retrieve the ITelemetry object.
        self._telemetry2 = omni.kit.telemetry.ITelemetry2()
        self.assertIsNotNone(self._telemetry2)

        # send some test events with default ordered parameters.
        self._telemetry2.send_custom_event("itelemetry2_event")
        self._telemetry2.send_custom_event("itelemetry2_event_duration", 1.25)
        self._telemetry2.send_custom_event("itelemetry2_event_data1", 0, "some data1")
        self._telemetry2.send_custom_event("itelemetry2_event_data2", 0, None, "some data2")
        self._telemetry2.send_custom_event("itelemetry2_event_value1", 0, None, None, 3.14159)
        self._telemetry2.send_custom_event("itelemetry2_event_value2", 0, None, None, 0, 2.71828)

        # send some test events with default named parameters.
        self._telemetry2.send_custom_event("itelemetry2_event2")
        self._telemetry2.send_custom_event("itelemetry2_event2_duration", duration = 5.05)
        self._telemetry2.send_custom_event("itelemetry2_event2_data1", data1 = "some data1_2")
        self._telemetry2.send_custom_event("itelemetry2_event2_data2", data2 = "some data2_2")
        self._telemetry2.send_custom_event("itelemetry2_event2_value1", value1 = 1.75)
        self._telemetry2.send_custom_event("itelemetry2_event2_value2", value2 = -14.28)

        # make sure all the messages are flushed to disk.
        self._control.stop()

        # read the log and verify that all the expected messages are present.
        events = self._read_log_lines(self._log_path,
                                      [
                                          "com.nvidia.omni.kit.internal.generic",
                                          "com.nvidia.omni.kit.telemetry.startup",
                                          "com.nvidia.omni.kit.extension.startup"
                                      ])

        # verify the ordered parameters events.
        self.assertTrue(self._is_event_present(events, {"eventType" : "itelemetry2_event", "duration" : 0, "data1" : "", "data2" : "", "value1" : 0, "value2" : 0}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "itelemetry2_event_duration", "duration" : 1.25, "data1" : "", "data2" : "", "value1" : 0, "value2" : 0}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "itelemetry2_event_data1", "duration" : 0, "data1" : "some data1", "data2" : "", "value1" : 0, "value2" : 0}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "itelemetry2_event_data2", "duration" : 0, "data1" : "", "data2" : "some data2", "value1" : 0, "value2" : 0}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "itelemetry2_event_value1", "duration" : 0, "data1" : "", "data2" : "", "value1" : 3.14159, "value2" : 0}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "itelemetry2_event_value2", "duration" : 0, "data1" : "", "data2" : "", "value1" : 0, "value2" : 2.71828}))

        # verify the named parameters events.
        self.assertTrue(self._is_event_present(events, {"eventType" : "itelemetry2_event2", "duration" : 0, "data1" : "", "data2" : "", "value1" : 0, "value2" : 0}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "itelemetry2_event2_duration", "duration" : 5.05, "data1" : "", "data2" : "", "value1" : 0, "value2" : 0}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "itelemetry2_event2_data1", "duration" : 0, "data1" : "some data1_2", "data2" : "", "value1" : 0, "value2" : 0}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "itelemetry2_event2_data2", "duration" : 0, "data1" : "", "data2" : "some data2_2", "value1" : 0, "value2" : 0}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "itelemetry2_event2_value1", "duration" : 0, "data1" : "", "data2" : "", "value1" : 1.75, "value2" : 0}))
        self.assertTrue(self._is_event_present(events, {"eventType" : "itelemetry2_event2_value2", "duration" : 0, "data1" : "", "data2" : "", "value1" : 0, "value2" : -14.28}))

        # make sure the other methods and accessors can be called.
        if self._telemetry2.cloud_session:
            self.assertNotNone(self._telemetry2.cloud_session_id)
            self.assertEqual(self._telemetry2.run_environment, omni.kit.telemetry.RunEnvironment.CLOUD)

            # make sure the 'cloud_session_id' property is read-only.
            try:
                self._telemetry2.cloud_session_id = "This donut is purple.  Purple is a fruit!"
                self.assertFalse(True, "unexpectedly able to write to the `omni.kit.telemetry.ITelemetry2().cloud_session_id` property.")

            except:
                pass

        # make sure the 'run_environment' property is read-only.
        try:
            self._telemetry2.run_environment = "The camembert is a little runny today"
            self.assertFalse(True, "unexpectedly able to write to the `omni.kit.telemetry.ITelemetry2().run_environment` property.")

        except:
            pass

        run_environment = self._telemetry2.run_environment;
        self.assertTrue(run_environment == omni.kit.telemetry.RunEnvironment.CLOUD or
                        run_environment == omni.kit.telemetry.RunEnvironment.INDIVIDUAL or
                        run_environment == omni.kit.telemetry.RunEnvironment.ENTERPRISE)

        try:
            self._telemetry2.customer_id = "Bachelor Chow Incorporated"
            self.assertFalse(True, "unexpectedly able to write to the `omni.kit.telemetry.ITelemetry2().customer_id` property.")

        except:
            pass

        # clean up.
        self._telemetry2 = None
