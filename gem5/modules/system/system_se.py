
import sys, os
from math import log, ceil

import m5

from modules.options import Options
from modules import filesystem
from modules import ruby


class ProcessSE(m5.objects.Process):
    def __init__(self, options, **kwargs):
        super(ProcessSE, self).__init__(**kwargs)
        self.pid = options.pid
        self.executable = options.cmd[0]
        self.cmd = options.cmd
        self.cwd = options.cwd
        self.env = options.env
        self.input  = options.input
        self.output = options.output
        self.errout = options.errout

class MemBus(m5.objects.SystemXBar):
    def __init__(self, **kwargs):
        super(MemBus, self).__init__(**kwargs)

class EPISystemSE(m5.objects.System):
    def __init__(self, options, **kwargs):
        super(EPISystemSE, self).__init__(**kwargs)

        self.workload = m5.objects.SEWorkload()

        self.mem_mode = options.architecture.cpu.init_class.memory_mode()
        self.mem_ranges = [m5.objects.AddrRange(options.architecture.memory.size)]
        self.cache_line_size = options.architecture.caches.cache_line_size

        # Create a top-level voltage domain
        self.voltage_domain = m5.objects.VoltageDomain(voltage = options.architecture.system.voltage)
        
        # Create a source clock for the system and set the clock period
        self.clk_domain = m5.objects.SrcClockDomain(clock=options.architecture.system.clock, voltage_domain=self.voltage_domain)
        
        # Create a CPU voltage domain
        self.cpu_voltage_domain = m5.objects.VoltageDomain()

        # Create a source clock for the CPUs and set the clock period
        self.cpu_clk_domain = m5.objects.SrcClockDomain(
            clock=options.architecture.cpu.clock,
            voltage_domain=self.cpu_voltage_domain)
        
        self.cpu = [ options.architecture.cpu.init_class( 
            options.architecture.cpu, 
            clk_domain=self.cpu_clk_domain, 
            cpu_id=i 
            ) for i in range(options.architecture.num_cpus) ]
        
        process = ProcessSE(options.process)
        
        for i in range(options.architecture.num_cpus):
            if options.architecture.cpu.use_cpu_checker:
                self.cpu[i].addCheckerCpu()
            self.cpu[i].workload = process
            self.cpu[i].createThreads()
            for j in range(self.cpu[i].numThreads):
                self.cpu[i].isa[j].sve_vl_se = int(options.architecture.cpu.sve_length)/128

        if options.architecture.NOC.active:
            ruby.configure_ruby(self, options)
            assert(options.architecture.num_cpus == len(self.ruby._cpu_ports))

            # self.ruby.clk_domain = m5.objects.SrcClockDomain(clock = options.architecture.NOC.clock, voltage_domain = self.voltage_domain)

            # for i in range(options.architecture.num_cpus):
            #     ruby_port = self.ruby._cpu_ports[i]
            #     # Create the interrupt controller and connect its ports to Ruby
            #     self.cpu[i].createInterruptController()
            #     # Connect the cpu's cache ports to Ruby
            #     self.cpu[i].icache_port = ruby_port.slave
            #     self.cpu[i].dcache_port = ruby_port.slave

        else:
            self.membus = MemBus()
            self.system_port = self.membus.slave
            self.configure_caches(options)
            self.configure_memory(options)
            filesystem.create(self, options)




    def configure_caches(self, options):
        from modules.caches import L1I, L1D, WalkCache, L2, L3Slice

        # Set the cache line size for the entire system
        self.cache_line_size = options.architecture.caches.cache_line_size
        
        last_cache_level = options.architecture.caches.cache_levels

        #membus = self.membus
        
        if last_cache_level == 3:
            bus_width_L2_L3_slice = options.parameters['caches']['SLC']['bus-width']
            L3_slice_per_core     = options.parameters['caches']['SLC']['slices_per_core']
            L2_xbar_width         = options.parameters['caches']['L2']['xbar_width']
            
            for cpu in self.cpu:
                cpu.addTwoLevelCacheHierarchy( 
                    L1I(options.parameters['caches']['L1I']),
                    L1D(options.parameters['caches']['L1D']),
                    L2(options.parameters['caches']['L2']),
                    WalkCache(options.parameters['caches']['WalkCache']),
                    WalkCache(options.parameters['caches']['WalkCache']),
                    m5.objects.L2XBar(width=L2_xbar_width, clk_domain=self.cpu_clk_domain)
                    )
            mem_size = options.architecture.memory.size
            mem_range = m5.objects.AddrRange('2GB', size='2GB') #self.realview._mem_regions[0]
            mem_range_size = mem_range.size()
            assert mem_range_size >= int(m5.objects.Addr(mem_size))
            
            #system_mem_range = m5.objects.AddrRange(start=mem_range.start, size=mem_size)
            
            # For SE mode, address range should be [0:memsize]
            system_mem_range = m5.objects.AddrRange(start=0, size=mem_size)
                    
            l3_array = []
            
            n_cores = len(self.cpu)
            n_bits = int(ceil(log(L3_slice_per_core*n_cores, 2)))
            
            for match in range(0, pow(2,n_bits)):
                l3_aux = L3Slice(options.parameters['caches']['SLC'],clk_domain=self.clk_domain)
                # Build address range for each l3
                addr_range = m5.objects.AddrRange(0, 
                  size=system_mem_range.end -1, 
                  intlvBits = n_bits, 
                  intlvHighBit = n_bits + 5, 
                  intlvMatch = match)
                l3_aux.addr_ranges = addr_range
                l3_array.append(l3_aux)
            
            self.l3 = l3_array
            self.toL3Bus = m5.objects.L2XBar(width=int(bus_width_L2_L3_slice))

            # For each l3 connect to the XBar
            for l3 in self.l3:
                self.toL3Bus.master = l3.cpu_side
                l3.mem_side = self.membus.slave
            
            #membus = self.toL3Bus
            
        # connect each cluster to the memory hierarchy
        for cpu in self.cpu:
            cpu.createInterruptController()
            if last_cache_level == 3:
                cpu.connectAllPorts(self.toL3Bus, self.membus)
            else:
                cpu.connectAllPorts(self.membus)
    
    def configure_memory(self, options):
        from modules.memory import create_memory_interface #HBM, HBM2, DDR4_2400_8x8

        subsystem = self
        xbar = self.membus

        mem_ctrls = []
        mem_channels = options.architecture.memory.channels
        if (options.architecture.NOC.active):
            mem_channels = options.architecture.NOC.controllers

        for r in self.mem_ranges:
            for i in range(mem_channels):
                dram_iface = create_memory_interface(r, i, mem_channels, options)
                if(options.architecture.memory.model == 'Simple'):
                    mem_ctrl = dram_iface
                else:
                    mem_ctrl = m5.objects.MemCtrl()
                    mem_ctrl.dram = dram_iface
                mem_ctrls.append(mem_ctrl)
        
        subsystem.mem_ctrls = mem_ctrls
        
        # Connect the controllers to the membus
        for i in range(len(subsystem.mem_ctrls)):
            if options.architecture.memory.model == "HMC_2500_1x32":
                subsystem.mem_ctrls[i].port = xbar[i/4].master
                # Set memory device size. There is an independent controller for each vault. All vaults are same size.
                subsystem.mem_ctrls[i].device_size = options.hmc_dev_vault_size
            else:
                subsystem.mem_ctrls[i].port = xbar.master

