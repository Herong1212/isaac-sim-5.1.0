import omni.ext
import omni.ui as ui
from pxr import Tf

from .list import ListDelegate, ListModel
from .table import TableDelegate, TableModel


def get_debug_flags_with_prefix(prefix):
    """
    Get list of flags for a given prefix
    """
    prefix += "_"
    return list(sorted([flag for flag in Tf.Debug.GetDebugSymbolNames() if flag.startswith(prefix)]))


class DebugFlagsExtension(omni.ext.IExt):
    """
    Main Window
    """

    def on_startup(self, ext_id):
        self._setup_debug_prefix_list()
        self._setup_debug_flags_list()

        self._window = ui.Window("Debug Flags", width=900, height=500)
        self._window.frame.set_style({"Window": {"background_color": 0xFF555555}})
        with self._window.frame:
            with ui.HStack(spacing=0):
                # Left Menu
                with ui.ScrollingFrame(
                    width=ui.Pixel(130),
                    horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                    vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                ):

                    with ui.ZStack():
                        ui.Rectangle(
                            style={"background_color": 0xFF3A3A3A, "border_color": 0xFF282828, "border_width": 2}
                        )
                        with ui.VStack():
                            ui.Spacer(height=5)
                            ui.TreeView(
                                self._debug_prefixes_model,
                                delegate=self._debug_prefixes_delegate,
                                root_visible=False,
                            )
                # Right Menu
                ui.Spacer(width=ui.Percent(1))
                with ui.ScrollingFrame():
                    ui.TreeView(
                        self._debug_flags_model,
                        delegate=self._debug_flags_delegate,
                        columns_resizable=True,
                        column_widths=[ui.Fraction(2), ui.Fraction(3)],
                        root_visible=False,
                        header_visible=True,
                    )

    def on_shutdown(self):
        self._debug_flag_prefixes = None
        self._debug_prefixes_model = None
        self._debug_prefixes_delegate = None
        self._debug_flags_model = None
        self._debug_flags_delegate = None
        if self._window:
            self._window.destroy()
            self._window = None

    def select_prefix(self, prefix):
        """
        Repopulate the table for a given prefix
        """
        new_flags = get_debug_flags_with_prefix(prefix)
        self._debug_flags_model.update_entries(new_flags)

    def _setup_debug_prefix_list(self):
        """
        Setup the list used for the left menu
        """
        allDebugFlags = Tf.Debug.GetDebugSymbolNames()
        debug_flag_prefixes = [x[: x.find("_")] if x.find("_") > 0 else x for x in allDebugFlags]
        self._debug_flag_prefixes = list(sorted(set(debug_flag_prefixes)))
        self._debug_prefixes_model = ListModel(self._debug_flag_prefixes)
        self._debug_prefixes_delegate = ListDelegate(self)

    def _setup_debug_flags_list(self):
        """
        Initialize classes for table
        """
        self._debug_flags_model = TableModel([])
        self._debug_flags_delegate = TableDelegate()
