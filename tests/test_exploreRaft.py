from unittest import TestCase
from exploreRaft import exploreRaft


class TestExploreRaft(TestCase):
    def test_raftContents(self):
        raftName = 'LCA-11021_RTM-004'

        eR = exploreRaft()

        ccd_list = eR.raftContents(raftName)

        self.assertEquals(ccd_list[0][0], 'ITL-3800C-078')

    def test_CCD_parent(self):
        eR = exploreRaft()

        CCD_name = "ITL-3800C-034"

        parentRaft = eR.CCD_parent(CCD_name, 'ITL-CCD')

        self.assertEquals(parentRaft, 'LCA-11021_RTM-004')

    def test_REB_parent(self):
        eR = exploreRaft()

        self.assertEquals(eR.REB_parent("LCA-13574-016"), "LCA-11021_RTM-004")

    def test_REB_CCD(self):
        eR = exploreRaft()

        reb_ccds = eR.REB_CCD('LCA-13574-016')
        self.assertEquals(reb_ccds[0], "ITL-3800C-078")
