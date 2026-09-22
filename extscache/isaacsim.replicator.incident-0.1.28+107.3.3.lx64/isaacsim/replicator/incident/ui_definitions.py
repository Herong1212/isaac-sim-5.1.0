import omni.ui as ui
COLOR_BLACK = 0x0
BOUNDING_RADIUS = 1.5
UI_DISTANCE = 120
STRING_FIELD_WIDTH = 300

LABEL_WIDTH = 100
BUTTON_WIDTH = 100
VSTACK_SPACING = 10


def get_collapsable_frame_style():
    return {
        "border_radius": BOUNDING_RADIUS * 2,
        "border_color": COLOR_BLACK,
        "border_width": 1,
        "padding": 6,
        # "spacing": 10,
    }

# def get_button_style():
#     return {
#         "spacing": 10,
#     }

# TODO: Copy the small ui library from isaacsim.gui.components
# def cb_builder(label="", type="checkbox", text="checkbox", tooltip="", on_clicked_fn=None):
#     """Creates a Stylized Checkbox

#     Args:
#         label (str, optional): Label to the left of the UI element. Defaults to "".
#         type (str, optional): Type of UI element. Defaults to "checkbox".
#         default_val (bool, optional): Checked is True, Unchecked is False. Defaults to False.
#         tooltip (str, optional): Tooltip to display over the Label. Defaults to "".
#         on_clicked_fn (Callable, optional): Call-back function when clicked. Defaults to None.

#     Returns:
#         ui.SimpleBoolModel: model
#     """
#     with ui.HStack():
#         ui.Label(label, width=LABEL_WIDTH - 12, alignment=ui.Alignment.LEFT_CENTER, tooltip=tooltip)
#         callable = on_clicked_fn
#         if callable is None:
#             callable = lambda x: None
#         model = ui.CheckBox(
#             text,
#             name="Checkbox",
#             clicked_fn=callable,
#             style=get_button_style(),
#         )

#         return model


# def btn_builder(label="", type="button", text="button", tooltip="", on_clicked_fn=None):
#     """Creates a stylized button.

#     Args:
#         label (str, optional): Label to the left of the UI element. Defaults to "".
#         type (str, optional): Type of UI element. Defaults to "button".
#         text (str, optional): Text rendered on the button. Defaults to "button".
#         tooltip (str, optional): Tooltip to display over the Label. Defaults to "".
#         on_clicked_fn (Callable, optional): Call-back function when clicked. Defaults to None.

#     Returns:
#         ui.Button: Button
#     """
#     with ui.HStack():
#         ui.Label(label, width=LABEL_WIDTH, alignment=ui.Alignment.LEFT_CENTER, tooltip=tooltip)
#         btn = ui.Button(
#             text.upper(),
#             name="Button",
#             width=BUTTON_WIDTH,
#             clicked_fn=on_clicked_fn,
#             style=get_button_style(),
#             tooltip=tooltip,
#             alignment=ui.Alignment.LEFT_CENTER,
#         )
#         ui.Spacer(width=5)
#     return btn
