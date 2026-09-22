import sys
import unittest
from omni.kit.test import AsyncTestCase
import psutil
from ..disk_partitions import disk_partitions, Partition
from .test_utils import time_logger

def filter_partitions(partition: Partition) -> bool:
    if any(x in partition.opts for x in ("nodev", "nosuid", "noexec")):
        return False
    if partition.fstype in (
        "tmpfs",
        "proc",
        "devpts",
        "sysfs",
        "nsfs",
        "autofs",
        "cgroup",
        "hugetlbfs",
    ):
        return False
    return True


@time_logger
class TestDiskPartitions(AsyncTestCase):

    @unittest.skipIf(sys.platform != "linux", "disk_partitions() is only supported on Linux/Darwin platforms")
    async def test_disk_partitions_match_psutil(self):
        """Test disk_partitions output matches that of psutil disk_partitions"""
        
        # check that output of psutil.disk_partitions and pure python is the same (order may differ thus use set)
        self.assertEqual(set((p.device, p.mountpoint, p.fstype) for p in disk_partitions()), set(
            (p.device or 'none', p.mountpoint, p.fstype) for p in psutil.disk_partitions(all=True)
        ))

        # OM-76424: Pre-filter some of the local directories that are of interest for users
        filtered_partitions_1 = filter(filter_partitions, disk_partitions())
        filtered_partitions_2 = filter(filter_partitions, psutil.disk_partitions(all=True))

        # check that filtered output of psuti..disk_partitions and pure python is the same (order may differ)
        self.assertEqual(set(
            (p.device, p.mountpoint, p.fstype) for p in filtered_partitions_1
        ), set((p.device, p.mountpoint, p.fstype) for p in filtered_partitions_2))
