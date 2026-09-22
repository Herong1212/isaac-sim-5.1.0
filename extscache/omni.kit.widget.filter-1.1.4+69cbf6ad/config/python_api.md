# Public API for module omni.kit.widget.filter:

## Classes

- class FilterButton
  - def __init__(self, option_items: List[OptionItem], width: ui.Length = ui.Pixel(24), height: ui.Length = ui.Pixel(24), hide_on_click: bool = False, menu_width: ui.Length = ui.Fraction(1), carot_size: ui.Length = ui.Pixel(3), style: Dict = {})
  - def destroy(self)
  - [property] def model(self) -> FilterModel
  - [property] def button(self) -> ui.Button
