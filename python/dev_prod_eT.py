from __future__ import print_function

from exploreFocalPlane import exploreFocalPlane
from exploreRaft import exploreRaft
from exploreRun import exploreRun
from findCCD import findCCD
from eTraveler.clientAPI.connection import Connection

"""
Helper tool to ease use of dev vs prod eTraveler databases.

Usage:

from dev_prod_eT import dev_prod_eT

t = dev_prod_eT()

t.add_app("Connection")

run = 10517
prod_eT = t.use_app("Connection", "Prod")

"""


class dev_prod_eT():

    def __init__(self):

        self.app_map = {}

    def add_app(self, app_name=None):

        a = self.app_map.setdefault(app_name, {})

        mod = globals()[app_name]
        kwargs = {"db": "Prod"}
        if app_name == "Connection":
            kwargs["operator"] = "richard"
        elif app_name == "findCCD":
            kwargs["run"] = 0
            kwargs["sensorId"] = ""
            kwargs["testName"] = ""
            kwargs["mirrorName"] = ""

        self.app_map[app_name]["Prod"] = mod(**kwargs)

        kwargs["db"] = "Dev"
        self.app_map[app_name]["Dev"] = mod(**kwargs)

    def use_app(self, app_name=None, mode=None):

        return self.app_map[app_name][mode]

    def set_db(self, run=None):

        db = "Prod"
        if type(run) == str:
            if "D" in run.upper():
                db = "Dev"

        return db
