#!/bin/bash

files=$(find ../../subjects/openssl_models/ -name "*.dot")


for file in $files
do
    python3 ../../dot-files/fix-dot-files.py $file
done 

