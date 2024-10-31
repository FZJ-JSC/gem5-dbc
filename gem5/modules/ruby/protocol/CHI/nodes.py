# Copyright (c) 2021 ARM Limited
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


import m5

from modules.options import Options

from modules.ruby.protocol.CHI import controllers
from modules.ruby.protocol.CHI.util import slc_mask


from modules.caches.prefetcher import Stride
from modules.caches.prefetcher import Tagged
from modules.caches.prefetcher import IndirectMemory
from modules.caches.prefetcher import SignaturePath
from modules.caches.prefetcher import SignaturePath2
from modules.caches.prefetcher import AMPM
from modules.caches.prefetcher import DCPT
from modules.caches.prefetcher import IrregularStreamBuffer
from modules.caches.prefetcher import SlimAMPM
from modules.caches.prefetcher import BOP
from modules.caches.prefetcher import SBOOE
from modules.caches.prefetcher import STeMS
from modules.caches.prefetcher import PIF

def get_prefetcher(options):
    def get_prefetcher_class(name: str):
        return dict(
            Stride=Stride,
            Tagged=Tagged,
            IndirectMemory=IndirectMemory,
            SignaturePath=SignaturePath,
            SignaturePath2=SignaturePath2,
            AMPM=AMPM,
            DCPT=DCPT,
            IrregularStreamBuffer=IrregularStreamBuffer,
            SlimAMPM=SlimAMPM,
            BOP=BOP,
            SBOOE=SBOOE,
            STeMS=STeMS,
            PIF=PIF
        ).get(name, None)
    pf_cls = get_prefetcher_class(options.selected) if options != None else None
    print(f"Prefetcher is {pf_cls.__name__ if pf_cls else 'None'}")
    print(f"Configuration: {options.configuration[options.selected] if pf_cls else 'None'}")
    return m5.objects.RubyPrefetcherWrapper(prefetcher=pf_cls(parameters=options.configuration[options.selected])) if pf_cls != None else m5.objects.NULL


class CHI_Node(m5.objects.SubSystem):
    '''
    Base class with common functions for setting up Cache or Memory
    controllers that are part of a CHI RNF, RNFI, HNF, or SNF nodes.
    Notice getNetworkSideControllers and getAllControllers must be implemented
    in the derived classes.
    '''

    def __init__(self, ruby_system):
        super(CHI_Node, self).__init__()
        self._ruby_system = ruby_system
        self._network = ruby_system.network

        self._router_id = None
        self._numa_id = 0

    def getNetworkSideControllers(self):
        '''
        Returns all ruby controllers that need to be connected to the
        network
        '''
        raise NotImplementedError()

    def getAllControllers(self):
        '''
        Returns all ruby controllers associated with this node
        '''
        raise NotImplementedError()

    def setDownstream(self, cntrls):
        '''
        Sets cntrls as the downstream list of all controllers in this node
        '''
        for c in self.getNetworkSideControllers():
            c.downstream_destinations = cntrls

    def connectController(self, cntrl, options: Options):
        '''
        Creates and configures the messages buffers for the CHI input/output
        ports that connect to the network
        '''
        cntrl.reqOut = m5.objects.MessageBuffer()
        cntrl.rspOut = m5.objects.MessageBuffer()
        cntrl.snpOut = m5.objects.MessageBuffer()
        cntrl.datOut = m5.objects.MessageBuffer()
        cntrl.reqIn = m5.objects.MessageBuffer()
        cntrl.rspIn = m5.objects.MessageBuffer()
        cntrl.snpIn = m5.objects.MessageBuffer()
        cntrl.datIn = m5.objects.MessageBuffer()

        # All CHI ports are always connected to the network.
        # Controllers that are not part of the getNetworkSideControllers list
        # still communicate using internal routers, thus we need to wire-up the
        # ports
        cntrl.reqOut.out_port = self._network.in_port
        cntrl.rspOut.out_port = self._network.in_port
        cntrl.snpOut.out_port = self._network.in_port
        cntrl.datOut.out_port = self._network.in_port
        cntrl.reqIn.in_port = self._network.out_port
        cntrl.rspIn.in_port = self._network.out_port
        cntrl.snpIn.in_port = self._network.out_port
        cntrl.datIn.in_port = self._network.out_port

        # Set the data message size
        cntrl.data_channel_size = options.architecture.NOC.network.data_width


class CPUSequencerWrapper:
    '''
    Other generic configuration scripts assume a matching number of sequencers
    and cpus. This wraps the instruction and data sequencer so they are
    compatible with the other scripts. This assumes all scripts are using
    connectCpuPorts/connectIOPorts to bind ports
    '''

    def __init__(self, iseq, dseq):
        # use this style due to __setattr__ override below
        self.__dict__['inst_seq'] = iseq
        self.__dict__['data_seq'] = dseq
        self.__dict__['support_data_reqs'] = True
        self.__dict__['support_inst_reqs'] = True
        # Compatibility with certain scripts that wire up ports
        # without connectCpuPorts
        self.__dict__['slave'] = dseq.in_ports
        self.__dict__['in_ports'] = dseq.in_ports

    def connectCpuPorts(self, cpu):
        assert(isinstance(cpu, m5.objects.BaseCPU))
        cpu.icache_port = self.inst_seq.in_ports
        for p in cpu._cached_ports:
            if str(p) != 'icache_port':
                exec('cpu.%s = self.data_seq.in_ports' % p)
        cpu.connectUncachedPorts(
            self.data_seq.in_ports, self.data_seq.interrupt_out_port)


    def connectIOPorts(self, piobus):
        self.data_seq.connectIOPorts(piobus)

    def __setattr__(self, name, value):
        setattr(self.inst_seq, name, value)
        setattr(self.data_seq, name, value)


class CHI_RNF(CHI_Node):
    '''
    Defines a CHI request node.
    Notice all contollers and sequencers are set as children of the cpus, so
    this object acts more like a proxy for seting things up and has no topology
    significance unless the cpus are set as its children at the top level
    '''

    def __init__(self, options: Options, cpus, ruby_system, router_id = None, numa_id=0):
        super(CHI_RNF, self).__init__(ruby_system)

        # All sequencers and controllers
        self._seqs = []
        self._cntrls = []

        # Last level controllers in this node, i.e.,
        # the ones that will send requests to the home nodes
        self._ll_cntrls = []

        self._cpus = cpus

        self._router_id = router_id
        self._numa_id   = numa_id

        self.create_caches(options)

    def create_caches(self, options: Options):
        print("[CHI_RNF@create_caches]")
        # First creates L1 caches and sequencers
        for cpu in self._cpus:
            # Set NUMA Id
            cpu.numa_id = self._numa_id

            cpu.inst_sequencer = controllers.Sequencer(
                self._ruby_system,
                max_outstanding_requests=options.architecture.caches.L1I.sequencer.max_outstanding_requests
            )
            cpu.data_sequencer = controllers.Sequencer(
                self._ruby_system,
                max_outstanding_requests=options.architecture.caches.L1D.sequencer.max_outstanding_requests
            )

            self._seqs.append(CPUSequencerWrapper(cpu.inst_sequencer, cpu.data_sequencer))

            l1i_pf = get_prefetcher(options.architecture.caches.L1I.prefetcher)
            l1d_pf = get_prefetcher(options.architecture.caches.L1D.prefetcher)

            # cache controllers
            cpu.l1i = controllers.CHI_L1Controller(
                self._ruby_system,
                cpu.inst_sequencer,
                options.architecture.caches.L1I,
                prefetcher=l1i_pf
            )
            cpu.l1d = controllers.CHI_L1Controller(
                self._ruby_system,
                cpu.data_sequencer,
                options.architecture.caches.L1D,
                prefetcher=l1d_pf
            )

            print(f"L1 Prefetcher: I -> {l1i_pf}, D -> {l1d_pf}")
            cpu.inst_sequencer.dcache = m5.objects.NULL
            cpu.data_sequencer.dcache = cpu.l1d.cache

            cpu.l1d.sc_lock_enabled = True

            cpu._ll_cntrls = [cpu.l1i, cpu.l1d]
            for c in cpu._ll_cntrls:
                self._cntrls.append(c)
                self.connectController(c, options)
                self._ll_cntrls.append(c)

    def getSequencers(self):
        return self._seqs

    def getAllControllers(self):
        return self._cntrls

    def getNetworkSideControllers(self):
        return self._cntrls

    def setDownstream(self, cntrls):
        for c in self._ll_cntrls:
            c.downstream_destinations = cntrls

    def getCpus(self):
        return self._cpus

    # Adds a private L2 for each cpu
    def addPrivL2Cache(self, options: Options):
        self._ll_cntrls = []

        for cpu in self._cpus:
            l2_pf = get_prefetcher(options.architecture.caches.L2.prefetcher)

            cpu.l2 = controllers.CHI_L2Controller(
                self._ruby_system,
                options.architecture.caches.L2,
                prefetcher=l2_pf
            )

            print(f"L2 Prefetcher: {l2_pf}")
            self._cntrls.append(cpu.l2)
            self.connectController(cpu.l2, options)

            self._ll_cntrls.append(cpu.l2)

            for c in cpu._ll_cntrls:
                c.downstream_destinations = [cpu.l2]
            cpu._ll_cntrls = [cpu.l2]


class CHI_HNF(CHI_Node):
    '''
    Encapsulates an HNF cache/directory controller.
    Before the first controller is created, the class method
    CHI_HNF.createAddrRanges must be called before creating any CHI_HNF object
    to set-up the interleaved address ranges used by the HNFs
    '''

    _addr_ranges = {}
    @classmethod
    def createAddrRanges(cls, options, mem_ranges, hnf_ids: list, numa_id=0):
        # Create the HNFs interleaved addr ranges
        cache_line_size = options.architecture.caches.cache_line_size

        # Create the HNFs interleaved addr ranges
        mask = slc_mask(len(hnf_ids), cache_line_size)
        for i, hnf_id in enumerate(hnf_ids):
            ranges = []
            for mem_range in mem_ranges:
                # [lnghrdntcr]: If mem_ranges is a list, consider the address range as starting from the beginning 
                # of the N memory ranges, and the size being the sum of sizes of the mem_ranges
                if type(mem_range) == list: 
                    mem_range_start = mem_range[0].start
                    mem_range_size  = sum([s.size() for s in mem_range])
                else: 
                    mem_range_start = mem_range.start
                    mem_range_size  = mem_range.size()

                addr_range = m5.objects.AddrRange(
                    mem_range_start,
                    size = mem_range_size, 
                    masks = mask,
                    intlvMatch = i
                )
                ranges.append(addr_range)
            cls._addr_ranges[hnf_id] = (ranges, numa_id, i)

    @classmethod
    def getAddrRanges(cls, hnf_id):
        assert(len(cls._addr_ranges) != 0)
        return cls._addr_ranges[hnf_id]

    # The CHI controller can be a child of this object or another if 'parent' is specified
    def __init__(self, options : Options, hnf_id, ruby_system, parent=None, router_id = None, numa_id=0):
        super(CHI_HNF, self).__init__(ruby_system)

        addr_ranges, addr_numa_id, intlvMatch = CHI_HNF.getAddrRanges(hnf_id)
        # All ranges should have the same interleaving
        assert(len(addr_ranges) >= 1)
        # Node NUMA ID should be same as address range NUMA ID
        assert(numa_id == addr_numa_id)

        self._router_id = router_id
        self._numa_id = numa_id

        slc_pf = get_prefetcher(options.architecture.caches.SLC.prefetcher)

        self._cntrl = controllers.CHI_HNFController(
            ruby_system,
            addr_ranges,
            options.architecture.caches.SLC,
            prefetcher=slc_pf
        )

        if parent == None:
            self.cntrl = self._cntrl
        else:
            parent.cntrl = self._cntrl

        self.connectController(self._cntrl, options)

    def getAllControllers(self):
        return [self._cntrl]

    def getNetworkSideControllers(self):
        return [self._cntrl]


class CHI_SNF_Base(CHI_Node):
    '''
    Creates CHI node controllers for the memory controllers
    '''

    # The CHI controller can be a child of this object or another if
    # 'parent' if specified
    def __init__(self, options : Options, ruby_system, parent=None, region_id=None):
        super(CHI_SNF_Base, self).__init__(ruby_system)

        self._cntrl = controllers.CHI_Memory_Controller(ruby_system)

        self.connectController(self._cntrl, options)

        self._region_id = region_id

        if parent:
            parent.cntrl = self._cntrl
        else:
            self.cntrl = self._cntrl


    def getAllControllers(self):
        return [self._cntrl]
    
    def getAllRegionIdControllers(self):
        return [(self._region_id, self._cntrl)]

    def getNetworkSideControllers(self):
        return [self._cntrl]

    def getMemRange(self, mem_ctrl):
        # TODO need some kind of transparent API for
        # MemCtrl+DRAM vs SimpleMemory
        if hasattr(mem_ctrl, 'range'):
            return mem_ctrl.range
        else:
            return mem_ctrl.dram.range


class CHI_SNF_BootMem(CHI_SNF_Base):
    '''
    Create the SNF for the boot memory
    '''
    def __init__(self, options: Options, ruby_system, parent, bootmem):
        super().__init__(options, ruby_system, parent)
        self._cntrl.memory_out_port = bootmem.port
        self._cntrl.addr_ranges = self.getMemRange(bootmem)


class CHI_SNF_MainMem(CHI_SNF_Base):
    '''
    Create the SNF for a list main memory controllers
    '''
    def __init__(self, options: Options, ruby_system, parent=None, mem_ctrl = None, router_id = None, region_id = None, numa_id=0):
        super().__init__(options, ruby_system, parent)
        self._router_id = router_id
        self._numa_id   = numa_id
        self._region_id = region_id
        if mem_ctrl:
            self._cntrl.memory_out_port = mem_ctrl.port
            self._cntrl.addr_ranges = self.getMemRange(mem_ctrl)
        # else bind ports and range later


class CHI_RNI_Base(CHI_Node):
    '''
    Request node without cache / DMA
    '''
    # The CHI controller can be a child of this object or another if
    # 'parent' if specified
    def __init__(self, options : Options, ruby_system, parent):
        super().__init__(ruby_system)

        self._sequencer = controllers.Sequencer(
            ruby_system,
            clk_domain  = ruby_system.clk_domain
        )

        self._cntrl = controllers.CHI_DMAController(ruby_system, self._sequencer)

        if parent:
            parent.cntrl = self._cntrl
        else:
            self.cntrl = self._cntrl

        self.connectController(self._cntrl, options)


    def getAllControllers(self):
        return [self._cntrl]

    def getNetworkSideControllers(self):
        return [self._cntrl]


class CHI_RNI_DMA(CHI_RNI_Base):
    '''
    DMA controller wiredup to a given dma port
    '''
    def __init__(self, options : Options, ruby_system, dma_port, parent):
        super().__init__(options, ruby_system, parent)
        assert(dma_port != None)
        self._sequencer.in_ports = dma_port


class CHI_RNI_IO(CHI_RNI_Base):
    '''
    DMA controller wiredup to ruby_system IO port
    '''
    def __init__(self, options : Options, ruby_system, parent):
        super().__init__(options, ruby_system, parent)
        ruby_system._io_port = self._sequencer
