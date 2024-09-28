# gem5-dbc

A Declarative Benchmark Configuration Framework
for architecture exploration with [gem5](https://www.gem5.org/).

## Simulation Workflow

### Prepare your local system

Specify local directories containing gem5-dbc source files and needed simulation artifacts

```bash
# Set the correct paths for your system
export G5DBC_SOURCE=$HOME/sources/gem5-dbc
export G5DBC_PREFIX=/opt/g5dbc
```
### Prepare resources directory

To use gem5-dbc you need to first configure a directory `$G5DBC_PREFIX` containing
different resources needed for configuring and running a full system simulation.

The compiled gem5 executable should be copied to `$G5DBC_PREFIX/bin/gem5.bin`.
```bash
cp  gem5/build/ARM/gem5.opt $G5DBC_PREFIX/bin/gem5.bin
```

The `$G5DBC_SOURCE/share` directory should be copied to `$G5DBC_PREFIX/share`.
```bash
cp -rv $G5DBC_SOURCE/share $G5DBC_PREFIX
```

The artifacts directory and corresponding index
can be generated using the provided [Packer](https://developer.hashicorp.com/packer)
templates, see [artifacts/README.md](artifacts/README.md).

After the build is finished, the created directory `artifacts`
and file `artifacts.yaml` can be copied to `$G5DBC_PREFIX/share/g5dbc`.

The resulting directory structure of `$G5DBC_PREFIX` should be as follows

| File | Description |
| ---- | ----------- |
| $G5DBC_PREFIX/bin/gem5.bin               | gem5 binary        |
| $G5DBC_PREFIX/share/g5dbc/artifacts.yaml | Artifact index     |
| $G5DBC_PREFIX/share/g5dbc/artifacts      | Artifact directory |
| $G5DBC_PREFIX/share/g5dbc/benchmarks     | Default benchmarks directory     |
| $G5DBC_PREFIX/share/g5dbc/configs        | Default configurations directory |
| $G5DBC_PREFIX/share/g5dbc/parser         | Default parser regexps directory |
| $G5DBC_PREFIX/share/g5dbc/templates      | Default templates directory      |


### Benchmark generation

```bash
# Generate set of simple benchmark scripts for stream using example system-single.yaml configuration
$G5DBC_SOURCE/src/main.py --path-prefix $G5DBC_PREFIX --benchmark-mod stream.py --benchmark-cfg system-single.yaml  --generate
```

### Benchmark results evaluation

```bash
# Parse results to json
$G5DBC_SOURCE/main.py --path-prefix $G5DBC_PREFIX --benchmark-mod stream.py  --parse
```
