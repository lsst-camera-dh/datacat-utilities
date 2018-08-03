"""Helper tools to fetch Camera EO Test analysis results."""

from eTraveler.clientAPI.connection import Connection
import numpy as np
import collections
import argparse


class get_EO_analysis_results():
    """
    get_EO_analysis_results:

    Purpose:

    Query the eTraveler results database for its analysis results values, eg gain, read_noise etc. It attempts
    to simplify the user inputs by abstracting out the details of what traveler and test steps were run.

    As such, it is limited to the 'standard' travelers. These are stable at BNL, but not necessarily so at
    SLAC for I&T.

    Example usage:

        g = get_EO_analysis_results()   # initialize (all Prod by default"
        raft_list, data = g.get_tests(site_type="I&T-Raft", test_type="gain")  # get the data for I&T-Raft
        res = g.get_results(test_type='gain', data=data, device=raft_list[0])  # get the data for a raft
    """
    def __init__(self, db='Prod', server='Prod', appSuffix=None):
        """
        __init__

         Inputs:
            db: eTraveler database to use. Choices are Prod or Dev (case matters)
            server: eTraveler server to use. Choices are Prod or Dev
        """

        self.site_type = {}
        self.dataTypes = {'gain', 'read_noise', 'bright_pixels', 'bright_columns' 'dark_pixels',
                          'dark_columns',
                          'traps',
                          'cti_low_serial', 'cti_high_serial', 'cti_low_parallel', 'cti_high_parallel',
                          'nonlinearity'

                          }

        # define hardware types and traveler names, respectively

        self.site_type['I&T-Raft'] = ['LCA-11021_RTM', 'INT-SR-EOT-01']
        self.site_type['BNL-Raft'] = ['LCA-11021_RTM', 'SR-RTM-EOT-03']
        self.site_type['BNL-ITL-CCD'] = ['ITL-CCD', 'SR-EOT-1']
        self.site_type['BNL-e2v-CCD'] = ['e2v-CCD', 'SR-EOT-1']
        self.site_type['vendor-e2v'] = ['e2v-CCD', 'SR-EOT-02']
        self.site_type['vendor-ITL'] = ['ITL-CCD', 'SR-EOT-02']

        self.type_dict = {}
        self.type_dict_raft = {}
        self.type_dict_ccd = {}

        # define step and schema names, respectively

        self.type_dict_raft['gain'] = ['fe55_raft_analysis', 'fe55_raft_analysis']
        self.type_dict_raft['gain_error'] = ['fe55_raft_analysis', 'fe55_raft_analysis']
        self.type_dict_raft['cti_low_serial'] = ['cte_raft', 'cte_raft']
        self.type_dict_raft['cti_high_serial'] = ['cte_raft', 'cte_raft']
        self.type_dict_raft['cti_low_parallel'] = ['cte_raft', 'cte_raft']
        self.type_dict_raft['cti_high_parallell'] = ['cte_raft', 'cte_raft']
        self.type_dict_raft['cti_low_serial_error'] = ['cte_raft', 'cte_raft']
        self.type_dict_raft['cti_high_serial_error'] = ['cte_raft', 'cte_raft']
        self.type_dict_raft['cti_low_parallel_error'] = ['cte_raft', 'cte_raft']
        self.type_dict_raft['cti_high_parallell_error'] = ['cte_raft', 'cte_raft']
        self.type_dict_raft['read_noise'] = ['read_noise_raft', 'read_noise_raft']
        self.type_dict_raft['system_noise'] = ['read_noise_raft', 'read_noise_raft']
        self.type_dict_raft['total_noise'] = ['read_noise_raft', 'read_noise_raft']
        self.type_dict_raft['nonlinearity'] = ['flat_pairs_raft_analysis', 'flat_pairs_raft']
        self.type_dict_raft['bright_pixels'] = ['bright_defects_raft', 'bright_defects_raft']
        self.type_dict_raft['bright_columns'] = ['bright_defects_raft', 'bright_defects_raft']
        self.type_dict_raft['dark_pixels'] = ['dark_defects_raft', 'dark_defects_raft']
        self.type_dict_raft['dark_columns'] = ['dark_defects_raft', 'dark_defects_raft']
        self.type_dict_raft['traps'] = ['traps_raft', 'traps_raft']
        self.type_dict_raft['dark_current'] = ['dark_current_raft', 'dark_current_raft']
        self.type_dict_raft['ptc'] = ['ptc_raft', 'ptc_raft']
        self.type_dict_raft['pixel_mean'] = ['prnu_raft', 'prnu']

        self.type_dict['raft'] = self.type_dict_raft

        self.type_dict_ccd['gain'] = ['fe55_analysis', 'fe55_analysis']
        self.type_dict_ccd['gain_error'] = ['fe55_analysis', 'fe55_analysis']
        self.type_dict_ccd['psf_sigma'] = ['fe55_analysis', 'fe55_analysis']
        self.type_dict_ccd['cti_low_serial'] = ['cte_offline', 'cte']
        self.type_dict_ccd['cti_high_serial'] = ['cte_offline', 'cte']
        self.type_dict_ccd['cti_low_parallel'] = ['cte_offline', 'cte']
        self.type_dict_ccd['cti_high_parallel'] = ['cte_offline', 'cte']
        self.type_dict_ccd['cti_low_serial_error'] = ['cte_offline', 'cte']
        self.type_dict_ccd['cti_high_serial_error'] = ['cte_offline', 'cte']
        self.type_dict_ccd['cti_low_parallel_error'] = ['cte_offline', 'cte']
        self.type_dict_ccd['cti_high_parallel_error'] = ['cte_offline', 'cte']
        self.type_dict_ccd['read_noise'] = ['read_noise_offline', 'read_noise']
        self.type_dict_ccd['system_noise'] = ['read_noise_offline', 'read_noise']
        self.type_dict_ccd['total_noise'] = ['read_noise_offline', 'read_noise']
        self.type_dict_ccd['max_frac_dev'] = ['flat_pairs_offline', 'flat_pairs']
        self.type_dict_ccd['bright_pixels'] = ['bright_defects_offline', 'bright_defects']
        self.type_dict_ccd['bright_columns'] = ['bright_defects_offline', 'bright_defects']
        self.type_dict_ccd['dark_pixels'] = ['dark_defects_offline', 'dark_defects']
        self.type_dict_ccd['dark_columns'] = ['dark_defects_offline', 'dark_defects']
        self.type_dict_ccd['num_traps'] = ['traps_offline', 'traps']
        self.type_dict_ccd['pixel_mean'] = ['prnu_offline', 'prnu']
        self.type_dict_ccd['num_traps'] = ['traps_offline', 'traps']
        self.type_dict_ccd['dark_current'] = ['dark_current_offline', 'dark_current_95CL']
        self.type_dict_ccd['ptc'] = ['ptc_offline', 'ptc']

        self.type_dict['ccd'] = self.type_dict_ccd

        self.camera_type = 'raft'

        if server == 'Prod':
            pS = True
        else:
            pS = False
        self.connect = Connection(operator='richard', db=db, exp='LSST-CAMERA', prodServer=pS)

    def get_tests(self, site_type=None, test_type=None, run=None):
        """
        get_tests:

        Inputs:

            site_type: kind of test desired, eg BNL-Raft
            test_type: result type desired, eg gain
            run: (Optional) specific run number to use. If specified, site_type is ignored.

        Outputs:

            dev_list: list of hardware devices associated with the query
            data: object containing data from the query to getResultsXXX
        """
        if 'Raft' not in site_type:
            self.camera_type = 'ccd'

        dev_list = []

        if run is None:
            #            hardwareLabels = ['Run_Quality:Run_for_the_record']
            # hardwareLabels = ["Run_Quality:"]
            data = self.connect.getResultsJH(htype=self.site_type[site_type][0],
                                             stepName=self.type_dict[self.camera_type][test_type][0],
                                             travelerName=self.site_type[site_type][1])
            # Get a list of devices
            for dev in data:
                dev_list.append(dev)

        else:
            data = self.connect.getRunResults(run=run,
                                              stepName=self.type_dict[self.camera_type][test_type][0])
            dev_list = data['experimentSN']

        # this step gives us dark columns and dark pixels

        return dev_list, data

    def get_results(self, test_type=None, data=None, device=None):
        """
        get_results:

        Inputs:

            test_type: result type desired (eg gain)
            data: object resulting from get_tests containing the results data
            device: specific hardware identifier desired

        Output:
            ccd_dict: dictionary of lists of values (eg gains) keyed on CCD name
        """
        ccd_dict = collections.OrderedDict()

        ccdName = None
        if self.camera_type == 'ccd':
            ccdName = device

        try:
            data[device]
            step = data[device]['steps'][self.type_dict[self.camera_type][test_type][0]]
        except KeyError:
            step = data['steps'][self.type_dict[self.camera_type][test_type][0]]

        for amp in step[self.type_dict[self.camera_type][test_type][1]][1:]:
            if self.camera_type == 'raft':
                ccdName = amp['sensor_id']
            c = ccd_dict.setdefault(ccdName, [])
            ampResult = amp[test_type]
            c.append(ampResult)

        return ccd_dict


if __name__ == "__main__":
    # Command line arguments
    parser = argparse.ArgumentParser(description='Find EO analysis test results.')

    #   The following are 'convenience options' which could also be specified in the filter string
    # parser.add_argument('-t', '--htype', default=None, help="hardware type (default=%(default)s)") #ITL-CCD
    parser.add_argument('-d', '--db', default='Prod', help="eT database (default=%(default)s)")
    parser.add_argument('-e', '--eTserver', default='Dev', help="eTraveler server (default=%(default)s)")
    parser.add_argument('--appSuffix', '--appSuffix', default='jrb',
                        help="eTraveler server (default=%(default)s)")
    parser.add_argument('-t', '--test_type', default='gain', help="test type (default=%(default)s)")
    parser.add_argument('-s', '--site_type', default='I&T-Raft', help="type & site of test (default=%("
                                                                      "default)s)")
    args = parser.parse_args()

    g = get_EO_analysis_results()
    raft_list, data = g.get_tests(site_type=args.site_type, test_type=args.test_type)
    res = g.get_results(test_type='gain', data=data, device=raft_list[0])
