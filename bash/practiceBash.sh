#!/bin/bash

NAME=${1?Error: No name given} #creates a variable by taking in first input
NAME2=${2:-friend} #here it takes in second input, but the :- notation says that friend will be defult
echo "Hello $NAME and $NAME2"
 
