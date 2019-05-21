from __future__ import print_function
import argparse
from eTraveler.clientAPI.connection import Connection


class exploreRun():
    def __init__(self, db='Prod', prodServer='Prod', appSuffix=''):

        if prodServer == 'Prod':
            pS = True
        else:
            pS = False

        self.connect = Connection(
            operator='richard',
            db=db,
            exp='LSST-CAMERA',
            prodServer=pS,
            appSuffix=appSuffix)

    def hardware_sn(self, run):
        run_info = self.connect.getRunSummary(run=run)
        return run_info['experimentSN']

    
    def slot_raft_map(self, run):
        run_info = self.connect.getRunSummary(run=run)
        kwds = {'experimentSN': run_info['experimentSN'],
                'htype': 'LCA-10134_Cryostat',
                'noBatched': 'true',
                'timestamp': run_info['begin']}
        response = self.connect.getHardwareHierarchy(**kwds)
        raft_list = []
        
        for ind in response:
            raft = ind['child_experimentSN']
            # ignore mechanical rafts
            if 'MTR' in raft or ind["child_hardwareTypeName"] != "LCA-11021_RTM":
                continue
            slot = ind['slotName']
            # kludge for first cryo definition with slot names as BayXY, not RXY
            if 'Bay' in slot:
                slot = slot.replace("Bay", "R")

            if ind['parent_experimentSN'] == parentName:
                raft_list.append([raft, slot])
        return response


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Find archived data in the LSST  data Catalog. '
                    'These include CCD test stand and vendor data files.')

    # The following are 'convenience options' which could also be specified in
    # the filter string
    parser.add_argument('--run', default=None,
                        help="Run number")
    parser.add_argument('-d', '--db', default="Prod",
                        help="eT database")
    args = parser.parse_args()

    eR = exploreRun(db=args.db)
    htype = eR.hardware_type(args.run)
    print(htype)
