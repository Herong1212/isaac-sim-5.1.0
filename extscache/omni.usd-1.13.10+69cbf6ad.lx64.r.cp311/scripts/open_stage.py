"""Script to open USD stage."""

import carb
import argparse
import omni.usd
import asyncio
import omni.client
import omni.kit.async_engine


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to USD stage.")

    try:
        options = parser.parse_args()
    except Exception as e:
        carb.log_error(str(e))
        return

    omni.kit.async_engine.run_coroutine(open_stage_async(options.path))


async def open_stage_async(path: str):
    async def _open_stage_internal(path):
        is_stage_with_session = False
        try:
            import omni.kit.usd.layers as layers
            live_session_name = layers.get_live_session_name_from_shared_link(path)
            is_stage_with_session = live_session_name is not None
        except Exception:
            pass

        if is_stage_with_session:
            # Try to open the stage with specified live session.
            (success, error) = await layers.get_live_syncing().open_stage_with_live_session_async(path)
        else:
            # Otherwise, use normal stage open.
            (success, error) = await omni.usd.get_context().open_stage_async(path)

        if not success:
            carb.log_error(f"Failed to open stage {path}: {error}.")

    result, _ = await omni.client.stat_async(path)
    if result == omni.client.Result.OK:
        await _open_stage_internal(path)

        return

    broken_url = omni.client.break_url(path)
    if broken_url.scheme == 'omniverse':
        # Attempt to connect to nucleus server before opening stage
        from omni.kit.widget.nucleus_connector import connect
        server_url = omni.client.make_url(scheme='omniverse', host=broken_url.host)
        connect(
            broken_url.host, server_url,
            on_success_fn=lambda *_: asyncio.ensure_future(_open_stage_internal(path)),
            on_failed_fn=lambda *_: carb.log_error(f"Open stage: Failed to connect to server '{server_url}'.")
        )
    else:
        carb.log_warn(f"Open stage: Could not open non-existent url '{path}'.")


main()
