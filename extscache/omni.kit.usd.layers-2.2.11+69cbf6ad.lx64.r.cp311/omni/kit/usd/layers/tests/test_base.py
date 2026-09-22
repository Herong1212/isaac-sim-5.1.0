import carb.settings


def enable_server_tests():
    settings = carb.settings.get_settings()

    return settings.get_as_bool("/exts/omni.kit.usd.layers/enable_server_tests")
