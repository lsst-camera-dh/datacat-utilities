from unittest import TestCase
from findCCD import findCCD


class TestFindCCD(TestCase):
    def test_find(self):
        fCCD = findCCD(FType="fits",
                       testName="fe55_raft_acq", sensorId="ITL-3800C-034", run="3764")

        files = fCCD.find()

        self.assertEquals(len(files), 25)
