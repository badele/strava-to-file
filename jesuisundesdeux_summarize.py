#!/bin/python
# -*- coding: UTF-8 -*-

import os
import re
import sys
import csv
import json
import locale
import argparse
from datetime import datetime

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from tabulate import tabulate
from matplotlib.ticker import FormatStrFormatter

import locale
import datetime
import dateparser

locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')


matplotlib.style.use('ggplot')
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# https://www.metromobilite.fr/pages/EmissionCO2.html
# https://fr.statista.com/statistiques/486554/consommation-de-carburant-moyenne-voiture-france/
# https://www.spritmonitor.de/fr/detail/244470.html

# Inspired by this spreadsheets
# https://docs.google.com/spreadsheets/d/1WzPupMB-fylNFcQa8tDKhvToyR8rMZ4wGUJvzKXEYZM/pubhtml?gid=999037188

frais_velo = 0
co2 = 123
conso_100km = 5.28
prix_litre = 1.6

LANG="fr"
locale.setlocale(locale.LC_ALL, "fr_FR.UTF-8")

MAXYEAR=2020
RIDE="Sortie à vélo"
KM = [
	"Ride","Run","Workout","Walk","Canoeing","Sortie à vélo","Course à pied","Stand up paddle",
	"Marche","Randonnée","Entraînement","Ski alpin","Raquettes","Escalade","Sortie à vélo électrique"]
M = ["Swim","Natation"]

COLUMNSNAME = {
	'en': {
		"Activity ID": "id",
		"Activity Date": "date",
		"Activity Name": "name",
		"Activity Type": "type",
		"Activity Description": "description",
		"Elapsed Time": "elapsed",
		"Distance": "distance",
		"Relative Effort": "effort",
		"Commute": "commute",
		"Activity Gear": "gear",
		"Filename": "filename",
		},
	'fr': {
		"ID de l'activité": "id",
		"Date de l'activité": "date",
		"Nom de l'activité": "name",
		"Type d'activité": "type",
		"Description de l'activité": "description",
		"Temps écoulé": "elapsed",
		"Distance": "distance",
		"Mesure d'effort": "effort",
		"Déplacement-transport": "commute",
		"Équipement utilisé pour l'activité": "gear",
		"Nom du fichier": "filename",
		},
}

def UpdateReadme(distanceallactivities,summaryallactivities,summaryeconomy,frais_velo,litres,euros,co2,economy):
	if os.path.isdir(f'{folderdest}/{user}'):
		with open(f'{folderdest}/{user}/README_template.md', 'r') as fr:
			content = fr.read()

			content = content.replace('{{DISTANCEALLACTIVITIES}}',str(distanceallactivities))
			content = content.replace('{{SUMMARYALLACTIVITIES}}',summaryallactivities)
			content = content.replace('{{SUMMARYECONOMY}}',summaryeconomy)
			content = content.replace('{{FRAIS}}',frais_velo)
			content = content.replace('{{ECONOMY}}',economy)
			content = content.replace('{{LITRES}}',litres)
			content = content.replace('{{EUROS}}',euros)
			content = content.replace('{{CO2}}',co2)

			with open(f'{folderdest}/{user}/README.md', 'w') as fw:
				fw.write(content)


###########################################################
# Read argument options
###########################################################
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--destination", required=True,
	help="destination")
ap.add_argument("-u", "--user", required=True,
	help="username")
args = vars(ap.parse_args())

folderdest = args['destination']
user = args['user']

# Vérify if template is present
if not os.path.exists(f'{folderdest}/{user}/README_template.md'):
	print (f'{folderdest}/{user}/README_template.md not existing')
	sys.exit(0)

###########################################################
# Read and analyse strava archive
###########################################################
# 13 mai 2019 à 14:45:37
dateparse = lambda x: pd.datetime.strptime(x, '%d %b %Y à %H:%M:%S')
pda = pd.read_csv(
	'activities.csv',
	# parse_dates=[DATENAME[LANG]],
	# date_parser=dateparse
	) # ,index_col='date')

# Rename column
pda = pda.rename(columns=COLUMNSNAME[LANG])

###########################################################
# Datas converssion
###########################################################

for idx,row in pda.iterrows():
	# Convert date
	pda.loc[idx,'date'] = dateparser.parse(pda.loc[idx,'date'])

	# Convert distance unit value
	if  pda.loc[idx,'type'] in M:
		try:
			pda.loc[idx,'distance'] = float(locale.atof(row.distance))/1000
		except:
			pda.loc[idx,'distance'] = float(re.sub('[^0-9]','', row.distance))/1000

	elif pda.loc[idx,'type'] in KM:
		pda.loc[idx,'distance'] = float(locale.atof(row.distance))
	else:
		print(f"Unknow \"{pda.loc[idx,'type']}\" activity, Please define in M or KM array")
		sys.exit(1)


pda['date'] = pd.to_datetime(pda['date'])
pda['distance'] = pd.to_numeric(pda['distance'])
pda['year'] = pda.date.dt.year.astype(int)
pda['month'] = pda.date.dt.month.astype(str).apply(lambda x: x.zfill(2))
pda['week'] = pda.date.dt.week.astype(str)
pda['year-month'] = pda['year'].astype(str) + "-" + pda['month'].astype(str)


# Select only year range
pda = pda[pda["year"]<MAXYEAR]
allactivities = pd.crosstab(index=pda['year'], columns=pda['type'],values=pda['distance'],aggfunc=['sum']).fillna(0).round(1)
cmonth = pd.crosstab(index=pda['year-month'], columns=pda['type'],values=pda['distance'],aggfunc=['sum']).fillna(0).round(1)

geconomy = pda[pda['type'] == RIDE].groupby(['year'])\
	.agg({'id':'count','distance':'sum'})\
	.rename(columns={'id':'Nb trajets','distance':'Distance(Km)'})\
	[::-1]
	#.reset_index()

# Compute economy
lastdate = geconomy.tail(1).index
geconomy['Eco CO2 en Kg'] = (geconomy['Distance(Km)'] * co2)/1000
geconomy['Eco Ess. en €'] = geconomy['Distance(Km)'] * conso_100km * prix_litre / 100
geconomy['Frais velo en €'] = geconomy['Eco Ess. en €']
geconomy.at[lastdate,'Frais velo en €'] = 0-frais_velo+geconomy['Eco Ess. en €'].tail(1)
geconomy['Economie VS Auto-Moto'] = geconomy['Frais velo en €'][::-1].cumsum(axis = 0)
geconomy = geconomy.drop(['Frais velo en €'], axis=1)

economy=geconomy['Economie VS Auto-Moto'].head(1)

# Markdown converssion
allactivities = allactivities.xs('sum', axis=1, drop_level=True)
totalallactivities = float(pda['distance'].sum())
summary_allactivities_byyear = tabulate(allactivities[::-1], tablefmt="pipe", headers="keys")
summary_economy = tabulate(geconomy, tablefmt="pipe", headers="keys")

# Convert to markdown
UpdateReadme(
	distanceallactivities=totalallactivities,
	summaryallactivities=summary_allactivities_byyear,
	summaryeconomy=summary_economy,
	frais_velo=str(frais_velo),
	litres=str(conso_100km),
	euros=str(5.08*prix_litre),
	co2=str(round(geconomy['Eco CO2 en Kg'].sum())),
	economy=str(round(float(economy)))
	)
print(summary_allactivities_byyear)
print()
print(summary_economy)


# geconomy = pda.groupby(['year','type']).sum().reset_index()
# gmonth = pda.groupby(['year-month','type']).sum().reset_index()
# pivot_month = gmonth.pivot(index='year-month', columns='type', values='distance')
# pivot_year = gmonth.pivot(index='year-month', columns='type', values='distance')

# Save graph result
if os.path.isdir('%(folderdest)s/%(user)s' % locals()):
	allactivities.plot.barh(stacked=True,title="Distance parcouru par %(user)s" % locals(),figsize=(10,5))
	plt.gca().xaxis.set_major_formatter(FormatStrFormatter('%d km'))
	plt.xlabel("Distance(Km)")
	plt.ylabel("Année")
	plt.savefig('%(folderdest)s/%(user)s/summary_user.png' % locals())
