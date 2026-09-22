# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import difflib
import os
import logging
from typing import Tuple

import omni.kit.test
import omni.kit.app
from omni.kit.actions.core import get_action_registry

logger = logging.getLogger(os.path.basename(__file__))


def _diff_textfiles(file_content1: str, file_content2: str) -> str:
    """
    Compare two strings (file contents) and return a string with differences.

    Args:
        file_content1 (str): Content of the first file.
        file_content2 (str): Content of the second file.

    Returns:
        str: A string containing the line-by-line differences.
    """
    # Split the file content into lines
    file1_lines = file_content1.splitlines()
    file2_lines = file_content2.splitlines()

    # Use unified diff to generate the difference
    diff_result = difflib.unified_diff(file1_lines, file2_lines, fromfile="original", tofile="new", lineterm="")

    # indent the diff lines with 2 spaces
    return "".join(f"  {line}\n" for line in diff_result)


class ActionsAPIDoc:
    def __init__(self, tested_ext):
        self.tested_ext = tested_ext
        manager = omni.kit.app.get_app().get_extension_manager()
        tested_ext_id = manager.get_enabled_extension_id(self.tested_ext)
        ext_path = manager.get_extension_path(tested_ext_id)
        self.doc_path = f"{ext_path}/config/actions_api.md"


    def compare_and_update(self) -> Tuple[bool, str]:
        content = self.generate_content()

        if os.path.exists(self.doc_path):
            if not content:
                return False, f"Actions API doc for extension {self.tested_ext} exists but no actions found. Remove the '{self.doc_path}' file."

            with open(self.doc_path, "r") as f:
                existing_content = f.read()

            diff = _diff_textfiles(existing_content, content)
            if not diff:
                logger.info(f"Actions API doc for extension {self.tested_ext} is up-to-date")
                return True, ""

            print(f"Actions API doc for extension {self.tested_ext} has changed. Diff:")
            print(diff)
        else:
            if not content:
                logger.info(f"No actions found for extension {self.tested_ext} and no existing actions API doc file. Nothing to do.")
                return True, ""

        # Do not update the file if running in GitLab. We re-try tests and the next run of the test will not fail if we update the file.
        if not omni.kit.test.is_running_in_gitlab():
            print(f"Updating API doc for extension {self.tested_ext}...")
            with open(self.doc_path, "w") as f:
                f.write(content)

        return False, f"Actions API doc for '{self.tested_ext}' extension has changed. Run this test locally and commit the updated '{self.doc_path}' file, e.g.: 'tests-{self.tested_ext}.bat -f test_extensions_api_md_is_uptodate'"

    def read_content(self):
        try:
            with open(self.doc_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return None


    def generate_content(self):
        ext_actions = get_action_registry().get_all_actions_for_extension(self.tested_ext)

        # Filter out internal actions (starting with "_")
        ext_actions = tuple(action for action in ext_actions if not action.id.startswith("_"))

        if not ext_actions:
            return ""

        # sort by id:
        ext_actions = sorted(ext_actions, key=lambda a: a.id)

        content = ""
        content += f"# Actions in {self.tested_ext}\n"

        def text_or_empty(value):
            return value if value else " "

        # Calculate max column widths for formatting
        max_id_len = max(len(str(a.id)) for a in ext_actions)
        max_display_name_len = max(len(text_or_empty(a.display_name)) for a in ext_actions)
        max_description_len = max(len(text_or_empty(a.description)) for a in ext_actions)

        # Table header
        content += f"\n| {'ID'.ljust(max_id_len)} | {'Display Name'.ljust(max_display_name_len)} | {'Description'.ljust(max_description_len)} |\n"
        content += f"|:{'-' * max_id_len}-|:{'-' * max_display_name_len}-|:{'-' * max_description_len}-|\n"

        for action in ext_actions:
            # Add row to the table, left-aligning the text by padding
            display_name = text_or_empty(action.display_name).ljust(max_display_name_len)
            description = text_or_empty(action.description).ljust(max_description_len)
            action_id = str(action.id).ljust(max_id_len)
            content += f"| {action_id} | {display_name} | {description} |\n"

        return content



class TestExtensionActionsAPI(omni.kit.test.AsyncTestCase):
    """Test case to check if the actions API doc (actions_api.md) is up-to-date.

    It is a special kind of test that is injected in every extension that depends on "omni.kit.actions.core".
    """
    def test_extensions_api_md_is_uptodate(self):
        tested_ext = omni.kit.test.unittests.get_ext_test_id()

        actions_doc = ActionsAPIDoc(tested_ext)
        success, fail_msg = actions_doc.compare_and_update()
        if not success:
            self.fail(fail_msg)
