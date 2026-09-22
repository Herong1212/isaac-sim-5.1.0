# Stub module due to directory structure change.
# This will maintain backwards compatibility for existing projects.

from typing import List  # pragma: no cover

from pxr import Usd, UsdShade  # pragma: no cover


def UsdMaterialAttributeWidget(  # noqa: N802
    schema: Usd.SchemaBase,
    title: str,
    include_names: List[str],
    exclude_names: List[str],
    schema_ignore: Usd.SchemaBase = None,
):  # pragma: no cover
    import carb

    from .widgets.usdshade import UsdShadeMaterialWidget, UsdShadeNodeGraphWidget, UsdShadeShaderWidget

    if schema == UsdShade.Material:
        return UsdShadeMaterialWidget(title)

    if schema == UsdShade.NodeGraph:
        return UsdShadeNodeGraphWidget(title)

    if schema == UsdShade.Shader:
        return UsdShadeShaderWidget(title)

    carb.log_error(f"UsdMaterialAttributeWidget called with unsupported schema: '{schema}'.")
    return None
