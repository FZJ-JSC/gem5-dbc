# gem5-dbc

A Declarative Benchmark Configuration Framework
for architecture exploration with [gem5](https://www.gem5.org/).

## Installation

### Prerequisites

To use gem5-dbc you need to provide all binary artifacts
required for configuring and running a full system simulation.

This repository contains a set of [Packer](https://developer.hashicorp.com/packer)
templates for building all needed binaries.
For more details, see [artifacts/README.md](artifacts/README.md).

After succesful building of all binary artifacts,
an index file `index.yaml` is generated containing
binary metadata and checksum information.

## Install gem5-dbc

Install gem5-dbc directly from the git repo

```bash
# Install gem5-dbc package locally
pip install --user git+https://github.com/FZJ-JSC/gem5-dbc.git@develop

# Configure gem5 binary
g5dbc --resource-add GEM5 gem5/build/ARM/gem5.fast
```

## Simulation Workflow

Once installed, the command `g5dbc` can be used to generate scripts for starting gem5 simulations
with the correct model paramters, and parse the resulting `stats.txt` file.


### Benchmark definition

To use gem5-dbc, a benchmark must be defined by
    1. listing a set of initial model parameters, the *initial configuration*,
    2. implementing a subclass of [AbstractBenchmark](src/g5dbc/benchmark/benchmark.py) and its methods.

The default location for initial configurations is `share/gem5-dbc/configs`.
The default location for AbstractBenchmark implementations is `share/gem5-dbc/benchmarks`.

### Benchmark simulation scripts generation

Once the initial configuration and AbstractBenchmark implementation is defined,
`g5dbc` may be invoked to generate simulations scripts.

```bash
# Generate simulation scripts for stream benchmark and example architecture configuration
# Include $ARTIFACTS directory containing artifacts.yaml index
g5dbc --generate stream example/garnet-DDR4 --artifacts-dir $G5DBC_IMAGES/artifacts
```

### Benchmark results evaluation

```bash
# Parse the generated benchmark statistics to flat JSON
g5dbc --parse stream
```
