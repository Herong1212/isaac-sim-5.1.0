# pylint: disable=unused-wildcard-import, wildcard-import, redefined-outer-name
import re
import sys

import carb
import omni.kit.test
from omni.kit import ui_test

from .test_func_common_help import *  # noqa: F403, F401
from .test_func_common_window import *  # noqa: F403, F401


class TestMenuCommon(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_common_menus(self):
        import omni.kit.material.library

        # wait for material to be preloaded so create menu is complete & menus don't rebuild during tests
        await omni.kit.material.library.get_mdl_list_async()
        await ui_test.human_delay()

        menus = omni.kit.menu.utils.get_merged_menus()
        prefix = "common_test"
        to_test = []
        this_module = sys.modules[__name__]
        for key in menus.keys():
            # edit menu only
            if key.startswith("Window") or key.startswith("Help"):
                for item in menus[key]["items"]:
                    if item.name != "" and item.has_action():
                        key_name = re.sub(r"\W|^(?=\d)", "_", key.lower())
                        func_name = re.sub(r"\W|^(?=\d)", "_", item.name.replace("${kit}/", "").lower())
                        while key_name and key_name[-1] == "_":
                            key_name = key_name[:-1]
                        while func_name and func_name[-1] == "_":
                            func_name = func_name[:-1]

                        test_fn = f"{prefix}_func_{key_name}_{func_name}"
                        try:
                            to_call = getattr(this_module, test_fn)
                            to_test.append(
                                (to_call, test_fn, item.original_menu_item if item.original_menu_item else item)
                            )
                        except AttributeError:
                            carb.log_error(f'test function "{test_fn}" not found')

                        if item.original_menu_item and item.original_menu_item.hotkey:
                            test_fn = f"{prefix}_hotkey_func_{key_name}_{func_name}"
                            try:
                                to_call = getattr(this_module, test_fn)
                                to_test.append((to_call, test_fn, item.original_menu_item))
                            except AttributeError:
                                carb.log_error(f'test function "{test_fn}" not found')

        for to_call, test_fn, menu_item in to_test:
            await omni.usd.get_context().new_stage_async()
            omni.kit.menu.utils.refresh_menu_items("Window")
            omni.kit.menu.utils.refresh_menu_items("Help")
            await ui_test.human_delay()
            print(f"Running test {test_fn}")
            try:
                await to_call(self, menu_item)
            except Exception as exc:  # pylint: disable=broad-exception-caught
                carb.log_error(f"error {test_fn} failed - {exc}")
                import traceback

                traceback.print_exc(file=sys.stdout)

    def get_stage_prims(self):
        stage = omni.usd.get_context().get_stage()
        return [prim.GetPath().pathString for prim in stage.TraverseAll() if not omni.usd.is_hidden_type(prim)]
