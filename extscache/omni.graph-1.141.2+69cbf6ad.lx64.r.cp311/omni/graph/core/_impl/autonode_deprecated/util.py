from contextlib import contextmanager

PROP_INFIX = "__PROP__"
FUNC_INFIX = "__FUNC__"
GET_SUFFIX = "__GET"
SET_SUFFIX = "__SET"
NAMESPACE_INFIX = "__NSP__"


# ================================================================================
def sanitize_qualname(name: str) -> str:
    return name.replace(".", NAMESPACE_INFIX)


# ================================================================================
def python_name_to_ui_name(name: str) -> str:
    # de-snake
    strings = name.split("_")
    case_corrected = [s.capitalize() if s.islower() else s for s in strings]
    return " ".join(case_corrected)


# ================================================================================
def sanitized_name_to_ui_name(name: str) -> str:
    def correct_case(s):
        return s.capitalize() if s.islower() else s

    strings = name.split(NAMESPACE_INFIX)
    name = ".".join([correct_case(s) for s in strings])

    strings = name.split(FUNC_INFIX)
    name = " : ".join([correct_case(s) for s in strings])

    strings = name.split(PROP_INFIX)
    name = " : ".join([correct_case(s) for s in strings])

    return name


# ================================================================================
def is_private(name: str) -> bool:
    """checks if a name should be considered private"""
    return len(name) > 1 and name.startswith("_")


# ================================================================================
def is_class_private(name: str) -> bool:
    """Checks if a name is a class private member.
    Used to warn if a name will get mangled.  Based on
    https://github.com/python/cpython/blob/bd46174a5a09a54e5ae1077909f923f56a7cf710/Python/compile.c#L236-L258
    """
    return name.startswith("__") and not name.endswith("__")


# ================================================================================
def is_dunder(name: str) -> bool:
    """Checks if a name is an internal python name. Based on
    https://github.com/python/cpython/blob/148f32913573c29250dfb3f0d079eb8847633621/Objects/typeobject.c#L3299-L3306
    """
    return len(name) > 4 and name.isascii() and name.startswith("__") and name.endswith("__")


# ================================================================================
class GeneratedCode:
    """Tiny code generation utility"""

    strbuf = ""
    indent_level = 0

    # --------------------------------------------------------------------------------
    def line(self, txt: str):
        self.strbuf += self.indent_level * " " + txt + "\n"

    # --------------------------------------------------------------------------------
    @contextmanager
    def indent(self, txt):
        try:
            self.line(txt)
            self.indent_level += 4
            yield None
        finally:
            self.indent_level -= 4

    # --------------------------------------------------------------------------------
    def __repr__(self) -> str:
        return self.strbuf
