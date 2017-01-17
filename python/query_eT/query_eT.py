import sqlalchemy
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import describe
import collections
import operator
import os

class query_eT():

    def __init__(self, schemaName=None, valueName=None, ccdType=None,dataType=None,resultType='FloatResultHarnessed',resultName='value', device=None, dbConnectFile='db_connect.txt'):
        self.schemaName = schemaName
        self.valueName = valueName
        self.ccdType = ccdType
        self.dataType = dataType
        self.resultType = resultType
        self.resultName = resultName
        self.device = device
        self.dbConnectFile = dbConnectFile

    def setParams(self, schemaName=None, valueName=None, ccdType=None,dataType=None,resultType=None, resultName=None, device=None, dbConnectFile=None):
        if schemaName is not None: self.schemaName = schemaName
        if valueName is not None:self.valueName = valueName
        if ccdType is not None:self.ccdType = ccdType
        if dataType is not None:self.dataType = dataType
        if resultType is not None:self.resultType = resultType
        if resultName is not None:self.resultName = resultName
        if device is not None:self.device = device
        if dbConnectFile is not None: self.dbConnectFile = dbConnectFile

    def connectDB(self):

        kwds = {}
        with open(self.dbConnectFile) as f:
            for line in f:
                (key, val) = line.split()
                kwds[key] = val


        # Create a new mysql connection object.
        db_url = sqlalchemy.engine.url.URL('mysql+mysqldb', **kwds)
        engine = sqlalchemy.create_engine(db_url)
        mysql_connection = engine.raw_connection()

        print 'connected to host' , kwds['host']

        cursor = mysql_connection.cursor()

        return engine

    def queryHardwareRegDate(self,engine):

        sql = 'select lsstId, manufactureDate from Hardware where upper(manufacturer) = "' + self.ccdType + '" order by manufactureDate asc'

        print sql


        result = engine.execute(sql)
        ccd = collections.OrderedDict()

        # grab the query data,

        for row in result:
            ccd[row[0]] = row[1]

        return ccd


    def queryResultsDB(self,engine):

        dev_query = ''
        if self.device is not None: dev_query = ' and hw.lsstId = ' + self.device


#        sqlVendor = "select hw.lsstId, res.activityId, act.rootActivityId, res." + self.resultName + ", res.schemaInstance from " + self.resultType + " res join Activity act on res.activityId=act.id JOIN Hardware hw ON act.hardwareId=hw.id join Process pr on act.processId=pr.id where lower(res.schemaName) ='" + self.schemaName + "' and res.name= '" + self.valueName + dev_query + "' order by res.activityId asc"
        sqlVendor = "select hw.lsstId, res.activityId, act.rootActivityId, res." + self.resultName + ", res.schemaInstance from " + self.resultType + " res join Activity act on res.activityId=act.id JOIN Hardware hw ON act.hardwareId=hw.id join Process pr on act.processId=pr.id where res.name ='" + self.valueName +  dev_query + "' order by res.activityId asc"

        sql = sqlVendor

        print sql


        result = engine.execute(sql)

        id = []
        ccd = collections.OrderedDict()

        parent = {}
        query = []

        # grab the query data, find the max parent id for each sensor (ie most recent run) and copy the result cursor into the query list

        for row in result:
            query.append([row['lsstId'], row['activityId'], row['rootActivityId'], row['value'], row['schemaInstance']])

        print 'len(query) = ', len(query)

        # get the parent traveler's id and name

        sqlParent = "select hw.id, hw.lsstId, act.id parId, pr.name from Activity act join Hardware hw on act.hardwareId=hw.id join Process pr on act.processId=pr.id join ActivityStatusHistory statusHist on act.id=statusHist.activityId where  pr.name='" + self.dataType + "'"

        print sqlParent

        resultParent = engine.execute(sqlParent)

        # only take data from the most recent run of the traveler

        parentAct = {}

        for row in resultParent:
            parentId = parent.setdefault(row['lsstId'])
            parent[row['lsstId']] = row['parId']

        resultParent.close()

        for row in query:
            if self.ccdType in row[0] and row[0] in parent:
                if parent[row[0]] == row[2]:
                    if row[0] not in ccd.keys():
                        ccd[row[0]] = []
                    value = row[3]
                    if self.resultType == 'FilepathResultHarnessed': value = os.path.split(value)
                    ccd[row[0]].append([value,row[4]])

# sort the lists per key by the instance number as they are not returned in order

        for key in ccd:
            ccd[key] = sorted(ccd[key],key=operator.itemgetter(1))

        return ccd

    

    def queryCatalogVirtualPaths(self,engine):

        self.resultType = 'FilepathResultHarnessed'
        self.resultName = 'virtualPath'

        dev_query = ''
        if self.device is not None: dev_query = "' and hw.lsstId = '" + self.device

        
        sqlVendor = "select hw.lsstId, res.activityId, act.rootActivityId, res." + self.resultName + ", res.schemaInstance from " + self.resultType + " res join Activity act on res.activityId=act.id JOIN StringResultHarnessed fl  on res.activityId=fl.activityId JOIN Hardware hw ON act.hardwareId=hw.id join Process pr on act.processId=pr.id where lower(fl.schemaName) ='" + self.schemaName + dev_query + "' order by res.activityId asc"

        sql = sqlVendor

        print sql


        result = engine.execute(sql)

        id = []
        ccd = collections.OrderedDict()

        parent = {}
        query = []

        # grab the query data, find the max parent id for each sensor (ie most recent run) and copy the result cursor into the query list

        for row in result:
            query.append([row['lsstId'], row['activityId'], row['rootActivityId'], row['virtualPath'], row['schemaInstance']])

        print 'len(query) = ', len(query)

        # get the parent traveler's id and name

        sqlParent = "select hw.id, hw.lsstId, act.id parId, pr.name from Activity act join Hardware hw on act.hardwareId=hw.id join Process pr on act.processId=pr.id join ActivityStatusHistory statusHist on act.id=statusHist.activityId where  pr.name='" + self.dataType + "'"

        print sqlParent

        resultParent = engine.execute(sqlParent)

        # only take data from the most recent run of the traveler

        parentAct = {}

        for row in resultParent:
            parentId = parent.setdefault(row['lsstId'])
            parent[row['lsstId']] = row['parId']

        resultParent.close()

        for row in query:
            if self.ccdType in row[0] and row[0] in parent:
                if parent[row[0]] == row[2]:
                    if row[0] not in ccd.keys():
                        ccd[row[0]] = []
                    value = row[3]
                    if self.resultType == 'FilepathResultHarnessed': value, junk = os.path.split(value)
                    value += '/'
                    ccd[row[0]].append([value,row[4]])

# sort the lists per key by the instance number as they are not returned in order

        for key in ccd:
            ccd[key] = sorted(ccd[key],key=operator.itemgetter(1))

# ccd is a dict, with CCD as key, and each key has a list of pairs - value and instance number (eg amp #)

        return ccd



if __name__ == "__main__":
    
    schemaName = 'read_noise'
    valueName = 'read_noise'
    #ccdType = 'ITL-3800C'
    ccdType = 'E2V'
    dataType = 'SR-EOT-1'

    title = valueName + '-' + dataType + '-' + ccdType

    eT = query_eT(schemaName=schemaName, valueName=valueName, ccdType=ccdType, dataType=dataType)

    engine = eT.connectDB()

    ccd  = eT.queryResultsDB(engine)


    data = []
    medians = []
    for key in ccd.keys():
        ampVal = ccd[key]
        vals = [item[0] for item in ampVal]
        [data.append(item[0]) for item in ampVal]
        medians.append(np.median(vals))

    # define figure size parameters to make figures larger than default
    figwidth=10
    figheight=10

    fig1=plt.figure(1)

    plt.hist(data,bins=20)

    hist_desc = describe(data)
    fmt_fields = ('nobs', 'minmax', 'mean', 'variance', 'skewness', 'kurtosis')
    fmt = '\n'.join([f + " : {" + f + "}" for f in fmt_fields])

    plt.figtext(0.6, 0.6, fmt.format(**hist_desc.__dict__),size='small')

    plt.xlabel(valueName)

    plt.title(title)
    plt.savefig(title + '.png')
    plt.close()


#    print ccd.items()

    fig2=plt.figure(2,[figwidth,figheight])

    print 'len id ', len(ccd.keys()), ' len medians ', len(medians), ' len data ', len(data)

    plt.bar(range(len(medians)),medians)
    plt.xticks(range(len(medians)),ccd.keys(),size='small',rotation='vertical')
    plt.ylabel('Median ' + valueName)
    plt.title(title)
    plt.savefig('Median-' + title + '.png')
