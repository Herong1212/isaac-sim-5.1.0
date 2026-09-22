# Python Usage Examples


## Creating Custom Stage Column Delegates
A custom `StageColumnDelegate` can be created by subclassing from `AbstractStageColumnDelegate` and implementing the
abstract methods. Here's an example from the built-in `VisibilityColumnDelegate`. For more details, please refer to
`omni.kit.widget.stage.VisibilityColumnDelegate`.

```{literalinclude} ../../../../source/extensions/omni.kit.widget.stage/omni/kit/widget/stage/delegates/visibility_column_delegate.py
---
language: python
start-after: BEGIN-DOC-custom_column_delegate
end-before: END-DOC-custom_column_delegate
---
```
```{literalinclude} ../../../../source/extensions/omni.kit.widget.stage/omni/kit/widget/stage/delegates/visibility_column_delegate.py
---
language: python
start-after: BEGIN-DOC-custom_column_delegate_build_fn
end-before: END-DOC-custom_column_delegate_build_fn
---
```


## Registering Stage Column Delegates
`StageColumnDelegateRegistry.register_column_delegate` can be used to register a custom `StageColumnDelegate`, as shown
below. It's important to keep the returned subscription object alive, otherwise the registration will be immediately
deregistered.

```python
# Register column delegates
self._name_column_sub = StageColumnDelegateRegistry().register_column_delegate("Name", NameColumnDelegate)
self._type_column_sub = StageColumnDelegateRegistry().register_column_delegate("Type", TypeColumnDelegate)
self._visibility_column_sub = StageColumnDelegateRegistry().register_column_delegate("Visibility", VisibilityColumnDelegate)
```


## Deregistering Stage Column Delegates
Unlike registering, to deregister a `StageColumnDelegate`, there's no explicit API calls required. The delegate will
automatically be deregistered when the subscription object is destroyed. For example:

```python
self._visibility_column_sub = None
self._type_column_sub = None
self._stage_open_sub = None
```
