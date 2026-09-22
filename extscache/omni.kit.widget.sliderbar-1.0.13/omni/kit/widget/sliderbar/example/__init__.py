import carb

try:
    from omni.kit.widget.examples import register_page

    from .slider_bar_page import SliderBarPage

    register_page(SliderBarPage())

except Exception as e:
    carb.log_info(f"Failed to add example for slider bar: {str(e)}")
    pass
