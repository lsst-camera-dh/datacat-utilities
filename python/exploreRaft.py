from __future__ import print_function
import argparse
from eTraveler.clientAPI.connection import Connection


class exploreRaft():
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

    def raftContents(self, raftName=None, when=None, run=None):
        kwds = {'experimentSN': raftName, 'htype': 'LCA-11021_RTM', 'noBatched': 'true'}
        if run is not None:
            run_info = self.connect.getRunSummary(run=run)
            kwds['timestamp'] = run_info['begin']
        elif when is not None:
            kwds['timestamp'] = when

        response = self.connect.getHardwareHierarchy(**kwds)

        # LCA-13574 is the REB.

        reb_list = []
        for row in response:
            kid = row['child_experimentSN']
            if '13574' in kid:
                reb_list.append((kid, row['slotName']))

            # match up the CCD to the REB via REB and slot numbering. The CCD in slot
            # Sxy is on REBx. Note that the CCD is actually
            # assembled onto the RSA.

        ccd_list = []
        for child in response:
            # print child['parent_experimentSN'], child['relationshipTypeName'],
            # child['child_experimentSN'], child['slotName']

            rebId = ""
            kid = child['child_experimentSN']
            if 'ITL' in kid.upper() or 'E2V' in kid.upper():
                slotName = child['slotName']
                rebNumber = slotName[1]
                for reb in reb_list:
                    rebLoc = reb[1][3]
                    if rebLoc == rebNumber:
                        rebId = reb[0]
                        break
                ccd_list.append((kid, slotName, rebId))

        return ccd_list

    def raft_type(self, raft=None):
        ccd_list = self.raftContents(raftName=raft)
        if 'ITL' in ccd_list[0][0]:
            type = 'ITL'
        else:
            type = 'e2v'

        return type

    def CCD_parent(self, CCD_name=None, htype='ITL-CCD', when=None, run=None):

        # now find raft for a CCD

        kwds = {'experimentSN': CCD_name, 'htype': htype, 'noBatched': 'true'}

        if run is not None:
            run_info = self.connect.getRunSummary(run=run)
            kwds['timestamp'] = run_info['begin']
        elif when is not None:
            kwds['timestamp'] = when

        # connect = connection.Connection('richard', db='Dev', exp='LSST-CAMERA', prodServer=True)

        response = self.connect.getContainingHardware(**kwds)
        parentRTM = ""

        for child in response:
            if 'RTM' in child['parent_experimentSN']:
                parentRTM = child['parent_experimentSN']
                break

        return parentRTM

    def REB_parent(self, REB_name=None, when=None, run=None):

        # now find raft for a REB

        kwds = {'experimentSN': REB_name, 'htype': 'LCA-13574',
                'noBatched': 'true'}  # need to fix REB htype!
        if run is not None:
            run_info = self.connect.getRunSummary(run=run)
            kwds['timestamp'] = run_info['begin']
        elif when is not None:
            kwds['timestamp'] = when

        response = self.connect.getContainingHardware(**kwds)
        parentRTM = ""

        for child in response:
            if 'RTM' in child['parent_experimentSN']:
                parentRTM = child['parent_experimentSN']
                break

        return parentRTM

    def REB_CCD(self, REB_name=None, when=None, run=None):

        raft = self.REB_parent(REB_name)
        if run is not None:
            run_info = self.connect.getRunSummary(run=run)
            when = run_info['begin']

        ccd_list = self.raftContents(raftName=raft, when=when)

        ccd_in_reb = []
        for ccd in ccd_list:
            if REB_name == ccd[2]:
                ccd_in_reb.append(ccd[0])

        return ccd_in_reb


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Find archived data in the LSST  data Catalog. '
                    'These include CCD test stand and vendor data files.')

    # The following are 'convenience options' which could also be specified in
    # the filter string
    parser.add_argument('-r', '--raft', default="LCA-11021_RTM-005",
                        help="raft serial number")
    parser.add_argument('--run', default=None,
                        help="optional run number")
    parser.add_argument('-d', '--db', default="Prod",
                        help="eT database")
    args = parser.parse_args()

    raftName = args.raft

    eR = exploreRaft(db=args.db)

    if args.run is None:
        ccd_list = eR.raftContents(raftName)
    else:
        ccd_list = eR.raftContents(raftName=raftName, run=args.run)

    print(ccd_list)
