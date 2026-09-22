from collections import defaultdict
from inspect import isclass
from functools import partial
import omni.kit.commands
import omni.kit.undo
from omni import ui
from .history import HistoryModel, HistoryDelegate, MainItem
from .search import SearchModel, SearchDelegate, CommandItem, Columns


class Window:
    def __init__(self, title):
        self._win_history = ui.Window(title, width=700, height=500)
        self._win_search = None
        self._search_frame = None
        self._doc_frame = None
        self._history_delegate = HistoryDelegate()
        self._search_delegate = SearchDelegate()

        self._build_ui()

        omni.kit.commands.subscribe_on_change(self._update_ui)
        self._update_ui()

    def destroy(self):
        self._win_history = None
        self._win_search = None
        self._search_frame = None
        self._doc_frame = None
        self._history_delegate = None
        self._search_delegate = None

        omni.kit.commands.unsubscribe_on_change(self._update_ui)

    def show(self):
        self._win_history.visible = True
        self._win_history.focus()

    def hide(self):
        self._win_history.visible = False
        if self._win_search is not None:
            self._win_search.visible = False

    def _build_ui(self):
        with self._win_history.frame:
            with ui.VStack():
                with ui.HStack(height=20):
                    ui.Button("Clear history", width=60, clicked_fn=self._clear_history)
                    ui.Button("Search commands", width=60, clicked_fn=self._show_registered)
                with ui.ScrollingFrame(
                    horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                    vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                    style_type_name_override="TreeView",
                ):
                    self._history_model = HistoryModel()
                    self._history_tree_view = ui.TreeView(
                        self._history_model,
                        delegate=self._history_delegate,
                        root_visible=False,
                        style={"TreeView.Item::error": {"color": 0xFF0000BB}},
                        column_widths=[ui.Fraction(1)],
                    )
                    self._history_tree_view.set_mouse_double_clicked_fn(self._on_double_click)
                with ui.HStack(height=20):
                    ui.Label("Generate script to clipboard from:", width=0)
                    ui.Button("Top-level commands", width=60, clicked_fn=partial(self._copy_to_clipboard, False))
                    ui.Button("Selected commands", width=60, clicked_fn=partial(self._copy_to_clipboard, True))

    def _on_double_click(self, x, y, b, m):
        if len(self._history_tree_view.selection) <= 0:
            return

        item = self._history_tree_view.selection[0]
        if isinstance(item, MainItem):
            self._history_tree_view.set_expanded(item, not self._history_tree_view.is_expanded(item), False)

    def _copy_to_clipboard(self, only_selected):
        omni.kit.clipboard.copy(self._generate_command_script(only_selected))

    def _clear_history(self):
        omni.kit.undo.clear_history()
        self._history_model._commands_changed()

    def _show_registered(self):
        if self._win_search is None:
            self._win_search = ui.Window(
                "Search Commands", width=700, height=500, dockPreference=ui.DockPreference.MAIN
            )

            with self._win_search.frame:
                with ui.VStack():
                    with ui.HStack(height=20):
                        ui.Label("Find in Command Class: ", width=0)
                        self._search_field_name = ui.StringField(width=ui.Fraction(0.5))
                        self._search_field_name.model.add_value_changed_fn(lambda _: self._refresh_list())
                        ui.Label(" Extension: ", width=0)
                        self._search_field_ext = ui.StringField(width=ui.Fraction(0.5))
                        self._search_field_ext.model.add_value_changed_fn(lambda _: self._refresh_list())
                    ui.Spacer(height=5)
                    with ui.HStack(height=300):
                        self._search_frame = ui.ScrollingFrame(
                            horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                            vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                            style_type_name_override="TreeView",
                        )
                        with self._search_frame:
                            self._search_tree_model = SearchModel()
                            self._search_tree_view = ui.TreeView(
                                self._search_tree_model,
                                delegate=self._search_delegate,
                                selection_changed_fn=self._on_selection_changed,
                                root_visible=False,
                                header_visible=True,
                                columns_resizable=True,
                                column_widths=[x.width for x in Columns.ORDER],
                            )
                    self._doc_frame = ui.ScrollingFrame(
                        horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                        vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                    )
            self._refresh_list()

        self._win_search.visible = True
        self._win_search.focus()

        if not self._win_search.docked:
            self._win_search.deferred_dock_in("Commands", ui.DockPolicy.CURRENT_WINDOW_IS_ACTIVE)

    def _on_selection_changed(self, selected_items):
        with self._doc_frame:
            with ui.VStack(height=40):
                for item in selected_items:
                    if isinstance(item, CommandItem):
                        class_sig = omni.kit.commands.get_command_class_signature(item.command_model.as_string)
                        ui.Label(f"{item.command_model.as_string}{class_sig}", height=30, word_wrap=True)
                        ui.Label(f"Documentation:", height=30)
                        if item.doc is None or item.doc == omni.kit.commands.Command.__doc__:
                            ui.Label("\n\t<None>")
                        else:
                            lbl = ui.Label(item.doc.strip(), word_wrap=True)


    def _update_ui(self):
        self._history_model._commands_changed()
        self._refresh_list()  # TODO: check if this is called too much

    def _refresh_list(self):
        if self._search_frame is None:
            return

        search_name = self._search_field_name.model.get_value_as_string().lower().strip()
        search_ext = self._search_field_ext.model.get_value_as_string().lower().strip()
        self._search_tree_model._clear_commands()

        commands = omni.kit.commands.get_commands()
        manager = omni.kit.app.get_app().get_extension_manager()

        for cmd_list in commands.values():
            for command in cmd_list.values():
                ext_id = manager.get_extension_id_by_module(command.__module__)
                if (
                    (search_name == "" or command.__name__.lower().find(search_name) != -1)
                    and (search_ext == "" or ext_id.find(search_ext) != -1)
                ):
                    ext_name = omni.ext.get_extension_name(ext_id) if ext_id else "Unknown"
                    self._search_tree_model._add_command(CommandItem(command, ext_name))

        self._search_tree_view.clear_selection()
        self._search_tree_model._commands_changed()

    def _generate_command_script(self, only_selected):
        history = omni.kit.undo.get_history().values()
        code_str = ""

        all_imports = defaultdict(set)
        arg_imports = defaultdict(set)

        """
        parses all parent module names into respective imports "import foo", "import foo.bar" or
        "from foo import baz, bar, ..." format and aggregates them across all found modules

        e.g.
        "foo" -> "import foo"
        "foo.bar" -> "from foo import bar"
        "foo.bar.baz" -> "import foo" and "from foo.bar import baz"

        direct will prevent using from e.g. "foo.bar" -> "import foo" "import foo.bar"
        """
        def parse_module_name(name, direct=False):
            if name == "builtins":
                return

            lst = name.split(".")
            ln = len(lst)
            if ln == 1:
                # import foo
                all_imports[0].add(lst[0])
            else:
                max_off = ln-1 if direct else ln-2

                # create the sequence of all import foo, import foo.bar etc.
                # not using direct allows to skip the penultimate module, since "from foo import bar" also imports foo
                for off in range(0, max_off):
                    all_imports[off].add(".".join(lst[0:off+1]))

                # either also use import foo.bar on the last or use from foo import bar
                if direct:
                    all_imports[ln-1].add(".".join(lst))
                else:
                    arg_imports[".".join(lst[0:-1])].add(lst[-1])

        def arg_import(val):
            val_str = "{!r}".format(val)

            ### exceptions
            # Usd.Stage.Open of anon stage transforms to omni.usd.get_context().get_stage()
            if val_str.startswith("Usd.Stage.Open("):
                parse_module_name("omni.usd", True)
                return "omni.usd.get_context().get_stage()"
            ###

            if isclass(val):
                parse_module_name(val.__module__)
            else:
                parse_module_name(val.__class__.__module__)
            return val_str

        def gen_cmd_str(cmd):
            if len(cmd.kwargs.items()) > 0:
                args = ",\n\t".join(["{}={}".format(k, arg_import(v)) for k, v in cmd.kwargs.items()])
                return f"\nomni.kit.commands.execute('{cmd.name}',\n\t{args})\n"
            else:
                return f"\nomni.kit.commands.execute('{cmd.name}')\n"

        # generate a script executing all commands incl. groups or all selected commands
        add_undo_import = False
        if only_selected:
            for item in self._history_tree_view.selection:
                if isinstance(item, MainItem):
                    code_str += gen_cmd_str(item._data)
        elif len(history) > 0:
            last_lvl = 0
            for cmd in history:
                if cmd.level > last_lvl:
                    code_str += "\nomni.kit.undo.begin_group()\n"
                    add_undo_import = True
                if cmd.level < last_lvl:
                    code_str += "\nomni.kit.undo.end_group()\n"
                    add_undo_import = True
                if cmd.name != "Group":
                    code_str += gen_cmd_str(cmd)
                last_lvl = cmd.level
            for _ in range(0, last_lvl):
                code_str += "\nomni.kit.undo.end_group()\n"
                add_undo_import = True

        # import all found modules of variables of executed command parameters
        imports = ""
        for k, v in all_imports.items():
            for name in v:
                imports += f"import {name}\n"
        for k, v in arg_imports.items():
            imports += f"from {k} import " + ", ".join(v) + "\n"
        imports += "import omni.kit.commands\n"
        if add_undo_import:
            imports += "import omni.kit.undo\n"

        return imports + code_str
