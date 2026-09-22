from omni.ui import color as cl


class ColorsNew:

    # New Tree Styles
    NewText = cl.shade(0xFF828282, light=0xFFE0E0E0)
    NewSelected = cl.shade(0xFFE39724, light=0xFFC5911A)
    NewSelectedBG = cl.shade(cl(.16, .16, .16, 1.0))


class Constants:
    FramePadding = 8


# Overrides for the new opt-in tree style
TREE_UI_STYLES = {
    "TreeView": {"background_selected_color": ColorsNew.NewSelectedBG},
    "TreeView.Frame": {"padding": Constants.FramePadding},
    "TreeView.Item.Name": {"color": ColorsNew.NewText},
    "TreeView.Item.Name:selected": {"color": ColorsNew.NewSelected},
    "TreeView.Item.Count:selected": {"color": ColorsNew.NewText},
}
