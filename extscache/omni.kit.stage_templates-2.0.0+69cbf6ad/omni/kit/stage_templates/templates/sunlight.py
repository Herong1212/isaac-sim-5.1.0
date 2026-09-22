import carb
import omni.ext
import omni.kit.commands
import omni.usd
from pxr import UsdLux, Usd


class SunlightStage:
    def __init__(self):
        omni.kit.stage_template.core.register_template("sunlight", self.new_stage)

    def __del__(self):  # pragma: no cover
        omni.kit.stage_template.core.unregister_template("sunlight")

    def new_stage(self, rootname, usd_context_name):
        # Create basic DistantLight
        usd_context = omni.usd.get_context(usd_context_name)
        stage = usd_context.get_stage()
        with Usd.EditContext(stage, stage.GetRootLayer()):
            # create Environment
            omni.kit.commands.execute(
                "CreatePrim",
                prim_path="/Environment",
                prim_type="Xform",
                select_new_prim=False,
                create_default_xform=True,
                context_name=usd_context_name
            )

            omni.kit.commands.execute(
                "CreatePrim",
                prim_path="/Environment/defaultLight",
                prim_type="DistantLight",
                select_new_prim=False,
                # https://github.com/PixarAnimationStudios/USD/commit/b5d3809c943950cd3ff6be0467858a3297df0bb7
                attributes={UsdLux.Tokens.inputsAngle: 1.0, UsdLux.Tokens.inputsIntensity: 3000} if hasattr(UsdLux.Tokens, 'inputsIntensity') else \
                    {UsdLux.Tokens.angle: 1.0, UsdLux.Tokens.intensity: 3000},
                create_default_xform=True,
                context_name=usd_context_name
            )
