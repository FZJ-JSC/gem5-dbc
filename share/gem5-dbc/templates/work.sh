#!/bin/sh 

echo "START WORK"

# Switch CPUS
/sbin/m5 exit

{benchmark_env}

SVE_SYS_VEC_LEN=/proc/sys/abi/sve_default_vector_length
if [ -f "$SVE_SYS_VEC_LEN" ]; then
    echo "$SVE_VEC_LEN" > $SVE_SYS_VEC_LEN
    printf "$SVE_SYS_VEC_LEN "
    cat $SVE_SYS_VEC_LEN
fi

export

echo "Running {benchmark_cmd}"

/sbin/m5 resetstats

{benchmark_cmd}

/sbin/m5 dumpstats

echo "Finished" 

/sbin/m5 exit
