import os
import random
import carb

__all__ = [
    "get_random_material_list",
]


async def get_random_material_list(max_items=5, use_hidden=False):
    try:
        import omni.kit.material.library

        mdl_list = await omni.kit.material.library.get_mdl_list_async()

        # remove hidden materials for random choices
        if not use_hidden:
            mdl_hidden_list = [os.path.splitext(os.path.basename(mdl_path))[0] for mdl_path in omni.kit.material.library.get_material_hidden_list()]
            for mtl_info in mdl_list.copy():
                if mtl_info[0] in mdl_hidden_list:
                    mdl_list.remove(mtl_info)

        return random.sample(mdl_list, max_items)
    except ModuleNotFoundError as ex:  # pragma: no cover
        carb.log_warn(f"omni.kit.material.library.get_mdl_list_async() failed with {ex}")

    return []  # pragma: no cover
