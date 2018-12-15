#!/bin/bash

# Convert to GPX
zcat $1 | sed 1d | gpsbabel -i gtrnctr -f - -o gpx -F $2

# FIRST=$(egrep -m1 -o "lat=\"[0-9\.]+\" lon=\"[0-9\.]+\"" $2.tmp | awk '{print $1","$2}' | tr -d '"' )
# LAST=$(egrep -o "lat=\"[0-9\.]+\" lon=\"[0-9\.]+\"" $2.tmp | tail -1 | awk '{print $1","$2}' | tr -d '"' )

# gpsbabel -i gpx -f $2.tmp \
# -x transform,wpt=trk,del \
# -x radius,distance=0.3k,$FIRST,nosort,exclude \
# -x radius,distance=0.3k,$LAST,nosort,exclude \
# -x transform,trk=wpt,del \
# -o gpx -F $2

gzip $2
# rm $2.tmp