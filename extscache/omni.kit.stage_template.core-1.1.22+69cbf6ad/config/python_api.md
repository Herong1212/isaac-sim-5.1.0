# Public API for module omni.kit.stage_template.core:

## Functions

- def register_template(name, new_stage_fn, group = 0)
- def unregister_template(name)
- def get_stage_template_list()
- def get_stage_template(name)
- def get_default_template()
- def new_stage(on_new_stage_fn = None, template = 'empty', usd_context = None)
- def new_stage_with_callback(on_new_stage_fn = None, template = 'empty', usd_context = None)
- async def new_stage_async(template = 'empty', usd_context = None)
