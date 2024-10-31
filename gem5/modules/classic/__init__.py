import m5


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
        mem_range = self.realview._mem_regions[0]
        mem_range_size = mem_range.size()
        assert mem_range_size >= int(m5.objects.Addr(mem_size))
        system_mem_range = m5.objects.AddrRange(start=mem_range.start, size=mem_size)
        
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
#if options.architecture.mem_type == "HMC_2500_1x32":
#    HMChost = HMC.config_hmc_host_ctrl(options, system)
#    HMC.config_hmc_dev(options, system, HMChost.hmc_host)
#    subsystem = system.hmc_dev
#    xbar = system.hmc_dev.xbar
#else:
    subsystem = self
    xbar = self.membus
        
    mem_ctrls = []
    mem_channels = options.architecture.memory.channels
    if (options.architecture.NOC.active):
        mem_channels = options.architecture.NOC.controllers

    # For every range (most systems will only have one), create an array of controllers and set their parameters to match their address mapping in the case of a DRAM
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


def configure_classic(system, options, piobus = None, dma_ports = [], bootmem=None):
    for i in range(options.architecture.num_cpus):
        if options.architecture.cpu.use_cpu_checker:
            system.cpu[i].addCheckerCpu()
        system.cpu[i].createThreads()
        for j in range(system.cpu[i].numThreads):
            system.cpu[i].isa[j].sve_vl_se = 2

    if options.elastic_trace and options.checkpoint_restore == None and not options.fast_forward:
        CpuConfig.config_etrace(init_cpu_class, system.cpu, options)

    if options.architecture.caches.cache_levels > 0:
        # By default the IOCache runs at the system clock
        system.iocache = m5.objects.IOCache(addr_ranges = system.mem_ranges)
        system.iocache.cpu_side = system.iobus.master
        system.iocache.mem_side = system.membus.slave
    elif not options.architecture.memory.external_memory_system:
        system.iobridge = m5.objects.Bridge(delay='50ns', ranges = system.mem_ranges)
        system.iobridge.slave = system.iobus.master
        system.iobridge.master = system.membus.slave

    configure_caches(system, options)
    configure_memory(system, options)