#!/bin/bash
#SBATCH --job-name={name}
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --chdir={outd}
#SBATCH --output={outd}/{name}_out.log
#SBATCH --error={outd}/{name}_err.log

WDIR={outd}
CONF={conf}
NAME={name}

CMD_ENV=$WDIR/{cmd_env}
CMD_OUT=$WDIR/{cmd_output}
CMD_ERR=$WDIR/{cmd_outerr}

GEM5_BIN={gem5_bin}
GEM5_SCRIPT={gem5_script}

pushd $WDIR

$GEM5_BIN {debug_opts} \
	--outdir=$WDIR $GEM5_SCRIPT \
	--config-file $CONF \
	--cmd          "{benchmark_cmd}"   \
	--cmd-env      $CMD_ENV    \
	--cmd-output   $CMD_OUT \
	--cmd-outerr   $CMD_ERR \
	 {gem5_args} \
	 2>&1 | tee -a $WDIR/output.log

cat stats.txt | sed '/^[[:space:]]*$/d' > results.txt
csplit -n 4 -z --suppress-matched --quiet --prefix="$NAME.roi." results.txt "/^-/" "{{*}}" 
rm -rf results.txt

cp $CMD_OUT $NAME.roi.txt

cp config.ini  $NAME.config.ini
cp config.json $NAME.config.json

popd
