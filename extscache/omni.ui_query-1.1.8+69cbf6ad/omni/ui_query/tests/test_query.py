from ..query import OmniUIQuery
import omni.kit.test
import omni.ui


class TestQuery(omni.kit.test.AsyncTestCase):
    def test_create_test_widget1(self):
        _window = omni.ui.Window("the window with space")
        button = None
        with _window.frame:  # the frame can only have 1 widget under it
            with omni.ui.HStack():
                with omni.ui.VStack():
                    omni.ui.Label("Test2")
                with omni.ui.VStack(width=150):
                    with omni.ui.HStack(height=30):
                        omni.ui.Label("Test1")
                        omni.ui.StringField()
                        button = omni.ui.Button("TestButton")

        button_path = OmniUIQuery.get_widget_path(_window, button)
        self.assertTrue(
            "the window with space//Frame/HStack[0]/VStack[1]/HStack[0]/Button[0]" == button_path,
            "was actually %s" % (button_path),
        )
        widget_paths = [
            "the window with space//Frame",
            "the window with space//Frame",
            "the window with space//Frame/HStack[0]",
            "the window with space//Frame/HStack[0]/VStack[0]",
            "the window with space//Frame/HStack[0]/VStack[0]/Label[0].text=='Test2'",
            "the window with space//Frame/HStack[0]/VStack[1]",
            "the window with space//Frame/HStack[0]/VStack[1]/HStack[0]",
            "the window with space//Frame/HStack[0]/VStack[1]/HStack[0]/Label[0].text=='Test1'",
            "the window with space//Frame/HStack[0]/VStack[1]/HStack[0]/StringField[0]",
            "the window with space//Frame/HStack[0]/VStack[1]/HStack[0]/Button[0].text=='TestButton'",
        ]
        def get_widget_postfix(widget: omni.ui.Widget):
            try:
                text = getattr(widget, "text")
                return f".text=='{text}'"
            except:
                return ""
        self.assertEqual(set(widget_paths), set(OmniUIQuery.get_window_widget_paths(_window, get_widget_postfix)))

    def test_create_test_widget2(self):
        _window = omni.ui.Window("the_window")
        hstack1 = None
        with _window.frame as frame1:
            hstack1 = omni.ui.HStack()
            with hstack1:
                vstack1 = omni.ui.VStack()
                with vstack1:
                    label1 = omni.ui.Label("Test2")
                vstack2 = omni.ui.VStack(width=150)
                with vstack2:
                    hstack2 = omni.ui.HStack(height=30)
                    with hstack2:
                        label2 = omni.ui.Label("Test1")
                        string1 = omni.ui.StringField()
                        button1 = omni.ui.Button()
                        button1.identifier = "The_Button1"
                        button2 = omni.ui.Button("TestButton")
                        button3 = omni.ui.Button(name="Button3")

        # NOTE: we can't look for the frame..
        # widget_path = OmniUIQuery.get_widget_path(_window, frame1)
        # self.assertTrue('the_window//Frame'== widget_path, "was actually %s"%(widget_path))

        widget_path = OmniUIQuery.get_widget_path(_window, hstack1)
        self.assertTrue("the_window//Frame/HStack[0]" == widget_path, "was actually %s" % (widget_path))

        found_widget = OmniUIQuery.find_widget(widget_path)
        self.assertTrue(found_widget == hstack1)

        widget_path = OmniUIQuery.get_widget_path(_window, vstack1)
        self.assertTrue("the_window//Frame/HStack[0]/VStack[0]" == widget_path, "was actually %s" % (widget_path))

        found_widget = OmniUIQuery.find_widget(widget_path)
        self.assertTrue(found_widget == vstack1)

        widget_path = OmniUIQuery.get_widget_path(_window, label1)
        self.assertTrue(
            "the_window//Frame/HStack[0]/VStack[0]/Label[0]" == widget_path, "was actually %s" % (widget_path)
        )

        found_widget = OmniUIQuery.find_widget(widget_path)
        self.assertTrue(found_widget == label1)

        widget_path = OmniUIQuery.get_widget_path(_window, vstack2)
        self.assertTrue("the_window//Frame/HStack[0]/VStack[1]" == widget_path, "was actually %s" % (widget_path))

        found_widget = OmniUIQuery.find_widget(widget_path)
        self.assertTrue(found_widget == vstack2)

        widget_path = OmniUIQuery.get_widget_path(_window, hstack2)
        self.assertTrue(
            "the_window//Frame/HStack[0]/VStack[1]/HStack[0]" == widget_path, "was actually %s" % (widget_path)
        )

        found_widget = OmniUIQuery.find_widget(widget_path)
        self.assertTrue(found_widget == hstack2)

        widget_path = OmniUIQuery.get_widget_path(_window, button2)
        self.assertTrue(
            "the_window//Frame/HStack[0]/VStack[1]/HStack[0]/Button[1]" == widget_path,
            "was actually %s" % (widget_path),
        )

        found_widget = OmniUIQuery.find_widget(widget_path)
        self.assertTrue(found_widget == button2)

        # Test where we reference with a name rather than a type. #TODO: reactivate when we have identifier support
        widget_path = OmniUIQuery.get_widget_path(_window, button1)
        self.assertTrue(
            "the_window//Frame/HStack[0]/VStack[1]/HStack[0]/Button[0]" == widget_path,
            "was actually %s" % (widget_path),
        )

        found_widget = OmniUIQuery.find_widget(widget_path)
        self.assertTrue(found_widget == button1)

        widget_paths = OmniUIQuery.get_widget_children_with_path(hstack1, "the_window//Frame/HStack[0]")
        self.assertEqual(len(widget_paths), 2)
        self.assertEqual(widget_paths[vstack1], "the_window//Frame/HStack[0]/VStack[0]")
        self.assertEqual(widget_paths[vstack2], "the_window//Frame/HStack[0]/VStack[1]")

        widget_paths = OmniUIQuery.get_widget_children_with_path(vstack1, "the_window//Frame/HStack[0]/VStack[0]")
        self.assertEqual(len(widget_paths), 1)
        self.assertEqual(widget_paths[label1], "the_window//Frame/HStack[0]/VStack[0]/Label[0]")

        widget_paths = OmniUIQuery.get_widget_children_with_path(vstack2, "the_window//Frame/HStack[0]/VStack[1]")
        self.assertEqual(len(widget_paths), 1)
        self.assertEqual(widget_paths[hstack2], "the_window//Frame/HStack[0]/VStack[1]/HStack[0]")

        widget_paths = OmniUIQuery.get_widget_children_with_path(hstack2, "the_window//Frame/HStack[0]/VStack[1]/HStack[0]")
        self.assertEqual(len(widget_paths), 5)
        self.assertEqual(widget_paths[label2], "the_window//Frame/HStack[0]/VStack[1]/HStack[0]/Label[0]")
        self.assertEqual(widget_paths[string1], "the_window//Frame/HStack[0]/VStack[1]/HStack[0]/StringField[0]")
        self.assertEqual(widget_paths[button1], "the_window//Frame/HStack[0]/VStack[1]/HStack[0]/Button[0]")
        self.assertEqual(widget_paths[button2], "the_window//Frame/HStack[0]/VStack[1]/HStack[0]/Button[1]")
        self.assertEqual(widget_paths[button3], "the_window//Frame/HStack[0]/VStack[1]/HStack[0]/Button[2]")

    def test_wildcards(self):
        _window = omni.ui.Window("the_window")
        hstack1 = None
        with _window.frame as frame1:
            hstack1 = omni.ui.HStack()
            with hstack1:
                vstack1 = omni.ui.VStack()
                with vstack1:
                    label1 = omni.ui.Label("Test2")
                vstack2 = omni.ui.VStack(width=150)
                with vstack2:
                    hstack2 = omni.ui.HStack(height=30)
                    with hstack2:
                        label2 = omni.ui.Label("Test1")
                        string1 = omni.ui.StringField()
                        button1 = omni.ui.Button()
                        button1.identifier = "TheButton_1"
                        button2 = omni.ui.Button("TestButton")
                        button3 = omni.ui.Button(name="Button3.dot.separated")

        # Run all tests in 2 modes:
        # 1. Full path including window
        # 2. Find subwidget first (Frame) and search from it
        for full_path in [True, False]:

            def find(path):
                if full_path:
                    return OmniUIQuery.find_widgets(f"the_window//Frame/{path}")
                else:
                    frame = OmniUIQuery.find_widget("the_window//Frame")
                    return OmniUIQuery.find_widgets(path, root_widgets=[frame])

            # Find every immediate child beneath the first HStack
            widgets = find("HStack[0]/*")
            self.assertTrue(widgets[0] == vstack1)
            self.assertTrue(widgets[1] == vstack2)
            self.assertTrue(len(widgets) == 2)

            # Find every immediate child beneath the first HStack Vstack combo
            widgets = find("HStack[0]/VStack[0]/*")
            self.assertTrue(len(widgets) == 1)
            self.assertTrue(widgets[0] == label1)

            # Index/Type - Find every immediate Vstack child
            widgets = find("HStack[0]/VStack[*]")
            self.assertTrue(widgets[0] == vstack1)
            self.assertTrue(widgets[1] == vstack2)
            self.assertTrue(len(widgets) == 2)

            # Recursion - Find every child beneath the Frame - recursively
            widgets = find("**")
            self.assertTrue(len(widgets) == 10)

            widgets = find("HStack[0]/**")
            self.assertTrue(len(widgets) == 9)

            # Recursion - with a specific type/indexed entry at the end
            widgets = find("HStack[0]/**/Button[0]")
            self.assertTrue(len(widgets) == 1)
            self.assertTrue(button1 in widgets)

            # Recursion - with a specific name at the end
            widgets = find("HStack[0]/**/TheButton_1")
            self.assertTrue(len(widgets) == 1, "actually %s" % (len(widgets)))
            self.assertTrue(button1 in widgets)

            # Recursion - find all the buttons
            widgets = find("**/Button[*]")
            self.assertTrue(len(widgets) == 3)
            self.assertTrue(button1 in widgets)
            self.assertTrue(button2 in widgets)
            self.assertTrue(button3 in widgets)

            widgets = find("*/VStack[*]")
            self.assertTrue(len(widgets) == 2)
            self.assertTrue(vstack1 in widgets)
            self.assertTrue(vstack2 in widgets)

            # Recursion - what's directly under the 2 vstacks vstack1 and vstack2?
            widgets = find("HStack[0]/VStack[*]/*")
            self.assertTrue(len(widgets) == 2)
            self.assertTrue(label1 in widgets)
            self.assertTrue(hstack2 in widgets)

            # We should be able to get the same result using recursion and non-recursion on a set of leaf nodes
            widgets = find("HStack[0]/VStack[1]/HStack[0]/*")
            self.assertTrue(len(widgets) == 5)
            widgets = find("HStack[0]/VStack[1]/HStack[0]/**")
            self.assertTrue(len(widgets) == 5)

            # Can we treat a standard path as am explicit query with no wildcard that returns a single result?
            widgets = find("HStack[0]/VStack[1]/HStack[0]/Button[0]")
            self.assertTrue(len(widgets) == 1)
            self.assertTrue(button1 in widgets)

            # #Can we treat a standard path as am explicit query with no wildcard that returns a single result?
            widgets = find("HStack[0]/VStack[1]/HStack[0]/TheButton_1")
            self.assertTrue(len(widgets) == 1)
            self.assertTrue(button1 in widgets)

            # Predicates
            widgets = find("**/Button[*].text=='TestButton'")
            self.assertTrue(button2 in widgets)
            self.assertTrue(len(widgets) == 1)

            widgets = find("**/Button[*].name=='Button3.dot.separated'")
            self.assertTrue(button3 in widgets)
            self.assertTrue(len(widgets) == 1)

    def test_bad_inputs(self):
        _window = omni.ui.Window("the_window2")
        with _window.frame:  # TODO Check - can the frame only have 1 widget under it?
            with omni.ui.HStack():
                with omni.ui.VStack():
                    omni.ui.Label("Test2")

        # check bad window
        widget_path = OmniUIQuery.find_widget("bad_window//Frame/HStack[0]/*")
        self.assertTrue(widget_path == None)

        # check pre-omniui window
        widget_path = OmniUIQuery.find_widget("Viewport//Frame/HStack[0]/*")
        self.assertTrue(widget_path == None)

        # check bad frame
        widget_path = OmniUIQuery.find_widget("the_window2//B/HStack[0]/*")
        self.assertTrue(widget_path == None)

        # bad first widget
        widget_path = OmniUIQuery.find_widget("the_window2//Frame/GStack[0]")
        self.assertTrue(widget_path == None)

        # wildcard query
        widgets = OmniUIQuery.find_widgets("blah")
        self.assertTrue(widgets == [])

        widgets = OmniUIQuery.find_widgets("blah/*")
        self.assertTrue(widgets == [])

    def test_with_real_widget(self):
        """
        This introduces a dependency on render settings and the renderer core
        We might want to abandon it if the dependency is too painful
        """
        windows = omni.ui.Workspace.get_windows()
        found_button = False
        for w in windows:
            if w.title == "Render Settings":
                the_path = f"{w.title}//Frame/**"
                widgets = OmniUIQuery.find_widgets(the_path)
                for w in widgets:
                    if isinstance(w, omni.ui.Button):
                        found_button = True
        self.assertTrue(found_button)

    def test_frame_query(self):
        # Test to validate whether we are able to query widget having Frames excludint parent frame in path

        _window = omni.ui.Window("Window")
        with _window.frame:  # the frame can only have 1 widget under it
            with omni.ui.HStack():
                child_frame1 = omni.ui.Frame(name="Frame1")
                child_frame2 = omni.ui.Frame()
                with child_frame1:
                    label = omni.ui.Label("Label1")
                with child_frame2:
                    button = omni.ui.Button()

        single_frame_path = "Window//Frame/HStack[0]/Frame[0]"
        multiple_frame_path = "Window//Frame/HStack[0]/Frame[*]"
        widget_inside_frame_path = "Window//Frame/HStack[0]/Frame[1]/Button[0]"
        frame_with_text_path = "Window//Frame/HStack[0]/Frame[*].name=='Frame1'"

        # Finding a single frame
        found_widget = OmniUIQuery.find_widgets(single_frame_path)[0]
        self.assertTrue(found_widget == child_frame1)

        # Finding multiple frames
        found_widget = OmniUIQuery.find_widgets(multiple_frame_path)
        self.assertTrue(found_widget[0] == child_frame1)
        self.assertTrue(found_widget[1] == child_frame2)
        found_widget = OmniUIQuery.find_first_widget(multiple_frame_path)
        self.assertTrue(found_widget == child_frame1)

        # Finding widget inside Frame with multiple Frame[0] in query
        found_widget = OmniUIQuery.find_widgets(widget_inside_frame_path)
        self.assertTrue(found_widget[0] == button)
        found_widget = OmniUIQuery.find_first_widget(widget_inside_frame_path)
        self.assertTrue(found_widget == button)

        # Finding frame using the text
        found_widget = OmniUIQuery.find_widgets(frame_with_text_path)
        self.assertTrue(found_widget[0] == child_frame1)
