# Copyright (c) 2012-2013 ARM Limited
# All rights reserved
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
# Copyright (c) 2006-2008 The Regents of The University of Michigan
# Copyright (c) 2010 Advanced Micro Devices, Inc.
# All rights reserved.
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
# Authors: Lisa Hsu

import os
import sys
import re
#from os import getcwd

import m5

from modules.options import Options

def config_etrace(cpu_cls, cpu_list, options):
    if issubclass(cpu_cls, m5.objects.O3CPU):
        # Assign the same file name to all cpus for now. This must be
        # revisited when creating elastic traces for multi processor systems.
        for cpu in cpu_list:
            # Attach the elastic trace probe listener. Set the protobuf trace
            # file names. Set the dependency window size equal to the cpu it
            # is attached to.
            cpu.traceListener = m5.objects.ElasticTrace(
                                instFetchTraceFile = options.inst_trace_file,
                                dataDepTraceFile = options.data_trace_file,
                                depWindowSize = 3 * cpu.numROBEntries)
            # Make the number of entries in the ROB, LQ and SQ very
            # large so that there are no stalls due to resource
            # limitation as such stalls will get captured in the trace
            # as compute delay. For replay, ROB, LQ and SQ sizes are
            # modelled in the Trace CPU.
            cpu.numROBEntries = 512
            cpu.LQEntries = 128
            cpu.SQEntries = 128
    else:
        m5.util.fatal("%s does not support data dependency tracing. Use a CPU model of type or inherited from O3CPU.", cpu_cls)

def find_checkpoint_dir(options, system):

    checkpoint_read_dir = options.checkpoint_directory

    if not checkpoint_read_dir:
        checkpoint_read_dir = m5.options.outdir

    dirs = os.listdir(checkpoint_read_dir)
    expr = re.compile("cpt\.([0-9]+)")
    cpts = []

    for item in dirs:
        match = expr.match(item)
        if match:
            cpts.append(match.group(1))

    cpts.sort(key=lambda b: int(b))
    cpt_num = options.checkpoint_restore
    if cpt_num > len(cpts):
        print('Checkpoint %d not found', cpt_num)
        sys.exit(1)

    cpt_starttick = int(cpts[cpt_num - 1])
    checkpoint_dir = os.path.join(checkpoint_read_dir, "cpt.%s" % cpts[cpt_num - 1])

    return cpt_starttick, checkpoint_dir


def get_max_tick(options, cpt_starttick):
    """
    Handle the max tick settings after tick frequency was resolved
    during system instantiation
    """
    maxtick_from_abs = m5.MaxTick
    maxtick_from_rel = m5.MaxTick
    maxtick_from_maxtime = m5.MaxTick
    if options.abs_max_tick:
        maxtick_from_abs = options.abs_max_tick
        #explicit_maxticks += 1
    if options.rel_max_tick:
        maxtick_from_rel = options.rel_max_tick
        if options.checkpoint_restore:
            # NOTE: this may need to be updated if checkpoints ever store
            # the ticks per simulated second
            maxtick_from_rel += cpt_starttick
            #if options.at_instruction or options.simpoint:
            #    m5.util.warn("Relative max tick specified with --at-instruction or" \
            #         " --simpoint\n      These options don't specify the " \
            #         "checkpoint start tick, so assuming\n      you mean " \
            #         "absolute max tick")
        #explicit_maxticks += 1
    if options.maxtime:
        maxtick_from_maxtime = m5.ticks.fromSeconds(options.maxtime)
        #explicit_maxticks += 1
    #if explicit_maxticks > 1:
    #    m5.util.warn("Specified multiple of --abs-max-tick, --rel-max-tick, --maxtime. Using least")
    maxtick = min([maxtick_from_abs, maxtick_from_rel, maxtick_from_maxtime])

    if options.simulation.checkpoint.restore != None and maxtick < cpt_starttick:
        print("Bad maxtick (%d) specified: Checkpoint starts starts from tick: %d", maxtick, cpt_starttick)
        sys.exit(1)

    return maxtick


def Simulation(root, testsys, options: Options):
    np = options.architecture.num_cpus
    switch_cpus = None

    if options.architecture.cpu.main_class:
        print("main class=", options.architecture.cpu.main_class)
        switch_cpus = [
            options.architecture.cpu.main_class(
                options.architecture.cpu,
                switched_out=True,
                cpu_id=i) for i in range(np)
            ]

        for i in range(np):
            print(f"proc: {i}")
            #if options.fast_forward:
            #    testsys.cpu[i].max_insts_any_thread = int(options.fast_forward)
            switch_cpus[i].system   = testsys
            switch_cpus[i].workload = testsys.cpu[i].workload
            switch_cpus[i].clk_domain = testsys.cpu[i].clk_domain
            switch_cpus[i].progress_interval = testsys.cpu[i].progress_interval
            switch_cpus[i].isa = testsys.cpu[i].isa
            switch_cpus[i].decoder = testsys.cpu[i].decoder

        testsys.switch_cpus = switch_cpus
        switch_cpu_list = [(testsys.cpu[i], switch_cpus[i]) for i in range(np)]
    else:
        print("No main class=", options.architecture.cpu.main_class)

    checkpoint_read_dir  = None
    checkpoint_write_dir = options.checkpoint_directory
    cpt_starttick = 0
    if options.checkpoint_restore:
        cpt_starttick, checkpoint_read_dir = find_checkpoint_dir(options, testsys)

    # Three ways to run simulations
    # 1. --checkpoint-mode: Create checkpoint within simulated application (ROI) - runs in atomic to completion
    # 2. --checkpoint-restore: Restore from checkpoint in detailed mode
    # 3. default: boots kernel in atomic and switch cpu after boot (via first m5exit of bootscript)

    # If we are restoring from checkpoint checkpoint_read_dir is set
    m5.instantiate(checkpoint_read_dir)

    maxtick = get_max_tick(options, cpt_starttick)

    if options.checkpoint_mode:
        print("Running in checkpoint mode")
        # simulate
        print("m5.simulate")
        exit_event = m5.simulate(maxtick - m5.curTick())
        exit_cause = exit_event.getCause()
        # simulate again without switch cpu
        print("m5.simulate")
        exit_event = m5.simulate(maxtick - m5.curTick())
        exit_cause = exit_event.getCause()

    elif options.checkpoint_restore:
        print("Running in checkpoint restore")
        # simulate
        print("m5.simulate")
        exit_event = m5.simulate(maxtick - m5.curTick())
        exit_cause = exit_event.getCause()

    else:
        print("Running in default - atomic+switch")
        # simulate
        print("m5.simulate")
        exit_event = m5.simulate(maxtick - m5.curTick())
        exit_cause = exit_event.getCause()
        # switch cpus
        print("Switch CPUs")
        m5.switchCpus(testsys, switch_cpu_list)
        #simulate
        print("m5.simulate")
        exit_event = m5.simulate(maxtick - m5.curTick())
        exit_cause = exit_event.getCause()


    num_checkpoints = 0
    while exit_cause == "checkpoint":
        if not options.checkpoint_mode:
            print("Error: Trying to write checkpoint but not in checkpoint mode")
            return

        print("Writing checkpoint {}".format(num_checkpoints))
        m5.checkpoint(os.path.join(checkpoint_write_dir, "cpt.%d"))
        num_checkpoints += 1

        if num_checkpoints == options.simulation.checkpoint.max_checkpoints:
            exit_cause = f"maximum {num_checkpoints} checkpoints dropped"
            break

        exit_event = m5.simulate(maxtick - m5.curTick())
        exit_cause = exit_event.getCause()

        print('Exiting @ tick %i because %s' % (m5.curTick(), exit_event.getCause()))

    if options.simulation.checkpoint.checkpoint_at_end:
        print("Writing final checkpoint")
        m5.checkpoint(os.path.join(checkpoint_write_dir, "cpt.%d"))

    if exit_event.getCode() != 0:
        print("Simulated exit code not 0! Exit code is", exit_event.getCode())
