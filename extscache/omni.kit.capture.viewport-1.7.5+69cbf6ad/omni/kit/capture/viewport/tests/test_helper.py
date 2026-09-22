import os
import os.path
from typing import List, Tuple
import carb
import omni.kit.app


async def _wait_for_image_files(files: List[str], max_iterations: int = 600) -> Tuple[int, bool, bool]:
    # Verify all output files generated

    app = omni.kit.app.get_app()
    frames_wait = 0
    any_generated, all_generated = False, True
    while max_iterations:
        all_generated = True
        for image_path in files:
            if not os.path.isfile(image_path) or not os.access(image_path, os.R_OK):
                all_generated = False
            else:
                any_generated = True

        await app.next_update_async()
        frames_wait += 1
        max_iterations -= 1

    carb.log_info(f"{frames_wait} frames waited for {'all' if all_generated else 'some' } output files generated!")
    return frames_wait, any_generated, all_generated


async def wait_for_capture_done(capture_instance, expect_outputs: List[str] = []) -> List[str]:
    while not capture_instance.done:
        await omni.kit.app.get_app().next_update_async()

    outputs = capture_instance.get_outputs()

    # Verify all output files generated
    await _wait_for_image_files(outputs)

    if expect_outputs:
        def check_outputs(outputs, expect_outputs):
            for expect in expect_outputs:
                if expect not in outputs:
                    # If capture render product, expect output may be missed due to more frames required to generate the image
                    carb.log_error(f"Expect output missed: {expect} not found in {outputs}")
                    return False

            return True

        all_found = check_outputs(outputs, expect_outputs)
        if not all_found:
            await _wait_for_image_files(outputs)
            check_outputs(outputs, expect_outputs)

    return outputs


async def capture_async(capture_instance, expect_outputs: List[str] = []) -> List[str]:
    capture_instance.start()

    return await wait_for_capture_done(capture_instance, expect_outputs=expect_outputs)
