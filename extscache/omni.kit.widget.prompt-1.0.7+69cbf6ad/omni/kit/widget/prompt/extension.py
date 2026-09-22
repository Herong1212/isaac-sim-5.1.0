import omni.ext

from .prompt import PromptManager


class PromptExtension(omni.ext.IExt):

    def on_startup(self):
        PromptManager.on_startup()

    def on_shutdown(self):
        PromptManager.on_shutdown()
        