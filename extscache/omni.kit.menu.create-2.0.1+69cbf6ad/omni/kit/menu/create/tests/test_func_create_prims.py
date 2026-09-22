import os

import carb
import omni.usd
from omni.kit import ui_test
from omni.kit.material.library.test_helper import MaterialLibraryTestHelper
from omni.kit.menu.utils import MenuItemDescription
from omni.kit.test_suite.helpers import get_test_data_path, select_prims, wait_for_window, wait_stage_loading
from pxr import UsdShade

PERSISTENT_SETTINGS_PREFIX = "/persistent"


async def create_test_func_create_camera(tester, menu_item: MenuItemDescription):
    # use menu
    await ui_test.menu_click("Create/Camera")

    # verify
    tester.assertTrue(tester.get_stage_prims() == ["/Camera"])

    # Test creation with typed-defaults
    settings = carb.settings.get_settings()
    try:
        focal_len_key = "/persistent/app/primCreation/typedDefaults/camera/focalLength"
        settings.set(focal_len_key, 48)
        await ui_test.menu_click("Create/Camera")

        cam_prim = omni.usd.get_context().get_stage().GetPrimAtPath("/Camera_01")
        tester.assertIsNotNone(cam_prim)
        tester.assertEqual(cam_prim.GetAttribute("focalLength").Get(), 48)
    finally:
        # Delete the change now for any other tests
        settings.destroy_item(focal_len_key)


async def create_test_func_create_scope(tester, menu_item: MenuItemDescription):
    # use menu
    await ui_test.menu_click("Create/Scope")

    # verify
    tester.assertTrue(tester.get_stage_prims() == ["/Scope"])


async def create_test_func_create_xform(tester, menu_item: MenuItemDescription):
    # use menu
    await ui_test.menu_click("Create/Xform")

    # verify
    tester.assertTrue(tester.get_stage_prims() == ["/Xform"])


async def create_test_func_create_shape_capsule(tester, menu_item: MenuItemDescription):
    # use menu
    await ui_test.menu_click("Create/Shape/Capsule")

    # verify
    tester.assertTrue(tester.get_stage_prims() == ["/Capsule"])


async def create_test_func_create_shape_cone(tester, menu_item: MenuItemDescription):
    # use menu
    await ui_test.menu_click("Create/Shape/Cone")

    # verify
    tester.assertTrue(tester.get_stage_prims() == ["/Cone"])


async def create_test_func_create_shape_cube(tester, menu_item: MenuItemDescription):
    # use menu
    await ui_test.menu_click("Create/Shape/Cube")

    # verify
    tester.assertTrue(tester.get_stage_prims() == ["/Cube"])


async def create_test_func_create_shape_cylinder(tester, menu_item: MenuItemDescription):
    # use menu
    await ui_test.menu_click("Create/Shape/Cylinder")

    # verify
    tester.assertTrue(tester.get_stage_prims() == ["/Cylinder"])


async def create_test_func_create_shape_sphere(tester, menu_item: MenuItemDescription):
    # use menu
    await ui_test.menu_click("Create/Shape/Sphere")

    # verify
    tester.assertTrue(tester.get_stage_prims() == ["/Sphere"])


async def create_test_func_create_shape_high_quality(tester, menu_item: MenuItemDescription):
    carb.settings.get_settings().set(PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/highQuality", False)

    # use menu
    await ui_test.menu_click("Create/Shape/High Quality")

    # verify
    tester.assertTrue(carb.settings.get_settings().get(PERSISTENT_SETTINGS_PREFIX + "/app/primCreation/highQuality"))


async def create_test_func_create_light_cylinder_light(tester, menu_item: MenuItemDescription):
    # use menu
    await ui_test.menu_click("Create/Light/Cylinder Light")

    # verify
    tester.assertTrue(tester.get_stage_prims() == ["/CylinderLight"])


async def create_test_func_create_light_disk_light(tester, menu_item: MenuItemDescription):
    # use menu
    await ui_test.menu_click("Create/Light/Disk Light")

    # verify
    tester.assertTrue(tester.get_stage_prims() == ["/DiskLight"])


async def create_test_func_create_light_distant_light(tester, menu_item: MenuItemDescription):
    # use menu
    await ui_test.menu_click("Create/Light/Distant Light")

    # verify
    tester.assertTrue(tester.get_stage_prims() == ["/DistantLight"])


async def create_test_func_create_light_dome_light(tester, menu_item: MenuItemDescription):
    # use menu
    await ui_test.menu_click("Create/Light/Dome Light")

    # verify
    tester.assertTrue(tester.get_stage_prims() == ["/DomeLight"])


async def create_test_func_create_light_rect_light(tester, menu_item: MenuItemDescription):
    # use menu
    await ui_test.menu_click("Create/Light/Rect Light")

    # verify
    tester.assertTrue(tester.get_stage_prims() == ["/RectLight"])


async def create_test_func_create_light_sphere_light(tester, menu_item: MenuItemDescription):
    # use menu
    await ui_test.menu_click("Create/Light/Sphere Light")

    # verify
    tester.assertTrue(tester.get_stage_prims() == ["/SphereLight"])


async def create_test_func_create_audio_spatial_sound(tester, menu_item: MenuItemDescription):
    # use menu
    await ui_test.menu_click("Create/Audio/Spatial Sound")

    # verify
    tester.assertTrue(tester.get_stage_prims() == ["/OmniSound"])


async def create_test_func_create_audio_non_spatial_sound(tester, menu_item: MenuItemDescription):
    # use menu
    await ui_test.menu_click("Create/Audio/Non-Spatial Sound")

    # verify
    tester.assertTrue(tester.get_stage_prims() == ["/OmniSound"])


async def create_test_func_create_audio_listener(tester, menu_item: MenuItemDescription):
    # use menu
    await ui_test.menu_click("Create/Audio/Listener")

    # verify
    tester.assertTrue(tester.get_stage_prims() == ["/OmniListener"])


async def create_test_func_create_mesh_cone(tester, menu_item: MenuItemDescription):
    # use menu
    await ui_test.menu_click("Create/Mesh/Cone")

    # verify
    tester.assertTrue(tester.get_stage_prims() == ["/Cone"])


async def create_test_func_create_mesh_cube(tester, menu_item: MenuItemDescription):
    # use menu
    await ui_test.menu_click("Create/Mesh/Cube")

    # verify
    tester.assertTrue(tester.get_stage_prims() == ["/Cube"])


async def create_test_func_create_mesh_cylinder(tester, menu_item: MenuItemDescription):
    # use menu
    await ui_test.menu_click("Create/Mesh/Cylinder")

    # verify
    tester.assertTrue(tester.get_stage_prims() == ["/Cylinder"])


async def create_test_func_create_mesh_disk(tester, menu_item: MenuItemDescription):
    # use menu
    await ui_test.menu_click("Create/Mesh/Disk")

    # verify
    tester.assertTrue(tester.get_stage_prims() == ["/Disk"])


async def create_test_func_create_mesh_plane(tester, menu_item: MenuItemDescription):
    # use menu
    await ui_test.menu_click("Create/Mesh/Plane")

    # verify
    tester.assertTrue(tester.get_stage_prims() == ["/Plane"])


async def create_test_func_create_mesh_sphere(tester, menu_item: MenuItemDescription):
    # use menu
    await ui_test.menu_click("Create/Mesh/Sphere")

    # verify
    tester.assertTrue(tester.get_stage_prims() == ["/Sphere"])


async def create_test_func_create_mesh_torus(tester, menu_item: MenuItemDescription):
    # use menu
    await ui_test.menu_click("Create/Mesh/Torus")

    # verify
    tester.assertTrue(tester.get_stage_prims() == ["/Torus"])


async def create_test_func_create_mesh_settings(tester, menu_item: MenuItemDescription):
    # use menu
    await ui_test.menu_click("Create/Mesh/Settings")
    await wait_for_window("Mesh Generation Settings")
    ui_test.find("Mesh Generation Settings").widget.visible = False


async def create_test_func_create_material(tester, material_name: str):
    mdl_name = material_name.split("/")[-1].replace(" ", "_")
    stage = omni.usd.get_context().get_stage()

    if mdl_name == "Add_MDL_File":
        # click on menu item
        await ui_test.menu_click(material_name)
        await ui_test.human_delay()

        # use add material dialog
        async with MaterialLibraryTestHelper() as material_test_helper:
            await material_test_helper.handle_add_material_dialog(
                get_test_data_path(__name__, "mdl/TESTEXPORT.mdl"), "TESTEXPORT.mdl"
            )

        # wait for material to load & UI to refresh
        await wait_stage_loading()

        # verify
        shader = UsdShade.Shader(stage.GetPrimAtPath("/Looks/Material/Shader"))
        identifier = shader.GetSourceAssetSubIdentifier("mdl")
        tester.assertTrue(identifier == "Material")
        return

    if mdl_name == "Add_MaterialX_File":
        await ui_test.menu_click(material_name)
        await ui_test.human_delay()

        async with MaterialLibraryTestHelper() as material_test_helper:
            await material_test_helper.handle_add_mtlx_material_dialog(
                get_test_data_path(__name__, "mtlx/standard_surface_gold.mtlx")
            )

        await wait_stage_loading()

        shader = UsdShade.Shader(
            stage.GetPrimAtPath("/Looks/standard_surface_gold/Materials/Gold/ND_standard_surface_surfaceshader")
        )
        shader_id = shader.GetShaderId()
        tester.assertTrue(shader_id == "ND_standard_surface_surfaceshader")
        return

    if mdl_name == "USD_Preview_Surface":
        await ui_test.menu_click(material_name)
        tester.assertTrue(
            tester.get_stage_prims() == ["/Looks", "/Looks/PreviewSurface", "/Looks/PreviewSurface/Shader"]
        )
        return

    if mdl_name == "USD_Preview_Surface_Texture":
        await ui_test.menu_click(material_name)
        tester.assertTrue(
            tester.get_stage_prims()
            == [
                "/Looks",
                "/Looks/PreviewSurfaceTexture",
                "/Looks/PreviewSurfaceTexture/PreviewSurfaceTexture",
                "/Looks/PreviewSurfaceTexture/st",
                "/Looks/PreviewSurfaceTexture/diffuseColorTex",
                "/Looks/PreviewSurfaceTexture/metallicTex",
                "/Looks/PreviewSurfaceTexture/roughnessTex",
                "/Looks/PreviewSurfaceTexture/normalTex",
            ]
        )
        return

    # create sphere, select & create material
    omni.kit.commands.execute("CreatePrimWithDefaultXform", prim_type="Sphere")
    await select_prims(["/Sphere"])
    await ui_test.menu_click(material_name)
    await ui_test.human_delay(50)

    # verify material is created
    tester.assertTrue(
        tester.get_stage_prims() == ["/Sphere", "/Looks", f"/Looks/{mdl_name}", f"/Looks/{mdl_name}/Shader"]
    )
    prim = stage.GetPrimAtPath(f"/Looks/{mdl_name}/Shader")
    asset_path = prim.GetAttribute("info:mdl:sourceAsset").Get()
    tester.assertFalse(os.path.isabs(asset_path.path))
    tester.assertTrue(os.path.isabs(asset_path.resolvedPath))

    # verify /Sphere is bound to material
    prim = stage.GetPrimAtPath("/Sphere")
    bound_material, _ = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
    tester.assertEqual(bound_material.GetPath().pathString, f"/Looks/{mdl_name}")
