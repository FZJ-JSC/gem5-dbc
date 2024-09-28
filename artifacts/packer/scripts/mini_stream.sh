#!/bin/bash

PRVDIR=/tmp/provision/mini_stream

BENCHMARK_BIN=/benchmarks/bin

mkdir -p $BENCHMARK_BIN

make MARCH="armv8-a+sve" -C $PRVDIR
make MARCH="armv8-a+sve"  M5_PREFIX=/usr -C $PRVDIR

install -D -m 0755 -t $BENCHMARK_BIN $PRVDIR/*.x