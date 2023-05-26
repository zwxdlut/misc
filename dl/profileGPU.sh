#!/bin/bash

program=$1
outfile=$2

rm -f $outfile
printf "Save GPU profile of %s to %s\n" $program $outfile
printf "%-10s %-10s %-10s\n" MemUsage MemTotal GPU-Util | tee -a $outfile

while true
do
    # nvidia-smi |head -10|tail -1|gawk '{printf "%-10s %-10s %-10s\n", $9, $11, $13}' | tee -a $outfile
    # nvidia-smi |head -10|tail -1|gawk '{print $9, "   ", $11, " ", $13}' | tee -a $outfile
    mem_total=`nvidia-smi |head -10|tail -1|gawk '{print $11}'`
    gpu=`nvidia-smi |head -10|tail -1|gawk '{print $13}'`
    mem=`nvidia-smi | grep $program |gawk '{print $8}'`
    printf "%-10s %-10s %-10s\n" $mem $mem_total $gpu | tee -a $outfile
    sleep 1s
done


