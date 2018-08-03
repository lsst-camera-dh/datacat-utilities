from unittest import TestCase
from get_EO_analysis_files import get_EO_analysis_files

class TestGet_EO_analysis_files(TestCase):
    def test_get_files(self):
        gF = get_EO_analysis_files()

        files_list = gF.get_files(run=3764, testName="fe55_raft_acq", FType="fits",
                                 imgtype="BIAS")

        self.assertEquals(len(files_list), 9)


    def test_deduce_mirror(self):
        gF = get_EO_analysis_files()

        mirrorName = gF.deduce_mirror(run=3764)

        self.assertEquals(mirrorName,"INT-Raft")