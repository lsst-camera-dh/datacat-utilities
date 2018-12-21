from unittest import TestCase
from exploreREB import exploreREB


class TestExploreREB(TestCase):
    def test_ASPIC_parent(self):
        eR = exploreREB()

        aspic_name = 'LCA-11721-ASPIC-1276'

        assert (eR.ASPIC_parent(ASPIC_name=aspic_name) == 'LCA-13574-064')


    def test_REBContents(self):

        REBName = 'LCA-13574-064'

        eR = exploreREB()

        aspic_list = eR.REBContents(REBName=REBName)

        assert (aspic_list[0][0] =='LCA-11721-ASPIC-1276')