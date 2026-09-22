R"""
This module contains bindings to the C++ rtx.neuraylib.plugin interface.

The central classes ``MdlModule``, ``MldEntity``, and ``MdlEntitySnapshot``
are ref-counted internally. So creating the first instance of them actually
creates a new object, further calls, with the same configuration (or same parameters)
will return the same object while internally the reference count is increased.
Every object returned from the create functions that is different from `None`
needs to be disposed by calling the corresponding destroy function to decrease the
reference counter of the instance. When this counter reaches zero, the object is disposed.

All the binding function are in the ``omni.mdl.neuraylib.NeurayLib`` class.
To access a chached instance, use the ``get_neuraylib`` method:

>>> import omni.mdl.neuraylib
>>> ovNeurayLib = omni.mdl.neuraylib.get_neuraylib()

There are more high-level usability functions to integrate extension content.
For instance:

>>> omni.mdl.neuraylib.register_extension_content(...)
"""

from ._neuraylib import NeurayLib
from ._neuraylib import MdlModule, MdlEntity, MdlEntity, MdlEntitySnapshot, Interop

from .scripts import *
from .utils import *