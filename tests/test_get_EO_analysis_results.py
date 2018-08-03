from unittest import TestCase
from get_EO_analysis_results import get_EO_analysis_results

class TestGet_EO_analysis_results(TestCase):
    def test_get_tests(self):
        gR = get_EO_analysis_results()

        raft_list, data = gR.get_tests(site_type="I&T-Raft", test_type="gain")

        self.assertNotEquals(len(raft_list), 0 )
        self.assertNotEquals(len(data), 0 )


    def test_get_results(self):
        gR = get_EO_analysis_results()

        raft_list, data = gR.get_tests(site_type="I&T-Raft", test_type="gain")

        res = gR.get_results(test_type='gain', data=data, device=raft_list[0])

        self.assertNotEquals(res,0)