# Public API for module omni.kit.stage_templates:

## Classes

- class NewStageExtension(omni.ext.IExt)
  - def on_startup(self, ext_id)
  - def on_shutdown(self)
  - def new_stage_empty(self, rootname)

## Functions

- def register_template(name, new_stage_fn, group = 0, rebuild = True)
- def unregister_template(name, rebuild: bool = True)
- def get_stage_template_list()
- def get_stage_template(name)
- def get_default_template()
- def new_stage(on_new_stage_fn = None, template = 'empty', usd_context = None)
- def new_stage_with_callback(on_new_stage_fn = None, template = 'empty', usd_context = None)
- async def new_stage_async(template = 'empty', usd_context = None)
- def load_user_templates()
