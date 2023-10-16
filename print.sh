#!/bin/bash
FILE=$1
awk -F, '{print($12 "," $13 "," $11 "," $16 "," $17 "," $18 "," $19 "," $22)}' $FILE | column --separator , -t
