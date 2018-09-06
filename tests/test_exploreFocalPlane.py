from unittest import TestCase
from exploreFocalPlane import exploreFocalPlane

class TestExploreRFocalPlane(TestCase):
    def test_focalPlaneContents(self):

        eFP = exploreFocalPlane()

        raft_list = eFP.focalPlaneContents(when="2018-09-03T00:00:00.0")

        assert (raft_list[0][0] == 'LCA-11021_RTM-002_ETU1'), "Failed to find Raft "

