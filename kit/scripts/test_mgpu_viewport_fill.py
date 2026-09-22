import carb
import asyncio
import omni.kit.viewport.utility
import omni.kit.app

FILL_VIEWPORT_SETTING  = "/persistent/app/viewport/{viewport_api_id}/fillViewport"

async def test_change_to_fill_viewport():
    viewport = omni.kit.viewport.utility.get_active_viewport()
    if not viewport:
        carb.log_warn(f"There is no active Viewport, skipping test_change_to_fill_viewport")
        return None

    setting_path = FILL_VIEWPORT_SETTING.format(viewport_api_id=viewport.id)

    # Make sure we get atleast a few frames with old resolution
    for i in range(10):
        await omni.kit.app.get_app().next_update_async()
        print(f"Frame {i}")

    # Set fillResolution
    carb.settings.get_settings().set_bool(setting_path, True)
    await omni.kit.app.get_app().next_update_async()
    print("Fill viewport resolution change done")

    # Make sure we get a a few frames with new resolution
    for i in range(10):
        await omni.kit.app.get_app().next_update_async()
        print(f"Frame {i}")

def main():
    asyncio.ensure_future(test_change_to_fill_viewport())

main()