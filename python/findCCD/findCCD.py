import argparse
from DataCatalog import *
import subprocess
import shlex


## Command line arguments
parser = argparse.ArgumentParser(description='Find archived data in the LSST  data Catalog. These include CCD test stand and vendor data files.')

##   The following are 'convenience options' which could also be specified in the filter string
parser.add_argument('-A','--activityId',default="",help="find data by test activityId")
parser.add_argument('-s','--sensorID', default="",help="(metadata) Sensor ID (default=%(default)s)")
parser.add_argument('-T','--TestName', default='',help="(metadata) test type (default=%(default)s)")
parser.add_argument('-c','--CCDType', default="ITL",help="(metadata) CCD vendor type (default=%(default)s)")
parser.add_argument('-S','--site', default="slac.lca.archive",help="File location (default=%(default)s) ")
parser.add_argument('-F','--FType', default='',help="File type (default=%(default)s)")
parser.add_argument('-q','--qType', default='',help="query type - report or blank (default all) ")

## Limit dataCatalog search to specified parts of the catalog
parser.add_argument('-m','--mirrorName',default='BNL-prod',help="mirror name to search, i.e. in dataCat /LSST/mirror/<mirrorName> (default=%(default)s)")
parser.add_argument('-X','--XtraOpts',default='',help="any extra 'datacat find' options (default=%(default)s)")

## Output
parser.add_argument('-o','--outputFile',default=None,help="Output result to specified file (default = %(default)s)")
parser.add_argument('-a','--displayAll',default=False,action='store_true',help="Display entire result set (default = %(default)s)")
parser.add_argument('-D','--download',default=False,action='store_true',help="download/ssh files (default=%(default)s)")
parser.add_argument('-u','--user',default='',help="SLAC unix username for ssh (default=%(default)s)")

## Verbosity
parser.add_argument('-p','--Print',default=False,action='store_true',help="print file paths to screen (default=%(default)s)")

args = parser.parse_args()

sensorID = args.sensorID

sourceMap = {
        'BNL-prod': 'BNL-prod/prod/',
        'BNL-test': 'BNL-test/test/',
        'vendorCopy-prod': 'SLAC-prod/prod/',
        'vendorCopy-test': 'SLAC-test/test/',
        'vendor-prod': 'vendorData/',
        'vendor-test': 'vendorData/',
        'SAWG-BNL': 'BNL-SAWG/SAWG/'
        }
    
folder = '/LSST/'

use_latest_activity = True

query = ''
site = args.site

if (args.mirrorName == 'BNL-prod' or args.mirrorName == 'BNL-test'):
        folder = folder + 'mirror/' + sourceMap[args.mirrorName] + args.CCDType + '-CCD/' + sensorID + '/'
        if args.TestName != '':
                folder += args.TestName + '/v0/'
        else:
                use_latest_activity = False
elif (args.mirrorName == 'vendorCopy-prod' or args.mirrorName == 'vendorCopy-test'):
	query = "TESTTYPE IS NOT NULL"
	site = "SLAC"
        folder = folder + 'mirror/' + sourceMap[args.mirrorName] + args.CCDType + '-CCD/' + sensorID
        if args.TestName != '':
                folder += '/' + args.TestName + '/v0/'
        elif args.qType == '':
                folder += '/vendorIngest/v0/'
        else:
                folder += '/test_report_offline/v0/'
elif (args.mirrorName == 'vendor-prod'):
        folder = folder + sourceMap[args.mirrorName] + args.CCDType  + '/' + sensorID + '/Prod/'
	site = "slac.lca.archive"
elif (args.mirrorName == 'vendor-test'):
        folder = folder + sourceMap[args.mirrorName] + args.CCDType  + '/' + sensorID + '/Dev/'
	site = "slac.lca.archive"
elif (args.mirrorName == 'SAWG-BNL'):
        folder = folder + 'mirror/' + sourceMap[args.mirrorName] + args.CCDType  + '/' + sensorID + '/' + args.TestName
        use_latest_activity = False
        

print folder

if args.XtraOpts != '':
	if query == '':
		query = args.XtraOpts
	else:
		query += "&&" + args.XtraOpts


if args.activityId != "":
	query = "ActivityId==" + args.activityId
	use_latest_activity = False

datacatalog = DataCatalog(folder=folder, experiment='LSST', site=site, use_newest_subfolder=use_latest_activity)

datasets = datacatalog.find_datasets(query)
print "%i datasets found\n" % len(datasets)

nfiles = 75
files = []

for item in datasets.full_paths():
        if (args.FType == '') or (args.FType != '' and item.endswith(args.FType)): 
                files.append(item)

if args.Print:
        print "File paths for files at %s:" % site
        for item in files:
                print item
print

## Write file with list of found data files, if requested
if args.outputFile != None and len(datasets)>0:
        print 'Writing output file ',args.outputFile,'...'
        ofile = open(args.outputFile,'w')
        for line in files:
                ofile.write(line+'\n')
                pass
        ofile.close()
elif args.outputFile != None:
        print "Result file requested, but no files found"
        pass

if args.download and site == 'slac.lca.archive':
        user_host='rhel6-64.slac.stanford.edu'
        if args.user != '':
                user_host = args.user + '@' + user_host
                
        for item in files:
                command = "scp %s:%s %s" \
                          % (user_host, item, '.')
		print command
		cmd = shlex.split(command)
                subprocess.call(cmd)
