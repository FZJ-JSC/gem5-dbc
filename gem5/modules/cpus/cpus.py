# Copyright (c) 2012 The Regents of The University of Michigan
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
# Authors: ICS-FORTH, Polydoros Petrakis <ppetrak@ics.forth.gr>
# Authors: ICS-FORTH, Vassilis Papaefstathiou <papaef@ics.forth.gr>
#
# Based on previous model for ARM Cortex A72 provided by Adria Armejach (BSC)
# and information from the following links regarding Cortex-A76:
# https://en.wikichip.org/wiki/arm_holdings/microarchitectures/cortex-a76
# https://www.anandtech.com/show/12785/\
#    arm-cortex-a76-cpu-unveiled-7nm-powerhouse/2
# https://www.anandtech.com/show/12785/\
#        arm-cortex-a76-cpu-unveiled-7nm-powerhouse/3

import m5
from m5.objects import OpDesc

#from modules.options.options import CPU

# Simple ALU Instructions have a latency of 1
class Cortex_A76_Simple_Int(m5.objects.FUDesc):
    opList = [ OpDesc(opClass='IntAlu', opLat=1) ]
    count = 3

# Complex ALU instructions have a variable latencies
class Cortex_A76_Complex_Int(m5.objects.FUDesc):
    opList = [ OpDesc(opClass='IntMult', opLat=3, pipelined=True),
               OpDesc(opClass='IntDiv', opLat=12, pipelined=False),
               OpDesc(opClass='IprAccess', opLat=3, pipelined=True) ]
    count = 2

# Floating point and SIMD instructions
class Cortex_A76_FP(m5.objects.FUDesc):
    opList = [ OpDesc(opClass='SimdAdd', opLat=4),
               OpDesc(opClass='SimdAddAcc', opLat=4),
               OpDesc(opClass='SimdAlu', opLat=4),
               OpDesc(opClass='SimdCmp', opLat=4),
               OpDesc(opClass='SimdCvt', opLat=3),
               OpDesc(opClass='SimdMisc', opLat=3),
               OpDesc(opClass='SimdMult',opLat=5),
               OpDesc(opClass='SimdMultAcc',opLat=5),
               OpDesc(opClass='SimdShift',opLat=3),
               OpDesc(opClass='SimdShiftAcc', opLat=3),
               OpDesc(opClass='SimdDiv', opLat=9, pipelined=False),
               OpDesc(opClass='SimdSqrt', opLat=9),
               OpDesc(opClass='SimdFloatAdd',opLat=5),
               OpDesc(opClass='SimdFloatAlu',opLat=5),
               OpDesc(opClass='SimdFloatCmp', opLat=3),
               OpDesc(opClass='SimdFloatCvt', opLat=3),
               OpDesc(opClass='SimdFloatDiv', opLat=3),
               OpDesc(opClass='SimdFloatMisc', opLat=3),
               OpDesc(opClass='SimdFloatMult', opLat=3),
               OpDesc(opClass='SimdFloatMultAcc',opLat=5),
               OpDesc(opClass='SimdFloatSqrt', opLat=9),
               OpDesc(opClass='SimdReduceAdd'),
               OpDesc(opClass='SimdReduceAlu'),
               OpDesc(opClass='SimdReduceCmp'),
               OpDesc(opClass='SimdFloatReduceAdd'),
               OpDesc(opClass='SimdFloatReduceCmp'),
               OpDesc(opClass='FloatAdd', opLat=5),
               OpDesc(opClass='FloatCmp', opLat=5),
               OpDesc(opClass='FloatCvt', opLat=5),
               OpDesc(opClass='FloatDiv', opLat=9, pipelined=False),
               OpDesc(opClass='FloatSqrt', opLat=33, pipelined=False),
               OpDesc(opClass='FloatMult', opLat=4),
               OpDesc(opClass='FloatMultAcc', opLat=5),
               OpDesc(opClass='FloatMisc', opLat=3) ]
    count = 2

# Load/Store Units
class Cortex_A76_Load(m5.objects.FUDesc):
    opList = [ OpDesc(opClass='MemRead'),
               OpDesc(opClass='FloatMemRead') ]
    count = 2

class Cortex_A76_Store(m5.objects.FUDesc):
    opList = [ OpDesc(opClass='MemWrite'),
               OpDesc(opClass='FloatMemWrite') ]
    count = 1

class Cortex_A76_PredALU(m5.objects.FUDesc):
    opList = [ OpDesc(opClass='SimdPredAlu') ]
    count = 1

# Functional Units for this CPU
class Cortex_A76_FUP(m5.objects.FUPool):
    FUList = [Cortex_A76_Simple_Int(),
              Cortex_A76_Complex_Int(),
              Cortex_A76_Load(),
              Cortex_A76_Store(),
              Cortex_A76_PredALU(),
              Cortex_A76_FP()]

# Bi-Mode Branch Predictor
class Cortex_A76_BP(m5.objects.BiModeBP):
    globalPredictorSize = 8192
    globalCtrBits = 2
    choicePredictorSize = 8192
    choiceCtrBits = 2
    BTBEntries = 4096
    BTBTagSize = 16
    RASSize = 16
    instShiftAmt = 2

class Cortex_A76(m5.objects.O3CPU):
    LSQDepCheckShift = 0
    LFSTSize = 1024
    SSITSize = 1024
    decodeToFetchDelay = 1
    renameToFetchDelay = 1
    iewToFetchDelay = 1
    commitToFetchDelay = 1
    renameToDecodeDelay = 1
    iewToDecodeDelay = 1
    commitToDecodeDelay = 1
    iewToRenameDelay = 1
    commitToRenameDelay = 1
    commitToIEWDelay = 1
    fetchWidth = 4
    fetchBufferSize = 16
    fetchToDecodeDelay = 1
    decodeWidth = 4
    decodeToRenameDelay = 1
    renameWidth = 4
    renameToIEWDelay = 1
    issueToExecuteDelay = 1
    dispatchWidth = 8
    issueWidth = 8
    wbWidth = 8
    fuPool = Cortex_A76_FUP()
    iewToCommitDelay = 1
    renameToROBDelay = 1
    commitWidth = 8
    squashWidth = 8
    trapLatency = 13
    backComSize = 5
    forwardComSize = 5
    numROBEntries = 192
    # the default value for numPhysVecPredRegs  is 32 in O3 config
    numPhysVecPredRegs = 64
    LQEntries = 68
    SQEntries = 72
    numIQEntries = 120

    #switched_out = False
    branchPred = Cortex_A76_BP()
    #branchPred = Param.BranchPredictor(TournamentBP(
    #    numThreads = Parent.numThreads), "Branch Predictor")

class R_CPU_Cortex(Cortex_A76):
    fetchWidth = 8
    decodeWidth = 8
    issueWidth = 8
    LQEntries = 96
    SQEntries = 96
    numIQEntries = 120
    numROBEntries = 224
    numPhysVecPredRegs = 64
    numPhysVecRegs = 364
    
    def __init__(self, opts, **kwargs):
        super(R_CPU_Cortex, self).__init__(**kwargs)


# Simple ALU Instructions have a latency of 1
class R_CPU_Simple_Int(m5.objects.FUDesc):
    opList = [ OpDesc(opClass='IntAlu', opLat=1) ]
    count = 3

# Complex ALU instructions have a variable latencies
class R_CPU_Complex_Int(m5.objects.FUDesc):
    opList = [ OpDesc(opClass='IntMult', opLat=3, pipelined=True),
               OpDesc(opClass='IntDiv', opLat=12, pipelined=False),
               OpDesc(opClass='IprAccess', opLat=3, pipelined=True) ]
    count = 2

# Floating point and SIMD instructions
class R_CPU_FP(m5.objects.FUDesc):
    opList = [ OpDesc(opClass='SimdAdd', opLat=4),
               OpDesc(opClass='SimdAddAcc', opLat=4),
               OpDesc(opClass='SimdAlu', opLat=4),
               OpDesc(opClass='SimdCmp', opLat=4),
               OpDesc(opClass='SimdCvt', opLat=3),
               OpDesc(opClass='SimdMisc', opLat=3),
               OpDesc(opClass='SimdMult',opLat=5),
               OpDesc(opClass='SimdMultAcc',opLat=5),
               OpDesc(opClass='SimdShift',opLat=3),
               OpDesc(opClass='SimdShiftAcc', opLat=3),
               OpDesc(opClass='SimdDiv', opLat=9, pipelined=False),
               OpDesc(opClass='SimdSqrt', opLat=9),
               OpDesc(opClass='SimdFloatAdd',opLat=5),
               OpDesc(opClass='SimdFloatAlu',opLat=5),
               OpDesc(opClass='SimdFloatCmp', opLat=3),
               OpDesc(opClass='SimdFloatCvt', opLat=3),
               OpDesc(opClass='SimdFloatDiv', opLat=3),
               OpDesc(opClass='SimdFloatMisc', opLat=3),
               OpDesc(opClass='SimdFloatMult', opLat=3),
               OpDesc(opClass='SimdFloatMultAcc',opLat=5),
               OpDesc(opClass='SimdFloatSqrt', opLat=9),
               OpDesc(opClass='SimdReduceAdd'),
               OpDesc(opClass='SimdReduceAlu'),
               OpDesc(opClass='SimdReduceCmp'),
               OpDesc(opClass='SimdFloatReduceAdd'),
               OpDesc(opClass='SimdFloatReduceCmp'),
               OpDesc(opClass='FloatAdd', opLat=5),
               OpDesc(opClass='FloatCmp', opLat=5),
               OpDesc(opClass='FloatCvt', opLat=5),
               OpDesc(opClass='FloatDiv', opLat=9, pipelined=False),
               OpDesc(opClass='FloatSqrt', opLat=33, pipelined=False),
               OpDesc(opClass='FloatMult', opLat=4),
               OpDesc(opClass='FloatMultAcc', opLat=5),
               OpDesc(opClass='FloatMisc', opLat=3) ]
    count = 2

# Load/Store Units
class R_CPU_Load(m5.objects.FUDesc):
    opList = [ OpDesc(opClass='MemRead'),
               OpDesc(opClass='FloatMemRead') ]
    count = 2

class R_CPU_Store(m5.objects.FUDesc):
    opList = [ OpDesc(opClass='MemWrite'),
               OpDesc(opClass='FloatMemWrite') ]
    count = 1

class R_CPU_PredALU(m5.objects.FUDesc):
    opList = [ OpDesc(opClass='SimdPredAlu') ]
    count = 1

# Functional Units for this CPU
class R_CPU_FUP(m5.objects.FUPool):
    FUList = [R_CPU_Simple_Int(),
              R_CPU_Complex_Int(),
              R_CPU_Load(),
              R_CPU_Store(),
              R_CPU_PredALU(),
              R_CPU_FP()]

class R_BP_Tournament(m5.objects.TournamentBP):
    pass

# Bi-Mode Branch Predictor
class R_BP_BiMode(m5.objects.BiModeBP):
    globalPredictorSize = 8192
    globalCtrBits = 2
    choicePredictorSize = 8192
    choiceCtrBits = 2
    BTBEntries = 4096
    BTBTagSize = 16
    RASSize = 16
    instShiftAmt = 2

class R_CPU(m5.objects.O3CPU):
    LSQDepCheckShift = 0
    LFSTSize = 1024
    SSITSize = 1024
    decodeToFetchDelay = 1
    renameToFetchDelay = 1
    iewToFetchDelay = 1
    commitToFetchDelay = 1
    renameToDecodeDelay = 1
    iewToDecodeDelay = 1
    commitToDecodeDelay = 1
    iewToRenameDelay = 1
    commitToRenameDelay = 1
    commitToIEWDelay = 1
    fetchToDecodeDelay = 1
    decodeToRenameDelay = 1
    renameWidth = 8
    renameToIEWDelay = 1
    issueToExecuteDelay = 1
    dispatchWidth = 8
    wbWidth = 8
    iewToCommitDelay = 1
    renameToROBDelay = 1
    commitWidth = 8
    squashWidth = 8
    trapLatency = 13
    backComSize = 5
    forwardComSize = 5
    fetchWidth = 8
    decodeWidth = 8
    issueWidth = 8
    numPhysVecPredRegs = 64
    numPhysVecRegs = 364
    numIQEntries = 120
    LQEntries = 96
    SQEntries = 96
    fetchBufferSize = 64
    #fetchQueueSize = 64
    numROBEntries = 224
    #switched_out = False

    fuPool = R_CPU_FUP()
    branchPred = R_BP_BiMode()

    def __init__(self, opts, **kwargs):
        super(R_CPU, self).__init__(**kwargs)

        if opts.branch_predictor == "Tournament":
            self.branchPred = R_BP_Tournament()

        if opts.branch_predictor == "BiMode":
            self.branchPred = R_BP_BiMode()

        parameters = opts.parameters["R_CPU"]

        self.fetchBufferSize    = parameters["fetchBufferSize"]
        self.LQEntries          = parameters["LQEntries"]
        self.SQEntries          = parameters["SQEntries"]
        self.LSQDepCheckShift   = parameters["LSQDepCheckShift"]
        self.numIQEntries       = parameters["numIQEntries"]
        self.numPhysVecPredRegs = parameters["numPhysVecPredRegs"]
        self.numPhysVecRegs     = parameters["numPhysVecRegs"]
        self.numROBEntries      = parameters["numROBEntries"]
        self.renameToIEWDelay   = parameters["renameToIEWDelay"]
        self.backComSize    = parameters["backComSize"]
        self.forwardComSize = parameters["forwardComSize"]
        self.decodeWidth = parameters["decodeWidth"]
        self.fetchWidth  = parameters["fetchWidth"]
        self.issueWidth  = parameters["issueWidth"]
        self.renameWidth = parameters["renameWidth"]


class AtomicSimple(m5.objects.AtomicSimpleCPU):
    def __init__(self, opts, **kwargs):
        super(AtomicSimple, self).__init__(**kwargs)

class TimingSimple(m5.objects.TimingSimpleCPU):
    def __init__(self, opts, **kwargs):
        super(TimingSimple, self).__init__(**kwargs)

class DefaultO3CPU(m5.objects.O3CPU):
    def __init__(self, opts, **kwargs):
        super(DefaultO3CPU, self).__init__(**kwargs)
        if opts.branchPred == "Tournament":
            self.branchPred = R_BP_Tournament()

        if opts.branchPred == "BiMode":
            self.branchPred = R_BP_BiMode()

        self.LQEntries = opts.LQEntries
        self.SQEntries = opts.SQEntries
        self.LSQDepCheckShift   = opts.LSQDepCheckShift
        self.numIQEntries       = opts.numIQEntries
        self.numPhysVecPredRegs = opts.numPhysVecPredRegs
        self.numPhysVecRegs     = opts.numPhysVecRegs
        self.numROBEntries      = opts.numROBEntries
        self.renameToIEWDelay   = opts.renameToIEWDelay

        self.backComSize    = opts.backComSize
        self.forwardComSize = opts.forwardComSize
