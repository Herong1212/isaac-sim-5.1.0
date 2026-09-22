from dataclasses import dataclass
from typing import List

import carb.logging
import omni.graph.core as og
import omni.graph.core.tests as ogts


@dataclass
class LogEntry:
    """Represents a log entry emitted by carb"""

    source: str
    level: int
    file_name: str
    line_number: int
    message: str


class LogRecorder:
    """Utility class to accumulate the log entries in a given scope."""

    @property
    def output(self) -> List[LogEntry]:
        """The log messages collected by the logger."""
        return self._log_entries

    def clear(self):
        """Clear the output messages"""
        self._log_entries = []

    def __init__(self):
        self._logging = carb.logging.acquire_logging()
        self._log_entries: List[LogEntry] = []
        self._logger_handle = None
        self._saved_threshold = carb.logging.LEVEL_VERBOSE

    def __enter__(self):
        self._logger_handle = self._logging.add_logger(self._on_log)
        self._saved_threshold = self._logging.get_level_threshold()
        self._logging.set_level_threshold(carb.logging.LEVEL_VERBOSE)
        return self

    def __exit__(self, *_):
        self._logging.remove_logger(self._logger_handle)
        self._logging.set_level_threshold(self._saved_threshold)

    def _on_log(self, source, level, file_name, line_number, message):
        entry = LogEntry(source, level, file_name, line_number, message)
        self._log_entries.append(entry)


class TestNodes(ogts.OmniGraphTestCase):
    """Tests omni.graph.nodes_core functionality"""

    async def test_log_message_node(self):
        """Test LogMessage Node"""

        log_levels = ["Verbose", "Info", "Warn", "Error"]
        log_enums = [
            carb.logging.LEVEL_VERBOSE,
            carb.logging.LEVEL_INFO,
            carb.logging.LEVEL_WARN,
            carb.logging.LEVEL_ERROR,
        ]

        # Create a graph with a LogMessage node
        keys = og.Controller.Keys
        controller = og.Controller()
        (graph, (log_node,), _, _) = controller.edit(
            "/World/TestGraph", {keys.CREATE_NODES: [("LogMessage", "omni.graph.action.LogMessage")]}
        )

        self.assertTrue(graph is not None)
        self.assertTrue(graph.is_valid())
        self.assertTrue(log_node is not None)

        # Test basic functionality with default settings
        test_message = "Test log message from LogMessage node"
        log_node.get_attribute("inputs:message").set(test_message)

        with LogRecorder() as log_recorder:
            await controller.evaluate(graph)

            # Verify that the message was logged
            self.assertGreater(len(log_recorder.output), 0, "No log messages were captured")

            # Find our test message in the logged entries
            found_message = False
            for entry in log_recorder.output:
                if test_message in entry.message:
                    found_message = True
                    # Verify the source is correct
                    self.assertEqual(entry.source, "omni.graph.nodes_core.plugin")
                    # Verify default log level is Info
                    self.assertEqual(entry.level, carb.logging.LEVEL_INFO)
                    break

            self.assertTrue(found_message, f"Test message '{test_message}' was not found in log output")

        # Test different log levels
        for log_lvl, level in zip(log_enums, log_levels):
            log_node.get_attribute("inputs:logLevel").set(level)
            test_message = f"Test message with level {level}"
            log_node.get_attribute("inputs:message").set(test_message)

            with LogRecorder() as log_recorder:
                await controller.evaluate(graph)

                # Find our test message in the logged entries
                found_message = False
                for entry in log_recorder.output:
                    if test_message in entry.message:
                        found_message = True
                        # Verify the log level is correct
                        self.assertEqual(entry.level, log_lvl)
                        break

                self.assertTrue(found_message, f"Test message with level {level} was not found in log output")

        # Test custom channel
        custom_channel = "test.custom.channel"
        log_node.get_attribute("inputs:channel").set(custom_channel)
        test_message = "Test message with custom channel"
        log_node.get_attribute("inputs:message").set(test_message)
        log_node.get_attribute("inputs:logLevel").set("Info")

        with LogRecorder() as log_recorder:
            await controller.evaluate(graph)

            # Find our test message in the logged entries
            found_message = any(test_message in entry.message for entry in log_recorder.output)
            self.assertTrue(found_message, "Test message with custom channel was not found in log output")

        # Test empty message (should not log anything)
        log_node.get_attribute("inputs:message").set("")

        with LogRecorder() as log_recorder:
            await controller.evaluate(graph)

            # Should not log anything for empty messages
            self.assertEqual(len(log_recorder.output), 0, "Empty message should not produce any log output")

        # Test invalid log level (should throw an error)
        log_node.get_attribute("inputs:message").set("Test message with invalid level")
        log_node.get_attribute("inputs:logLevel").set("InvalidLevel")

        with LogRecorder() as log_recorder:
            # This should cause an error in the node
            await controller.evaluate(graph)

            # Check if there are any error messages in the node's compute messages
            error_messages = log_node.get_compute_messages(og.Severity.ERROR)
            self.assertGreater(len(error_messages), 0, "Expected error message for invalid log level")

            # Verify the error message contains information about the invalid level
            error_found = False
            for error_msg in error_messages:
                if "Invalid logging level" in error_msg:
                    error_found = True
                    break

            self.assertTrue(error_found, "Expected error message about invalid logging level")

        # Test multiple messages in vectorized mode
        # Create multiple LogMessage nodes to test vectorized behavior
        (_, (log_node2, log_node3), _, _) = controller.edit(
            graph,
            {
                keys.CREATE_NODES: [
                    ("LogMessage2", "omni.graph.action.LogMessage"),
                    ("LogMessage3", "omni.graph.action.LogMessage"),
                ]
            },
        )

        # Set different messages and levels (the message is the same as the level string)
        check_levels = ["Verbose", "Info", "Warn"]
        for node, lvl in zip([log_node, log_node2, log_node3], check_levels):
            node.get_attribute("inputs:message").set(lvl)
            node.get_attribute("inputs:logLevel").set(lvl)

        with LogRecorder() as log_recorder:
            await controller.evaluate(graph)

            # Verify all three messages were logged (not checking Error)
            messages_found = {lvl: False for lvl in check_levels}
            levels_found = {lvl_enum: False for lvl_enum in log_enums[0:-1]}

            for entry in log_recorder.output:
                for msg in messages_found:
                    if msg in entry.message:
                        messages_found[msg] = True
                        break

                if entry.level in levels_found:
                    levels_found[entry.level] = True

            # Verify all messages were found
            for msg, found in messages_found.items():
                self.assertTrue(found, f"Message '{msg}' was not found in log output")

            # Verify all levels were found
            for level, found in levels_found.items():
                self.assertTrue(found, f"Level '{level}' was not found in log output")
