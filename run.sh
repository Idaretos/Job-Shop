#!/bin/bash

# Check if $1 (input filename) is not provided
if [ -z "$1" ]
then
  inputfile='input/orb01.txt' # Replace with your default input file
else
  inputfile="$1"
fi

# Check if $2 (output filename) is not provided
if [ -z "$2" ]
then
  outputfile='output' # Replace with your default output file
else
  outputfile="$2"
fi

# Check if $3 (SPT value) is not provided
if [ -z "$3" ]
then
  spt='SPT' # Replace with your default SPT value
else
  spt="$3"
fi

# Execute the script
python main.py "$inputfile" "$outputfile" "$spt"
