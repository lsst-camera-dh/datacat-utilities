# datacat-utilities
Tools for using/reading/interacting with the LSST Data Catalog

- exploreRaft - find CCD, REB content of raft. Find parents of CCD, REB
- exploreREB - find ASPIC content of raft. Find parent REB of ASPIC
- findCCD - find files associated with eTraveler tests, returning file lists for SLAC or BNL, specified by run and CCD.
- get_steps_schema - list the traveler steps and schema for a given test, specified by run

2017-04-25: currently one must use the dev eTraveler server and '-jrb' eTraveler instance on that server. That will be rectified once the client API goes fully prod.

## Prerequisites
- python >= 2.7.10 with mysql-python
- [datacat](https://gist.github.com/brianv0/c1ef2269e87060647fa3) >= 0.4
- eTraveler-clientAPI repo. Point your PYTHONPATH at the contained python/ directory

## Setup for use at SLAC
https://confluence.slac.stanford.edu/display/LSSTCAM/Finding+CCD+Acceptance+Data
