# Copyright (c) 2019 ARM Limited
# All rights reserved.
#
# The license below extends only to copyright in the software and shall
# not be construed as granting a license to any other intellectual
# property including but not limited to intellectual property relating
# to a hardware implementation of the functionality of the software
# licensed hereunder.  You may use the software subject to the license
# terms below provided that you ensure that this notice is replicated
# unmodified and in its entirety in all distributions of the software,
# modified or unmodified, in source code or in binary form.
#
# Copyright (c) 2015 Advanced Micro Devices, Inc.
# All rights reserved
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Authors: David Hashe

import m5

import functools
import operator
import os
import shutil

kibi = 1024
mega = 1.0e6

def hex_mask(terms):
    dec_mask = functools.reduce(operator.or_, [2**i for i in terms], 0)
    return "%08x" % dec_mask

def file_append(path, contents):
    with open(os.path.join(*path), 'a') as f:
        f.write(str(contents))

def replace_tree(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.mkdir(path)


def register_node(cpu_list, mem, node_number):
    print("mem",mem)
    nodebasedir = os.path.join(m5.options.outdir, 'fs', 'sys', 'devices', 'system', 'node')

    nodedir = os.path.join(nodebasedir,'node%d' % node_number)
    os.makedirs(nodedir)

    file_append((nodedir, 'cpumap'), hex_mask(cpu_list))
    file_append((nodedir, 'meminfo'), 'Node %d MemTotal: %dkB' % (node_number, m5.util.convert.toMemorySize(str(mem))/kibi))

def register_cpu(physical_package_id, core_siblings, core_id, thread_siblings):
    cpudir = os.path.join(m5.options.outdir, 'fs',  'sys', 'devices', 'system', 'cpu', 'cpu%d' % core_id)

    if not os.path.isdir(os.path.join(cpudir, 'topology')):
        os.makedirs(os.path.join(cpudir, 'topology'))
    if not os.path.isdir(os.path.join(cpudir, 'cache')):
        os.makedirs(os.path.join(cpudir, 'cache'))

    file_append((cpudir, 'online'), '1')
    file_append((cpudir, 'topology', 'physical_package_id'),
                physical_package_id)
    file_append((cpudir, 'topology', 'core_siblings'),
                hex_mask(core_siblings))
    file_append((cpudir, 'topology', 'core_id'), core_id)
    file_append((cpudir, 'topology', 'thread_siblings'),
                hex_mask(thread_siblings))

def register_cache(level, idu_type, size, line_size, assoc, cpus):
    fsdir = os.path.join(m5.options.outdir, 'fs')
    for i in cpus:
        cachedir = os.path.join(fsdir, 'sys', 'devices', 'system', 'cpu', 'cpu%d' % i, 'cache')

        j = 0
        while os.path.isdir(os.path.join(cachedir, 'index%d' % j)):
            j += 1
        indexdir = os.path.join(cachedir, 'index%d' % j)
        os.makedirs(indexdir)

        file_append((indexdir, 'level'), level)
        file_append((indexdir, 'type'), idu_type)
        file_append((indexdir, 'size'), "%dK" % (m5.util.convert.toMemorySize(size)/kibi))
        file_append((indexdir, 'coherency_line_size'), line_size)

        # Since cache size = number of indices * associativity * block size
        num_sets = m5.util.convert.toMemorySize(size) / int(assoc) * int(line_size)

        file_append((indexdir, 'number_of_sets'), num_sets)
        file_append((indexdir, 'physical_line_partition'), '1')
        file_append((indexdir, 'shared_cpu_map'), hex_mask(cpus))


def _redirect_paths(options):
    # Redirect filesystem syscalls from src to the first matching dests
    redirect_paths = [
        m5.objects.RedirectPath(
            app_path = "/proc",
            host_paths = ["%s/fs/proc" % m5.options.outdir]),
        m5.objects.RedirectPath(
            app_path = "/sys",
            host_paths = ["%s/fs/sys"  % m5.options.outdir]),
        m5.objects.RedirectPath(
            app_path = "/tmp",
            host_paths = ["%s/fs/tmp"  % m5.options.outdir])
        ]

    return redirect_paths

def create(system, options = None):
    """ This function parses the system object to create the pseudo file system
    @param system: The system to create the config for
    @param options: An optional argument which contains an Options.py options
           object. This is useful if when use se.py and will set the L2 cache
           size and the clock in /proc/cpuinfo if provided.

    First, this function walks the system object to find all CPUs.
    Then, this function creates the following files with the CPU information
      - /proc/cpuinfo which contains the clock  and the L2 size
        (assumes all L2s private and the same size)
      - /proc/stat simply lists all CPUs
      - /sys/devices/system/cpu/online and /sys/devices/system/cpu/possible
        These files list all of the CPUs in this system.
      - /tmp

    These files are created in the `fs` directory in the outdir path.
    """
    

    fsdir = os.path.join(m5.options.outdir, 'fs')
    replace_tree(fsdir)

    # Set up /proc
    procdir = os.path.join(fsdir, 'proc')
    os.mkdir(procdir)

    cpus = [obj for obj in system.descendants() if isinstance(obj, m5.objects.BaseCPU)]

    cpu_clock = m5.util.convert.toFrequency(options.architecture.cpu.clock) / mega
    #if hasattr(options, 'cpu_clock'):
    #cpu_clock = m5.util.convert.toFrequency(options.cpu_clock) / mega

    l2_size = m5.util.convert.toMemorySize(options.architecture.caches.L2.size) / kibi
    #if hasattr(options, 'l2_size'):
    #    l2_size = m5.util.convert.toMemorySize(options.l2_size) / kibi

    for i,cpu in enumerate(cpus):
        one_cpu = 'processor       : {proc}\n'                    + \
                  'vendor_id       : Generic\n'                   + \
                  'cpu family      : 0\n'                         + \
                  'model           : 0\n'                         + \
                  'model name      : Generic\n'                   + \
                  'stepping        : 0\n'                         + \
                  'cpu MHz         : {clock:0.3f}\n'              + \
                  'cache size:     : {l2_size}K\n'                + \
                  'physical id     : 0\n'                         + \
                  'siblings        : {num_cpus}\n'                + \
                  'core id         : {proc}\n'                    + \
                  'cpu cores       : {num_cpus}\n'                + \
                  'fpu             : yes\n'                       + \
                  'fpu exception   : yes\n'                       + \
                  'cpuid level     : 1\n'                         + \
                  'wp              : yes\n'                       + \
                  'flags           : fpu\n'                       + \
                  'cache alignment : {cacheline_size}\n'          + \
                  '\n'
        one_cpu = one_cpu.format(proc = i, num_cpus = len(cpus),
                       # Note: it would be nice to use cpu.clock, but it hasn't
                       # been finalized yet since m5.instantiate() isn't done.
                       clock = cpu_clock,
                       # Note: this assumes the L2 is private to each core
                       l2_size = l2_size,
                       cacheline_size=system.cache_line_size.getValue())
        file_append((procdir, 'cpuinfo'), one_cpu)

    file_append((procdir, 'stat'), 'cpu 0 0 0 0 0 0 0\n')
    for i in range(len(cpus)):
        file_append((procdir, 'stat'), 'cpu%d 0 0 0 0 0 0 0\n' % i)

    # Set up /sys
    sysdir = os.path.join(fsdir, 'sys')
    os.mkdir(sysdir)

    # Set up /sys/devices/system/cpu
    cpudir = os.path.join(sysdir, 'devices', 'system', 'cpu')
    os.makedirs(cpudir)

    file_append((cpudir, 'online'), '0-%d' % (len(cpus) - 1))
    file_append((cpudir, 'possible'), '0-%d' % (len(cpus) - 1))

    # Set up /tmp
    tmpdir = os.path.join(fsdir, 'tmp')
    replace_tree(tmpdir)

    system.redirect_paths = _redirect_paths(options)