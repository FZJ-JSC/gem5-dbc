#!/bin/bash
#SBATCH --job-name={name}
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --chdir={outd}
#SBATCH --output={outd}/{name}_out.log
#SBATCH --error={outd}/{name}_err.log

function split_rois {{
	cat stats.txt | sed '/^[[:space:]]*$/d' > results.txt
	csplit -n 4 -z --suppress-matched --quiet --prefix="$1.roi." results.txt "/^-/" "{{*}}" 
	rm -rf results.txt
}}

function copy_files {{
	cat system.terminal | sed -n '/START WORK/,$p' > $1.terminal.txt

	cp output.log  $1.output.txt
	cp config.ini  $1.config.ini
	cp config.json $1.config.json
}}

{modules}

WDIR={outd}
CONF={conf}
KERNEL={kernel}
ROOTDISK={rootdisk}
ROOTPART={rootpart}
BOOT={bootloader}
WORK={bootscript}
NAME={name}
GEM5_BIN={gem5_bin}
GEM5_SCRIPT={gem5_script}
ONLY_PARSE=false

{amd_preamble}

# read options
for opt in "$@"; do
	case $opt in
		--parse)  ONLY_PARSE=true; ;;
		*) ;; #NOOP
esac
done

if [ "$ONLY_PARSE" = true ]; then
	if [ -f "stats.txt" ]; then
		echo "Writig ROIs from stats.txt."
		split_rois $NAME
		exit 0
	else
		echo "stats.txt does not already exists. Exiting."
		exit 1
	fi
fi

if [ -f "$WDIR/stats.txt" ]; then
	echo "$WDIR/stats.txt already exists. Exiting."
	exit 1
fi

pushd $WDIR

$GEM5_BIN {debug_opts} \
	--outdir=$WDIR $GEM5_SCRIPT \
	--config-file  $CONF \
	{checkpoint} \
	--kernel       $KERNEL\
	--disk         $ROOTDISK\
        {benchdisk} \
	--root-partition $ROOTPART \
	--bootloader   $BOOT \
	--bootscript   $WDIR/$WORK \
	 {gem5_args} \
	 2>&1 | tee -a $WDIR/output.log

split_rois $NAME

copy_files $NAME

popd
