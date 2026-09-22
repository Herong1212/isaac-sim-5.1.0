"""This module defines custom highlight styles for labels in the omni.kit.widget.highlight_label package."""


from omni.ui import color as cl

cl.highlight_default = cl.shade(cl("#848484"))
cl.highlight_highlight = cl.shade(cl("#DFCB4A"))
cl.highlight_selected = cl.shade(cl("#1F2123"))

UI_STYLE = {
    # "HighlightLabel": {"color": cl.highlight_default},
    # "HighlightLabel:selected": {"color": cl.highlight_selected},
    "HighlightLabel::highlight": {"color": cl.highlight_highlight},
}
