from omni.ui import color as cl

# Use same context menu style with content browser
cl.context_menu_background= cl.shade(cl('#343432'))
cl.context_menu_separator = cl.shade(0x449E9E9E)
cl.context_menu_text = cl.shade(cl('#9E9E9E'))

CONTEXT_MENU_STYLE = {
    "Menu": {"background_color": cl.context_menu_background_color, "color": cl.context_menu_text, "border_radius": 2},
    "Menu.Item": {"background_color": 0x0, "margin": 0},
    "Separator": {"background_color": 0x0, "color": cl.context_menu_separator},
}
