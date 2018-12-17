#!/bin/bash

# routeconverter suport more files conversion than gpsbabel
# https://www.routeconverter.de/stable-releases/en

# Convert to GPX
file $1 | grep gzip > /dev/null
if [ $? -eq 0 ]; then
    gunzip -c $1 > $2.unziped
else
    cp $1 $2.unziped
fi

# Convert to GPX
java -jar ~/.bin/RouteConverterCmdLine.jar $2.unziped "Gpx10Format" $2
gzip $2
rm $2.unziped