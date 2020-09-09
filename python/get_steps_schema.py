from __future__ import print_function
from eTraveler.clientAPI.connection import Connection
import argparse
from collections import OrderedDict


class get_steps_schema:
    def __init__(self, db="Prod", eTserver="Prod"):

        self.eTserver = eTserver
        self.db = db

        self.runData = None

        if self.eTserver == 'Prod':
            pS = True
        else:
            pS = False

        self.connect = Connection(
            operator='richard',
            db=self.db,
            exp='LSST-CAMERA',
            prodServer=pS)

    def get(self, run=None):

        if run is None:
            print('Error: missing run number')
            raise ValueError

        self.runData = self.connect.getRunResults(run=run)

        return self.runData

    def get_test_info(self, runData=None):

        if runData is None:
            r = self.runData
        else:
            r = runData

        self.test_dict = OrderedDict()

        for steps in r["steps"]:
            if "acq" in steps:
                continue
            schema_list = r["steps"][steps]

            for schema in schema_list:
                if "info" in schema or "versions" in schema:
                    continue

                test_list = schema_list[schema][0]
                for item in test_list:
                    if 'amp' in item or "slot" in item or "raft" in item or "sensor" in item \
                            or "schema" in item or "job" in item or "detections" in item or \
                            "subset" in item or "file" in item or "host" in item or "wavelength" in item:
                        continue

                    self.test_dict[item] = [steps, schema]

        return self.test_dict


if __name__ == "__main__":

    # Command line arguments
    parser = argparse.ArgumentParser(
        description='Query given eTraveler run for available steps and schema names.')
    # The following are 'convenience options' which could also be specified in
    # the filter string
    parser.add_argument(
        '-r',
        '--run',
        default="6774D",
        help="(required raft run number (default=%(default)s)")
    parser.add_argument(
        '-d',
        '--db',
        default='Prod',
        help="database to use (default=%(default)s)")
    parser.add_argument(
        '-e',
        '--eTserver',
        default='Prod',
        help="eTraveler server (default=%(default)s)")

    parser.add_argument(
        '--appSuffix',
        default='jrb',
        help="separate app instance, dash should not be prepended ")
    args = parser.parse_args()

    print('Discover step and schema names for run ', args.run)

    get = get_steps_schema(db=args.db, eTserver=args.eTserver)

    returnData = get.get(run=str(args.run))
    test_list = get.get_test_info()

    print("available tests: \n", test_list)

    print(len(returnData["steps"]), " steps found in run ", args.run)
    for step in returnData['steps']:
        stepDict = returnData['steps'][step]
        print('\n Step ', step, '\n')

        for schemaList in stepDict:
            print(schemaList)
