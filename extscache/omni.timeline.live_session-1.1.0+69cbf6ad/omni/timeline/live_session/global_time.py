import time


# For now we use system time, later we may use something from Nucleus
def get_global_time_s() -> float:
    return time.time()