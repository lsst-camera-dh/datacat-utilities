from exploreRaft import exploreRaft
from  eTraveler.clientAPI.connection import Connection
from findCCD import findCCD
import os

class raft_observation():

    def __init__(self, run=None, raft=None, step=None, imgtype=None, db='Prod', prodServer='Prod', appSuffix=''):

        if prodServer == 'Prod': pS = True
        else: pS = False

        self.connect = Connection(operator='richard', db=db, exp='LSST-CAMERA', prodServer=pS, appSuffix=appSuffix)

        self.run = run
        self.raft = raft
        self.step = step
        self.imgtype = imgtype

    def find(self):

        eR = exploreRaft()
        ccd_list = eR.raftContents(self.raft)
        obs_dict = {}
        
        XtraOpts = ''
        if self.imgtype is not None:
            XtraOpts = 'IMGTYPE=="' + self.imgtype + '"'

        for row in ccd_list:
            ccd = str(row[0])
           
            fCCD= findCCD(FType='fits', testName=self.step, sensorId=ccd, run= str(self.run), XtraOpts=XtraOpts)
            files = fCCD.find()

            for f in files:
# grab the timestamp from the end of the filename 
                name_split = os.path.splitext(os.path.basename(f).split('_')[-1])[0]
                if name_split not in obs_dict: obs_dict[name_split] = []
                obs_dict[name_split].append(f)

        return obs_dict

    
if __name__ == "__main__":

    raft = 'LCA-11021_RTM-004'

    rO = raft_observation(run=3764, raft=raft, step='fe55_raft_acq', imgtype="BIAS")

    obs_dict = rO.find()
    print obs_dict
