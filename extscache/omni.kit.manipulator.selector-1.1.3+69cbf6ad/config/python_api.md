# Public API for module omni.kit.manipulator.selector:

## Classes

- class ManipulatorBase(ABC)
  - def __init__(self, name: str, usd_context_name: str)
  - def destroy(self)
  - def on_selection_changed(self, stage: Usd.Stage, selection: Union[List[Sdf.Path], None], *args, **kwargs) -> bool
  - [property] def enabled(self) -> bool
  - [enabled.setter] def enabled(self, value: bool)

- class ManipulatorOrderManager
  - def __init__(self)
  - def destroy(self)
  - [property] def orders_dict(self) -> Dict[str, int]
  - def subscribe_to_orders_changed(self, fn: Callable) -> int
  - def unsubscribe_to_orders_changed(self, id: int)

- class ManipulatorSelector
  - def __init__(self, order_manager: ManipulatorOrderManager, usd_context_name: str)
  - def destroy(self)
  - def register_manipulator_instance(self, name: str, manipulator: ManipulatorBase)
  - def unregister_manipulator_instance(self, name: str, manipulator: ManipulatorBase)

## Functions

- def get_manipulator_selector(usd_context_name: str) -> ManipulatorSelector
