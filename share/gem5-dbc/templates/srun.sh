#!/bin/bash

GEM5_BIN={gem5_bin}
GEM5_SCRIPT={gem5_script}

WDIR={benchmark_output}
CONF={benchmark_config}

if [ -f "$WDIR/stats.txt" ]; then
	echo "$WDIR/stats.txt already exists. Exiting."
	exit 1
fi

pushd $WDIR

$GEM5_BIN \
    {gem5_debug_opts} \
	--outdir=$WDIR $GEM5_SCRIPT \
	--benchmark-cfg  $CONF \
	{gem5_script_opts} \
	2>&1 | tee -a $WDIR/output.log

popd
