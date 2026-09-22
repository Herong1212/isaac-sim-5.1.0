"""Script to open USD stage."""

import carb
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to USD stage.")

    try:
        options = parser.parse_args()
    except Exception as e:
        carb.log_error(str(e))
        return

    import omni.usd
    omni.usd.get_context().open_stage_with_callback(options.path, None)


main()
