import datetime
import os, sys

import carb
import omni.kit.app


def run():
    # Load app plugin
    framework = carb.get_framework()
    framework.load_plugins(loaded_file_wildcards=["omni.kit.app.plugin"], search_paths=["${CARB_APP_PATH}/kernel/plugins"])
    app = omni.kit.app.get_app()

    # Path to where kit was built to
    app_root = os.environ["CARB_APP_PATH"]

    # Inject experience config:
    sys.argv.insert(1, f"{app_root}/apps/omni.app.empty.kit")

    # Start the default Kit Experience App
    res = app.run("kit", app_root, sys.argv)

    framework.unload_all_plugins()

    return res
