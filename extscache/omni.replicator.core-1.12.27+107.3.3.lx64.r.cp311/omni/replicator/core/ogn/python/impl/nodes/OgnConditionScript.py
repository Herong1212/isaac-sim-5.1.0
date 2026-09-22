# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ctypes
import inspect
import os
import tempfile
import traceback

import carb
import numpy as np
import omni.graph.core as og
import omni.replicator.core as rep
from omni.replicator.core import annotators
from omni.replicator.core.ogn.OgnConditionScriptDatabase import OgnConditionScriptDatabase


def get_address(attr):
    ptr_type = ctypes.POINTER(ctypes.c_size_t)
    ptr = ctypes.cast(attr.memory, ptr_type)
    return ptr.contents.value


# A hacky context manager that captures local variable name declarations and saves them in a dict
class ScriptContextSaver:
    def __init__(self, script_context: dict):
        self.script_context = script_context
        self.local_names = None

    def __enter__(self):
        caller_frame = inspect.currentframe().f_back
        self.local_names = set(caller_frame.f_locals)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        caller_frame = inspect.currentframe().f_back
        caller_locals = caller_frame.f_locals
        for name in caller_locals:
            if name not in self.local_names:
                self.script_context[name] = caller_locals[name]


class OgnConditionScriptInternalState:
    def __init__(self):
        self.rng = rep.rng.ReplicatorRNG()
        self.omni_cur_script = None
        self.omni_cur_script_path = None
        self.omni_tempfile_path = None
        self.omni_code_object = None
        self.omni_script_context = {}
        self.omni_initialized = False
        self.has_warned_disabled = False


class OgnConditionScript:
    @staticmethod
    def internal_state():
        return OgnConditionScriptInternalState()

    @staticmethod
    def initialize(context, node):
        rep.annotators.annotator_utils.script_node_check([node])
        state = OgnConditionScriptDatabase.shared_internal_state(node)

        # Create a temporary file for storing the script
        with tempfile.NamedTemporaryFile(prefix="ConditionScript_", suffix=".py", delete=False) as tf:
            state.omni_tempfile_path = tf.name

        og.Controller.set(og.Controller.attribute("state:omni_initialized", node), False)

    @staticmethod
    def release(node):
        rep.rng.release(node.get_prim_path())

        state = OgnConditionScriptDatabase.shared_internal_state(node)

        # Same logic as when the reset button is pressed
        OgnConditionScript._try_cleanup(node)

        # Delete the temporary file for storing the script
        if os.path.exists(state.omni_tempfile_path):
            os.remove(state.omni_tempfile_path)

    @staticmethod
    def _try_cleanup(node):
        # Skip if not setup in the fist place
        if og.Controller.get(og.Controller.attribute("state:omni_initialized", node)) is False:
            return

        state = OgnConditionScriptDatabase.shared_internal_state(node)

        # Call the user-defined cleanup function
        if state.omni_cleanup_fn is not None:
            # Get the database object
            per_node_data = OgnConditionScriptDatabase.PER_NODE_DATA[node.node_id()]
            db = per_node_data.get("_db")

            try:
                db.inputs._setting_locked = True  # noqa: PLW0212
                state.omni_cleanup_fn(db)
                db.inputs._setting_locked = False  # noqa: PLW0212
            except Exception:  # noqa: PLW0703 (anything can be thrown by the script)
                OgnConditionScript._print_stacktrace(db)

        og.Controller.set(og.Controller.attribute("state:omni_initialized", node), False)

    @staticmethod
    def _print_stacktrace(db):
        stacktrace = traceback.format_exc().splitlines(keepends=True)
        stacktrace_iter = iter(stacktrace)
        stacktrace_output = ""

        for stacktrace_line in stacktrace_iter:
            if "OgnConditionScript.py" in stacktrace_line:
                # The stack trace shows that the exception originates from this file
                # Removing this useless information from the stack trace
                next(stacktrace_iter, None)
            else:
                stacktrace_output += stacktrace_line

        db.log_error(stacktrace_output)

    @staticmethod
    def release(node):
        rep.rng.release(node.get_prim_path())

    @staticmethod
    def compute(db) -> bool:
        state = db.shared_state
        # Check if user has opted in to running script nodes
        if not rep.annotators.annotator_utils.check_should_run_script():
            # User has not opted in, node will not be run
            if not state.has_warned_disabled:
                state.has_warned_disabled = True
                carb.log_warn("Condition script cannot run, script nodes are disabled.")
            return False

        # compile script if needed
        cur_script = db.inputs.conditionScript
        if len(cur_script) == 0:
            return False
        cur_script_path = state.omni_tempfile_path
        if state.omni_cur_script != cur_script:
            with open(cur_script_path, "w", encoding="utf-8") as tf:
                tf.write(cur_script)
            del tf

            state.omni_code_object = compile(cur_script, cur_script_path, "exec")
            state.omni_cur_script = cur_script
            state.omni_cur_script_path = cur_script_path
            del cur_script
            del cur_script_path

        if not state.omni_initialized:
            with ScriptContextSaver(state.omni_script_context):
                exec(state.omni_code_object)  # noqa: PLW0122
            if not state.omni_code_object.co_names:
                return False
            function_name = state.omni_code_object.co_names[0]
            state.condition_fn = state.omni_script_context[function_name]
            state.omni_initialized = True

        __condition_fn = state.condition_fn

        fn_params = inspect.signature(__condition_fn).parameters
        inputs = {}
        for param_name, param in fn_params.items():
            if db.node.get_attribute_exists(f"inputs:{param_name}"):
                inputs[param_name] = db.node.get_attribute(f"inputs:{param_name}").get()
            elif param.default is not inspect._empty:
                inputs[param_name] = param.default
            else:
                db.log_error(f"Missing parameter {param_name}")

        script_output = __condition_fn(**inputs)
        if type(script_output) != bool:
            db.log_warn(
                (
                    f"Condition script for node `{db.node.get_prim_path()}` did not return a `bool`, instead got ",
                    f"`{type(script_output)}` which evaluates to `{bool(script_output)}`",
                )
            )
        db.outputs.isConditionMet = bool(script_output)

        return True
