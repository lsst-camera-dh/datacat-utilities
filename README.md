# datacat-utilities
Tools for using/reading/interacting with the LSST Data Catalog

## Prerequisites
- python >= 2.7.10 with mysql-python
- [datacat](https://gist.github.com/brianv0/c1ef2269e87060647fa3) >= 0.4
- eTraveler API

## Setup for use at SLAC
DATACAT_INSTDIR points to datacat-utilities installation directory

```export PATH=/nfs/farm/g/lsst/u1/software/redhat6-x86_64-64bit-gcc44/anaconda/2.5.0/bin:$PATH```

```export PYTOHNPATH=$DATACAT_INSTDIR/lsst_camera_datacat_util:/nfs/farm/g/lsst/u/jrb/jrbTestJH/devSrc/fetchHarnessed-sandbox-stable:/u/ey/richard/LSST/eT/datacat/0.4/lib:$PYTHONPATH```
