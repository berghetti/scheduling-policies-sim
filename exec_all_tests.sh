#!/bin/bash

echo "Executing dfcfs"
for i in 10 20 30 40 50 60 65 70 75 80 85 90 95 100 105 110; do
    ./run_variation_simulaton.sh configs/bimodal_dfcfs.json dfcfs_$i $i;
done;
rm dfcfs/*
mv *dfcfs*csv dfcfs/

echo "Executing persephone"
for i in 10 20 30 40 50 60 65 70 75 80 85 90; do
    ./run_variation_simulaton.sh configs/bimodal_persephone.json persephone_$i $i;
done;
rm persephone/*
mv *persephone*csv persephone/

echo "Executing afp"
for i in 10 20 30 40 50 60 65 70 75 80 85 90 95 100 105 110 115 120 125 130 135 140 145 150 155 160 165; do
    ./run_variation_simulaton.sh configs/bimodal_afp.json afp_$i $i;
done;
rm afp/*
mv *afp*csv afp/

echo "Coping data to matplot directory"

cp dfcfs/* ~/testes/matplotlib/policys/dfcfs/
for i in ~/testes/matplotlib/policys/dfcfs/*; do
    mv $i ~/testes/matplotlib/policys/dfcfs/$(echo $i | cut -d '_' -f 4,5,6);
done;

cp persephone/* ~/testes/matplotlib/policys/persephone/
for i in ~/testes/matplotlib/policys/persephone/*; do
    mv $i ~/testes/matplotlib/policys/persephone/$(echo $i | cut -d '_' -f 4,5,6);
done;

cp afp/* ~/testes/matplotlib/policys/afp/
for i in ~/testes/matplotlib/policys/afp/*; do
    mv $i ~/testes/matplotlib/policys/afp/$(echo $i | cut -d '_' -f 4,5,6);
done;

echo "Ploting results"
~/testes/matplotlib/plot_figs.sh

