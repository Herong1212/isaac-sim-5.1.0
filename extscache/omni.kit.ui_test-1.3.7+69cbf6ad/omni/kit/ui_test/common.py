import omni.ext
import asyncio
import omni.kit.app
import carb

import sys
import logging

logger = logging.getLogger(__name__)


def setup_logging():
    printInfoLog = carb.settings.get_settings().get("/exts/omni.kit.ui_test/printInfoLog")
    if not printInfoLog:
        return
    # Always log info to stdout to debug tests. Since we tend to reload modules avoid adding more than once.
    logger = logging.getLogger("omni.kit.ui_test")
    if len(logger.handlers) == 0:
        stdout_hdlr = logging.StreamHandler(sys.stdout)
        stdout_hdlr.setLevel(logging.INFO)
        stdout_hdlr.setFormatter(logging.Formatter("[%(name)s] [%(levelname)s] %(message)s", "%H:%M:%S"))
        logger.addHandler(stdout_hdlr)


class InitExt(omni.ext.IExt):
    def on_startup(self):
        setup_logging()


async def wait_n_updates_internal(update_count=2):
    app = omni.kit.app.get_app()
    for _ in range(update_count):
        await app.next_update_async()


async def wait_n_updates(update_count=2):
    """Wait N updates (frames)."""
    logger.debug(f"wait {update_count} updates")
    await wait_n_updates_internal(update_count)


async def human_delay(human_delay_speed: int = 2):
    """Imitate human delay/slowness.

    In practice that function just waits couple of frames, but semantically it is different from other wait function.
    It is used when we want to wait because it would look like normal person interaction. E.g. instead of moving mouse
    and clicking with speed of light wait a bit.

    This is also a place where delay can be increased with a setting to debug UI tests.
    """
    logger.debug("human delay")
    await wait_n_updates_internal(human_delay_speed)

    # Optional extra delay
    human_delay = carb.settings.get_settings().get("/exts/omni.kit.ui_test/humanDelay")
    if human_delay:
        await asyncio.sleep(human_delay)
