from omni.metropolis.utils.triggers.core import TriggerBase


class SpillEventBase:
    def __init__(self):
        self.trigger_sub = None

    def set_trigger(self, trigger: TriggerBase):
        self.trigger = trigger

    def on_create_spill(self):
        pass

    def on_trigger_spill(self):
        pass

    def on_reset_spill(self):
        pass

    def destroy(self):
        if self.trigger:
            self.trigger.destroy()
        self.trigger = None
