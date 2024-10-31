# Copyright (c) 2010-2012, 2015-2019 ARM Limited
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
# Copyright (c) 2012-2014 Mark D. Hill and David A. Wood
# Copyright (c) 2010-2011 Advanced Micro Devices, Inc.
# Copyright (c) 2006-2008 The Regents of The University of Michigan
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
# Authors: Kevin Lim
# Authors: Ali Saidi
#          Brad Beckmann

import sys, os
from math import log, ceil

import m5

from modules.options import Options
from modules import classic, ruby

def create_cow_image(name):
    """Helper function to create a Copy-on-Write disk image"""
    image = m5.objects.CowDiskImage()
    image.child.image_file = name

    return image

def attach_9p(parent, bus):
    viopci = m5.objects.PciVirtIO()
    viopci.vio = m5.objects.VirtIO9PDiod()
    viodir = os.path.join(m5.options.outdir, '9p')
    viopci.vio.root = os.path.join(viodir, 'share')
    viopci.vio.socketPath = os.path.join(viodir, 'socket')
    if not os.path.exists(viopci.vio.root):
        os.makedirs(viopci.vio.root)
    if os.path.exists(viopci.vio.socketPath):
        os.remove(viopci.vio.socketPath)
    parent.viopci = viopci
    parent.attachPciDevice(viopci, bus)


class MemBus(m5.objects.SystemXBar):
    badaddr_responder = m5.objects.BadAddr()
    default = m5.objects.Self.badaddr_responder.pio

class FileDiskImage(m5.objects.CowDiskImage):
    def __init__(self, child_image_file, **kwargs):
        super(FileDiskImage, self).__init__(**kwargs)
        self.child.image_file = child_image_file

class CowIdeDisk(m5.objects.IdeDisk):
    def __init__(self, child_image_file, **kwargs):
        super(CowIdeDisk, self).__init__(**kwargs)
        self.image = FileDiskImage(child_image_file)

class EPISystem(m5.objects.ArmSystem):
    def __init__(self, options, **kwargs):
        # type: (Options, **str) -> None

        super(EPISystem, self).__init__(**kwargs)

        options = options # type: Options

        self.sve_vl = int(options.architecture.cpu.sve_length)/128

        self.mem_mode = options.architecture.cpu.init_class.memory_mode()

        # Ruby only supports atomic accesses in noncaching mode
        if f"{self.mem_mode}" == "atomic" and options.architecture.NOC.active:
            self.mem_mode = 'atomic_noncaching'

        self.iobus = m5.objects.IOXBar()

        if not options.architecture.NOC.active:
            self.bridge = m5.objects.Bridge(delay='50ns')
            self.bridge.mem_side_port = self.iobus.cpu_side_ports
            self.membus = MemBus()
            self.membus.badaddr_responder.warn_access = "warn"
            self.bridge.cpu_side_port = self.membus.mem_side_ports

        platform_class = dict(
            VExpress_GEM5_V1=m5.objects.VExpress_GEM5_V1,
            VExpress_GEM5_V2=m5.objects.VExpress_GEM5_V2
        ).get(options.architecture.system.model, None)

        self.realview = platform_class()
        self._bootmem = self.realview.bootmem

        # Attach any PCI devices this platform supports
        self.realview.attachPciDevices()

        self.create_memory_ranges_VExpress_GEM5(options)

        self.configure_system_boot(options)

        self.attach_chip_io(options)

        self.attach_disk_images(options)

        self.terminal  = m5.objects.Terminal()
        self.vncserver = m5.objects.VncServer()

        if options.vio_9p:
            attach_9p(self.realview, self.iobus)

        if not options.architecture.NOC.active:
            self.system_port = self.membus.cpu_side_ports

        if options.enable_context_switch_stats_dump:
            self.enable_context_switch_stats_dump = True

        # Set the cache line size for the entire system
        # self.cache_line_size = options.architecture.caches.cache_line_size

        self.configure_system_clocks(options)

        self.create_cpus(options)

        if options.architecture.NOC.active:
            ruby.configure_ruby(self, options, piobus = self.iobus, dma_ports=self._dma_ports, bootmem=self._bootmem)
        else:
            classic.configure_classic(self, options, piobus = self.iobus, dma_ports=self._dma_ports, bootmem=self._bootmem)

    def create_memory_ranges_VExpress_GEM5(self, options):
        # Assume VExpress_GEM5_Base platform
        self.mem_ranges = []

        sys_mem_region = self.realview._mem_regions[0]
        start = sys_mem_region.start
        for region in options.architecture.memory.regions:
            print(region)
            sizes = []
            # [lnghrdntcr] For HMEM systems, the size variable is a list that holds 
            # the sizes 
            # This will fail in the creation of the ArmSystem: 
            # The number of mem_ranges should equal the number of numa nodes
            if type(region.size) == list: 
                for s in region.size: 
                    sizes.append(int(m5.objects.Addr(s)))
            else: 
                sizes.append(int(m5.objects.Addr(region.size)))

            size = sum(sizes)
            self.mem_ranges.append(m5.objects.AddrRange(start, size=size))
            print("Size = ", self.mem_ranges[-1].size())
            start = start + size

    def configure_system_boot(self, options):
        # Resolve the real platform name, the original machine_type
        # variable might have been an alias.
        machine_type = type(self.realview).__name__

        if options.architecture.system.bare_metal:
            self.realview.uart[0].end_on_eot = True
            self.workload = m5.objects.ArmFsWorkload(dtb_addr=0)
        else:
            workload = m5.objects.ArmFsLinux()
            workload.dtb_filename  = options.dtb_filename
            workload.machine_type = machine_type if machine_type in m5.objects.ArmMachineType.map else "DTOnly"

            if hasattr(self.realview.gic, 'cpu_addr'):
                self.gic_cpu_addr = self.realview.gic.cpu_addr

            # set cmdline
            cmdline = None
            if options.command_line and options.command_line_file:
                print("Error: --command-line and --command-line-file are mutually exclusive")
                sys.exit(1)
            if options.command_line:
                cmdline = options.command_line
            if options.command_line_file:
                cmdline = open(options.command_line_file).read().strip()

            # Ensure that writes to the UART actually go out early in the boot
            if not cmdline:
                cmdline = f"earlyprintk=pl011,0x1c090000 console=ttyAMA0 lpj=19988480 norandmaps rw loglevel=8 root={options.root_partition}"
            workload.command_line = cmdline

            self.workload = workload
            self.realview.setupBootLoader(self, lambda name:  options.bootloader )

        self.workload.object_file = options.kernel
        self.readfile = options.bootscript
        
        # Parameter available in simulation with m5 initparam
        # self.init_param = init_param

    def attach_chip_io(self, options):
        if options.architecture.memory.external_memory_system:
            # I/O traffic enters iobus
            self.external_io = m5.objects.ExternalMaster(
                port_data="external_io",
                port_type=options.memory.external_memory_system
            )
            self.external_io.port = self.iobus.cpu_side_ports

            # Ensure iocache only receives traffic destined for (actual) memory.
            self.iocache = m5.objects.ExternalSlave(
                port_data="iocache",
                port_type=options.memory.external_memory_system,
                addr_ranges=self.mem_ranges
            )
            self.iocache.port = self.iobus.mem_side_ports

            # Let system_port get to nvmem and nothing else.
            self.bridge.ranges = [self.realview.nvmem.range]

            self.realview.attachOnChipIO(self.iobus)
            # Attach off-chip devices
            self.realview.attachIO(self.iobus)

        elif options.architecture.NOC.active:
            self._dma_ports = [ ]
            self._mem_ports = [ ]
            self.realview.attachOnChipIO(self.iobus, dma_ports=self._dma_ports, mem_ports=self._mem_ports)
            self.realview.attachIO(self.iobus, dma_ports=self._dma_ports)
        else:
            self.realview.attachOnChipIO(self.membus, self.bridge)
            # Attach off-chip devices
            self.realview.attachIO(self.iobus)

    def attach_disk_images(self, options):
        pci_devices = []
        # Setup IDE Disks
        # disks = [CowIdeDisk(f, driveID=f'device{i}') for i,f in enumerate(options.disk)]
        # self.pci_ide = m5.objects.IdeController(disks=disks)
        # pci_devices.append(self.pci_ide)

        # Setup VirtIO disk images
        disks = [ FileDiskImage(f) for f in options.disk ]

        self.pci_vio_block = [ m5.objects.PciVirtIO(vio=m5.objects.VirtIOBlock(image=img))
                              for img in disks ]

        for dev in self.pci_vio_block:
            pci_devices.append(dev)

        for dev in pci_devices:
            self.realview.attachPciDevice(dev, self.iobus, dma_ports=self._dma_ports if options.architecture.NOC.active else None)

    def configure_system_clocks(self, options):
        # Create a top-level voltage domain
        self.voltage_domain = m5.objects.VoltageDomain(
            voltage = options.architecture.system.voltage
        )
        # Create a CPU voltage domain
        self.cpu_voltage_domain = m5.objects.VoltageDomain()

        # Create a source clock for the system and set the clock period
        self.clk_domain = m5.objects.SrcClockDomain(
            clock=options.architecture.system.clock,
            voltage_domain=self.voltage_domain
        )

        # Create a source clock for the CPUs and set the clock period
        self.cpu_clk_domain = m5.objects.SrcClockDomain(
            clock=options.architecture.cpu.clock,
            voltage_domain=self.cpu_voltage_domain
        )

    def create_cpus(self, options):
        # For now, assign all the CPUs to the same clock domain
        self.cpu = [
            options.architecture.cpu.init_class(
                options.architecture.cpu,
                clk_domain=self.cpu_clk_domain,
                cpu_id=i
            ) for i in range(options.architecture.num_cpus)
        ]
