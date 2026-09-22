import omni.ext
from .. import get_physx_foundation_interface
from ..bindings._physxFoundation import release_physx_foundation_interface


class PhysxFoundationExtension(omni.ext.IExt):
    def on_startup(self):
        self._physx_foundation_interface = get_physx_foundation_interface()

    def on_shutdown(self):
        release_physx_foundation_interface(self._physx_foundation_interface)
        self._physx_foundation_interface = None
