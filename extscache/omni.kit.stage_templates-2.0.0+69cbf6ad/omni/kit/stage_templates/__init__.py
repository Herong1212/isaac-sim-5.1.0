__all__ = ['NewStageExtension', 'register_template', 'unregister_template', 'get_stage_template_list', 'get_stage_template', 'get_default_template', 'new_stage', 'new_stage_with_callback', 'new_stage_async', 'load_templates', 'unload_templates', 'load_user_templates']

# NOTE: all imported classes must have different class names
from .new_stage import *
from .templates import *
