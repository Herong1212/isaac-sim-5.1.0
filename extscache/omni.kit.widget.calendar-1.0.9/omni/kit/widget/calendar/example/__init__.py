import carb

try:
    from omni.kit.widget.examples import register_page

    from .calendar_page import CalendarPage

    register_page(CalendarPage())

except Exception as e:
    carb.log_info(f"Failed to add example for Calendar: {str(e)}")
    pass
