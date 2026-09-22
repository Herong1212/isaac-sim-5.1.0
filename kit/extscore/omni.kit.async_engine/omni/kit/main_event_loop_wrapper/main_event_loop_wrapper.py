# Python global variables are module-scoped, so in order to have the main event loop
# object persist across modules when loaded (after being set in async_engine.py upon
# that extension's start-up) we enclose it inside this wrapper class.
class MainEventLoopWrapper:
    """Wrapper class to store a global, inter-module accessible, persistent copy of the main event loop."""
    g_main_event_loop = None
