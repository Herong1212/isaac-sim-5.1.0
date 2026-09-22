import carb

"""

Helper class to format debug print and bind the enablement to a carb setting.

Example usage:
    dprint = DebugPrint("/ext/my.example.ext/debug_print", "MyClass")
    def MyClass:
        @dprint.debug
        def func():
            ...
            dprint.print("check point 01")
            ...
            dprint.print("check point 02")

Expect output:
    [Debug MyClass] func Starts:
    [Debug MyClass]     check point 01
    [Debug MyClass]     check point 02
    [Debug MyClass] func Ends.
"""


class DebugPrint:
    def __init__(self, carb_key: str, header: str):
        self.carb_key = carb_key
        self.header = header
        self.settings = carb.settings.get_settings()
        self.indent = 0

    def debug_func(self, func):
        def wrapper(*args, **kargs):
            func_name = func.__name__
            self.print(f"{func_name} Starts:")
            self.indent += 4
            result = func(*args, **kargs)
            self.indent -= 4
            self.print(f"{func_name} Ends.")
            return result

        return wrapper

    def print(self, msg):
        if not self.settings.get(self.carb_key):
            return
        indent = " " * self.indent
        print(f"[Debug {self.header}]{indent} {msg}")
