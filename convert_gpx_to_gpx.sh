#!/bin/bash

# routeconverter suport more files conversion than gpsbabel
# https://www.routeconverter.de/stable-releases/en

# Convert to GPX
file $1 | grep gzip > /dev/null
if [ $? -eq 0 ]; then
    cp $1 $2
else
    cp $1 $2
    gzip $2
fi