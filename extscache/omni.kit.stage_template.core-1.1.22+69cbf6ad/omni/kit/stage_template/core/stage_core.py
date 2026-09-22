"""This module provides core functionality for registering and unregistering new stage templates, handling stage creation with templates and setting transformations for USD primitives."""

__all__ = ['CoreStageExtension', 'register_template', 'unregister_template', 'get_stage_template_list', 'get_stage_template', 'get_default_template', 'new_stage', 'new_stage_with_callback', 'new_stage_async']

import carb
import carb.settings
import omni.ext
import omni.usd
import asyncio
import omni.kit.actions.core
from inspect import signature
from functools import partial
from pxr import Sdf, UsdGeom, Usd, Gf


_template_list = []
_clear_dirty_task = None


class CoreStageExtension(omni.ext.IExt):
    """This class provides core functionality for registering and unregistering new stage templates, handling stage creation with templates and setting transformations for USD primitives."""

    def on_startup(self, ext_id):
        """Called when the extension starts up.

        Args:
            ext_id (str): The unique identifier for the extension.
        """
        global clear_dirty_task

        _clear_dirty_task = None

    def on_shutdown(self):
        """Called when the extension is shutting down."""
        global _template_list
        global _clear_dirty_task

        if _clear_dirty_task:
            _clear_dirty_task.cancel()
            _clear_dirty_task = None

        _template_list = None


def get_action_name(name):
    """Converts a name to a valid action identifier.

    This function takes a given name string and converts it to a lowercase string
    that can be used as an action identifier. It replaces hyphens and spaces with underscores.

    Args:
        name (str): The name to convert into an action identifier.

    Returns:
        str: A valid action identifier derived from the input name."""
    return name.lower().replace("-", "_").replace(" ", "_")


def register_template(name, new_stage_fn, group=0):
    """Registers a new stage template and associates it with an action.

    Args:
        name (str): The unique name of the template to register.
        new_stage_fn (callable): The function to create a new stage when this template is used.
        group (int): An identifier to group templates, used by the menu to split into groups with separators.

    Returns:
        bool: True if the template was successfully registered, False if the template already exists."""
    # check if element exists
    global _template_list

    exists = get_stage_template(name)
    if exists:
        carb.log_warn(f"template {name} already exists")
        return False

    try:
        exists = _template_list[group]
    except IndexError:
        _template_list.insert(group, {})

    _template_list[group][name] = (name, new_stage_fn)

    omni.kit.actions.core.get_action_registry().register_action(
        "omni.kit.stage.templates",
        f"create_new_stage_{get_action_name(name)}",
        lambda t=name: omni.kit.window.file.new(t),
        display_name=f"Create New Stage {name}",
        description=f"Create New Stage {name}",
        tag="Create Stage Template",
    )

    return True


def unregister_template(name):
    """Unregisters a previously registered new_stage template.

    Args:
        name (str): The name of the template to unregister.

    Returns:
        None
    """
    global _template_list
    if _template_list is not None:
        for templates in _template_list:
            if name in templates:
                del templates[name]

    omni.kit.actions.core.get_action_registry().deregister_action(
        "omni.kit.stage.templates", f"create_new_stage_{get_action_name(name)}"
    )


def get_stage_template_list():
    """Returns a list of loaded new_stage templates.

    Returns:
        list or None: A list of groups, each containing new_stage template names and their corresponding creation function pointers, or None if no templates are loaded.
    """
    global _template_list
    if not _template_list or len(_template_list) == 0:
        return None
    return _template_list


def get_stage_template(name):
    """Get named new_stage template & create function pointer

    Args:
        param1 (str): template name

    Returns:
        tuple: new_stage template name & create function pointer
    """
    global _template_list
    if not _template_list:
        return None

    for templates in _template_list:
        if name in templates:
            return templates[name]
    return None


def get_default_template():
    """Get name of default new_stage template. Used when new_stage is called without template name specified

    Returns:
        str: The name of the default new_stage template."""
    settings = carb.settings.get_settings()
    return settings.get("/persistent/app/newStage/defaultTemplate")


def __new_stage_finalize(create_result, error_message, usd_context, template=None, on_new_stage_fn=None):
    """Finalizes the creation of a new USD stage after the stage is created.

    Args:
        create_result (bool): Result of the stage creation, True if successful.
        error_message (str): Message describing the error if stage creation failed.
        usd_context (:obj:`omni.usd.UsdContext`): Context of the USD stage that is being finalized.
        template (Optional[str]): Name of the template to use for initializing the stage. Uses default if None.
        on_new_stage_fn (Optional[callable]): Callback function to be called after stage finalization.
    """
    global _clear_dirty_task

    if _clear_dirty_task:
        _clear_dirty_task.cancel()
        _clear_dirty_task = None

    if create_result:
        stage = usd_context.get_stage()

        # already finalized
        if stage.HasDefaultPrim():
            return

        with Usd.EditContext(stage, stage.GetRootLayer()):
            settings = carb.settings.get_settings()
            default_prim_name = settings.get("/persistent/app/stage/defaultPrimName")
            up_axis = settings.get("/persistent/app/stage/upAxis")
            time_codes_per_second = settings.get_as_float("/persistent/app/stage/timeCodesPerSecond")
            time_code_range = settings.get("/persistent/app/stage/timeCodeRange")
            if time_code_range is None:
                time_code_range = [0, 100]

            rootname = f"/{default_prim_name}"

            # Set up axis
            if up_axis == "Y" or up_axis == "y":
                UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)
            else:
                UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)

            # Set timecodes per second
            stage.SetTimeCodesPerSecond(time_codes_per_second)

            # Start and end time code
            if time_code_range:
                stage.SetStartTimeCode(time_code_range[0])
                stage.SetEndTimeCode(time_code_range[1])

            # Create defaultPrim
            default_prim = UsdGeom.Xform.Define(stage, Sdf.Path(rootname)).GetPrim()
            if not default_prim:
                carb.log_error("Failed to create defaultPrim at {rootname}")
                return
            stage.SetDefaultPrim(default_prim)

            if template is None:
                template = get_default_template()

            # Run script
            item = get_stage_template(template)
            if item and item[1]:
                try:
                    create_fn = item[1]
                    sig = signature(create_fn)
                    if len(sig.parameters) == 1:
                        create_fn(rootname)
                    elif len(sig.parameters) == 2:
                        create_fn(rootname, usd_context.get_name())
                    else:
                        carb.log_error(f"template {template} has incorrect parameter count")

                except Exception as error:
                    carb.log_error(f"exception in {template} {error}")

    omni.kit.undo.clear_stack()
    usd_context.set_pending_edit(False)

    # Clear the stage dirty state again, as bound materials can set it
    async def clear_dirty(usd_context):
        import omni.kit.app

        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        usd_context.set_pending_edit(False)
        _clear_dirty_task = None
        if on_new_stage_fn:
            on_new_stage_fn(create_result, error_message)

    _clear_dirty_task = asyncio.ensure_future(clear_dirty(usd_context))


def new_stage(on_new_stage_fn=None, template="empty", usd_context=None):
    """Execute new_stage

    Args:
        on_new_stage_fn (Optional[callable]): Callback function to be called when new stage is created.
        template (str): Template name. If not specified, the default template is used.
        usd_context (Optional[:obj:`omni.usd.UsdContext`]): The UsdContext to create a new stage in. If not provided, the current context is used.
    """
    if usd_context is None:
        usd_context = omni.usd.get_context()

    if on_new_stage_fn is not None:
        carb.log_warn(
            "omni.kit.stage_template.core.new_stage(callback, ...) is deprecated. \
            Use `omni.kit.stage_template.core.new_stage_with_callback` instead."
        )
        new_stage_with_callback(on_new_stage_fn, template, usd_context)
    else:
        __new_stage_finalize(usd_context.new_stage(), "", usd_context, template=template, on_new_stage_fn=None)


def new_stage_with_callback(on_new_stage_fn=None, template="empty", usd_context=None):
    """Creates a new USD stage using the specified template and context, then applies post-creation operations via a callback.

    Args:
        on_new_stage_fn (Optional[callable]): A callback function to be called after the new stage is created. It should accept two arguments: a boolean indicating the success of the stage creation, and an error message if the creation failed.
        template (str): The name of the template to use for creating the new stage. If not specified, 'empty' is used as the default.
        usd_context (Optional[:obj:`omni.usd.UsdContext`]): The USD context within which the new stage is to be created. If not provided, the default USD context is used.

    Returns:
        None"""

    if usd_context is None:
        usd_context = omni.usd.get_context()

    usd_context.new_stage_with_callback(
        partial(__new_stage_finalize, usd_context=usd_context, template=template, on_new_stage_fn=on_new_stage_fn)
    )


async def new_stage_async(template="empty", usd_context=None):
    """Execute new_stage asynchronously

    This function initializes the creation of a new USD stage asynchronously based on the specified template name. The operation is performed in the context of the given UsdContext. If no UsdContext is provided, the default context is used. The function is a coroutine and should be awaited to ensure the stage creation process is completed.

    Args:
        template (str): The name of the template to use for creating the new stage. If not specified, the default 'empty' template is used.
        usd_context (Optional[:obj:`omni.usd.UsdContext`]): The UsdContext in which the new stage will be created. If not provided, the default UsdContext is used.

    Returns:
        Tuple[bool, str]: A tuple containing a boolean indicating the success status of the stage creation and an error message, if any occurred.
    """

    if usd_context is None:
        usd_context = omni.usd.get_context()

    f = asyncio.Future()

    def on_new_stage(result, err_msg):
        if not f.done():
            f.set_result((result, err_msg))

    new_stage_with_callback(on_new_stage, template, usd_context)
    return await f
