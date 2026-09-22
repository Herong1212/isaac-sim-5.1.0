from typing import List

from omni.sensors.nv.radar.scripts.radar_detection import *  # noqa: E402

# --- Data integrity check for gmo radar frame ---
# Those checks are run as part of the compute stability test.
# They are testing problems that were seen with radar in the past.
# These checks operate on an h5 file that has been written to disk.


class DataIntegrityTest:
    def __init__(self):
        pass

    def checkFrame(self, frame: GmoRadarFrame) -> bool:
        raise NotImplementedError("To be implemented by subclasses")


class DiGmoHeader(DataIntegrityTest):
    def __init__(self):
        pass

    def checkFrame(self, frame: GmoRadarFrame):
        if not isinstance(frame, GmoRadarFrame):
            print("Radar gmo data integrity check failed: Frame is not of type GmoRadarFrame!")
            return False

        value_pairs = [
            (frame.magicNumber, 0x4E474D4F, "magic number"),
            (frame.majorVersion, 1, "major version"),
            (frame.minorVersion, 0, "minor version"),
            (frame.patchVersion, 0, "patch version"),
            (frame.frameOfReference, GmoFrameOfReference.SENSOR, "frame of reference"),
            (frame.motionCompensationState, GmoMotionCompensationState.NONCOMPENSATED, "motion compensation state"),
            (frame.elementsCoordsType, GmoCoordsType.SPHERICAL, "elements coordinates type"),
            (frame.outputType, GmoOutputType.POINTCLOUD, "output type"),
        ]

        for value, expected, name in value_pairs:
            if value != expected:
                print(f"Radar gmo data integrity check failed: {name} mismatch!")
                return False

        return True


class DiTimestamps(DataIntegrityTest):
    def __init__(self):
        self.last_scan_ts = 0

    def checkFrame(self, frame: GmoRadarFrame):
        if frame.timestampNs <= self.last_scan_ts:
            print("Radar gmo data integrity check failed: Timestamps not increasing!")
            print("  FrameId: ", frame.frameId)
            print(f"  Last timestamp: {self.last_scan_ts} ns")
            print(f"  Current timestamp: {frame.timestampNs} ns")
            return False
        self.last_scan_ts = frame.timestampNs
        return True


class DiFrameIds(DataIntegrityTest):
    def __init__(self):
        self.last_frame_id = None

    def checkFrame(self, frame: GmoRadarFrame):
        if self.last_frame_id is None:
            if not isinstance(frame.frameId, int):
                print("Radar gmo data integrity check failed: Frame ID is not an integer!")
                return False
            self.last_frame_id = frame.frameId
        else:
            if frame.frameId != self.last_frame_id + 1:
                print("Radar gmo data integrity check failed: Frame IDs not increased by 1!")
                return False
            self.last_frame_id = frame.frameId
        return True


class DiRangeValuesSorted(DataIntegrityTest):
    def __init__(self):
        pass

    def checkFrame(self, frame: GmoRadarFrame):
        last_det_r_m = 0
        _, _, ranges_meter = frame.get_az_el_range()
        for r_m in ranges_meter:
            if r_m < last_det_r_m:
                print("Radar gmo data integrity check failed: Range values not increasing!")
                return False
            last_det_r_m = r_m
        return True


class DiDetectionValueLimits(DataIntegrityTest):
    def __init__(self):
        pass

    def checkFrame(self, frame: GmoRadarFrame):

        minAzRad = frame.minAzRad
        maxAzRad = frame.maxAzRad
        minElRad = frame.minElRad
        maxElRad = frame.maxElRad
        minRangeM = 0
        maxRangeM = frame.maxRangeM
        minVelMps = frame.minVelMps
        maxVelMps = frame.maxVelMps
        minRcsDbsm = -60
        maxRcsDbsm = 60

        az_radians, el_radians, ranges_meter = frame.get_az_el_range()
        velocities_mps = frame.rv_ms
        rcss_dbsm = frame.scalar

        list_bounds_tuples = [
            (az_radians, minAzRad, maxAzRad, "azimuth"),
            (el_radians, minElRad, maxElRad, "elevation"),
            (ranges_meter, minRangeM, maxRangeM, "range"),
            (velocities_mps, minVelMps, maxVelMps, "velocity"),
            (rcss_dbsm, minRcsDbsm, maxRcsDbsm, "RCS"),
        ]

        for values_list, min_val, max_val, name in list_bounds_tuples:
            for value in values_list:
                if not (min_val <= value <= max_val):
                    print(f"Radar gmo data integrity check failed: {name} value out of bounds!")
                    return False

        return True


class DiDetectionCountMatches(DataIntegrityTest):
    def __init__(self):
        pass

    def checkFrame(self, frame: GmoRadarFrame):
        az_len = len(frame.x)
        el_len = len(frame.y)
        range_len = len(frame.z)
        flags_len = len(frame.flags)
        scalar_len = len(frame.scalar)
        rv_len = len(frame.rv_ms)

        if not (frame.numElements == az_len == el_len == range_len == flags_len == scalar_len == rv_len):
            print("Radar gmo data integrity check failed: Detection count mismatch!")
            return False

        return True


def run_radar_data_integrity_tests(frames: List[GmoRadarFrame]):
    tests = [
        DiGmoHeader(),
        DiTimestamps(),
        DiFrameIds(),
        DiRangeValuesSorted(),
        DiDetectionValueLimits(),
        DiDetectionCountMatches(),
    ]

    for frame in frames:
        for test in tests:
            if not test.checkFrame(frame):
                print("Data integrity test failed for frame: ", frame.frameId)
                return False

    return True
