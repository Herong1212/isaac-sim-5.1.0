# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.kit.app
import omni.kit.test
import omni.usd

from ..scripts.core_adapter import StageAdapter
from ..scripts.extension import RegistryEventType, get_adapter_registry

CALLBACK_MISSED_MSG = "Callback not hit."
CALLBACK_TYPE_WRONG_MSG = "The callback type does not match."
INSTANCE_FAIL_MSG = "Failed to instance adapter."
INSTANCE_TYPE_MISMATCH_MSG = "Instanced adapter type does not match expected."
ADAPTER_METHOD_CALL_FAIL_MSG = "Failed to call method on adapter."


# Dummy test class
class TestStageAdapter(StageAdapter):
    def GetPrimAtPath(self, path):
        pass

    def GetAttributeAtPath(self, path):
        pass

    def CreateChangeTracker(self, attr_names, prim_paths, callback, stage):  # pylint: disable=arguments-differ
        pass

    def convert_data(self, data, dst_adapter_name: str):
        pass

    def resolve_path_array(self, path, resolve_path: str, path_list, index):
        pass

    def get_notice_paths(self, stage, notice):
        pass

    # Dummy test method that returns true when called
    def test_hook(self) -> bool:
        return True


class TestAdapterRegistry(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        self._stage = omni.usd.get_context().get_stage()
        self._callback_hit = False, None
        self._registry = get_adapter_registry()
        self._registry_event_sub = self._registry.event_stream.create_subscription_to_pop(
            self._registry_updated, name="registery_updated"
        )

    async def tearDown(self):
        self._stage = None
        self._callback_hit = False, None
        self._registry_event_sub = None

    # ============ REGISTRY TESTS ============

    # Add an adapter to the registry and make sure the callback was hit
    async def test_add_adapter(self):
        self._unregister_all_stage_adapters()
        self._callback_hit = False, None
        self._registry.register_stage_adapter("test_stage_adapter", TestStageAdapter)
        registry_results = self._check_registry("test_stage_adapter", TestStageAdapter)
        # Make sure the adapter actually got added to the registry
        self.assertTrue(registry_results[0], registry_results[1])
        # Make sure the callback was hit
        self.assertTrue(self._callback_hit[0] is True, CALLBACK_MISSED_MSG)
        self.assertTrue(self._callback_hit[1] is RegistryEventType.ADAPTER_ADDED, CALLBACK_TYPE_WRONG_MSG)
        self._callback_hit = False, None

    # Remove an adapter from the registry and make sure the callback was hit
    async def test_remove_adapter(self):
        self._unregister_all_stage_adapters()
        self._callback_hit = False, None
        self._registry.register_stage_adapter("test_stage_adapter", TestStageAdapter)
        self._registry.unregister_stage_adapter("test_stage_adapter")
        registry_results = self._check_registry("test_stage_adapter", TestStageAdapter)
        # Make sure the adapter actually got removed from the registry
        self.assertFalse(registry_results[0], registry_results[1])
        # Make sure the callback was hit
        self.assertTrue(self._callback_hit[0] is True, CALLBACK_MISSED_MSG)
        self.assertTrue(self._callback_hit[1] is RegistryEventType.ADAPTER_REMOVED, CALLBACK_TYPE_WRONG_MSG)
        self._callback_hit = False, None

    # Add an adapter to the registry, make sure the callback was hit, and then initialize the adapter
    async def test_adapter_initialization(self):
        self._unregister_all_stage_adapters()
        self._callback_hit = False, None
        self._registry.register_stage_adapter("test_stage_adapter", TestStageAdapter)
        registry_results = self._check_registry("test_stage_adapter", TestStageAdapter)
        # Make sure the adapter actually got added to the registry
        self.assertTrue(registry_results[0], registry_results[1])
        # Make sure the callback was hit
        self.assertTrue(self._callback_hit[0] is True, CALLBACK_MISSED_MSG)
        self.assertTrue(self._callback_hit[1] is RegistryEventType.ADAPTER_ADDED, CALLBACK_TYPE_WRONG_MSG)
        self._callback_hit = False, None

        instantiated_adapters = self._registry.instantiate_all_stage_adapters(self._stage)
        adapter = instantiated_adapters["test_stage_adapter"]
        # Make sure the adapter was initialized, type matches as expected, and methods are accessible
        self.assertTrue(adapter is not None, INSTANCE_FAIL_MSG)
        self.assertTrue(
            type(adapter) == TestStageAdapter, INSTANCE_TYPE_MISMATCH_MSG  # pylint: disable=unidiomatic-typecheck
        )
        self.assertTrue(adapter.test_hook(), ADAPTER_METHOD_CALL_FAIL_MSG)

    # ============ UTILITY METHODS ============

    def _registry_updated(self, event):
        self._callback_hit = True, RegistryEventType(event.type)

    def _check_registry(self, name, adapter_type):
        if name not in self._registry.registered_adapters.keys():
            return False, f"{name} is missing from the dictionary of registered adapters."
        if adapter_type not in self._registry.registered_adapters.values():
            return False, f"{adapter_type} is missing from the dictionary of registered adapters."
        return True, f"{name} and {adapter_type} are registered."

    def _unregister_all_stage_adapters(self):
        self._registry.registered_adapters.clear()
