# pylint: disable=missing-function-docstring, missing-class-docstring

import omni.kit.commands
from pxr import UsdLux


def create_test_stage():
    stage = omni.usd.get_context().get_stage()
    rootname = ""
    if stage.HasDefaultPrim():  # pragma: no cover
        rootname = stage.GetDefaultPrim().GetPath().pathString

    prim_path = f"{rootname}/defaultLight"

    # Create basic DistantLight
    omni.kit.commands.execute(
        "CreatePrim",
        prim_path=prim_path,
        prim_type="DistantLight",
        select_new_prim=False,
        # https://github.com/PixarAnimationStudios/USD/commit/b5d3809c943950cd3ff6be0467858a3297df0bb7
        attributes=(
            {UsdLux.Tokens.inputsAngle: 1.0, UsdLux.Tokens.inputsIntensity: 3000}
            if hasattr(UsdLux.Tokens, "inputsIntensity")
            else {UsdLux.Tokens.angle: 1.0, UsdLux.Tokens.intensity: 3000}
        ),
        create_default_xform=True,
    )

    return prim_path
