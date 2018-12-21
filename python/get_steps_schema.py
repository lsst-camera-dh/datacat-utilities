from __future__ import print_function
from eTraveler.clientAPI.connection import Connection
import argparse


class get_steps_schema:
    def __init__(self, db="Prod", eTserver="Prod", appSuffix=""):

        self.eTserver = eTserver
        self.db = db
        self.appSuffix = appSuffix

        if self.eTserver == 'Prod':
            pS = True
        else:
            pS = False

        if self.appSuffix != "":
            appSuffix = '-' + self.appSuffix

        self.connect = Connection(
            operator='richard',
            db=self.db,
            exp='LSST-CAMERA',
            prodServer=pS,
            appSuffix=appSuffix)

    def get(self, run=None):

        if run is None:
            print ('Error: missing run number')
            raise ValueError

        returnData = self.connect.getRunResults(run=run)

        return returnData


if __name__ == "__main__":

    # Command line arguments
    parser = argparse.ArgumentParser(
        description='Query given eTraveler run for available steps and schema names.')
    # The following are 'convenience options' which could also be specified in
    # the filter string
    parser.add_argument(
        '-r',
        '--run',
        default=7983,
        help="(required raft run number (default=%(default)s)")
    parser.add_argument(
        '-d',
        '--db',
        default='Prod',
        help="database to use (default=%(default)s)")
    parser.add_argument(
        '-e',
        '--eTserver',
        default='Dev',
        help="eTraveler server (default=%(default)s)")

    parser.add_argument(
        '--appSuffix',
        default='jrb',
        help="separate app instance, dash should not be prepended ")
    args = parser.parse_args()

    print ('Discover step and schema names for run ', args.run)

    get = get_steps_schema(db=args.db, eTserver=args.eTserver, appSuffix=args.appSuffix)

    returnData = get.get(run=str(args.run))

    print (len(returnData["steps"]), " steps found in run ", args.run)
    for step in returnData['steps']:
        stepDict = returnData['steps'][step]
        print ('\n Step ', step, '\n')

        for schemaList in stepDict:
            print (schemaList)
