import argparse
import carb
import omni.timeline

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--time", default=None, help="Time that will be set via timeline.set_current_time.")

    try:
        options = parser.parse_args()
    except Exception as e:
        carb.log_error(str(e))
        return

    timeline = omni.timeline.get_timeline_interface()
    if timeline is None:
        carb.log_error("control_timeline: Timeline interface not available")
        return

    if options.time:
        timeline.set_current_time(float(options.time))

main()