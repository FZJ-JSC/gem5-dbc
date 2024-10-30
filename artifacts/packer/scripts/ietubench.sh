#!/bin/bash

SRCDIR=/root/sources
BUILDD=/root/build

BENCHMARK_BIN=/benchmarks/bin/micro

mkdir -p $SRCDIR $BINDIR

# IETUBENCH
IETUBENCH_GIT="https://github.com/FZJ-JSC/ietubench.git"
IETUBENCH_VER="main"

git -C $SRCDIR clone --depth 1 --branch $IETUBENCH_VER $IETUBENCH_GIT

cmake -B $BUILDD/ietubench $SRCDIR/ietubench -D CMAKE_BUILD_TYPE="Release" -D PROJECT_LOOP_LENGTHS="256;4096" -D PROJECT_USE_M5="OFF"

make  -C $BUILDD/ietubench -j$(nproc)

cmake -B $BUILDD/ietubench $SRCDIR/ietubench -D CMAKE_BUILD_TYPE="Release" -D PROJECT_LOOP_LENGTHS="256;4096" -D PROJECT_USE_M5="ON"

make  -C $BUILDD/ietubench -j$(nproc)

install -D -m 0755 -t $BENCHMARK_BIN $BUILDD/ietubench/src/micro/**/*.x
