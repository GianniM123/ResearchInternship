#!/bin/bash

MAX_PROCS=4
subjects_dir=../subjects/tcp/
out_dir=../results/tcp_preset_50_rerun
END=10
TIMEOUT=20m


mkdir -p $out_dir

files=$(md5sum `find ../subjects/tcp/ -name "*_Server.dot"` | sort | uniq -w 33 | cut -c35-)

for i in $(seq 1 $END)
do
    for file1 in $files
    do
        for file2 in $files
        do
            f1=${file1#${subjects_dir}}
            f2=${file2#${subjects_dir}}
            f1=${f1///}
            f2=${f2///}
            name="${out_dir}/${f1%.*}-${f2%.*}-${i}.dot"
            match_file="../subjects/tcp_k_pairs/${f1%.*}-${f2%.*}-50.txt"
            echo python3 ../algorithm/main.py --ref=$file1 --upd=$file2 -o $name -t 0.4 -s "yices" -l -m $match_file
        done
    done | xargs -I CMD --max-procs=$MAX_PROCS timeout $TIMEOUT bash -c "CMD"
done
