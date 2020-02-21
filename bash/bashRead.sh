#!/bin/bash
OLDIFS = $IFS
IFS=","

while read platform iname vname vsize ssize
    do
        echo "$platform" 
        echo "$iname"
        echo "$vsize" 
        echo "$ssize"
        echo " "
    done < $1

IFS=$OLDIFS