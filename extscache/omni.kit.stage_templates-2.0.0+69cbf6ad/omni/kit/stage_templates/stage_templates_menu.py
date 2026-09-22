import locale
import carb
import functools
import carb.settings
import omni.kit.app
from functools import partial


def get_action_name(name):
    return name.lower().replace('-', '_').replace(' ', '_')


class StageTemplateMenu:
    def __init__(self):
        pass

    def on_startup(self):
        self._build_sub_menu()
        omni.kit.menu.utils.add_menu_items(self._menu_list, "File")

        # update submenu if defaultTemplate changes
        self._update_setting = omni.kit.app.SettingChangeSubscription(
            "/persistent/app/newStage/defaultTemplate", lambda *_: omni.kit.menu.utils.refresh_menu_items("File")
        )

    def on_shutdown(self):  # pragma: no cover
        self._update_setting = None
        omni.kit.menu.utils.remove_menu_items(self._menu_list, "File")
        self._menu_list = None

    def _build_sub_menu(self):
        from omni.kit.menu.utils import MenuItemDescription

        def sort_cmp(template1, template2):
            return locale.strcoll(template1[0], template2[0])

        sub_menu = []
        default_template = omni.kit.stage_templates.get_default_template()
        stage_templates = omni.kit.stage_templates.get_stage_template_list()

        def template_ticked(sn: str) -> bool:
            return omni.kit.stage_templates.get_default_template() == sn

        for template_list in stage_templates:
            for template in sorted(template_list.items(), key=functools.cmp_to_key(sort_cmp)):
                stage_name = template[0]
                sub_menu.append(
                    MenuItemDescription(
                        name=stage_name.replace("_", " ").title(),
                        ticked=True,
                        ticked_fn=lambda sn=template[0]: template_ticked(sn),
                        onclick_action=("omni.kit.stage.templates", f"create_new_stage_{get_action_name(stage_name)}")
                    )
                )

        self._menu_list = [
            MenuItemDescription(
                name="New From Stage Template", glyph="file.svg", appear_after=["Open Recent", "New"], sub_menu=sub_menu
            )
        ]

    def _rebuild_sub_menu(self):
        if self._menu_list:
            omni.kit.menu.utils.remove_menu_items(self._menu_list, "File")
            self._build_sub_menu()
            omni.kit.menu.utils.add_menu_items(self._menu_list, "File")
