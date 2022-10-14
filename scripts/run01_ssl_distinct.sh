#!/bin/bash

MAX_PROCS=4
subjects_dir=../subjects/openssl/
out_dir=../results/openssl
END=10
TIMEOUT=20m


declare -a sat_solvers=("msat" "cvc4" "z3" "yices")
# "btor" "picosat" "bdd" do not suppport logic
mkdir -p $out_dir

files=$(md5sum `find ../subjects/openssl -name "*.dot"` | sort | uniq -w 33 | cut -c35-)

for i in $(seq 1 $END)
do
    for file1 in $files
    do
        for file2 in $files
        do
            for solver in ${sat_solvers[@]};
            do
                f1=${file1#${subjects_dir}}
                f2=${file2#${subjects_dir}}
                f1=${f1///}
                f2=${f2///}
                name="${out_dir}/${f1%lea*}-${f2%lea*}-${solver}-${i}.dot"
                echo python3 ../algorithm/main.py --ref=$file1 --upd=$file2 -o $name -t 0.5 -s $solver -l

                #echo ${name}
            done
            name="${out_dir}/${f1%lea*}-${f2%lea*}-umfpack-${i}.dot"
            echo python3 ../algorithm/main.py --ref=$file1 --upd=$file2 -o $name -t 0.5 -l
        done
    done | xargs -I CMD --max-procs=$MAX_PROCS timeout $TIMEOUT bash -c "CMD"
done

python3 ./add_date.py "${out_dir}/"
