#!/bin/python
# -*- coding: UTF-8 -*-

# cd exported strava activities
# python summarize.py | jq -S

import csv
import json
import argparse
from datetime import datetime

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from tabulate import tabulate

matplotlib.style.use('ggplot')


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--destination", required=True,
	help="destination")
ap.add_argument("-u", "--user", required=True,
	help="username")
args = vars(ap.parse_args())

pda = pd.read_csv('activities.csv',parse_dates=['date']) # ,index_col='date')
pda['distance'] = pda['distance'] / 1000.0
pda['year'] = pda.date.dt.year.astype(str)
pda['month'] = pda.date.dt.month.astype(str).apply(lambda x: x.zfill(2))
pda['week'] = pda.date.dt.week.astype(str)
pda['year-month'] = pda['year'] + "-" + pda['month']


cyear = pd.crosstab(index=pda['year'], columns=pda['type'],values=pda['distance'],aggfunc=['sum'],margins=True,margins_name="Total").fillna(0).round(1)
cmonth = pd.crosstab(index=pda['year-month'], columns=pda['type'],values=pda['distance'],aggfunc=['sum']).fillna(0).round(1)


# Convert to markdown
cyear = cyear.xs('sum', axis=1, drop_level=True)
cmonth = cmonth.xs('sum', axis=1, drop_level=True)
print(tabulate(cyear, tablefmt="pipe", headers="keys"))

with open('/tmp/activity.html', 'w') as fw:
    cyear.to_html(fw)

gmonth = pda.groupby(['year-month','type']).sum().reset_index()
pivot_month = gmonth.pivot(index='year-month', columns='type', values='distance')
print(gmonth)
print(pivot_month)

colors = ["#006D2C", "#31A354","#74C476"]
cmonth.plot.bar(stacked=True,figsize=(10,7))
plt.show()