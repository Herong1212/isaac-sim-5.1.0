# noqa: PLC0302
# Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import asyncio
import datetime
import io
import json
import os
import pathlib
import tempfile
import textwrap

import carb.settings
import omni.graph.core as og
import omni.graph.core._unstable as ogu
import omni.graph.core.types as ot
import omni.graph.tools.ogn as ogn
import omni.kit.test
import omni.structuredlog
from pxr import Sdf

from .._telemetry import send_graph_event, send_graph_info


class TestOmniGraphTelemetry(omni.kit.test.AsyncTestCase):  # pragma: no cover
    """Tests the functionality of omni.graph.telemetry"""

    TEST_GRAPH_PATH = "/World/TestGraph"
    EXTENSION_NAME = "omni.graph.telemetry"
    GRAPH_INFO_TYPE = "com.nvidia.omni.graph.graphInfo"
    GRAPH_EVENT_TYPE = "com.nvidia.omni.graph.graphEvent"

    def setUp(self):
        self._structured_log_settings = omni.structuredlog.IStructuredLogSettings()
        self._control = omni.structuredlog.IStructuredLogControl()
        self._settings = carb.settings.get_settings_interface()
        self._extension_manager = omni.kit.app.get_app_interface().get_extension_manager()
        self.assertIsNotNone(self._control)
        self.assertIsNotNone(self._settings)
        self.assertIsNotNone(self._structured_log_settings)
        self.assertIsNotNone(self._extension_manager)

        # Flush any pending events before changing the output path and log name
        self._control.stop()

        # Create a temporary directory for testing and set the log output path and name
        self._temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)  # noqa: PLR1732
        self._log_file_name = "omni.graph.test.log"
        self._old_log_name = self._structured_log_settings.log_default_name
        self._old_log_path = self._structured_log_settings.log_output_path
        self._structured_log_settings.log_default_name = self._log_file_name
        self._structured_log_settings.log_output_path = self._temp_dir.name

        # Piece together the expected path of the log file we'll be watching
        self._log_path = pathlib.Path(self._temp_dir.name).joinpath(self._log_file_name)
        self.assertEqual(pathlib.Path(self._structured_log_settings.log_default_name), self._log_path)
        self.assertEqual(pathlib.Path(self._structured_log_settings.log_output_path), pathlib.Path(self._temp_dir.name))

        # Create a privacy settings file for testing and load it
        self._privacy_path = pathlib.Path(self._temp_dir.name).joinpath("privacy.toml")
        self._settings.set_string("/structuredLog/privacySettingsFile", str(self._privacy_path))
        self._update_privacy_settings()

        # Get the versions of nodes used in tests
        graph_registry = og.GraphRegistry()
        self._add_node_ver = graph_registry.get_node_type_version("omni.graph.nodes.Add")
        self._int_node_ver = graph_registry.get_node_type_version("omni.graph.nodes.ConstantInt")

    def tearDown(self):
        # Restore the original log output path and name
        self._structured_log_settings.log_output_path = self._old_log_path
        self._structured_log_settings.log_default_name = self._old_log_name

        # Restore the original privacy settings
        self._settings.set_string("/structuredLog/privacySettingsFile", "")
        self._structured_log_settings.load_privacy_settings()

        # Cleanup the temporary directory
        self._temp_dir.cleanup()

        self._structured_log_settings = None
        self._control = None
        self._settings = None
        self._extension_manager = None
        self._temp_dir = None
        self._log_file_name = None
        self._old_log_name = None
        self._old_log_path = None
        self._log_path = None
        self._privacy_path = None

    def _update_privacy_settings(self, usage="true"):
        self._structured_log_settings.log_default_name = "ignore.log"
        self._extension_manager.set_extension_enabled_immediate(self.EXTENSION_NAME, False)
        with io.open(self._privacy_path, "w", encoding="utf8") as fp:
            fp.write("[privacy]\n")
            fp.write("performance = false\n")
            fp.write("personalization = false\n")
            fp.write(f"usage = {usage}\n")
            fp.write('userId = "test-user@external.com"\n')
            fp.write('extraDiagnosticDataOptIn = ""\n')
        self._structured_log_settings.load_privacy_settings()
        self._extension_manager.set_extension_enabled_immediate(self.EXTENSION_NAME, True)
        self._control.stop()
        self._structured_log_settings.log_default_name = self._log_file_name

    def _read_log_lines(self, filename, expected_types, session=None, time_delta=-1, log_time_range=900):
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
        with io.open(filename, "r", encoding="utf8") as f:
            lines = f.readlines()

        if time_delta >= 0:
            timestamp = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=time_delta)

        # Walk through all the lines in the file except the first one (the log header)
        for i in range(1, len(lines)):
            line = lines[i]
            try:
                event = json.loads(line)
                self.assertTrue(event["type"] in expected_types)
                msg_time = datetime.datetime.strptime(event["time"], "%Y-%m-%dT%H:%M:%S.%f%z")

                # Always add the 'type' and 'session' properties to the output event.  Since the
                # "type" and "session" property names are rather generic and could legitimately
                # be part of the "data" property, we'll rename them to something less generic
                # that the caller can consume.
                event["data"]["cloudEventsEventType"] = event["type"]
                event["data"]["cloudEventsSessionId"] = event["session"]

                if (session is None or session == "0" or event["session"] == session) and (
                    time_delta < 0 or msg_time >= timestamp
                ):
                    events.append(event["data"])

            except json.decoder.JSONDecodeError as e:
                print("failed to parse the line '" + line + "' as JSON {reason = '" + str(e) + "'}")
            except Exception as e:  # noqa: PLW0703
                print("error processing the line '" + line + "' as JSON {error = '" + str(e) + "'}")
                raise

        # Parse and verify the header line
        try:
            header = json.loads(lines[0])
        except json.decoder.JSONDecodeError as e:
            print("failed to parse the header '" + lines[0] + "' as JSON {reason = '" + str(e) + "'}")
            self.assertFalse(True)
        except Exception as e:  # noqa: PLW0703
            print("error processing the header '" + lines[0] + "' as JSON {error = '" + str(e) + "'}")
            self.assertFalse(True)

        self.assertEqual(header["source"], "omni.structuredlog")
        self.assertIsNotNone(header["version"])

        # Make sure the log was created recently
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

        # Go through each event in the log file and check if it has all the required properties
        for event in events:
            matches = True

            # Go through each of the required properties and verify they are all present and have the expected value
            for key, value in properties.items():
                if key not in event:
                    continue

                if event[key] != value:
                    matches = False
                    break

            if matches:
                return True

        return False

    def test_send_graph_event_helper(self):
        """
        Tests the send_graph_event helper function for constructing and sending a graphEvent event
        """
        descriptor = "test-event"
        send_graph_event(descriptor)

        # Make sure the event is flushed to disk
        self._control.stop()

        # Verify that the event is present
        events = self._read_log_lines(self._log_path, [self.GRAPH_EVENT_TYPE])
        self.assertTrue(
            self._is_event_present(
                events,
                {
                    "descriptor": descriptor,
                },
            ),
            "Missing/incorrect graphEvent event",
        )

    async def test_send_graph_info_helper_basic(self):
        """
        Tests the basic functionality of the send_graph_info helper function to construct and send a graphInfo event
        """
        await omni.usd.get_context().new_stage_async()

        keys = og.Controller.Keys
        (graph, _, _, _) = og.Controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("Constant_a", "omni.graph.nodes.ConstantInt"),
                    ("Constant_b", "omni.graph.nodes.ConstantInt"),
                    ("Add_a_b", "omni.graph.nodes.Add"),
                ],
            },
        )

        send_graph_info(graph.get_path_to_graph())

        # Make sure that the events are flushed to disk
        self._control.stop()

        # Verify that the events are present
        events = self._read_log_lines(self._log_path, [self.GRAPH_INFO_TYPE])
        self.assertTrue(
            self._is_event_present(
                events,
                {
                    "fileId": "0",
                    "graphId": "819736871301921921",
                    "rootGraphId": "819736871301921921",
                    "graphType": "push",
                    "nodeTypes": [
                        {"typeName": "omni.graph.nodes.Add", "version": self._add_node_ver, "instanceCount": 1},
                        {"typeName": "omni.graph.nodes.ConstantInt", "version": self._int_node_ver, "instanceCount": 2},
                    ],
                },
            ),
            "Missing/incorrect graphInfo event",
        )

    async def test_send_graph_info_helper_empty(self):
        """
        Tests the send_graph_info helper function with an empty graph
        """
        await omni.usd.get_context().new_stage_async()

        (graph, _, _, _) = og.Controller.edit(self.TEST_GRAPH_PATH, {})

        send_graph_info(graph.get_path_to_graph())

        # Make sure that the events are flushed to disk
        self._control.stop()

        # Verify that the events are present
        events = self._read_log_lines(self._log_path, [self.GRAPH_INFO_TYPE])
        self.assertTrue(
            self._is_event_present(
                events,
                {
                    "fileId": "0",
                    "graphId": "819736871301921921",
                    "rootGraphId": "819736871301921921",
                    "graphType": "push",
                    "nodeTypes": [],
                },
            ),
            "Missing/incorrect graphInfo event",
        )

    async def test_send_graph_info_helper_compounds(self):
        """
        Tests the send_graph_info helper function with compound nodes/subgraphs
        """
        await omni.usd.get_context().new_stage_async()

        keys = og.Controller.Keys
        (graph, _, _, _) = og.Controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("Constant_root", "omni.graph.nodes.ConstantInt"),
                    ("Compound_empty_1", {}),
                    ("Compound_empty_2", {}),
                    (
                        "Compound_nested_1",
                        {
                            keys.CREATE_NODES: [
                                ("Constant_nested_1", "omni.graph.nodes.ConstantInt"),
                                (
                                    "Compound_nested_2",
                                    {
                                        keys.CREATE_NODES: [
                                            ("Constant_nested_2", "omni.graph.nodes.ConstantInt"),
                                        ],
                                    },
                                ),
                                (
                                    "Compound_nested_3",
                                    {
                                        keys.CREATE_NODES: [
                                            ("Constant_nested_3", "omni.graph.nodes.ConstantInt"),
                                        ],
                                    },
                                ),
                            ],
                        },
                    ),
                ],
            },
        )

        send_graph_info(graph.get_path_to_graph())

        # Make sure that the events are flushed to disk
        self._control.stop()

        # Verify that the events are present
        events = self._read_log_lines(self._log_path, [self.GRAPH_INFO_TYPE])
        self.assertTrue(
            self._is_event_present(
                events,
                {  # Root graph
                    "fileId": "0",
                    "graphId": "819736871301921921",
                    "rootGraphId": "819736871301921921",
                    "graphType": "push",
                    "nodeTypes": [
                        {"typeName": "compound:11533280347681659452", "version": 1, "instanceCount": 1},
                        {"typeName": "compound:174119116561962610", "version": 1, "instanceCount": 1},
                        {"typeName": "compound:2193831960993102007", "version": 1, "instanceCount": 1},
                        {"typeName": "omni.graph.nodes.ConstantInt", "version": self._int_node_ver, "instanceCount": 1},
                    ],
                },
            ),
            "Missing/incorrect graphInfo event for the root graph",
        )
        self.assertTrue(
            self._is_event_present(
                events,
                {  # Compound_empty_1
                    "fileId": "0",
                    "graphId": "11533280347681659452",
                    "rootGraphId": "819736871301921921",
                    "graphType": "push",
                    "nodeTypes": [],
                },
            ),
            "Missing/incorrect graphInfo event for the subgraph of Compound_empty_1",
        )
        self.assertTrue(
            self._is_event_present(
                events,
                {  # Compound_empty_2
                    "fileId": "0",
                    "graphId": "2193831960993102007",
                    "rootGraphId": "819736871301921921",
                    "graphType": "push",
                    "nodeTypes": [],
                },
            ),
            "Missing/incorrect graphInfo event for the subgraph of Compound_empty_2",
        )
        self.assertTrue(
            self._is_event_present(
                events,
                {  # Compound_nested_1
                    "fileId": "0",
                    "graphId": "174119116561962610",
                    "rootGraphId": "819736871301921921",
                    "graphType": "push",
                    "nodeTypes": [
                        {"typeName": "compound:17736520268679576680", "version": 1, "instanceCount": 1},
                        {"typeName": "compound:3658183881271514113", "version": 1, "instanceCount": 1},
                        {"typeName": "omni.graph.nodes.ConstantInt", "version": self._int_node_ver, "instanceCount": 1},
                    ],
                },
            ),
            "Missing/incorrect graphInfo event for the subgraph of Compound_nested_1",
        )
        self.assertTrue(
            self._is_event_present(
                events,
                {  # Compound_nested_2
                    "fileId": "0",
                    "graphId": "17736520268679576680",
                    "rootGraphId": "819736871301921921",
                    "graphType": "push",
                    "nodeTypes": [
                        {"typeName": "omni.graph.nodes.ConstantInt", "version": self._int_node_ver, "instanceCount": 1}
                    ],
                },
            ),
            "Missing/incorrect graphInfo event for the subgraph of Compound_nested_2",
        )
        self.assertTrue(
            self._is_event_present(
                events,
                {  # Compound_nested_3
                    "fileId": "0",
                    "graphId": "3658183881271514113",
                    "rootGraphId": "819736871301921921",
                    "graphType": "push",
                    "nodeTypes": [
                        {"typeName": "omni.graph.nodes.ConstantInt", "version": self._int_node_ver, "instanceCount": 1}
                    ],
                },
            ),
            "Missing/incorrect graphInfo event for the subgraph of Compound_nested_3",
        )

    async def test_send_graph_info_helper_compound_instancing(self):
        """
        Tests the send_graph_info helper function with compound node instances sharing the same subgraph
        """
        await omni.usd.get_context().new_stage_async()

        # Create a compound node type to be instanced
        (success, schema_prim) = ogu.cmds.CreateCompoundNodeType(compound_name="TestCompound", graph_name="Graph")
        self.assertTrue(success, "Failed to create compound node type")
        compound_path = str(schema_prim.GetPrim().GetPath())
        og.cmds.CreateNode(
            graph=og.get_graph_by_path(f"{compound_path}/Graph"),
            node_path=f"{compound_path}/Graph/add",
            node_type="omni.graph.nodes.Add",
            create_usd=True,
        )

        keys = og.Controller.Keys
        (graph, _, _, _) = og.Controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("Compound_instanced_1", compound_path),
                    ("Compound_instanced_2", compound_path),
                    (
                        "Compound",
                        {
                            keys.CREATE_NODES: [
                                ("Compound_instanced_3", compound_path),
                            ],
                        },
                    ),
                ],
            },
        )

        send_graph_info(graph.get_path_to_graph())

        # Make sure that the events are flushed to disk
        self._control.stop()

        # Verify that the events are present
        events = self._read_log_lines(self._log_path, [self.GRAPH_INFO_TYPE])
        self.assertTrue(
            self._is_event_present(
                events,
                {  # Root graph
                    "fileId": "0",
                    "graphId": "819736871301921921",
                    "rootGraphId": "819736871301921921",
                    "graphType": "push",
                    "nodeTypes": [
                        {"typeName": "compound:10401758611828045834", "version": 1, "instanceCount": 1},
                        {"typeName": "compound:2836377198843945986", "version": 1, "instanceCount": 2},
                    ],
                },
            ),
            "Missing/incorrect graphInfo event for the root graph",
        )
        self.assertTrue(
            self._is_event_present(
                events,
                {  # Compound_instanced_1/2/3
                    "fileId": "0",
                    "graphId": "2836377198843945986",
                    "rootGraphId": "819736871301921921",
                    "graphType": "push",
                    "nodeTypes": [
                        {"typeName": "omni.graph.nodes.Add", "version": self._add_node_ver, "instanceCount": 1}
                    ],
                },
            ),
            "Missing/incorrect graphInfo event for the subgraph of Compound_instanced_1/2/3",
        )
        self.assertTrue(
            self._is_event_present(
                events,
                {  # Compound
                    "fileId": "0",
                    "graphId": "10401758611828045834",
                    "rootGraphId": "819736871301921921",
                    "graphType": "push",
                    "nodeTypes": [{"typeName": "compound:2836377198843945986", "version": 1, "instanceCount": 1}],
                },
            ),
            "Missing/incorrect graphInfo event for the subgraph of Compound",
        )

    async def test_send_graph_info_helper_pseudonodes(self):
        """
        Tests the send_graph_info helper function with pseudonodes in the root graph and subgraphs
        """
        await omni.usd.get_context().new_stage_async()

        keys = og.Controller.Keys
        (graph, nodes, _, _) = og.Controller.edit(self.TEST_GRAPH_PATH, {keys.CREATE_NODES: [("Compound", {})]})

        # Add two Backdrops and one OmniNote to the root graph
        root_graph_path = Sdf.Path(graph.get_path_to_graph())
        omni.kit.commands.execute("CreateUsdUIBackdropCommand", parent_path=root_graph_path, identifier="OGBackdrop")
        omni.kit.commands.execute("CreateUsdUIBackdropCommand", parent_path=root_graph_path, identifier="OGBackdrop")
        omni.kit.commands.execute("CreateUsdUINoteCommand", parent_path=root_graph_path, identifier="OGNote")

        # Add one Backdrop and two OmniNotes to the compound subgraph
        compound_subgraph_path = Sdf.Path(nodes[0].get_compound_graph_instance().get_path_to_graph())
        omni.kit.commands.execute(
            "CreateUsdUIBackdropCommand", parent_path=compound_subgraph_path, identifier="OGBackdrop"
        )
        omni.kit.commands.execute("CreateUsdUINoteCommand", parent_path=compound_subgraph_path, identifier="OGNote")
        omni.kit.commands.execute("CreateUsdUINoteCommand", parent_path=compound_subgraph_path, identifier="OGNote")

        send_graph_info(graph.get_path_to_graph())

        # Make sure that the events are flushed to disk
        self._control.stop()

        # Verify that the events are present
        events = self._read_log_lines(self._log_path, [self.GRAPH_INFO_TYPE])
        self.assertTrue(
            self._is_event_present(
                events,
                {  # Root graph
                    "fileId": "0",
                    "graphId": "819736871301921921",
                    "rootGraphId": "819736871301921921",
                    "graphType": "push",
                    "nodeTypes": [
                        {"typeName": "compound:10401758611828045834", "version": 1, "instanceCount": 1},
                        {"typeName": "pseudo:Backdrop", "version": 1, "instanceCount": 2},
                        {"typeName": "pseudo:OmniNote", "version": 1, "instanceCount": 1},
                    ],
                },
            ),
            "Missing/incorrect graphInfo event for the root graph",
        )
        self.assertTrue(
            self._is_event_present(
                events,
                {  # Compound
                    "fileId": "0",
                    "graphId": "10401758611828045834",
                    "rootGraphId": "819736871301921921",
                    "graphType": "push",
                    "nodeTypes": [
                        {"typeName": "pseudo:Backdrop", "version": 1, "instanceCount": 1},
                        {"typeName": "pseudo:OmniNote", "version": 1, "instanceCount": 2},
                    ],
                },
            ),
            "Missing/incorrect graphInfo event for the subgraph of Compound",
        )

    async def test_send_graph_info_helper_breadth(self):
        """
        Tests the send_graph_info helper function on a graph with many compound subgraphs directly under the root graph
        """
        await omni.usd.get_context().new_stage_async()

        num_compounds = 40
        num_nodes = 40

        keys = og.Controller.Keys
        (graph, _, _, _) = og.Controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    (
                        f"Compound_{i}",
                        {
                            keys.CREATE_NODES: [(f"Add_{i}_{j}", "omni.graph.nodes.Add") for j in range(num_nodes)],
                        },
                    )
                    for i in range(num_compounds)
                ],
            },
        )

        send_graph_info(graph.get_path_to_graph())

        # Make sure that the events are flushed to disk
        self._control.stop()

        # Find and verify the event for the root graph
        events = self._read_log_lines(self._log_path, [self.GRAPH_INFO_TYPE])
        root_graph_event = None
        for event in events:
            node_type_names = [item["typeName"] for item in event["nodeTypes"]]
            if (
                event["graphId"] == "819736871301921921"
                and len(node_type_names) == num_compounds
                and sorted(set(node_type_names)) == node_type_names
                and all((item["instanceCount"] == 1 for item in event["nodeTypes"]))
            ):
                root_graph_event = event
                break
        self.assertIsNotNone(root_graph_event, "Missing/incorrect graphInfo event for the root graph")

        # Verify the events for the compound subgraphs
        expected_subgraph_ids = [item["typeName"][len("compound:") :] for item in root_graph_event["nodeTypes"]]
        for subgraph_id in expected_subgraph_ids:
            self.assertTrue(
                self._is_event_present(
                    events,
                    {
                        "fileId": "0",
                        "graphId": subgraph_id,
                        "rootGraphId": "819736871301921921",
                        "graphType": "push",
                        "nodeTypes": [
                            {
                                "typeName": "omni.graph.nodes.Add",
                                "version": self._add_node_ver,
                                "instanceCount": num_nodes,
                            }
                        ],
                    },
                ),
                f"Missing/incorrect graphInfo event for the compound subgraph with graphId={subgraph_id}",
            )

    async def test_send_graph_info_helper_depth(self):
        """
        Tests the send_graph_info helper function on a graph with a long chain of nested subgraphs
        """
        await omni.usd.get_context().new_stage_async()

        num_compounds = 40
        num_nodes = 40

        keys = og.Controller.Keys

        def recursive_graph(i=0):
            if i < num_compounds:  # Recursive case, where i=0 corresponds to the root graph
                return {
                    keys.CREATE_NODES: [(f"Add_{i}_{j}", "omni.graph.nodes.Add") for j in range(num_nodes)]
                    + [(f"Compound_{i + 1}", recursive_graph(i + 1))]
                }

            return {  # Base case
                keys.CREATE_NODES: [(f"Add_{i}_{j}", "omni.graph.nodes.Add") for j in range(num_nodes)]
            }

        (graph, _, _, _) = og.Controller.edit(self.TEST_GRAPH_PATH, recursive_graph())

        send_graph_info(graph.get_path_to_graph())

        # Make sure that the events are flushed to disk
        self._control.stop()

        # Recursively find and verify the events
        events = self._read_log_lines(self._log_path, [self.GRAPH_INFO_TYPE])

        def verify_events_recursive(cur_graph_id="819736871301921921", i=0):
            if i < num_compounds:  # Recursive case, where i=0 corresponds to the root graph
                cur_graph_event = None
                for event in events:
                    if (
                        event["graphId"] == cur_graph_id
                        and len(event["nodeTypes"]) == 2
                        and event["nodeTypes"][0]["typeName"].startswith("compound:")
                        and event["nodeTypes"][0]["instanceCount"] == 1
                        and event["nodeTypes"][1]["typeName"] == "omni.graph.nodes.Add"
                        and event["nodeTypes"][1]["instanceCount"] == num_nodes
                    ):
                        cur_graph_event = event
                        break
                self.assertIsNotNone(cur_graph_event, f"Missing/incorrect graphInfo event for recursive graph {i}")

                subgraph_id = cur_graph_event["nodeTypes"][0]["typeName"][len("compound:") :]
                verify_events_recursive(subgraph_id, i + 1)

            else:  # Base case
                cur_graph_event = None
                for event in events:
                    if (
                        event["graphId"] == cur_graph_id
                        and len(event["nodeTypes"]) == 1
                        and event["nodeTypes"][0]["typeName"] == "omni.graph.nodes.Add"
                        and event["nodeTypes"][0]["instanceCount"] == num_nodes
                    ):
                        cur_graph_event = event
                        break
                self.assertIsNotNone(cur_graph_event, f"Missing/incorrect graphInfo event for recursive graph {i}")

        verify_events_recursive()

    async def test_send_graph_info_helper_autonode(self):
        """
        Tests the send_graph_info helper function with a graph containing an instance of a node type created by Autonode
        """
        await omni.usd.get_context().new_stage_async()

        # Temporarily change the module name to pretend we're in a main script before using Autonode
        module_name_temp = __name__
        globals()["__name__"] = "__main__"
        try:

            @og.create_node_type
            def add(a: ot.int, b: ot.int) -> ot.int:
                return a + b

        finally:
            globals()["__name__"] = module_name_temp

        keys = og.Controller.Keys
        (graph, _, _, _) = og.Controller.edit(
            self.TEST_GRAPH_PATH, {keys.CREATE_NODES: [("Autonode_add", f"{og.RUNTIME_MODULE_NAME}.add")]}
        )

        send_graph_info(graph.get_path_to_graph())

        # Make sure that the events are flushed to disk
        self._control.stop()

        # Verify that the events are present
        events = self._read_log_lines(self._log_path, [self.GRAPH_INFO_TYPE])
        self.assertTrue(
            self._is_event_present(
                events,
                {
                    "fileId": "0",
                    "graphId": "819736871301921921",
                    "rootGraphId": "819736871301921921",
                    "graphType": "push",
                    "nodeTypes": [{"typeName": "autonode:12921755730960449834", "version": 1, "instanceCount": 1}],
                },
            ),
            "Missing/incorrect graphInfo event",
        )

    async def test_send_graph_info_helper_external_node(self):
        """
        Tests the send_graph_info helper function with a graph containing an instance of a node type defined in an
        external extension
        """
        await omni.usd.get_context().new_stage_async()

        # Create an extension containing a node type for testing
        ext_name = "some.external.extension"
        ext_path = os.path.join(self._temp_dir.name, ext_name)

        os.mkdir(ext_path)
        ext = ogn.OmniGraphExtension(self._temp_dir.name, ext_name)
        ext.create_directory_tree()

        # Create the ogn file for the node type
        name = "SomeExternalNodeType"
        ogn_file_path = pathlib.Path(ext.ogn_nodes_directory, f"{name}.ogn")
        ogn_file_data = {name: {"version": 1, "description": "Some external node type", "language": "Python"}}
        with io.open(ogn_file_path, "w", encoding="utf8") as ogn_fp:
            json.dump(ogn_file_data, ogn_fp, indent=4)
            ogn_fp.flush()
            os.fsync(ogn_fp.fileno())

        # Create the implementation file for the node type
        py_file_path = pathlib.Path(ext.ogn_nodes_directory, f"{name}.py")
        py_file_data = textwrap.dedent(
            f"""\
            class {name}:
                @staticmethod
                def compute(db) -> bool:
                    return True
            """
        )
        with io.open(py_file_path, "w", encoding="utf8") as py_fp:
            py_fp.write(py_file_data)
            py_fp.flush()
            os.fsync(py_fp.fileno())

        # Create other necessary extension files
        ext.write_all_files()

        # Wait for the extension manager to scan and add the extension
        extension_manager_ready = asyncio.Future()
        extension_manager_sub = self._extension_manager.get_change_event_stream().create_subscription_to_pop(
            lambda _: not extension_manager_ready.done() and extension_manager_ready.set_result(None), name=ext_name
        )

        self._extension_manager.add_path(ext_path, omni.ext.ExtensionPathType.DIRECT_PATH)
        await extension_manager_ready
        extension_manager_sub.unsubscribe()

        # Enable the extension
        self._structured_log_settings.log_default_name = "ignore.log"
        self._extension_manager.set_extension_enabled_immediate(ext_name, True)
        self._control.stop()
        self._structured_log_settings.log_default_name = self._log_file_name

        # Create a graph containing an instance of the node type and log a graphInfo event for it
        node_type_name = ".".join([ext_name, name])
        keys = og.Controller.Keys
        (graph, _, _, _) = og.Controller.edit(
            self.TEST_GRAPH_PATH, {keys.CREATE_NODES: [("Some_external_node", node_type_name)]}
        )

        send_graph_info(graph.get_path_to_graph())
        self._control.stop()

        # Disable and remove the extension
        self._structured_log_settings.log_default_name = "ignore.log"
        self._extension_manager.set_extension_enabled_immediate(ext_name, False)
        self._control.stop()
        self._structured_log_settings.log_default_name = self._log_file_name

        self._extension_manager.remove_path(ext_path)

        # Verify that the event is present
        events = self._read_log_lines(self._log_path, [self.GRAPH_INFO_TYPE])
        self.assertTrue(
            self._is_event_present(
                events,
                {
                    "fileId": "0",
                    "graphId": "819736871301921921",
                    "rootGraphId": "819736871301921921",
                    "graphType": "push",
                    "nodeTypes": [{"typeName": "external:16114804888670342666", "version": 1, "instanceCount": 1}],
                },
            )
        )

    async def test_extension_send_graph_info_trigger(self):
        """
        Tests that the send_graph_info helper function is called when expected
        """
        await omni.usd.get_context().new_stage_async()

        # Verify that just creating nodes does not trigger send_graph_info
        keys = og.Controller.Keys
        controller = og.Controller()
        controller.edit(
            self.TEST_GRAPH_PATH,
            {
                keys.CREATE_NODES: [
                    ("Add", "omni.graph.nodes.Add"),
                    ("Constant_a", "omni.graph.nodes.ConstantInt"),
                    ("Constant_b", "omni.graph.nodes.ConstantInt"),
                ],
            },
        )
        self._control.stop()
        events = self._read_log_lines(self._log_path, [self.GRAPH_INFO_TYPE])
        self.assertTrue(len(events) == 0)

        # Verify that adding a connection does trigger send_graph_info
        controller.edit(self.TEST_GRAPH_PATH, {keys.CONNECT: [("Constant_a.inputs:value", "Add.inputs:a")]})
        self._control.stop()
        events = self._read_log_lines(self._log_path, [self.GRAPH_INFO_TYPE])
        self.assertTrue(len(events) == 1)
        self.assertTrue(
            self._is_event_present(
                events,
                {
                    "fileId": "0",
                    "graphId": "819736871301921921",
                    "rootGraphId": "819736871301921921",
                    "graphType": "push",
                    "nodeTypes": [
                        {"typeName": "omni.graph.nodes.Add", "version": self._add_node_ver, "instanceCount": 1},
                        {"typeName": "omni.graph.nodes.ConstantInt", "version": self._int_node_ver, "instanceCount": 2},
                    ],
                },
            )
        )

        # Verify that adding another connection does not trigger send_graph_info again due to the 1-minute timeout
        controller.edit(self.TEST_GRAPH_PATH, {keys.CONNECT: [("Constant_b.inputs:value", "Add.inputs:b")]})
        self._control.stop()
        self.assertTrue(events == self._read_log_lines(self._log_path, [self.GRAPH_INFO_TYPE]))

        # Set up a second test graph containing a compound
        controller = og.Controller()
        (_, nodes, _, _) = controller.edit(
            self.TEST_GRAPH_PATH + "2",
            {
                keys.CREATE_NODES: [
                    (
                        "Compound",
                        {
                            keys.CREATE_NODES: [
                                ("Add", "omni.graph.nodes.Add"),
                                ("Constant_a", "omni.graph.nodes.ConstantInt"),
                            ],
                            keys.PROMOTE_ATTRIBUTES: [
                                ("Add.inputs:b", "inputs:b"),
                            ],
                        },
                    ),
                    ("Constant_b", "omni.graph.nodes.ConstantInt"),
                ]
            },
        )
        compound_path = nodes[0].get_compound_graph_instance().get_path_to_graph()
        self._control.stop()
        self.assertTrue(events == self._read_log_lines(self._log_path, [self.GRAPH_INFO_TYPE]))

        # Verify that adding a connection inside a compound also triggers send_graph_info for the root graph,
        # and that the timeout is not shared between root graphs
        controller.edit(compound_path, {keys.CONNECT: [("Constant_a.inputs:value", "Add.inputs:a")]})
        self._control.stop()
        events = self._read_log_lines(self._log_path, [self.GRAPH_INFO_TYPE])
        self.assertTrue(len(events) == 3)
        self.assertTrue(
            self._is_event_present(
                events,
                {
                    "fileId": "0",
                    "graphId": "10546028960371156009",
                    "rootGraphId": "10546028960371156009",
                    "graphType": "push",
                    "nodeTypes": [
                        {"typeName": "compound:11151175611307390306", "version": 1, "instanceCount": 1},
                        {"typeName": "omni.graph.nodes.ConstantInt", "version": self._int_node_ver, "instanceCount": 1},
                    ],
                },
            )
        )
        self.assertTrue(
            self._is_event_present(
                events,
                {
                    "fileId": "0",
                    "graphId": "11151175611307390306",
                    "rootGraphId": "10546028960371156009",
                    "graphType": "push",
                    "nodeTypes": [
                        {"typeName": "omni.graph.nodes.Add", "version": self._add_node_ver, "instanceCount": 1},
                        {"typeName": "omni.graph.nodes.ConstantInt", "version": self._int_node_ver, "instanceCount": 1},
                    ],
                },
            )
        )

        # Check that the timeout is shared between a root graph and its compound subgraphs
        controller.edit(self.TEST_GRAPH_PATH + "2", {keys.CONNECT: [("Constant_b.inputs:value", "Compound.inputs:b")]})
        self._control.stop()
        self.assertTrue(events == self._read_log_lines(self._log_path, [self.GRAPH_INFO_TYPE]))

    async def test_extension_no_usage_consent(self):
        """
        Tests that messages are not logged when usage consent is not given
        """
        await omni.usd.get_context().new_stage_async()

        self._update_privacy_settings(usage="false")
        try:
            keys = og.Controller.Keys
            og.Controller.edit(self.TEST_GRAPH_PATH, {keys.CREATE_NODES: [("Add", "omni.graph.nodes.Add")]})
            send_graph_event("test_extension_no_usage_consent")
            self._control.stop()
            events = self._read_log_lines(self._log_path, [self.GRAPH_INFO_TYPE, self.GRAPH_EVENT_TYPE])
            self.assertTrue(len(events) == 0)
        finally:
            self._update_privacy_settings()
