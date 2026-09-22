from dataclasses import dataclass, field


# TODO:: Remove dependency for dataclass
@dataclass
class UpdateNotifier:
    """
    Base class that implements sending and listening update notification.
    """

    _on_update_funcs: list = field(default_factory=lambda: [])

    def register_update_func(self, func):
        self._on_update_funcs.append(func)

    def deregister_update_func(self, func):
        if func in self._on_update_funcs:
            self._on_update_funcs.remove(func)

    def notify_update(self, *args):
        for func in self._on_update_funcs:
            if args:
                func(args)
            else:
                func()
