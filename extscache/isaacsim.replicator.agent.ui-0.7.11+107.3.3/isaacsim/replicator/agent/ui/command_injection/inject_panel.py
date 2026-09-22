from isaacsim.replicator.agent.core.agent_manager import AgentManager
from isaacsim.replicator.agent.ui.settings import *
from isaacsim.replicator.agent.ui.ui_util import *


class InjectPanel:
    """
    Inject Panel in the Command Injection window.
    - For simulation control injecttion
    """

    def __init__(self, events, variables):
        self._variables = variables
        self._events = events
        self._frame = None
        self._inject_agent_button = None
        self._inject_agent_textbox = None

    def _inject_agent_command_callback(self):
        cmd_lines = self._inject_command_string.splitlines()
        AgentManager.get_instance().inject_command_for_all_agents(cmd_lines, True)

    def _on_agent_command_changed(self, model):
        self._inject_command_string = model.get_value_as_string()

    def build_ui_frame(self):
        if self._frame == None:
            self._frame = ui.CollapsableFrame(
                title="Inject Control",
                height=0,
                collapsed=False,
                style=get_collapsable_frame_style(),
                name="subFrame",
                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
            )
            self.build_ui()

    def build_ui(self):
        if self._inject_agent_button is None:
            with self._frame:
                with ui.VStack(spacing=5, height=0):
                    with ui.HStack():
                        command_label = ui.Label("\tCommand", width=UI_DISTANCE)
                        command_label.set_tooltip(
                            'Enter the full commands here in the format of "agent_name command parameters".'
                        )
                        self._inject_agent_textbox = ui.StringField(
                            height=100, multiline=True, width=STRING_FIELD_WIDTH
                        )
                        self._inject_agent_textbox.model.add_value_changed_fn(self._on_agent_command_changed)
                    with ui.HStack():
                        ui.Spacer(width=UI_DISTANCE)
                        self._inject_agent_button = ui.Button(
                            text="Inject",
                            width=120,
                        )
                        self._inject_agent_button.set_clicked_fn(self._inject_agent_command_callback)
