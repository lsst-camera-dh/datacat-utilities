from  eTraveler.clientAPI.connection import Connection
import argparse


## Command line arguments
parser = argparse.ArgumentParser(description='Query given eTraveler run for available steps and schema names.')

##   The following are 'convenience options' which could also be specified in the filter string
parser.add_argument('-r', '--run', default=None,help="(required raft run number (default=%(default)s)")
parser.add_argument('-d','--db',default='Prod',help="database to use (default=%(default)s)")
parser.add_argument('-e','--eTserver',default='Dev',help="eTraveler server (default=%(default)s)")
parser.add_argument('--appSuffix', default='jrb',help="separate app instance, dash should not be prepended ")
args = parser.parse_args()

print 'Discover step and schema names for run ', args.run
if args.run == None:
    print 'Error: missing run number'
    raise ValueError

if args.eTserver == 'Prod': pS = True
else: pS = False
    
if args.appSuffix != '':
    appSuffix = '-' + args.appSuffix

print 'args. appSuffix, appSuffix = ', args.appSuffix, appSuffix
    
connect = Connection(operator='richard', db=args.db, exp='LSST-CAMERA', prodServer=pS, appSuffix=appSuffix)

returnData  = connect.getRunResults(run=args.run)
    
for step in returnData['steps']:
        stepDict = returnData['steps'][step]
        print '\n Step ', step, '\n'

        for schemaList in stepDict:
            print schemaList




    

