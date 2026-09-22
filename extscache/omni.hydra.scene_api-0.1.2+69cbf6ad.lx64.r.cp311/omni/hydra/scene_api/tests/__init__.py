import sys
# Temporarily disable all omni.rtx.tests cases until they are stable on Linux with
# a driver common to all TC agents
if sys.platform == "win32":
    from .test_backgroundloadingscenedelegate import TestBackgroundLoadingSceneDelegate
