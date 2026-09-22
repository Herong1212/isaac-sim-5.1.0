import carb
import omni.kit.ui

window = omni.kit.ui.Window("Foo2", 400, 400)
window.layout = omni.kit.ui.RowColumnLayout(2, True)

l1 = omni.kit.ui.Label("Foo")
l2 = omni.kit.ui.Label("Bar")
window.layout.add_child(l1)
window.layout.add_child(l2)
