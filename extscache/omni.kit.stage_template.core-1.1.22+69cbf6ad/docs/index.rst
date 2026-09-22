omni.kit.stage_template.core
#################################################################################

.. toctree::
   :maxdepth: 1

   CHANGELOG


new_stage scripts

#################################################################################

user script example (Documents\Kit\kit-default\scripts\new_stage\test.py)

.. code-block:: python

    class TestStage():

        def __init__(self):
            omni.kit.stage_template.core.register_template("test", self.new_stage, 1)

        def __del__(self):
            omni.kit.stage_template.core.unregister_template("test")

        def new_stage(self, rootname):
            import omni.kit.commands
            from pxr import Usd, UsdLux
            # Create basic DistantLight
            omni.kit.commands.execute(
                "CreatePrim",
                prim_path="{}/defaultLight".format(rootname),
                prim_type="DistantLight",
                select_new_prim=False,
                # https://github.com/PixarAnimationStudios/USD/commit/b5d3809c943950cd3ff6be0467858a3297df0bb7
                attributes={UsdLux.Tokens.inputsAngle: 1.0, UsdLux.Tokens.inputsIntensity: 3000} if hasattr(UsdLux.Tokens, 'inputsIntensity') else \
                    UsdLux.Tokens.angle: 1.0, UsdLux.Tokens.intensity: 3000},
            )

    TestStage()

#################################################################################

API Reference
==============

.. automodule:: omni.kit.stage_template.core
    :platform: Windows-x86_64, Linux-x86_64
    :members:
    :undoc-members:
    :imported-members:
    :exclude-members: partial, contextlib, suppress
