def _get_ext_version():
    """
    Extract isaacsim.replicator.object based on the local extension.toml file
    """
    import os

    script_directory = os.path.dirname(os.path.abspath(__file__))
    toml_relative_path = "../../../config/extension.toml"
    toml_file = os.path.abspath(os.path.join(script_directory, toml_relative_path))

    with open(toml_file, "r") as f:
        ext_conf = f.read()
        import re

        return re.search(r'(version\s*=\s*")([^\"]+)(")', ext_conf).group(2)


VERSION = _get_ext_version()
EXTENSION_NAME = f"[METROPERF][isaacsim.replicator.object:{VERSION}]"
SEMANTIC_CLASS_STRING = "oro"
