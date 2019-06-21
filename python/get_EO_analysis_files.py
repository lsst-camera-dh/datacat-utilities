from __future__ import print_function
from eTraveler.clientAPI.connection import Connection
from findCCD import findCCD
from findFullFocalPlane import findFullFocalPlane
from exploreRaft import exploreRaft
from exploreFocalPlane import exploreFocalPlane
import argparse

"""Helper tools to fetch Camera EO Test image files."""


class get_EO_analysis_files():
    """
    get_EO_analysis_files:

    Purpose:

    Query the eTraveler database for associated image files It attempts to simplify the user inputs by
    abstracting out the details of what traveler and test steps were run.

    As such, it is limited to the 'standard' travelers. These are stable at BNL, but not necessarily so at
    SLAC for I&T.

    Example usage:

        g = get_EO_analysis_files(db=args.db, server=args.eTserver)
        files_list = g.get_files(run=args.run, testName=args.test_type, FType="fits",
                                 imgtype=args.imgtype)
    """

    def __init__(self, db='Prod', server='Prod', appSuffix=None, slot_or_ccd='slot'):
        """
        __init__

         Inputs:
            db: eTraveler database to use. Choices are Prod or Dev (case matters)
            server: eTraveler server to use. Choices are Prod or Dev
            slot_or_ccd: key results off slot or CCD name
        """
        self.slot_or_ccd = slot_or_ccd
        self.db = db
        self.ccd_slots = ["S00", "S01", "S02", "S10", "S11", "S12", "S20", "S21", "S22"]

        if server == 'Prod':
            pS = True
        else:
            pS = False
        self.connect = Connection(operator='richard', db=db, exp='LSST-CAMERA', prodServer=pS)

        self.eFP = exploreFocalPlane(db=db, prodServer=server)
        self.eR = exploreRaft(db=db, prodServer=server)
        self.fCCD = findCCD(db=db, prodServer=server, mirrorName="", testName="", run=0, sensorId="")
        self.f_FP = findFullFocalPlane(prodServer=server)

    def get_files(self, FType=None, testName=None, run=None, imgtype=None, matchstr=None):
        """
        get_files:

        Inputs:

            FType: output file type (eg fits)
            testName: step name of test, eg fe55_raft_acq
            run: desired run number
            imgtype: (Optional) use Catalog metadata to select image type, eg BIAS
            matchstr: (Optional) include only those files that include this string

        Output:
            ccd_dict: dictionary of lists of files  keyed on slot or CCD name
            or raft_dict : dict by raft of dict of list of files, both keyed on slot names
        """
        data = self.connect.getRunResults(run=run, stepName=testName)
        self.run_sum = self.connect.getRunSummary(run=run)
        when = self.run_sum['begin']

        mirrorName = self.deduce_mirror(run=run)

        device = data['experimentSN']
        dev_list = []
        ccd_dict = {}
        raft_dict = {}

        idx = 0
        if self.slot_or_ccd == 'ccd':
            idx = 0
        else:
            idx = 1

        if imgtype is not None:
            imgtype = "IMGTYPE=='" + imgtype + "'"

        if 'CRYO' in device.upper():

            files = self.f_FP.find(run=run, testName=testName, FType=FType)

            for f in files:
                if matchstr is not None:
                    if f.find(matchstr) < 0:
                        continue

                parse_path = f.split("/")
                fn = parse_path[-1].split(".")[0]
                fn_split = fn.split("_")
                ccd_slot = fn_split[-1]
                raft_slot = fn_split[-2]

                r = raft_dict.setdefault(raft_slot, {})
                c = r.setdefault(ccd_slot, [])
                c.append(f)

            return raft_dict

        else:
            if 'RTM' in device:
                ccd_list = self.eR.raftContents(raftName=device, when=when)
                for ccd in ccd_list:
                    dev_list.append(ccd)
            else:
                dev_list = [[device, 0, 0]]
                self.slot_or_ccd = 'ccd'

            for ccd in dev_list:
                filelist = self.fCCD.find(mirrorName=mirrorName, FType=FType,
                                          XtraOpts=imgtype, run=run,
                                          testName=testName, sensorId=ccd[0])
                matchlist = []
                for f in filelist:
                    if matchstr is not None:
                        if f.find(matchstr) < 0 or f.find(ccd[0]) < 0:
                            continue
                    matchlist.append(f)
                ccd_dict[ccd[idx]] = matchlist
            return ccd_dict

    def deduce_mirror(self, run=None):
        """
        deduce_mirror: Given the run number, figure out which Data Catalog mirror its data is registered in
        """
        mirrorName = 'INT-prod'

        if "Integration" in self.run_sum['subsystem']:
            if self.db == 'Prod':
                mirrorName = "INT-prod"
            else:
                mirrorName = "INT-test"
        else:
            if self.db == 'Prod':
                if self.run_sum['travelerName'] == "SR-EOT-02":
                    mirrorName = 'vendorCopy-prod'
                else:
                    mirrorName = "BNL-prod"
            else:
                if self.run_sum['travelerName'] == "SR-EOT-02":
                    mirrorName = 'vendorCopy-test'
                else:
                    mirrorName = "BNL-test"

        return mirrorName


if __name__ == "__main__":
    # Command line arguments
    parser = argparse.ArgumentParser(description='Find EO analysis test results.')

    #   The following are 'convenience options' which could also be specified in the filter string
    parser.add_argument('-r', '--run', default=None, help="run number (default=%(default)s)")
    parser.add_argument('-t', '--test_type', default=None, help="test type (default=%(default)s)")
    parser.add_argument('-d', '--db', default='Prod', help="eT database (default=%(default)s)")
    parser.add_argument('-e', '--eTserver', default='Prod', help="eTraveler server (default=%(default)s)")
    parser.add_argument('-i', '--imgtype', default=None, help="image type (eg BIAS) (default=%(default)s)")
    parser.add_argument('--appSuffix', '--appSuffix', default='jrb',
                        help="eTraveler server (default=%(default)s)")
    args = parser.parse_args()

    g = get_EO_analysis_files(db=args.db, server=args.eTserver)
    files_list = g.get_files(run=args.run, testName=args.test_type, FType="fits",
                             imgtype=args.imgtype)
    print(files_list)
