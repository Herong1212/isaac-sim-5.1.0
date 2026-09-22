import omni.ui as ui


class CaptionResultsPanel:
    def __init__(self):
        self.content_frame = None
        self.global_caption_field = None
        self.brief_caption_field = None

    def shutdown(self):
        self.content_frame = None
        self.global_caption_field = None
        self.brief_caption_field = None

    def _build_ui(self):
        self.content_frame = ui.CollapsableFrame(
            title="Caption Results",
            height=0,
            collapsed=True,
            style={
                "border_radius": 3,
                "border_color": 0x0,
                "border_width": 1,
                "padding": 6,
            },
            horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
            vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
        )

        with self.content_frame:
            with ui.VStack(spacing=10):
                # Brief Caption (showing first as it's most concise)
                with ui.CollapsableFrame(title="Brief Summary", height=0, collapsed=False):
                    with ui.HStack():
                        with ui.ScrollingFrame(height=300, width=400, style={"margin": 5}):
                            self.brief_caption_field = ui.StringField(
                                height=200,
                                multiline=True,
                                read_only=True,
                                alignment=ui.Alignment.LEFT_TOP,
                                style={
                                    "font_size": 14,
                                    "color": 0xFFCCCCCC,
                                    "background_color": 0xFF1E1E1E,
                                    "padding": 5,
                                    "word_wrap": True,
                                },
                            )

                # Global Caption
                with ui.CollapsableFrame(title="Global Scene Description", height=0, collapsed=False):
                    with ui.HStack():
                        with ui.ScrollingFrame(height=400, width=400, style={"margin": 5}):
                            self.global_caption_field = ui.StringField(
                                height=300,
                                multiline=True,
                                read_only=True,
                                alignment=ui.Alignment.LEFT_TOP,
                                style={
                                    "font_size": 14,
                                    "color": 0xFFCCCCCC,
                                    "background_color": 0xFF1E1E1E,
                                    "padding": 5,
                                    "word_wrap": True,
                                },
                            )

    def _wrap_text(self, text, width=50):
        """Wrap text to specified width by inserting newlines"""
        if not text:
            return ""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            if word.endswith(":") or current_length + len(word) > width:
                if word.endswith(":"):
                    current_line.append(word)
                    lines.append(" ".join(current_line))
                    current_line = []
                    current_length = 0
                else:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                    current_length = len(word)
            else:
                current_line.append(word)
                current_length += len(word) + 1

        if current_line:
            lines.append(" ".join(current_line))

        return "\n".join(lines)

    def update_caption_results(self, caption_results):
        """Update the displayed caption results"""
        if caption_results is None:
            self.brief_caption_field.model.set_value("")
            self.global_caption_field.model.set_value("")
            return

        if self.brief_caption_field and "brief_caption" in caption_results:
            text = caption_results["brief_caption"] or "No brief caption available"
            self.brief_caption_field.model.set_value(self._wrap_text(text))

        if self.global_caption_field and "global_caption" in caption_results:
            text = caption_results["global_caption"] or "No global caption available"
            self.global_caption_field.model.set_value(self._wrap_text(text))
