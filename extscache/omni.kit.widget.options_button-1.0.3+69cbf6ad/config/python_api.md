# Public API for module omni.kit.widget.options_button:

## Classes

- class OptionsButton
  - def __init__(self, option_items: List[OptionItem], width: ui.Length = ui.Pixel(24), height: ui.Length = ui.Pixel(24), hide_on_click: bool = False, menu_width: ui.Length = ui.Fraction(1), style: Dict = {})
  - def destroy(self)
  - [property] def model(self) -> OptionsModel
  - [property] def button(self) -> ui.Button
