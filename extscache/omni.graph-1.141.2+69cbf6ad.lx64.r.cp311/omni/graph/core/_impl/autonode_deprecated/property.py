# ================================================================================
class AutoPropertyWrapper:
    """Wrapper to generate a getter and setter from a property in a class"""

    def __init__(self, target_class, name: str, *, type_override: type = None) -> None:
        try:
            self._type = type_override or target_class.__annotations__[name]
        except KeyError:
            self._type = type(target_class.__dict__[name])

        self._name = name

        self.get.__annotations__["target"] = type(target_class)
        self.get.__annotations__["return"] = self._type

        self.set.__annotations__["target"] = type(target_class)
        self.set.__annotations__["value"] = self._type

    def get(self, target):
        return getattr(target, self._name)

    def set(self, target, value):  # noqa: A003
        setattr(target, self._name, value)
        return target
