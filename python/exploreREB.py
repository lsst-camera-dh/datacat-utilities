from eTraveler.clientAPI.connection import Connection
import argparse


class exploreREB():

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

    def REBContents(self, REBName=None):
        kwds = {'experimentSN': REBName, 'htype': 'LCA-13574', 'noBatched': 'true'}

        response = self.connect.getHardwareHierarchy(**kwds)

# LCA-11721 is the ASPIC.

        aspic_list = []
        for row in response:
            kid = row['child_experimentSN']
            if '11721' in kid:
                aspic_list.append((kid, row['slotName']))

        return aspic_list

    def ASPIC_parent(self, ASPIC_name=None, htype='LCA-11721'):

        # now find ASPIC for a REB

        kwds = {'experimentSN': ASPIC_name, 'htype': htype, 'noBatched': 'true'}

        response = self.connect.getContainingHardware(**kwds)

        for child in response:
            if '13574' in child['parent_experimentSN']:
                parentREB = child['parent_experimentSN']
                break

        return parentREB


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Find archived data in the LSST  data Catalog. '
                    'These include CCD test stand and vendor data files.')

    # The following are 'convenience options' which could also be specified in
    # the filter string
    parser.add_argument('-r', '--reb', default="LCA-13574-017",
                        help="reb serial number")
    args = parser.parse_args()

    REBName = args.reb

    eR = exploreREB()

    aspic_list = eR.REBContents(REBName)

    print aspic_list