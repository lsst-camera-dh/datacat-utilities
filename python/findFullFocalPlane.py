from __future__ import print_function

import argparse

from DataCatalog import DataCatalog
from eTraveler.clientAPI.connection import Connection


class findFullFocalPlane:
    def __init__(self, prodServer="Prod"):

        self.mirrorName = None
        self.FType = None
        self.XtraOpts = None
        self.testName = None

        self.site = "SLAC"
        self.run = None

        self.db = None
        self.prodServer = prodServer

        self.connect_Prod = Connection(operator='richard', db="Prod", exp='LSST-CAMERA',
                                       prodServer=prodServer)
        self.connect_Dev = Connection(operator='richard', db="Dev", exp='LSST-CAMERA', prodServer=prodServer)

        self.connections = {}
        o = self.connections.setdefault("connect", {})
        o["Prod"] = self.connect_Prod
        o["Dev"] = self.connect_Dev

    def find(self, FType=None, XtraOpts=None, testName=None, run=None):

        if "D" not in run:
            self.db = "Prod"
        else:
            self.db = "Dev"

        if FType is not None:
            self.FType = FType
        if XtraOpts is not None:
            self.XtraOpts = XtraOpts
        if testName is not None:
            self.testName = testName
        if run is not None:
            self.run = run

        self.mirrorName = "INT-prod"

        run_info = self.connections["connect"][self.db].getRunResults(run=self.run)
        device = run_info['experimentSN']
        acq_step = ""
        dev_type = "LCA-10134_Cryostat"

        if 'CRYO' in device.upper():
            sourceMap = {
                'INT-prod': 'SLAC-prod/prod/',
                'INT-test': 'SLAC-test/test/',
            }
            if self.db == "Dev":
                self.mirrorName = "INT-test"
            acq_step = "BOT_acq_sim"  # we only have simulated BOT runs as of 2019-02-12
            step_info = self.connections["connect"][self.db].getRunFilepaths(run=self.run)
            for steps in step_info:
                if "acq" in steps.lower():
                    acq_step = steps
                    break
        elif 'RTM' in device.upper():
            run_sum = self.connections["connect"][self.db].getRunSummary(run=run)
            if "Integration" in run_sum['subsystem']:
                if self.db == "Dev":
                    self.mirrorName = "INT-test"
                sourceMap = {
                    'INT-prod': 'INT-prod/prod/',
                    'INT-test': 'INT-test/test/',
                }
            else:
                if self.db == "Dev":
                    self.mirrorName = "BNL-test"
                else:
                    self.mirrorName = "BNL-prod"

                sourceMap = {
                    'BNL-prod': 'BNL-prod/prod/',
                    'BNL-test': 'BNL-test/test/',
                }
            dev_type = "LCA-11021_RTM"
            acq_step = testName

        else:
            print("Run " + run + " not a BOT run")
            raise ValueError

        use_latest_activity = False

        query = ''
        site = self.site

        folderList = []

        # get the path to this run

        folderList.append("/LSST/mirror/" + sourceMap[self.mirrorName] +
                          dev_type + "/" + device + "/" + self.run + "/" +
                          acq_step + "/v0/")

        if self.XtraOpts is not None:
            if query == '':
                query = self.XtraOpts
            else:
                query += "&&" + self.XtraOpts

        dsList = []
        for folder in folderList:
            datacatalog = DataCatalog(
                folder=folder,
                site=site,
                use_newest_subfolder=use_latest_activity)

            datasets = datacatalog.find_datasets(query)
            if len(datasets) != 0:
                dsList.append(datasets)

        files = []

        for ds in dsList:
            pathsList = ds.full_paths()
            for item in pathsList:
                if (self.FType is None) or \
                        (self.FType is not None and item.endswith(self.FType)):
                    # if item not in files:
                    if (self.testName is None) or \
                            (self.testName is not None and self.testName.upper() in item.upper()):
                        files.append(item)

        return files


if __name__ == "__main__":
    # Command line arguments
    parser = argparse.ArgumentParser(
        description='Find archived data in the LSST  data Catalog. '
                    'These include CCD test stand and vendor data files.')

    parser.add_argument(
        '-T',
        '--testName',
        default="dark",
        help="(metadata) test type (default=%(default)s)")
    parser.add_argument(
        '-F',
        '--FType',
        default=None,
        help="File type (default=%(default)s)")
    parser.add_argument('-r', '--run', default=None, help="optional run number ")
    parser.add_argument('--server', default='Prod', help="Prod or Dev eT server ")
    parser.add_argument(
        '-X',
        '--XtraOpts',
        default=None,
        help="any extra 'datacat find' options (default=%(default)s)")

    args = parser.parse_args()

    f_FP = findFullFocalPlane(prodServer=args.server)

    files = f_FP.find(run=args.run, testName=args.testName, FType=args.FType)

    print(len(files), " files found")
    print(files)
