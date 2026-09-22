__all__ = ["Partition", "disk_partitions"]
import platform
from dataclasses import dataclass


@dataclass
class Partition:
    device: str
    mountpoint: str
    fstype: str
    opts: list[str]


def disk_partitions():
    """Minimal implementation of disk_partitions from psutil."""
    if platform.system() not in ("Linux", "Darwin"):
        raise RuntimeError("disk_partitions() is only supported on Linux/Darwin platforms.")

    partitions: list[Partition] = []
    with open("/proc/mounts", "r") as f:
        lines = f.readlines()
        for line in lines:
            parts = line.split()
            device, mountpoint, fstype, opts = parts[0], parts[1], parts[2], parts[3]
            partitions.append(Partition(device, mountpoint, fstype, opts))

    return partitions
