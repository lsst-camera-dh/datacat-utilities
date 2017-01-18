import argparse
from DataCatalog import *
import subprocess
import shlex
import query_eT


class findCCD():

    def __init__(self, mirrorName='BNL-prod', FType=None, XtraOpts=None, testName=None, CCDType=None, sensorId=None, outputFile=None, dataType=None):

        if None in (mirrorName, testName, sensorId, dataType, CCDType):
            print 'Error: missing input to findCCD'
            raise ValueError
            
        self.mirrorName = mirrorName
        self.FType = FType
	self.XtraOpts = XtraOpts
        self.testName = testName
        self.CCDType = CCDType
        self.sensorId = sensorId
	self.outputFile = outputFile
	self.dataType = dataType

	schemaName =  self.testName
	valueName =  self.testName
	ccdType = self.CCDType
	dataType = self.dataType

	self.eT = query_eT.query_eT(schemaName=schemaName, valueName=valueName, ccdType=ccdType, dataType=dataType, device=self.sensorId)

	self.engine = self.eT.connectDB()




    def find(self):

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

	use_latest_activity = False

	query = ''
	site = args.site
	use_query_eT = True

	if (self.mirrorName == 'BNL-prod' or self.mirrorName == 'BNL-test'):
		site = 'slac.lca.archive'
	
	elif (self.mirrorName == 'vendorCopy-prod' or self.mirrorName == 'vendorCopy-test'):
#		query = "TESTTYPE IS NOT NULL"
		site = "SLAC"
	elif (self.mirrorName == 'vendor-prod'):
		folder = folder + sourceMap[self.mirrorName] + self.CCDType  + '/' + self.sensorId + '/Prod/'
		site = "slac.lca.archive"
		use_query_eT = False
	elif (self.mirrorName == 'vendor-test'):
		folder = folder + sourceMap[self.mirrorName] + self.CCDType  + '/' + self.sensorId + '/Dev/'
		site = "slac.lca.archive"
		use_query_eT = False
	elif (self.mirrorName == 'SAWG-BNL'):
		folder = folder + 'mirror/' + sourceMap[self.mirrorName] + self.CCDType  + '/' + self.sensorId + '/' + self.testName
		use_latest_activity = False
		use_query_eT = False

	if use_query_eT:
		filePaths  = self.eT.queryCatalogVirtualPaths(self.engine)
		folder = filePaths[self.sensorId][0][0]


	print folder

	if self.XtraOpts is not None:
		if query == '':
			query = self.XtraOpts
		else:
			query += "&&" + self.XtraOpts


	datacatalog = DataCatalog(folder=folder, experiment='LSST', site=site, use_newest_subfolder=use_latest_activity)

	datasets = datacatalog.find_datasets(query)
	print "%i datasets found\n" % len(datasets)

	nfiles = 75
	files = []

	for item in datasets.full_paths():
		if (self.FType is None) or (self.FType is not None and item.endswith(self.FType)): 
			files.append(item)

	if args.Print:
		print "File paths for files at %s:" % site
		for item in files:
			print item


## Write file with list of found data files, if requested

	if self.outputFile != None and len(datasets)>0:
		print 'Writing output file ',self.outputFile,'...'
		ofile = open(self.outputFile,'w')
		for line in files:
			ofile.write(line+'\n')
			pass
		ofile.close()
	elif self.outputFile != None:
		print "Result file requested, but no files found"
		pass


	return files


if __name__ == "__main__":

	## Command line arguments
	parser = argparse.ArgumentParser(description='Find archived data in the LSST  data Catalog. These include CCD test stand and vendor data files.')

	##   The following are 'convenience options' which could also be specified in the filter string
	parser.add_argument('-A','--activityId',default=None,help="find data by test activityId")
	parser.add_argument('-s','--sensorID', default=None,help="(metadata) Sensor ID (default=%(default)s)")
	parser.add_argument('-T','--testName', default=None,help="(metadata) test type (default=%(default)s)")
	parser.add_argument('-c','--CCDType', default="ITL",help="(metadata) CCD vendor type (default=%(default)s)")
	parser.add_argument('-S','--site', default="slac.lca.archive",help="File location (default=%(default)s) ")
	parser.add_argument('-F','--FType', default=None,help="File type (default=%(default)s)")
	parser.add_argument('-q','--qType', default=None,help="query type - report or blank (default all) ")
	parser.add_argument('-d','--dataType', default=None,help="test type (SR-EOT-1, etc) ")

	## Limit dataCatalog search to specified parts of the catalog
	parser.add_argument('-m','--mirrorName',default='BNL-prod',help="mirror name to search, i.e. in dataCat /LSST/mirror/<mirrorName> (default=%(default)s)")
	parser.add_argument('-X','--XtraOpts',default=None,help="any extra 'datacat find' options (default=%(default)s)")

	## Output
	parser.add_argument('-o','--outputFile',default=None,help="Output result to specified file (default = %(default)s)")
	parser.add_argument('-a','--displayAll',default=False,action='store_true',help="Display entire result set (default = %(default)s)")
	parser.add_argument('-D','--download',default=False,action='store_true',help="download/ssh files (default=%(default)s)")
	parser.add_argument('-u','--user',default='',help="SLAC unix username for ssh (default=%(default)s)")

	## Verbosity
	parser.add_argument('-p','--Print',default=False,action='store_true',help="print file paths to screen (default=%(default)s)")

	args = parser.parse_args()


	fCCD= findCCD(mirrorName=args.mirrorName, FType=args.FType, XtraOpts=args.XtraOpts, testName=args.testName, CCDType=args.CCDType, sensorId=args.sensorID, outputFile=args.outputFile, dataType=args.dataType )

	files = fCCD.find()

        print files
