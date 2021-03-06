from __future__ import print_function
from eTraveler.clientAPI.connection import Connection
import argparse


class exploreFocalPlane:

    def __init__(self, db='Prod', prodServer='Prod', appSuffix=''):

        self.SR_htype = "LCA-11021_RTM"
        self.CR_htype = "LCA-10692_CRTM"
        self.raft_types = [self.SR_htype, self.CR_htype]

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

    def focalPlaneContents(self, parentName="LCA-10134_Cryostat-0001",
                           htype='LCA-10134_Cryostat', when=None, run=None):

        # when format: %Y-%m-%dT%H:%M:%S.%f  eg: 2016-11-11T04:24:35.0
        kwds = {'experimentSN': parentName, 'htype': htype, 'noBatched': 'true'}
        if run is not None:
            run_info = self.connect.getRunSummary(run=run)
            kwds['timestamp'] = run_info['begin']
        elif when is not None:
            kwds['timestamp'] = when

        response = self.connect.getHardwareHierarchy(**kwds)

        raft_list = []

        for ind in response:
            raft = ind['child_experimentSN']
            # ignore mechanical rafts
            if 'MTR' in raft or ind["child_hardwareTypeName"] not in self.raft_types:
                continue
            slot = ind['slotName']
            # kludge for first cryo definition with slot names as BayXY, not RXY
            if 'Bay' in slot:
                slot = slot.replace("Bay", "R")

            if ind['parent_experimentSN'] == parentName:
                raft_list.append([raft, slot])

        return raft_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Find archived data in the LSST  data Catalog. '
                    'These include CCD test stand and vendor data files.')

    # The following are 'convenience options' which could also be specified in
    # the filter string
    parser.add_argument('-f', '--focalPlane', default="LCA-10134_Cryostat",
                        help="focal plane type")
    parser.add_argument('-i', '--fpInstance', default="LCA-10134_Cryostat-0001",
                        help="focal plane type")
    parser.add_argument('-r', '--run', default=None,
                        help="run number")
    parser.add_argument('-d', '--db', default="Prod",
                        help="eT database Dev or Prod")
    args = parser.parse_args()

    eFP = exploreFocalPlane(db=args.db)

    kwds = {"parentName": args.fpInstance, "htype": args.focalPlane}
    if args.run is not None:
        kwds["run"] = args.run

    rafts = eFP.focalPlaneContents(**kwds)

    print(rafts)
