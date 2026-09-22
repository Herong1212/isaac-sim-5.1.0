import os
import carb
import carb.settings
import omni.ext
import omni.kit.app
import asyncio
import glob
import omni.kit.actions.core
import omni.kit.stage_template.core
from functools import partial

import pxr.UsdGeom

from pxr import Sdf, UsdGeom, Usd, Gf
from contextlib import suppress


_extension_instance = None
_extension_path = None


def _try_unregister_page(page: str):  # pragma: no cover
    with suppress(Exception):
        import omni.kit.window.preferences

        omni.kit.window.preferences.unregister_page(page)


# must be initialized before templates
class NewStageExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        global _extension_path
        _extension_path = omni.kit.app.get_app().get_extension_manager().get_extension_path(ext_id)

        register_template("empty", self.new_stage_empty, 0)
        self._load_templates()
        self._load_user_templates()

        # as omni.kit.stage_templates loads before the UI, it cannot depend on omni.kit.window.preferences or other extensions.
        self._preferences_page = None
        self._menu_button1 = None
        self._menu_button2 = None
        self._hooks = []

        manager = omni.kit.app.get_app().get_extension_manager()
        self._hooks.append(
            manager.subscribe_to_extension_enable(
                on_enable_fn=lambda _: self._register_page(),
                on_disable_fn=lambda _: self._unregister_page(),
                ext_name="omni.kit.window.preferences",
                hook_name="omni.kit.stage_templates omni.kit.window.preferences listener",
            )
        )

        self._stage_template_menu = None
        self._hooks.append(
            manager.subscribe_to_extension_enable(
                on_enable_fn=lambda _: self._register_menu(),
                on_disable_fn=lambda _: self._unregister_menu(),
                ext_name="omni.kit.menu.utils",
                hook_name="omni.kit.stage_templates omni.kit.menu.utils listener",
            )
        )

        self._hooks.append(
            manager.subscribe_to_extension_enable(
                on_enable_fn=lambda _: self._register_property_menu(),
                on_disable_fn=lambda _: self._unregister_property_menu(),
                ext_name="omni.kit.property.usd",
                hook_name="omni.kit.stage_templates omni.kit.property.usd listener",
            )
        )

        global _extension_instance
        _extension_instance = self

    def on_shutdown(self):  # pragma: no cover
        global _extension_instance

        unregister_template("empty")
        self._unregister_page()
        self._unregister_menu()
        self._unregister_property_menu()
        self._hooks = None
        _extension_instance = None
        for user_template in self._user_scripts:
            del user_template
        self._unload_templates()
        self._user_scripts = None

    def _load_templates(self):
        from .templates.sunlight import SunlightStage
        from .templates.default_stage import DefaultStage

        self._new_stage_template_list = [SunlightStage(), DefaultStage()]

    def _unload_templates(self):  # pragma: no cover
        self._new_stage_template_list = None

    def _register_page(self):
        try:
            from omni.kit.window.preferences import register_page
            from .stage_templates_page import StageTemplatesPreferences

            self._preferences_page = register_page(StageTemplatesPreferences())
        except ModuleNotFoundError:  # pragma: no cover
            pass

    def _unregister_page(self):  # pragma: no cover
        if self._preferences_page:
            try:
                import omni.kit.window.preferences

                omni.kit.window.preferences.unregister_page(self._preferences_page)
                self._preferences_page = None
            except ModuleNotFoundError:  # pragma: no cover
                pass

    def _register_menu(self):
        try:
            from .stage_templates_menu import StageTemplateMenu

            self._stage_template_menu = StageTemplateMenu()
            self._stage_template_menu.on_startup()
        except ModuleNotFoundError:  # pragma: no cover
            pass

    def _unregister_menu(self):  # pragma: no cover
        if self._stage_template_menu:
            try:
                self._stage_template_menu.on_shutdown()
                self._stage_template_menu = None
            except ModuleNotFoundError:  # pragma: no cover
                pass

    def _has_axis(self, objects, axis):
        if not "stage" in objects:
            return False
        stage = objects["stage"]
        if stage:
            return UsdGeom.GetStageUpAxis(stage) != axis
        else:
            carb.log_error("_click_set_up_axis stage not found")
        return False

    def _click_set_up_axis(self, payload, axis):
        stage = payload.get_stage()
        if stage:
            rootLayer = stage.GetRootLayer()
            if rootLayer:
                rootLayer.SetPermissionToEdit(True)
                with Usd.EditContext(stage, rootLayer):
                    UsdGeom.SetStageUpAxis(stage, axis)
                    from omni.kit.property.usd import PrimPathWidget

                    PrimPathWidget.rebuild()
            else:
                carb.log_error("_click_set_up_axis rootLayer not found")
        else:
            carb.log_error("_click_set_up_axis stage not found")

    def _register_property_menu(self):
        # +add menu item(s)
        try:
            import omni.kit.widget.context_menu
            from omni.kit.property.usd import PrimPathWidget

            context_menu = omni.kit.widget.context_menu.get_instance()
            if context_menu is None:  # pragma: no cover
                self._menu_button1 = None
                self._menu_button2 = None
                carb.log_error("context_menu is disabled!")
                return None
        except ModuleNotFoundError:  # pragma: no cover
            pass

        self._menu_button1 = PrimPathWidget.add_button_menu_entry(
            "Stage/Set up axis +Y",
            show_fn=partial(self._has_axis, axis=UsdGeom.Tokens.y),
            onclick_fn=partial(self._click_set_up_axis, axis=UsdGeom.Tokens.y),
            add_to_context_menu=False,
        )
        self._menu_button2 = PrimPathWidget.add_button_menu_entry(
            "Stage/Set up axis +Z",
            show_fn=partial(self._has_axis, axis=UsdGeom.Tokens.z),
            onclick_fn=partial(self._click_set_up_axis, axis=UsdGeom.Tokens.z),
            add_to_context_menu=False,
        )

    def _unregister_property_menu(self):  # pragma: no cover
        if self._menu_button1 or self._menu_button2:
            try:
                from omni.kit.property.usd import PrimPathWidget

                if self._menu_button1:
                    PrimPathWidget.remove_button_menu_entry(self._menu_button1)
                    self._menu_button1 = None

                if self._menu_button2:
                    PrimPathWidget.remove_button_menu_entry(self._menu_button2)
                    self._menu_button2 = None
            except ModuleNotFoundError:  # pragma: no cover
                pass

    def new_stage_empty(self, rootname):
        pass

    def _load_user_templates(self):
        settings = carb.settings.get_settings()
        template_paths = settings.get("/persistent/app/newStage/templatePath")

        # Create template directories
        original_umask = os.umask(0)
        for path in template_paths:
            path = carb.tokens.get_tokens_interface().resolve(path)
            if not os.path.isdir(path):
                try:
                    os.makedirs(path)
                except Exception:
                    carb.log_error(f"Failed to create directory {path}")
        os.umask(original_umask)

        # Load template scripts
        self._user_scripts = []
        for path in template_paths:

            for full_path in glob.glob(f"{carb.tokens.get_tokens_interface().resolve(path)}/*.py"):
                try:
                    with open(os.path.normpath(full_path)) as f:
                        user_script = f.read()
                        carb.log_warn(f"loaded new_stage template {full_path}")
                        exec(user_script)
                        self._user_scripts.append(user_script)
                except Exception as e:  # pragma: no cover
                    carb.log_error(f"error loading {full_path}: {e}")


def register_template(name, new_stage_fn, group=0, rebuild=True):
    """Register new_stage Template

    Args:
        param1 (str): template name
        param2 (callable): function to create template
        param3 (int): group number. User by menu to split into groups with separators

    Returns:
        bool: True for success, False when template already exists.
    """
    value = omni.kit.stage_template.core.register_template(name, new_stage_fn, group)
    if rebuild:
        rebuild_stage_template_menu()
    return value


def unregister_template(name, rebuild: bool=True):  # pragma: no cover
    """Remove registered new_stage Template

    Args:
        param1 (str): template name

    Returns:
        nothing
    """
    value = omni.kit.stage_template.core.unregister_template(name)
    if rebuild:
        rebuild_stage_template_menu()
    return value


def rebuild_stage_template_menu() -> None:
    if _extension_instance and _extension_instance._stage_template_menu:
        _extension_instance._stage_template_menu._rebuild_sub_menu()


def get_stage_template_list():
    """Get list of loaded new_stage templates

    Args:
        none

    Returns:
        list: list of groups of new_stage template names & create function pointers
    """
    return omni.kit.stage_template.core.get_stage_template_list()


def get_stage_template(name):
    """Get named new_stage template & create function pointer

    Args:
        param1 (str): template name

    Returns:
        tuple: new_stage template name & create function pointer
    """
    return omni.kit.stage_template.core.get_stage_template(name)


def get_default_template():
    """Get name of default new_stage template. Used when new_stage is called without template name specified

    Args:
        None

    Returns:
        str: new_stage template name
    """
    return omni.kit.stage_template.core.get_default_template()


def new_stage(on_new_stage_fn=None, template="empty", usd_context=None):
    """Execute new_stage

    Args:
        param2 (str): template name, if not specified default name is used
        param3 (omni.usd.UsdContext): usd_context, the usd_context to create new stage

    Returns:
        nothing
    """
    return omni.kit.stage_template.core.new_stage(on_new_stage_fn, template, usd_context)


def new_stage_with_callback(on_new_stage_fn=None, template="empty", usd_context=None):
    """Execute new_stage

    Args:
        param1 (callable): callback when new_stage is created
        param2 (str): template name, if not specified default name is used
        param3 (omni.usd.UsdContext): usd_context, the usd_context to create new stage

    Returns:
        nothing
    """
    return omni.kit.stage_template.core.new_stage_with_callback(on_new_stage_fn, template, usd_context)


async def new_stage_async(template="empty", usd_context=None):
    """Execute new_stage asynchronously

    Args:
        param1 (str): template name, if not specified default name is used
        param2 (omni.usd.UsdContext): usd_context, the usd_context to create new stage

    Returns:
        awaitable object until stage is created
    """
    return await omni.kit.stage_template.core.new_stage_async(template, usd_context)


def load_user_templates():
    if _extension_instance:
        _extension_instance._load_user_templates()
