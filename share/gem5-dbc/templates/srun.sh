#!/bin/bash
GEM5_BIN={gem5_bin}
GEM5_SCR={gem5_script}
WORK_DIR={gem5_workdir}
FILE_OUT={gem5_output}

if [ -f "$WORK_DIR/stats.txt" ]; then
  echo "$WORK_DIR/stats.txt already exists. Exiting."
  exit 1
fi

pushd $WORK_DIR
$GEM5_BIN --outdir=$WORK_DIR $GEM5_SCR > $FILE_OUT 2>&1
popd
