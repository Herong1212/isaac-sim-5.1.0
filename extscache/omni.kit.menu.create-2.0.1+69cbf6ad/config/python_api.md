# Public API for module omni.kit.menu.create:

## Classes

- class CreateMenuExtension(omni.ext.IExt)
  - def __init__(self)
  - def on_startup(self, ext_id)
  - def on_shutdown(self)
  - static def on_create_prim(prim_type, attributes, use_settings: bool = False)
  - static def on_create_light(light_type, attributes)
  - static def on_create_prims()

## Functions

- def rebuild_menus()
