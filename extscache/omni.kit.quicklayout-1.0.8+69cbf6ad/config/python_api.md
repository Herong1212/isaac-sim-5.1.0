# Public API for module omni.kit.quicklayout:

## Classes

- class QuickLayout
  - def __init__(self)
  - def destroy(self)
  - static def save_file(workspace_file: str)
  - static def load_file(workspace_file: str, keep_windows_open = False)
  - static def compare_file(workspace_file: str, compare_delegate: CompareDelegate = CompareDelegate())
  - def save(self, menu: str, value: bool)
  - def load(self, menu: str, value: bool)
  - static def quick_save(menu: str, value: bool)
  - static def quick_load(menu: str, value: bool)
