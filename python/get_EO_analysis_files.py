"""Helper tools to fetch Camera EO Test image files."""

from eTraveler.clientAPI.connection import Connection
from findCCD import findCCD
from exploreRaft import exploreRaft
import argparse


class get_EO_analysis_files():

    def __init__(self, db='Prod', server='Prod', appSuffix=None, slot_or_ccd='slot'):

        self.slot_or_ccd = slot_or_ccd
        self.db = db

        if server == 'Prod':
            pS = True
        else:
            pS = False
        self.connect = Connection(operator='richard', db=db, exp='LSST-CAMERA', prodServer=pS)

        self.eR = exploreRaft(db=db, prodServer=pS)
        self.fCCD = findCCD(db=db, prodServer=pS, mirrorName="", testName="", run=0, sensorId="")

    def get_files(self, FType=None, testName=None, run=None, imgtype=None):

        data = self.connect.getRunResults(run=run, stepName=testName)
        self.run_sum = self.connect.getRunSummary(run=run)
        when = self.run_sum['begin']

        mirrorName = self.deduce_mirror(run=run)

        device = data['experimentSN']
        dev_list = []
        ccd_dict = {}
        idx = 0

        if imgtype is not None:
            imgtype = "IMGTYPE=='" + imgtype + "'"

        if 'RTM' in device:
            ccd_list = self.eR.raftContents(raftName=device, when=when)
            if self.slot_or_ccd == 'ccd':
                idx = 0
            else:
                idx = 1
            for ccd in ccd_list:
                dev_list.append(ccd)
        else:
            dev_list = [[device, 0, 0]]
            self.slot_or_ccd = 'ccd'

        for ccd in dev_list:
            ccd_dict[ccd[idx]] = self.fCCD.find(mirrorName=mirrorName, FType=FType,
                                                XtraOpts=imgtype, run=run,
                                                testName=testName, sensorId=ccd[0])

        return ccd_dict

    def deduce_mirror(self, run=None):

        mirrorName = 'INT-prod'

        if "integration" in self.run_sum['subsystem']:
            if self.db == 'Prod':
                mirrorName = "INT-prod"
            else:
                mirrorName = "Int-test"
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
    parser.add_argument('-i', '--imgtype', default='', help="image type (eg BIAS) (default=%(default)s)")
    parser.add_argument('--appSuffix', '--appSuffix', default='jrb',
                        help="eTraveler server (default=%(default)s)")
    args = parser.parse_args()

    g = get_EO_analysis_files(db=args.db, server=args.eTserver)
    files_list = g.get_files(run=args.run, testName=args.test_type, FType="fits",
                             imgtype=args.imgtype)