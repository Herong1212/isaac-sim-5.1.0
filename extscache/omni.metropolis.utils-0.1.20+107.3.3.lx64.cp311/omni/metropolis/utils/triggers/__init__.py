from .time_trigger import TimeTrigger
from .carb_event_trigger import CarbEventTrigger


def get_all_trigger_types():
    return [TimeTrigger, CarbEventTrigger]
