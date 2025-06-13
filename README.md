# gem5-dbc

A Declarative Benchmark Configuration Framework for architecture exploration with [gem5](https://www.gem5.org/).

The gem5-dbc framework allows for a simplified gem5 simulation workflow.
After installing, the `g5dbc` command line tool can be used to


0. [Configure](#binary-artifact-configuration) required binary artifacts including full system simulation images.
1. [Generate](#generate-simulation-scripts) a set simulation scripts from a [benchmark definition](#benchmark-specification) and initial [architecture configuration](#initial-architecture-configuration).
2. [Run](#run-generated-simulation-scripts) generated gem5 simulation scripts.
3. [Parse](#parse-simulation-results) gem5 stats.txt output to flat json files.
4. [Evaluate](#evaluate-parsed-results) parsed statistics to collect data of interest to a CSV file.

Currently, benchmark configuration and simulation is only supported for the ARM ISA.
Support for general ISAs will be implemented soon.

## Installation

### Install gem5-dbc using pip

Install gem5-dbc directly from the git repo

```bash
# Install gem5-dbc package locally
pip install --user git+https://github.com/FZJ-JSC/gem5-dbc.git
```

## Simulation Workflow

In the following, we describe the simulation workflow in more detail.

<!-- Binary artifacts required for full system simulations need to be configured.-->

## Binary artifact configuration

To use gem5-dbc, you need a working installation of the [gem5](https://www.gem5.org/) computer architecture simulator.

You also need to provide all binary artifacts required for configuring and running a full system simulation.

### Compile gem5 binary

```bash
# Clone gem5 repository
git clone https://github.com/gem5/gem5.git

# Compile gem5 binary for ARM ISA
scons -C gem5 --ignore-style -j $(nproc) gem5/build/ARM/gem5.fast
```


### Add gem5 binary to gem5 artifact registry

Add gem5 binary to the local user artifact registry with the command `g5dbc --resource-add <PATH> --resource-type GEM5` 

```bash
# Add gem5 binary to user artifact registry
g5dbc --resource-add gem5/build/ARM/gem5.fast --resource-type GEM5
```

When adding a gem5 binary for the first time, an artifact registry
is created by default in your platform’s local user configuration directory,
for example: `$HOME/.config/gem5-dbc/artifacts.yaml`.

<details>
<summary>Example user artifact registry</summary>

```yaml
arm64:
- bintype: GEM5
  md5hash: 06fc82f21f6e82e03e538252a05131e6
  metadata: Apr  3 2025 10:07:41
  name: gem5.fast
  path: /home/user/sources/gem5/build/ARM/gem5.fast
  version: 24.1.0.2
```

</details>

### Artifact registry

An *artifact registry* is a collection of artifact lists, each indexed by an architecture name (e.g. `arm64`).
Each list contains entries describing individual artifacts using a set of key-value pairs, as detailed below:

| Key | Description |
| ---- | ----------- |
| name     | Artifact name identifier. |
| path     |   Relative or absolute path to the binary or image file. |
| bintype  | The type of artifact (DISK, BOOT, KERNEL,GEM5).  |
| version  |  The version label or tag of the artifact.  |
| md5hash  | The MD5 checksum used for integrity verification.   |
| metadata | Additional context, such as the disk image root partition (e.g. `/dev/vda2`) or kernel boot parameters.  |


### Add Linux Binary Artifacts for Full System Simulation

If you already have binary artifacts available for use with gem5 full-system simulation,
you can add them via the command line, either to your user artifact registry
or to a separate registry file.

Using separate registry files is recommended when working with multiple sets of binary images,
as each set can be described by its own independent registry.

Example commands are listed below.

```bash
# Add Linux Image
# For DISK artifacts, gem5-dbc uses the metadata field to speficy the correct root partition.
g5dbc -a arm64/disks/disk.img -A arm64 -T DISK -N disk.img -V debian -M /dev/vda2 -i index.yaml

# Add Linux Kernel
# For KERNEL artifacts, gem5-dbc uses the metadata field to speficy kernel boot parameters
g5dbc -a arm64/binaries/vmlinux-5.15.68 -A arm64 -T KERNEL -N vmlinux -V 5.15.68 -M "earlyprintk=pl011,0x1c090000 console=ttyAMA0 lpj=19988480 norandmaps rw loglevel=8" -i index.yaml

# Add ARM64 Bootloader
# For BOOT artifacts, gem5-dbc uses the version field to select correct bootloader for selected platform
g5dbc -a arm64/binaries/boot.arm64 -A arm64 -T BOOT -N boot.arm64 -V V1 -i index.yaml

# Add ARM64 Bootloader
# For BOOT artifacts, gem5-dbc uses the version field to select correct bootloader for selected platform
g5dbc -a arm64/binaries/boot_v2.arm64 -A arm64 -T BOOT -N boot.arm64 -V V2 -i index.yaml

```

For `DISK` artifacts, gem5-dbc uses the `metadata` field to specify the correct root partition.

For `KERNEL` artifacts, gem5-dbc uses the `metadata` field to specify kernel boot parameters.

For `BOOT` artifacts, gem5-dbc uses the `version` field to select the appropriate bootloader for the selected platform.


### Generate Linux Binary Artifacts for Full System Simulation with gem5

This repository contains a set of [Packer](https://developer.hashicorp.com/packer)
templates for building disk images to use for Full System Simulation with [gem5](https://www.gem5.org/).

Currently, artifact generation is supported only for the ARM64 architecture.

```bash
# Directory where Linux Binary Artifacts for Full System Simulation will be generated
export ARTIFACTS=$HOME/artifacts

# Init packer plugins
packer init gem5-dbc/artifacts/packer

# Generate binary artifacts
packer build -var artifacts_dir=$ARTIFACTS gem5-dbc/artifacts/packer
```

After succesful building of all binary images,
an index file `$ARTIFACTS/index.yaml` is created containing
metadata and checksum information for all generated binaries.
The index file will be referenced later in order to automatically generate simulation scripts.

For more details, see [artifacts/packer/README.md](artifacts/packer/README.md).

<details>
<summary>Linux Binary Artifact Registry</summary>

After the ARM64 image build is finished, the directory `$ARTIFACTS`
will contain the generated binary artifacts.

| File | Description |
| ---- | ----------- |
| $ARTIFACTS/index.yaml     | Index of binary artifacts for use with `g5dbc`  |
| $ARTIFACTS/arm64/disks    | Disk Images   |
| $ARTIFACTS/arm64/keys     | SSH Keys for generated image   |
| $ARTIFACTS/arm64/binaries | ARM64 bootloaders and Linux kernels |

Example generated `index.yaml` file after successful build of an ARM64 debian-testing image with [Packer](https://developer.hashicorp.com/packer).

```yaml
arm64:
- bintype: "DISK"
  name: disk.img
  path: arm64/disks/disk.img-debian-testing
  md5hash: d37bfb08faa9ba10c861b649b6fbac8a
  version: debian-testing
  metadata: /dev/vda2
- bintype: "BOOT"
  name: boot.arm64
  path: arm64/binaries/boot.arm64-V1
  md5hash: 64e7904dccf73a73f9cb8040f7a27a0c
  version: V1
  metadata: V1
- bintype: "BOOT"
  name: boot.arm64
  path: arm64/binaries/boot.arm64-V2
  md5hash: c81d1a6d4ee9621a9b08284cfb00190e
  version: V2
  metadata: V2
- bintype: "KERNEL"
  name: Image
  path: arm64/binaries/Image-5.15.68
  md5hash: 66d18afe5d0cb4c4ec9cb0641982ff38
  version: 5.15.68
  metadata: qemu
- bintype: "KERNEL"
  name: vmlinux
  path: arm64/binaries/vmlinux-5.15.68
  md5hash: a98b65636bbac2a1fe4ab4eb5948d66b
  version: 5.15.68
  metadata: earlyprintk=pl011,0x1c090000 console=ttyAMA0 lpj=19988480 norandmaps rw loglevel=8
```
</details>


## Generate Simulation Scripts

To let gem5-dbc automatically generate gem5 simulation scripts for you,
you need to define

1. A set of initial model parameters, the *initial architecture configuration*,
2. A gem5 benchmark specification, by implementing a subclass of [AbstractBenchmark](src/g5dbc/benchmark/__init__.py).


### Initial architecture configuration

The initial configuration is described using human-readable [YAML format](https://yaml.org/).
Example configurations are located under [share/gem5-dbc/configs](share/gem5-dbc/configs).

A schema definition documenting currently supported configuration values is located at [share/gem5-dbc/schema.json](share/gem5-dbc/schema.json).


<details>
<summary>Initial configuration example</summary>

The following lists the example [garnet](share/gem5-dbc/configs/garnet) configuration using Garnet and DDR4 memory.
A schema definition documenting currently supported configuration values is located at [share/gem5-dbc/schema.json](share/gem5-dbc/schema.json).

Note that gem5-dbc uses a YAML loader with support for [!include constructor](src/g5dbc/util/dict_yaml.py).

An initial configuration can be defined as a single YAML file, or a directory containing an index file `index.yaml`.

```yaml
# Example configuration with Garnet interconnect and DDR4 memory model
simulation:
  gem5_version: 24.1.0.2
  full_system: True

system:
  architecture: arm64
  num_cpus: 2
  num_slcs: 2
  clock: 2.6GHz
  sve_vl: 256
  cache_line_size: 64

cpus:
  simple:
    model: AtomicSimple
    clock: 2.6GHz
  o3cpu: !include cpu.yaml

caches: !include caches.yaml

memory:
  regions:
    - model: DRAM
      channels: 4
      size:  2GiB
      dram_settings: !include ../memory/DDR4_2400_16x4.yaml

interconnect:
  model: garnet

network: !include network.yaml
```

A variety of Ruby network topologies can be defined as well.
Currently, gem5-dbc only supports the [`Simple2D`](src/g5dbc/sim/model/topology/ruby/Simple2D/__init__.py) network topology model.
The `Simple2D` model constructs simple 2D meshes based on a list of internal links.
An example for a simple 2D mesh topology is given below.

```yaml
# 1x Link for all VNETs
mesh_vnet_support: [[0,1,2,3]]
node_vnet_support: [[0,1,2,3]]
# 2x3 2D mesh topology
#
# [3] - [4] - [5]
#  |     |     |
# [0] - [1] - [2]
#
topology:
  model: Simple2D
  parameters:
    num_mesh_routers: 6
    router_numa_ids: [0,0,0,0,0,0]
    cpu_routers: [[1,4]]
    slc_routers: [[1,4]]
    mem_routers: [[0,3]]
    rom_routers: [2]
    dma_routers: [2]
    # Tuples describe internal links between routers A,B in the format:
    # [Router A, Router B, Weight]
    internal_links:
      - [0, 1, 1]
      - [1, 2, 1]
      - [3, 4, 1]
      - [4, 5, 1]
      - [0, 3, 2]
      - [1, 4, 2]
      - [2, 5, 2]
```
</details>


### Benchmark specification

A gem5 benchmark is defined by implementing a subclass of [AbstractBenchmark](src/g5dbc/benchmark/__init__.py)

Example benchmark implementations are located under [share/gem5-dbc/benchmarks](share/gem5-dbc/benchmarks).


<details>
<summary>Benchmark specification</summary>

Specify a gem5 benchmark by implementing following abstract methods:

```python
class benchmark(AbstractBenchmark[T]):
  @abstractmethod
  def get_command(self, params: T, config: Config) -> str:
    """Return command to execute"""

  @abstractmethod
  def get_env(self, params: T, config: Config) -> dict:
    """Return dictionary of environment variables to set before running benchmark"""

  @abstractmethod
  def get_varparams(self) -> dict[str, list]:
    """Return the parameter space definition as a map
       parameter name => list of parameter values"""

  @abstractmethod
  def filter_varparams(self, params: T, config: Config) -> bool:
      """Return True if given initial configuration and parameter combination is valid"""

  @abstractmethod
  def update_config(self, params: T, config: Config) -> Config:
      """Update configuration from given parameters"""

  @abstractmethod
  def get_data_rows(self, params: T, stats: dict) -> dict | list[dict]:
      """Return a single data row or multiple data rows to be written to a CSV file"""
```

</details>


### Benchmark simulation scripts generation

Once the initial configuration and AbstractBenchmark implementation is defined,
`g5dbc` may be invoked to generate simulations scripts.

For this example, we generate simulation scripts for the [`mini_triad`](share/gem5-dbc/benchmarks/stream/mini_triad.py)
benchmark using [`garnet`](share/gem5-dbc/configs/garnet) as initial configuration.

The  [`mini_triad`](share/gem5-dbc/benchmarks/stream/mini_triad.py) benchmark will modify
the initial [`garnet`](share/gem5-dbc/configs/garnet) configuration by attaching
`m5.SimpleMemory` memory controllers with varying bandwidth parameters.

We also need to specify the artifacts directory, `--artifacts-dir $ARTIFACTS`.

Generate the simulation scripts using 4 threads, `--nprocs 4`.

```bash
# Generate simulation scripts for stream/mini_triad benchmark and example garnet configuration
# Include $ARTIFACTS directory containing artifacts.yaml index
g5dbc --generate stream/mini_triad --init-config garnet --artifact-index $ARTIFACTS --nprocs 4
```

The command will generate simulation scripts under `mini_triad/work`.

Each subdirectory is labeled by an integer `$benchId`, and contains the following files

| File | Description |
| ---- | ----------- |
| `$benchName/work/$benchId/srun.sh`       | Shell script to start gem5 simulation for `$benchId` configuration |
| `$benchName/work/$benchId/work.sh`       | Shell script to execute under Full System Simulation  |
| `$benchName/work/$benchId/config.yaml`   | Architecture configuration file for `$benchId`  |


## Run generated simulation scripts

The `srun.sh` script is generated from a [template](share/gem5-dbc/templates/srun.sh)
which can be modified to run simulations in a cluster environment, for example.

To run the first 10 benchmarks on the local machine, you may use the command line

```bash
# Run the first 10 benchmarks
for i in {00..09} ; do ./mini_triad/work/$i/srun.sh & done
```


## Parse Simulation Results

After successful simulation run, a `stats.txt` file will be written for each  `$benchId`.
We can use `g5dbc` to parse the results to flat JSON,

```bash
# Parse the generated benchmark statistics to flat JSON
g5dbc --parse mini_triad --nprocs 4
```

Resulting JSON files will be written to `$benchName/parsed/$benchId.$roiId.json`


## Evaluate Parsed Results

From the parsed JSON files we can generate a CSV file with relevant data,
as implemented in `get_data_rows`:

```bash
# Evaluate the parsed results and write relevant data to a CSV file.
g5dbc --eval mini_triad --nprocs 4
```

The command will generate a file `$benchName/parsed/data.csv`
