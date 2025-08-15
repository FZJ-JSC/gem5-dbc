#!/bin/bash
GEM5_BIN={gem5_bin}
GEM5_SCR={gem5_script}
WORK_DIR={gem5_workdir}
FILE_OUT={gem5_output}
COMPRESS={compress_stats}

check_stats() {{
    for f in $WORK_DIR/stats.txt*; do
        [ -e "$f" ] && return 0
    done
    return 1
}}

if check_stats; then
  echo "$WORK_DIR/stats.txt already exists. Exiting."
  exit 1
fi

pushd $WORK_DIR
$GEM5_BIN --outdir=$WORK_DIR $GEM5_SCR > $FILE_OUT 2>&1

# Compress stats.txt
if [ -n "$COMPRESS" ] && [ -x "$(command -v $COMPRESS)" ]; then
  echo "Compressing stats.txt with $COMPRESS"
  $COMPRESS stats.txt
fi

popd
