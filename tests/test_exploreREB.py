from unittest import TestCase
from exploreREB import exploreREB


class TestExploreREB(TestCase):
    def test_ASPIC_parent(self):
        eR = exploreREB()

        aspic_name = 'LCA-11721-ASPIC-0453'

        self.assertEqual(eR.ASPIC_parent(aspic_name, 'LCA-11721'), 'LCA-13574-017')


    def test_REBContents(self):

        REBName = 'LCA-13574-017'

        eR = exploreREB()

        aspic_list = eR.REBContents(REBName)

        self.assertEqual(aspic_list[0][0],'LCA-11721-ASPIC-0453')