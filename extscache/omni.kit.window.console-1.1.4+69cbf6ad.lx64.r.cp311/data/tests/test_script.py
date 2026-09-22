import sys
import carb

message = sys.argv[1] if len(sys.argv) > 1 else "Sample script"
carb.log_info(message)