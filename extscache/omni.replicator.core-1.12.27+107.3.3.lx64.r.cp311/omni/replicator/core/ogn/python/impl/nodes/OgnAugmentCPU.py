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
from functools import reduce

import carb
import numpy as np
import omni.graph.core as og
import omni.replicator.core as rep
import warp as wp
from omni.replicator.core import annotators
from omni.replicator.core.ogn.OgnAugmentCPUDatabase import OgnAugmentCPUDatabase


def get_address(attr):
    ptr_type = ctypes.POINTER(ctypes.c_size_t)
    ptr = ctypes.cast(attr.memory, ptr_type)
    return ptr.contents.value


def get_wp_array(ptr, shape, strides, capacity, dtype, device):
    return wp.types.array(
        dtype=dtype,
        shape=shape,
        strides=strides,
        capacity=capacity,
        ptr=ptr,
        device=device,
        requires_grad=False,
    )


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


class OgnAugmentCPUInternalState:
    def __init__(self):
        self.rng = rep.rng.ReplicatorRNG()
        self.omni_cur_script = None
        self.omni_cur_script_path = None
        self.omni_tempfile_path = None
        self.omni_code_object = None
        self.omni_script_context = {}
        self.omni_initialized = False
        self.has_warned_disabled = False
        self.output_array = None


def get_seed(db, seed):
    state = db.shared_state
    is_seed_valid = seed is not None
    is_seed_changed = state.rng is None or seed != state.rng.seed
    if is_seed_valid and is_seed_changed:
        node_id = db.inputs.nodeId if db.node.get_attribute_exists("inputs:nodeId") else 0
        state.rng.initialize(seed, db.node, node_id)
    return state.rng.generator.integers(2147483647)


class OgnAugmentCPU:
    @staticmethod
    def internal_state():
        return OgnAugmentCPUInternalState()

    @staticmethod
    def initialize(context, node):
        rep.annotators.annotator_utils.script_node_check([node])
        state = OgnAugmentCPUDatabase.shared_internal_state(node)

        # Create a temporary file for storing the script
        with tempfile.NamedTemporaryFile(
            prefix="CustomAugmentationScriptEnteredByUser_", suffix=".py", delete=False
        ) as tf:
            state.omni_tempfile_path = tf.name

        og.Controller.set(og.Controller.attribute("state:omni_initialized", node), False)

    @staticmethod
    def release(node):
        rep.rng.release(node.get_prim_path())

        state = OgnAugmentCPUDatabase.shared_internal_state(node)

        # Same logic as when the reset button is pressed
        OgnAugmentCPU._try_cleanup(node)

        # Delete the temporary file for storing the script
        if os.path.exists(state.omni_tempfile_path):
            os.remove(state.omni_tempfile_path)

        state.output_array = None

    @staticmethod
    def _try_cleanup(node):
        # Skip if not setup in the fist place
        if og.Controller.get(og.Controller.attribute("state:omni_initialized", node)) is False:
            return

        state = OgnAugmentCPUDatabase.shared_internal_state(node)

        # Call the user-defined cleanup function
        if state.omni_cleanup_fn is not None:
            # Get the database object
            per_node_data = OgnAugmentCPUDatabase.PER_NODE_DATA[node.node_id()]
            db = per_node_data.get("_db")

            try:
                db.inputs._setting_locked = True  # noqa: PLW0212
                state.omni_cleanup_fn(db)
                db.inputs._setting_locked = False  # noqa: PLW0212
            except Exception:  # noqa: PLW0703 (anything can be thrown by the script)
                OgnAugmentCPU._print_stacktrace(db)

        og.Controller.set(og.Controller.attribute("state:omni_initialized", node), False)

    @staticmethod
    def _print_stacktrace(db):
        stacktrace = traceback.format_exc().splitlines(keepends=True)
        stacktrace_iter = iter(stacktrace)
        stacktrace_output = ""

        for stacktrace_line in stacktrace_iter:
            if "OgnAugmentCPU.py" in stacktrace_line:
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
        # Check if user has opted in to running script nodes
        if not rep.annotators.annotator_utils.check_should_run_script():
            # User has not opted in, node will not be run
            if not db.shared_state.has_warned_disabled:
                db.shared_state.has_warned_disabled = True
                carb.log_warn("Augmentation cannot run, script nodes are disabled.")
            return False

        # compile script if needed
        cur_script = db.inputs.augmentationScript
        cur_script_path = db.shared_state.omni_tempfile_path
        if db.shared_state.omni_cur_script != cur_script:
            with open(cur_script_path, "w", encoding="utf-8") as tf:
                tf.write(cur_script)
            del tf

            db.shared_state.omni_code_object = compile(cur_script, cur_script_path, "exec")
            db.shared_state.omni_cur_script = cur_script
            db.shared_state.omni_cur_script_path = cur_script_path
            del cur_script
            del cur_script_path

        width = db.inputs.width
        height = db.inputs.height
        array_format = db.inputs.format
        buffer_size = db.inputs.bufferSize
        data_in_type = db.inputs.dataType
        data_ptr = db.inputs.dataPtr
        strides_2 = db.inputs.strides
        device_idx = db.inputs.cudaDeviceIndex
        device = f"cuda:{device_idx}" if device_idx >= 0 else "cpu"
        state = db.shared_state

        if not db.shared_state.omni_initialized:
            with ScriptContextSaver(db.shared_state.omni_script_context):
                exec(db.shared_state.omni_code_object)  # noqa: PLW0122
            function_name = db.inputs.augmentationFunctionName
            if not function_name:
                return False

            db.shared_state.augmentation_fn = db.shared_state.omni_script_context[function_name]
            db.shared_state.omni_initialized = True

        augmentation_fn = db.shared_state.augmentation_fn

        fn_params = inspect.signature(augmentation_fn).parameters
        inputs = {}
        for param_name, param in fn_params.items():
            if param_name == "data_in":
                if data_ptr:
                    if (
                        param.annotation is not param.empty
                        and param.annotation.dtype in annotators.annotator_utils.NUMPY_TO_WARP_MAP
                    ):
                        data_in_type_np = param.annotation.dtype
                    elif data_in_type:
                        data_in_type_np = np.dtype(data_in_type).type
                    else:
                        # default to uint8
                        data_in_type_np = np.uint8
                    data_in_type_wp = annotators.annotator_utils.NUMPY_TO_WARP_MAP[data_in_type_np]
                    if array_format:
                        channels = annotators.annotator_utils._format_to_elem_count(array_format)
                    else:
                        channels = buffer_size // width // height // wp.types.type_size_in_bytes(dtype_in)
                    strides = (strides_2[1], strides_2[0], wp.types.type_size_in_bytes(data_in_type_wp))
                    data_in = get_wp_array(
                        data_ptr,
                        shape=(height, width, channels),
                        capacity=buffer_size,
                        strides=strides,
                        device=device,
                        dtype=data_in_type_wp,
                    ).numpy()
                elif db.inputs.data:
                    data_in = db.inputs.data.array_value()
                else:
                    return False
                inputs[param_name] = data_in.reshape(height, width, -1)
            elif param_name == "seed":
                if db.node.get_attribute_exists(f"inputs:{param_name}"):
                    input_seed = db.node.get_attribute(f"inputs:{param_name}").get()
                else:
                    input_seed = -1
                seed = get_seed(db, input_seed)
                inputs[param_name] = seed
            elif db.node.get_attribute_exists(f"inputs:{param_name}"):
                inputs[param_name] = db.node.get_attribute(f"inputs:{param_name}").get()
            else:
                inputs[param_name] = param.default

        # Set data output to match output data type and shape
        data_out = augmentation_fn(**inputs)
        shape_out = data_out.shape
        dtype_out = annotators.annotator_utils.NUMPY_TO_WARP_MAP[data_out.dtype.type]

        # Move to warp
        if (
            state.output_array is None
            or tuple(shape_out) != state.output_array.shape
            or dtype_out != state.output_array.dtype
        ):
            state.output_array = wp.empty(
                dtype=dtype_out,
                shape=tuple(shape_out),
                device="cpu",
                requires_grad=False,
            )

        state.output_array.assign(data_out)

        db.outputs.dataPtr = state.output_array.ptr
        db.outputs.dataShape = shape_out
        db.outputs.dataType = str(state.output_array.dtype)[:-2].split("warp.types.")[-1]
        db.outputs.deviceIndex = -1
        db.outputs.strides = state.output_array.strides[1], state.output_array.strides[0]
        db.outputs.width = width
        db.outputs.height = height
        db.outputs.bufferSize = reduce(lambda x, y: x * y, shape_out) * data_out.dtype.itemsize
        db.outputs.format = array_format
        db.outputs.exec = og.ExecutionAttributeState.ENABLED
        return True
