# Manipulator Snap Tool [omni.kit.manipulator.tool.snap]

Extension that provides snap functionality to transform manipulator as well as a registry for external snap tools.

It allows developer to register their own `Snap Provider` to the registry to provide customized snapping behavior. The registered provider will be an option in the toolbar's context menu that user can choose as their manipulator's snap provider.

This extension also contains 3 built-in snap providers:
- Snap to Surface (framebuffer based).
- Snap to Prim transform.
- Snap to Grid (when grid is enabled).

It also contains `Explicit Transform` snapping, which is minimal increment for translate, scale and rotate.