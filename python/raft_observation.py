from exploreRaft import exploreRaft
from eTraveler.clientAPI.connection import Connection
from findCCD import findCCD
import os


class raft_observation():

    def __init__(self, run=None, step=None, imgtype=None,
                 db='Prod', prodServer='Dev', appSuffix='-jrb', site ='slac.lca.archive'):

        if prodServer == 'Prod':
            pS = True
        else:
            pS = False

        self.db = db
        self.prodServer = prodServer
        self.appSuffix = appSuffix
        self.site = site

        self.connect = Connection(
            operator='richard',
            db=db,
            exp='LSST-CAMERA',
            prodServer=pS,
            appSuffix=appSuffix,
            debug=False)

        self.run = run

        self.step = step
        self.imgtype = imgtype

        rsp = self.connect.getRunSummary(run=self.run)
        self.raft = rsp['experimentSN']


    def find(self, imgtype=None):

        eR = exploreRaft(db=self.db, prodServer=self.prodServer, appSuffix=self.appSuffix)
        ccd_list = eR.raftContents(self.raft)
        obs_dict = {}

        XtraOpts = ''
        if self.imgtype is not None:
            XtraOpts = 'IMGTYPE=="' + self.imgtype + '"'

        for row in ccd_list:
            ccd = str(row[0])

            self.fCCD = findCCD(
                FType='fits',
                testName=self.step,
                sensorId=ccd,
                run=str(
                    self.run),
                db = self.db,
                prodServer = self.prodServer,
                appSuffix = self.appSuffix,
                site=self.site,
                XtraOpts = XtraOpts
                )
            files = self.fCCD.find()

            for f in files:
                # grab the timestamp from the end of the filename
                name_split = os.path.splitext(os.path.basename(f).split('_')[-1])[0]
                if name_split not in obs_dict:
                    obs_dict[name_split] = []
                obs_dict[name_split].append(f)

        return obs_dict


if __name__ == "__main__":

    rO = raft_observation(run=4963, step='fe55_raft_acq', imgtype="BIAS", db='Dev', site='BNL',prodServer='Dev', appSuffix='-jrb')

    obs_dict = rO.find()
    print obs_dict
