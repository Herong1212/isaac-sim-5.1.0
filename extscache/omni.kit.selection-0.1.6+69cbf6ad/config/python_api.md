# Public API for module omni.kit.selection:

## Classes

- class SelectAllCommand(omni.kit.commands.Command)
  - def __init__(self, type = None)
  - def do(self)
  - def undo(self)

- class SelectNoneCommand(omni.kit.commands.Command)
  - def __init__(self)
  - def do(self)
  - def undo(self)

- class SelectInvertCommand(omni.kit.commands.Command)
  - def __init__(self)
  - def do(self)
  - def undo(self)

- class HideUnselectedCommand(omni.kit.commands.Command)
  - def __init__(self)
  - def do(self)
  - def undo(self)

- class SelectParentCommand(omni.kit.commands.Command)
  - def __init__(self)
  - def do(self)
  - def undo(self)

- class SelectLeafCommand(omni.kit.commands.Command)
  - def __init__(self)
  - def collect_leafs(self, prim, leaf_set)
  - def do(self)
  - def undo(self)

- class SelectHierarchyCommand(omni.kit.commands.Command)
  - def __init__(self)
  - def do(self)
  - def undo(self)

- class SelectSimilarCommand(omni.kit.commands.Command)
  - def __init__(self)
  - def do(self)
  - def undo(self)

- class SelectListCommand(omni.kit.commands.Command)
  - def __init__(self, **kwargs)
  - def do(self)
  - def undo(self)

- class SelectKindCommand(omni.kit.commands.Command)
  - def __init__(self, **kwargs)
  - def do(self)
  - def undo(self)
