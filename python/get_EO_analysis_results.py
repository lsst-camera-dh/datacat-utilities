"""Helper tools to fetch Camera EO Test analysis results."""

from eTraveler.clientAPI.connection import Connection
from exploreFocalPlane import exploreFocalPlane
from exploreRaft import exploreRaft

import numpy as np
import collections
import argparse
import time


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
        self.raft_dataTypes = ['gain', 'gain_error', 'psf_sigma', 'read_noise', 'system_noise',
                               'total_noise', 'bright_pixels', 'bright_columns', 'dark_pixels',
                               'dark_columns', 'num_traps',
                               'cti_low_serial', 'cti_high_serial', 'cti_low_parallel', 'cti_high_parallel',
                               'nonlinearity', 'dark_current_95CL', 'ptc_gain', 'pixel_mean', 'full_well',
                               'max_frac_dev']

        # define hardware types and traveler names, respectively

        self.site_type['I&T-BOT'] = ['LCA-10134_Cryostat-0001', 'INT-SR-EOT-01']  # supply hw instance name
        self.site_type['I&T-Raft'] = ['LCA-11021_RTM', 'INT-SR-EOT-01']
        self.site_type['BNL-Raft'] = ['LCA-11021_RTM', 'SR-RTM-EOT-03']
        self.site_type['BNL-ITL-CCD'] = ['ITL-CCD', 'SR-EOT-1']
        self.site_type['BNL-e2v-CCD'] = ['e2v-CCD', 'SR-EOT-1']
        self.site_type['vendor-e2v'] = ['e2v-CCD', 'SR-EOT-02']
        self.site_type['vendor-ITL'] = ['ITL-CCD', 'SR-EOT-02']

        self.type_dict = {}
        self.type_dict_BOT = {}
        self.type_dict_raft = {}
        self.type_dict_ccd = {}

        # define step and schema names, respectively

        self.type_dict_BOT['gain'] = ['fe55_analysis_BOT', 'fe55_BOT_analysis']
        self.type_dict_BOT['gain_error'] = ['fe55_analysis_BOT', 'fe55_BOT_analysis']
        self.type_dict_BOT['psf_sigma'] = ['fe55_analysis_BOT', 'fe55_BOT_analysis']
        self.type_dict_BOT['cti_low_serial'] = ['cte_BOT', 'cte_BOT']
        self.type_dict_BOT['cti_high_serial'] = ['cte_BOT', 'cte_BOT']
        self.type_dict_BOT['cti_low_parallel'] = ['cte_BOT', 'cte_BOT']
        self.type_dict_BOT['cti_high_parallel'] = ['cte_BOT', 'cte_BOT']
        self.type_dict_BOT['cti_low_serial_error'] = ['cte_BOT', 'cte_BOT']
        self.type_dict_BOT['cti_high_serial_error'] = ['cte_BOT', 'cte_BOT']
        self.type_dict_BOT['cti_low_parallel_error'] = ['cte_BOT', 'cte_BOT']
        self.type_dict_BOT['cti_high_parallel_error'] = ['cte_BOT', 'cte_BOT']
        self.type_dict_BOT['read_noise'] = ['read_noise_BOT', 'read_noise_BOT']
        self.type_dict_BOT['system_noise'] = ['read_noise_BOT', 'read_noise_BOT']
        self.type_dict_BOT['total_noise'] = ['read_noise_BOT', 'read_noise_BOT']
        self.type_dict_BOT['bright_pixels'] = ['bright_defects_BOT', 'bright_defects_BOT']
        self.type_dict_BOT['bright_columns'] = ['bright_defects_BOT', 'bright_defects_BOT']
        self.type_dict_BOT['dark_pixels'] = ['dark_defects_BOT', 'dark_defects_BOT']
        self.type_dict_BOT['dark_columns'] = ['dark_defects_BOT', 'dark_defects_BOT']
        self.type_dict_BOT['num_traps'] = ['traps_BOT', 'traps_BOT']
        self.type_dict_BOT['dark_current_95CL'] = ['dark_current_BOT', 'dark_current_BOT']
        self.type_dict_BOT['ptc_gain'] = ['ptc_BOT', 'ptc_BOT']
        self.type_dict_BOT['ptc_gain_error'] = ['ptc_BOT', 'ptc_BOT']

        self.type_dict_BOT['QE'] = ['qe_BOT_analysis', 'qe_BOT_analysis']
        self.type_dict_BOT['full_well'] = ['flat_pairs_BOT_analysis', 'flat_pairs_BOT']
        self.type_dict_BOT['max_frac_dev'] = ['flat_pairs_BOT_analysis', 'flat_pairs_BOT']

        self.type_dict['BOT'] = self.type_dict_BOT

        self.BOT_schema_meas = {}
        self.BOT_schema_meas['fe55_BOT_analysis'] = ['gain', 'gain_error', 'psf_sigma']
        self.BOT_schema_meas['read_noise_BOT'] = ['read_noise', 'system_noise', 'total_noise']
        self.BOT_schema_meas['bright_defects_BOT'] = ['bright_pixels', 'bright_columns']
        self.BOT_schema_meas['dark_defects_BOT'] = ['dark_pixels', 'dark_columns']
        self.BOT_schema_meas['dark_current_BOT'] = ['dark_current_95CL']
        self.BOT_schema_meas['traps_BOT'] = ['num_traps']
        self.BOT_schema_meas['cte_BOT'] = ['cti_high_serial', 'cti_high_serial_error',
                                           'cti_high_parallel', 'cti_high_parallel_error', 'cti_low_serial',
                                           'cti_low_serial_error',
                                           'cti_low_parallel', 'cti_low_parallel_error']
        self.BOT_schema_meas['flat_pairs_BOT'] = ['full_well', 'max_frac_dev']
        self.BOT_schema_meas['ptc_BOT'] = ['ptc_gain', 'ptc_gain_error']
        self.BOT_schema_meas['qe_BOT_analysis'] = ['QE']
        self.BOT_schema_meas['tearing_detection_BOT'] = ['detections']

        #        self.type_dict_raft['pixel_mean'] = ['prnu_raft', 'prnu']
        self.type_dict_raft['gain'] = ['fe55_raft_analysis', 'fe55_raft_analysis']
        self.type_dict_raft['gain_error'] = ['fe55_raft_analysis', 'fe55_raft_analysis']
        self.type_dict_raft['psf_sigma'] = ['fe55_raft_analysis', 'fe55_raft_analysis']
        self.type_dict_raft['cti_low_serial'] = ['cte_raft', 'cte_raft']
        self.type_dict_raft['cti_high_serial'] = ['cte_raft', 'cte_raft']
        self.type_dict_raft['cti_low_parallel'] = ['cte_raft', 'cte_raft']
        self.type_dict_raft['cti_high_parallel'] = ['cte_raft', 'cte_raft']
        self.type_dict_raft['cti_low_serial_error'] = ['cte_raft', 'cte_raft']
        self.type_dict_raft['cti_high_serial_error'] = ['cte_raft', 'cte_raft']
        self.type_dict_raft['cti_low_parallel_error'] = ['cte_raft', 'cte_raft']
        self.type_dict_raft['cti_high_parallel_error'] = ['cte_raft', 'cte_raft']
        self.type_dict_raft['read_noise'] = ['read_noise_raft', 'read_noise_raft']
        self.type_dict_raft['system_noise'] = ['read_noise_raft', 'read_noise_raft']
        self.type_dict_raft['total_noise'] = ['read_noise_raft', 'read_noise_raft']
        self.type_dict_raft['bright_pixels'] = ['bright_defects_raft', 'bright_defects_raft']
        self.type_dict_raft['bright_columns'] = ['bright_defects_raft', 'bright_defects_raft']
        self.type_dict_raft['dark_pixels'] = ['dark_defects_raft', 'dark_defects_raft']
        self.type_dict_raft['dark_columns'] = ['dark_defects_raft', 'dark_defects_raft']
        self.type_dict_raft['num_traps'] = ['traps_raft', 'traps_raft']
        self.type_dict_raft['dark_current_95CL'] = ['dark_current_raft', 'dark_current_raft']
        self.type_dict_raft['ptc_gain'] = ['ptc_raft', 'ptc_raft']
        self.type_dict_raft['ptc_gain_error'] = ['ptc_raft', 'ptc_raft']

        self.type_dict_raft['QE'] = ['qe_raft_analysis', 'qe_raft_analysis']
        self.type_dict_raft['full_well'] = ['flat_pairs_raft_analysis', 'flat_pairs_raft']
        self.type_dict_raft['max_frac_dev'] = ['flat_pairs_raft_analysis', 'flat_pairs_raft']

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
        self.type_dict_ccd['dark_current_95CL'] = ['dark_current_offline', 'dark_current_95CL']
        self.type_dict_ccd['ptc_gain'] = ['ptc_offline', 'ptc']
        self.type_dict_ccd['ptc_gain_error'] = ['ptc_offline', 'ptc']
        self.type_dict_ccd['QE'] = ['qe_offline', 'qe']

        self.type_dict['ccd'] = self.type_dict_ccd

        self.camera_type = 'raft'

        if server == 'Prod':
            pS = True
        else:
            pS = False
        self.connect = Connection(operator='richard', db=db, exp='LSST-CAMERA', prodServer=pS)
        self.eFP = exploreFocalPlane(db=db, prodServer=server)
        self.eR = exploreRaft(db=db, prodServer=server)

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
        if 'Raft' in site_type:
            self.camera_type = 'raft'
        elif "BOT" in site_type:
            self.camera_type = 'BOT'
        else:
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
            if test_type is None:
                data = self.connect.getRunResults(run=run)
            else:
                stepName = self.type_dict[self.camera_type][test_type][0]
                #if self.camera_type == "BOT":
                #    stepName = "BOT_EO_analysis"
                data = self.connect.getRunResults(run=run, stepName=stepName)
            if self.camera_type == "BOT":
                rl = self.eFP.focalPlaneContents(parentName=self.site_type["I&T-BOT"][0], run=run)
                for r in rl:
                    dev_list.append(r[0])
            else:
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
            ccd_dict: single raft or CCD - dictionary of lists of values (eg gains) keyed on CCD name
                        full FP: dict (by test) of dict by raft slot by dict of ccd slot containing lists
                        of results. Note the use of slots (Rxx, Sxx) not raft or CCD names.
        """
        ccd_dict = collections.OrderedDict()
        test_dict = collections.OrderedDict()

        test_array = [-1.]*16
        ccd_idx = {"S00":0, "S01":1, "S02":2, "S10":3, "S11":4, "S12":5, "S20":6, "S21":7, "S22":8 }


        ccdName = None
        if self.camera_type == 'ccd':
            ccdName = device

        if self.camera_type is not "BOT":

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

        else:
            step = "BOT_EO_analysis"
            if len(data) != 1:
                step = data["steps"][self.type_dict["raft"][test_type][0]]

            t_dict = data['steps'][step]
            # find schema for test type
            test_name_type = ""
            for schemas in self.BOT_schema_meas:
                if test_type in self.BOT_schema_meas[schemas]:
                    test_name_type = schemas

            for a in t_dict[test_name_type][1:]:
                ccd_slot = a["slot"]
                raft_slot = a["raft"]

                if test_type == "QE":
                    band = a["band"]
                    qe_band = test_type + "-" + str(band)
                    t = test_dict.setdefault(qe_band, {})
                else:
                    t = test_dict.setdefault(test_type, {})
                r = t.setdefault(raft_slot, {})
                #c = r.setdefault(ccd_slot, [])
                c = r.setdefault(ccd_slot, test_array.copy())
                meas = a[test_type]
                amp_id = a["amp"] - 1
                slot_id = ccd_idx[ccd_slot]
                array_idx = 16 * slot_id + amp_id
                # c.append(meas)
                c[amp_id] = meas
                #c.append(meas)

            return test_dict

    def get_all_results(self, data=None, device=None):
        """
        get_results:

        Inputs:

            data: object resulting from get_tests containing the results data
            device: specific hardware identifier desired

        Output:
            test_dict: single raft: dictionary (by test, eg gain) of dictionary (by CCD) of lists of values
                        full FP: dict (by test) of dict by raft slot by dict of ccd slot containing lists
                        of results. Note the use of slots (Rxx, Sxx) not raft or CCD names.
            (eg gains)
        """
        test_dict = collections.OrderedDict()
        # get the list of supported tests from member dict
        test_list = self.type_dict[self.camera_type]

        test_array = [-1.]*16
        ccd_idx = {"S00":0, "S01":1, "S02":2, "S10":3, "S11":4, "S12":5, "S20":6, "S21":7, "S22":8 }

        ccdName = None
        if self.camera_type == 'ccd':
            ccdName = device

        if self.camera_type is not "BOT":

            for tests in test_list:
                steps = test_list[tests][0]
                test_name_type = test_list[tests][1]

                # set up empty dict, keyed off test name
                t = test_dict.setdefault(tests, {})

                # test_name_type is the test's EO schema name
                results_list = data['steps'][steps][test_name_type]
                for amp in results_list[1:]:
                    if self.camera_type == 'raft':
                        ccdName = amp['sensor_id']
                    # set up dict by CCD with list of test quantities
                    c = t.setdefault(ccdName, [])
                    ampResult = amp[tests]
                    c.append(ampResult)

        else:
            for step in data["steps"]:
                t_dict = data['steps'][step]
                for test_name_type in t_dict:
                    # only accept known EO test steps
                    if test_name_type not in [t[1] for t in self.type_dict_BOT.values()]:
                    #if test_name_type == "job_info" or test_name_type == 'tearing_detection_BOT' or \
                    #        test_name_type == "package_versions":
                        continue

                    for a in t_dict[test_name_type][1:]:
                        try:
                            raft_slot = a["raft"]
                            ccd_slot = a["slot"]
                        except KeyError:
                            print(a)

                        for res in self.BOT_schema_meas[test_name_type]:
                            if res == "QE":
                                band = a["band"]
                                qe_band = res + "-" + str(band)
                                t = test_dict.setdefault(qe_band, {})
                            else:
                                t = test_dict.setdefault(res, {})
                            r = t.setdefault(raft_slot, {})
                            #c = r.setdefault(ccd_slot, [])
                            c = r.setdefault(ccd_slot, test_array.copy())
                            meas = a[res]
                            amp_id = a["amp"] - 1
                            slot_id = ccd_idx[ccd_slot]
                            array_idx = 16*slot_id+amp_id
                            #c.append(meas)
                            c[amp_id] = meas

        return test_dict


if __name__ == "__main__":
    # Command line arguments
    parser = argparse.ArgumentParser(description='Find EO analysis test results.')

    #   The following are 'convenience options' which could also be specified in the filter string
    # parser.add_argument('-t', '--htype', default=None, help="hardware type (default=%(default)s)") #ITL-CCD
    parser.add_argument('-d', '--db', default='Prod', help="eT database (default=%(default)s)")
    parser.add_argument('-e', '--eTserver', default='Prod', help="eTraveler server (default=%(default)s)")
    parser.add_argument('--appSuffix', '--appSuffix', default='jrb',
                        help="eTraveler server (default=%(default)s)")
    parser.add_argument('-t', '--test_type', default='gain', help="test type (default=%(default)s)")
    parser.add_argument('-s', '--site_type', default='I&T-Raft', help="type & site of test (default=%("
                                                                      "default)s)")
    parser.add_argument('-r', '--run', default=None, help="run number (default=%(default)s)")
    args = parser.parse_args()

    g = get_EO_analysis_results(db=args.db, server=args.eTserver)

    if True:
        start = time.time()

        raft_list, data = g.get_tests(site_type=args.site_type, test_type=args.test_type, run=args.run)
        res = g.get_results(test_type=args.test_type, data=data, device=raft_list)
        after_sngl = time.time() - start

        raft_list_all, data_all = g.get_tests(site_type=args.site_type, run=args.run)
        res_all = g.get_all_results(data=data_all, device=raft_list_all)
        after_all = time.time() - start

    print("timing info: ", start, after_sngl, after_all)
