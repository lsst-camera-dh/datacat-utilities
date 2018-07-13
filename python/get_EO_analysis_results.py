"""Helper tools to fetch Camera EO Test analysis results."""

from eTraveler.clientAPI.connection import Connection
import numpy as np

import argparse


class get_EO_analysis_results():

    def __init__(self, db='Prod', server='Prod', appSuffix=None):

        self.site_type = {}
        self.dataTypes = {'gain', 'read_noise', 'bright_pixels', 'bright_columns' 'dark_pixels', 'dark_columns',
                          'traps',
                          'cti_low_serial', 'cti_high_serial', 'cti_low_parallel', 'cti_high_parallel', 'nonlinearity'

                          }

        self.site_type['I&T-Raft'] = ['LCA-11021_RTM', 'INT-SR-EOT-01']
        self.site_type['BNL-Raft'] = ['LCA-11021_RTM', 'SR-RTM-EOT-03']
        self.site_type['BNL-ITL-CCD'] = ['ITL-CCD', 'SR-EOT-1']
        self.site_type['BNL-e2v-CCD'] = ['e2v-CCD', 'SR-EOT-1']
        self.site_type['vendor-e2v'] = ['e2v-CCD', 'SR-EOT-02']

        self.type_dict = {}

        self.type_dict['gain'] = ['fe55_raft_analysis', 'fe55_raft_analysis']
        self.type_dict['cti_low_serial'] = ['cte_offline', 'cte']
        self.type_dict['cti_high_serial'] = ['cte_offline', 'cte']
        self.type_dict['cti_low_parallel'] = ['cte_offline', 'cte']
        self.type_dict['cti_high_parallell'] = ['cte_offline', 'cte']
        self.type_dict['read_noise'] = ['read_noise_offline', 'read_noise']
        self.type_dict['nonlinearity'] = ['flat_pairs_offline', 'flat_pairs']
        self.type_dict['bright_pixels'] = ['bright_defects_offline', 'bright_defects']
        self.type_dict['bright_columns'] = ['bright_defects_offline', 'bright_defects']
        self.type_dict['dark_pixels'] = ['dark_defects_offline', 'dark_defects']
        self.type_dict['dark_columns'] = ['dark_defects_offline', 'dark_defects']
        self.type_dict['traps'] = ['traps_offline', 'traps']

        if server == 'Prod':
            pS = True
        else:
            pS = False
        self.connect = Connection(operator='richard', db=db, exp='LSST-CAMERA', prodServer=pS)

    def get_tests(self, site_type=None, test_type=None, run=None):

        if run == None:
            data = self.connect.getResultsJH(htype=self.site_type[site_type][0], stepName=self.type_dict[test_type][0],
                                          travelerName=self.site_type[site_type][1])
        else:
            data = self.connect.getRunResults(stepName=self.type_dict[test_type][0])

        # this step gives us dark columns and dark pixels

        raft_list = []

        # Get a list of ccd's
        for raft in data:
            raft_list.append(raft)

        return raft_list, data

    def get_results(self, test_type=None, data=None, raft=None):

        results = []

        step = data[raft]['steps'][self.type_dict[test_type][0]]

        for amp in step[self.type_dict[test_type][1]][1:]:
            ccd = amp['sensor_id']
            ampResult = amp[test_type]
            results.append(ampResult)

        return results

    def raft_type(self, raft=None):
        eR = exploreRaft()
        ccd_list = eR.raftContents(raftName=raft)
        if 'ITL' in ccd_list[0][0]:
            type = 'ITL'
        else:
            type = 'e2v'

        return type


if __name__ == "__main__":
    ## Command line arguments
    parser = argparse.ArgumentParser(
        description='Find archived data in the LSST  data Catalog. These include CCD test stand and vendor data files.')

    ##   The following are 'convenience options' which could also be specified in the filter string
    # parser.add_argument('-t', '--htype', default=None, help="hardware type (default=%(default)s)") #ITL-CCD
    parser.add_argument('-d', '--db', default='Prod', help="eT database (default=%(default)s)")
    parser.add_argument('-e', '--eTserver', default='Dev', help="eTraveler server (default=%(default)s)")
    parser.add_argument('--appSuffix', '--appSuffix', default='jrb',
                        help="eTraveler server (default=%(default)s)")
    args = parser.parse_args()

    g = get_EO_analysis_results()
    raft_list, data = g.get_tests(site_type="I&T-Raft", test_type="gain")
    res = g.get_results(test_type='gain', data=data, raft=raft_list[0])
