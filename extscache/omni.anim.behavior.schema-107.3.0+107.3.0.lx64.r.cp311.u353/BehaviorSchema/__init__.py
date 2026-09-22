from pxr import Tf

# PreparePythonModule didn't make it's way into USD
# until 21.08 - older versions import the module
# manually and call PrepareModule
if hasattr(Tf, "PreparePythonModule"):
    Tf.PreparePythonModule()
else:
    from . import _behaviorSchema
    Tf.PrepareModule(_behaviorSchema, locals())

del Tf
