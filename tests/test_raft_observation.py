from unittest import TestCase
from raft_observation import raft_observation

class TestRaft_observation(TestCase):
    def test_find(self):

        rO = raft_observation(run=4418, step='fe55_raft_acq', imgtype="BIAS", db='Prod', site='BNL', prodServer='Dev',
                              appSuffix='-jrb')

        obs_dict = rO.find()

        self.assertEqual(len(obs_dict),5)
