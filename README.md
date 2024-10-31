# MICRO24-MESS 
## Generate gem5 simulation binaries

### Prepare your local system
For this example we use `$SRCDIR`, `$IMGDIR`, `$RUNDIR`, to point to local directories
containing sources, the generated linux image, and simulation data, respectively.

```bash
# Change the paths accordingly.
export SRCDIR=$HOME/gem5/sources
export IMGDIR=$HOME/gem5/images
export RUNDIR=$HOME/gem5/runs
# Create directories
mkdir -p $SRCDIR $IMGDIR $RUNDIR
```

You will need to have Python 3, SCons, and other library dependencies
available in your system for building and running gem5 simulations.

### Clone this repository

```bash
# Clone gem5-dbc
git -C $SRCDIR clone https://github.com/FZJ-JSC/gem5-dbc 
pushd gem5-dbc
git checkout MICRO24-MESS
popd
```

### Build gem5  
Clone the mainline gem5 repository and apply the Mess patches
```bash 
git -C $SRCDIR/ clone https://github.com/gem5/gem5.git
pushd $SRCDIR/gem5
cp $SRCDIR/gem5-dbc/gem5-patches/bw-lat-ctrl.patch .
git checkout v22.0.0.2
git apply bw-lat-ctrl.patch
popd
```

```bash
# Build gem5 using scons with NPROCS number of jobs
scons -C $SRCDIR/gem5 --verbose --no-compress-debug --ignore-style --with-lto -j $NPROCS $SRCDIR/gem5/build/ARM/gem5.opt PROTOCOL=CHI NUMBER_BITS_PER_SET=512
```

This creates a binary gem5.opt at `$SRCDIR/gem5/build/ARM/gem5.opt`

### Generate FS simulation scripts for stream-mpi benchmark

```bash
# Change to predefined simulations directory
cd $RUNDIR
# Create link to objects directory
ln -ns $IMGDIR/objects $RUNDIR/objects
# Generate set of stream-mpi benchmark scripts for stream using graviton3BL configuration
$SRCDIR/gem5-dbc/exploration/exploration.py --config graviton3BL --benchmark stream-mpi
```

Simulation scripts are generated under `$RUNDIR/stream-mpi`.
Simulation scripts expect the gem5 executable `gem5.bin` to reside under `$RUNDIR/objects`.
Simulation scripts expect the generated Linux system binary files to reside under `$RUNDIR/objects`.


## Parse gem5 simulations results

```bash
# Change to predefined simulations directory
cd $RUNDIR
# Parse results using gem5-dbc
$SRCDIR/gem5-dbc/exploration/exploration.py --parse --benchmark stream-mpi
```

The parsing module will produce a CSV file `$RUNDIR/stream-mpi/stream_cols.txt`
containing selected benchmark statistics, and an HDF5 file  `$RUNDIR/stream-mpi/stream_data_fixed.h5`
containing all parsed statistics for the benchmark.

## Binaries for full-system simulation

Our infrastructure to create root disk, linux, and benchmark disk images has been merged into gem5-dbc, see `tools/binaries` and `tools/benchmarks-image`.

Checkout the documentation [here](tools/binaries/README.md).

## Added checkpoint support 

You may generate job scripts to create checkpoints by adding the `--checkpoint` flag:

```bash
# Change to predefined simulations directory
cd $RUNDIR
# Setup an additional dir
mkdir -p create_cpts && cd $_
# gem5-dbc expects the gem5 binary to reside under images/gem5.bin
ln -s $IMGDIR/ $PWD/images
# Generate script for checkpoint creation
$SRCDIR/gem5-dbc/exploration/exploration.py --benchmark stream-mpi --config graviton3BL --checkpoint
```

This will generate job scripts to create checkpoints, i.e, the entire simulation runs in `atomic` mode. Checkpoints are created in `$RUNDIR/cpts/` and can be used by any simulation that restores from a checkpoint that already exists.

To generate job scripts that restore from a checkpoint use the `--restore-checkpoint` flag:

```bash
# Change to predefined simulations directory
cd $RUNDIR
# Setup an additional dir
mkdir -p mysimulations && cd $_
# gem5-dbc expects the gem5 binary to reside under images/gem5.bin
ln -s $IMGDIR/ $PWD/images
# Restore from checkpoint 
$SRCDIR/gem5-dbc/exploration/exploration.py --benchmark stream-mpi --config graviton3BL  --restore-checkpoint
```
Simulations restore from existing checkpoints in `detailed` mode.

### Acknowledgement
We acknowledge Nam Ho and Carlos Falquez for their work on the gem5 simulation infrastructure
