from unittest import TestCase
from exploreRaft import exploreRaft


class TestExploreRaft(TestCase):
    def test_raftContents(self):
        raftName = 'LCA-11021_RTM-004'

        eR = exploreRaft()

        ccd_list = eR.raftContents(raftName)

        assert (ccd_list[0][0] == 'ITL-3800C-372'), "Failed CCD id"

    def test_CCD_parent(self):
        eR = exploreRaft()

        CCD_name = "ITL-3800C-372"

        parentRaft = eR.CCD_parent(CCD_name, 'ITL-CCD')

        assert (parentRaft == 'LCA-11021_RTM-004'), "Failed parent raft id"

    def test_REB_parent(self):
        eR = exploreRaft()

        assert (eR.REB_parent("LCA-13574-069") == "LCA-11021_RTM-004"), "failed REB parent id"

    def test_REB_CCD(self):
        eR = exploreRaft()

        reb_ccds = eR.REB_CCD('LCA-13574-064')
        assert (reb_ccds[0] == "ITL-3800C-381"), "Failed Raft CCD content id"
