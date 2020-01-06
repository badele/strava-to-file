#!/bin/python
# -*- coding: UTF-8 -*-

# cd exported strava activities
# python summarize.py | jq -S


import os
import sys
import csv
import json
import hashlib
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

RIDE = ['Ride','Sortie à vélo']

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--destination", required=True,
	help="destination")
ap.add_argument("-u", "--user", required=True,
	help="username")
args = vars(ap.parse_args())


# def md5(filename):
#     hash_md5 = hashlib.md5()
#     with open(filename, "rb") as f:
#         for chunk in iter(lambda: f.read(4096), b""):
#             hash_md5.update(chunk)
#     return hash_md5.hexdigest()

# Crete hashfolder
home = str(Path.home())
RUNNING_PATH = os.path.dirname(os.path.realpath(__file__))

def readcsv(filename):
    with open(filename, 'rt') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')

        lines = []
        for row in reader:
            lines.append (row)

    return lines

# Create traces folder
rootfolder = args["destination"]
user = args["user"]
destfolder = "%(rootfolder)s/%(user)s" % locals()
if not os.path.exists(destfolder):
    os.makedirs(destfolder)

noconverted = []
nbrides = 0
traces = readcsv('activities.csv')
for row in traces:
    (id,date,name,activity,description,elapsed_time,distance,effort_measurement,transport,material,origfilename) = row

    if activity not in RIDE:
        continue

    nbrides += 1
    if os.path.exists(origfilename):

        filename = origfilename.replace("activities/","")
        filename, ext = os.path.splitext(filename)

        destfilename = "%(destfolder)s/%(filename)s_converted_trace.gpx" % locals()
        destgziped = "%(destfilename)s.gz" % locals()
        if not os.path.exists(destgziped):
            if origfilename.rfind('.fit') > 0:
                converter="convert_fit_to_gpx.sh"
            elif origfilename.rfind('.tcx') > 0:
                converter="convert_tcx_to_gpx.sh"
            elif origfilename.rfind('.gpx') > 0:
                converter="convert_gpx_to_gpx.sh"
            else:
                print ("Please add support for %(origfilename)s" % locals())
                continue

            # Convert
            print("Convert %(filename)s%(ext)s to %(destgziped)s" % locals())
            cmd = "%(RUNNING_PATH)s/%(converter)s %(origfilename)s %(destfilename)s" % locals()
            print (cmd)

            subprocess.call(cmd.split())

        if not os.path.exists(destgziped):
            noconverted.append(filename)
sys.exit()
print ("This files bollow, cannot be convert")
print ("====================================")
for line in noconverted:
    print (line)
print ("====================================")
print ("%s files cannot be convert on %s" % (len(noconverted),nbrides))
