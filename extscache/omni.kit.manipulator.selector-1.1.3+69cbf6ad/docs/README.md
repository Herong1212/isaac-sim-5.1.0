# Prim Manipulator Selector Extension [omni.kit.manipulator.selector]

This is the extension providing prim manipulator selector in Kit.

Manipulator selector acts like the central manager for all _prim_ manipulators. Instead of subscribing to UsdStageEvent for selection change, prim manipulator should inherit `ManipulatorBase` class in this extension and implements all abstractmethods to support choosing between multiple types of prim manipulators based on their order and enable criterions.

The order of the manipulator is specified at carb.settings path `/persistent/exts/omni.kit.manipulator.selector/orders/<name>"`
