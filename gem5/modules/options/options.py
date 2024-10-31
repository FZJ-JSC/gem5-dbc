import argparse
import importlib
import os
import yaml
from pathlib import Path

from modules import cpus, util

class Sequencer:
    def __init__(self,parameters):
        self.max_outstanding_requests=parameters['max_outstanding_requests']

class System:
    def __init__(self,parameters):

        self.num_cpus         = parameters['num_cpus']
        self.num_slcs_per_cpu = parameters['num_slcs_per_cpu']
        self.model   = parameters['model']
        self.clock   = parameters['clock']
        self.voltage = parameters['voltage']
        
        #self.platform_class = m5.objects.VExpress_GEM5_V1
        self.bare_metal = False

class CPU:
    def __init__(self,parameters, checkpoint_restore=False):

        def get_cpu_class(name: str):
            return dict(
                AtomicSimple=cpus.AtomicSimple,
                TimingSimple=cpus.TimingSimple,
                DefaultO3CPU=cpus.DefaultO3CPU,
                R_CPU=cpus.R_CPU,
            ).get(name, None)

        self.init_class = None
        self.main_class = None
        self.use_cpu_checker = False

        self.clock       = parameters['clock']
        self.sve_length  = parameters['sve_vl']
        self.have_sve    = parameters['have_sve']
        #self.sequencer = Sequencer(parameters['sequencer'])

        self.branch_predictor = parameters['branch_predictor']

        self.parameters = dict(
            DefaultO3CPU = parameters.get('DefaultO3CPU',dict()),
            R_CPU = parameters['R_CPU']
        )

        if isinstance(parameters['model'], list):
            if checkpoint_restore:
                self.init_class = get_cpu_class(parameters['model'][1])
            else:
                self.init_class = get_cpu_class(parameters['model'][0])
            self.main_class = get_cpu_class(parameters['model'][1])
        else:
            self.init_class = get_cpu_class(parameters['model'])



class MemoryRegion:
    def __init__(self, parameters):
        self.model    = parameters.get('model')
        self.size     = parameters.get('size')
        self.channels = parameters.get('channels')
        self.kind     = parameters.get('kind')
        self.ctrl     = parameters.get('controller')

        if self.ctrl or self.model == "BwLatCtrl": 
            self.ctrl_config = {
                        "sampling_window": parameters['ctrl_config']['sampling_window'],
                        "curves_path": parameters['ctrl_config']['curves_path'] 
                    }

        if self.model == "Ramulator2": 
            self.config_file = parameters['config_file']

        if (self.model == "Simple"):
            self.simple_latency   = parameters['latency']
            self.simple_bandwidth = parameters['bandwidth']
            self.simple_latency_var = parameters['latency_var']
        self.enable_dram_powerdown = False

class Memory:
    def __init__(self, regions):

        self.regions = []
        self.external_memory_system = None

        for region in regions:
            self.regions.append(MemoryRegion(region))

class CacheLatency:
    def __init__(self,parameters):
        self.tag      = parameters['tag']
        self.data     = parameters['data']
        self.response = parameters['response']

class CacheController:
    def __init__(self,parameters):
        self.number_of_TBEs       = parameters['number_of_TBEs']
        self.number_of_repl_TBEs  = parameters['number_of_repl_TBEs']
        self.number_of_snoop_TBEs = parameters['number_of_snoop_TBEs']
        self.unify_repl_TBEs      = parameters['unify_repl_TBEs']

        self.enable_DMT           = parameters.get("enable_DMT", False)
        self.enable_DCT           = parameters.get("enable_DCT", False)
        self.allow_SD             = parameters.get("allow_SD", True)

        # Allocate if CHIR0equestType = Load, Store
        self.alloc_on_seq_acc_load   = parameters.get("alloc_on_seq_acc_load",   False)
        self.alloc_on_seq_acc_store  = parameters.get("alloc_on_seq_acc_store",  False)
        # Allocate if CHIRequestType = StoreLine
        self.alloc_on_seq_line_write = parameters.get("alloc_on_seq_line_write", False)
        # Allocate if CHIRequestType = ReadShared, ReadNotSharedDirty
        self.alloc_on_readshared     = parameters.get("alloc_on_readshared", True)
        # Allocate if CHIRequestType = ReadUnique
        self.alloc_on_readunique     = parameters.get("alloc_on_readunique", True)
        # Allocate if CHIRequestType = ReadOnce
        self.alloc_on_readonce       = parameters.get("alloc_on_readonce",   True)
        # Allocate if CHIRequestType = WriteBackFull, WriteCleanFull, WriteEvictFull
        # Allocate if HN and CHIRequestType = WriteUniqueFull
        self.alloc_on_writeback      = parameters.get("alloc_on_writeback",  True)
        # Deallocate if CHIRequestType = ReadUnique, CleanUnique
        self.dealloc_on_unique       = parameters.get("dealloc_on_unique",   False)
        # Deallocate if CHIRequestType = ReadShared, ReadNotSharedDirty
        self.dealloc_on_shared       = parameters.get("dealloc_on_shared",   False)
        # follwing triggers Local_Eviction + back-invalidate line in all upstream requesters
        self.dealloc_backinv_unique  = parameters.get("dealloc_backinv_unique", True)
        self.dealloc_backinv_shared  = parameters.get("dealloc_backinv_shared", True)

class CachePrefetcher:
    def __init__(self,parameters):
        self.selected = parameters['selected']
        self.configuration = dict()
        self.configuration.update(parameters['configuration'])

class CacheOptions:
    def __init__(self,parameters, is_icache=False):
        # type: (dict[str,str]) -> None

        self.active = parameters.get("active", True)
        self.is_icache = is_icache

        self.size  =  parameters['size']
        self.assoc = parameters['assoc']
        self.latencies = CacheLatency(parameters['latency'])

        self.sequencer  = None
        self.controller = None
        self.prefetcher = None

        if 'sequencer' in parameters:
            self.sequencer  = Sequencer(parameters['sequencer'])
        if 'controller' in parameters:
            self.controller = CacheController(parameters['controller'])
        if ('prefetcher' in parameters) and (parameters['prefetcher']['selected'] != 'None'):
            self.prefetcher = CachePrefetcher(parameters['prefetcher'])
        else: 
            print("Don't have prefetcher")

class Caches:
    def __init__(self,parameters,cache_levels=3):
        # type: (dict[str,str], int) -> None

        self.cache_levels = cache_levels
        self.cache_line_size = parameters['cache_line_size']

        self.L1D = CacheOptions(parameters['L1D'])
        self.L1I = CacheOptions(parameters['L1I'], is_icache=True)
        self.L2  = CacheOptions(parameters['L2'])
        self.SLC = CacheOptions(parameters['SLC'])

class Topology:
    def __init__(self,parameters):
        self.model = parameters["model"]

        self.parameters = parameters[self.model]

        self.router_latency    = parameters["router_latency"]
        self.mesh_link_latency = parameters["mesh_link_latency"]
        self.node_link_latency = parameters["node_link_latency"]
        self.cbar_link_latency = 1
        self.cbar_router_latency = 0

        self.cross_links = []
        self.cross_link_latency = 0

class Garnet:
    def __init__(self,parameters):
        self.vcs_per_vnet       = parameters["vcs_per_vnet"]
        self.routing_algorithm  = parameters["routing_algorithm"]
        self.deadlock_threshold = parameters["deadlock_threshold"]
        self.use_link_bridges   = parameters["use_link_bridges"]

class SimpleNetwork:
    def __init__(self, parameters) -> None:
        # Router port buffer (per vnet)
        self.router_buffer_size = 4
        self.link_bandwidth = 64

class Network:
    def __init__(self,parameters):
        self.model = parameters["model"]
        self.garnet = Garnet(parameters["garnet"])
        self.simple = SimpleNetwork(parameters["simple"])

        self.mesh_vnet_support  = parameters["link_vnet_support"]
        self.cbar_vnet_support  = parameters["link_vnet_support"]

        self.cntrl_msg_size = 8
        self.data_width = parameters['data_width']

        self.data_link_width = self.cntrl_msg_size + self.data_width

        if self.model == "garnet":
            #Used by garnet ni_flit_size=link_width_bits/8
            self.ni_flit_size    = self.data_link_width
            self.link_width_bits = self.data_link_width * 8
        else:
            self.link_width_bits = 128 #parameters["link-width-bits"]


class NOC:
    def __init__(self,parameters,num_cpus=None,num_slcs=None):

        self.active = parameters["active"]
        self.clock  = parameters["clock"]

        self.topology = Topology(parameters["topology"])
        
        self.network  = Network(parameters["network"])

        self.n_vnets = 4

        protocol_name   = parameters["protocol"]['model'] #m5.defines.buildEnv['PROTOCOL']
        protocol_params = parameters["protocol"][f"{protocol_name}"]
        Protocol = importlib.import_module(f"modules.options.protocol.{protocol_name}")

        self.protocol = Protocol.Options(protocol_params, num_cpus=num_cpus, num_slcs=num_slcs, link_latency=self.topology.node_link_latency)

        self.xor_low_bit = 20

        self.numa_high_bit = 0

        self.network_fault_model = False
        # Should ruby maintain a second copy of memory
        self.access_backing_store = False

class Architecture:
    def __init__(self, parameters, checkpoint_restore=False):
        self.parameters = parameters
        
        #use_noc = parameters['NOC']['active'] if 'active' in parameters['NOC'] else False
        
        self.num_cpus = parameters['system']['num_cpus']
        self.num_slcs = self.num_cpus * parameters['system']['num_slcs_per_cpu']
        self.checkpoint_restore = checkpoint_restore

        # if(checkpoint_mode):
            # parameters['cpu']['model'] = parameters['checkpoint']['cpu']['model']
            # parameters['memory']['channels'] = 1
            # parameters['memory']['channels-per-core'] = 0
            
        parameters['caches']['SLC']['bus-width']  = int(util.divide_float_unitless(parameters['caches']['SLC']['bandwidth'], parameters['system']['clock']))

        self.cpu = CPU(parameters['cpu'], checkpoint_restore=self.checkpoint_restore)
        self.caches = Caches(parameters['caches'])
        self.system = System(parameters['system'])
        self.memory = Memory(parameters['memory'])
        self.NOC = NOC(parameters['NOC'], num_cpus=self.num_cpus, num_slcs=self.num_slcs)

class Checkpoint:
    def __init__(self, parameters):
        self.restore = None
        self.directory = None

        self.max_checkpoints=5
        self.take_checkpoints=None
        self.take_simpoint_checkpoints = None
        self.restore_simpoint_checkpoint = None
        self.checkpoint_at_end = None
    
class Simulation:
    def __init__(self, parameters):
        self.fs_mode = parameters['fs_mode']
        self.timesync = None
        self.checkpoint = Checkpoint(parameters['checkpoint'])

class Process:
    def __init__(self,options):
        self.cwd = os.getcwd()
        self.cmd = options.cmd.split()
        
        self.env = []
        self.input  = options.cmd_input
        self.output = options.cmd_output
        self.errout = options.cmd_outerr
        self.pid = 100

class Options:
    def __init__(self):
        parser = argparse.ArgumentParser(description="Configuration")
        add_options(parser)

        # Parse command line options
        options = parser.parse_args()

        # Parse architecture parameters from YAML file
        self.parameters = yaml.safe_load(Path(options.config_file).read_text())

        self.checkpoint_mode      = options.checkpoint_mode
        self.checkpoint_restore   = options.checkpoint_restore
        self.checkpoint_directory = options.checkpoint_directory

        self.architecture = Architecture(
            self.parameters,
            checkpoint_restore=self.checkpoint_restore
        )
        self.simulation  = Simulation(self.parameters['simulation'])
        self.process     = Process(options)

        self.dtb_filename   = options.dtb_filename
        self.kernel         = options.kernel
        self.disk           = options.disk
        self.bootloader     = options.bootloader
        self.bootscript     = options.bootscript
        self.root_partition = options.root_partition

        self.elastic_trace  = None #options.elastic_trace
        self.bare_metal = None
        self.command_line      = None
        self.command_line_file = None        
        self.fast_forward = None
        self.enable_security_extensions = False
        self.vio_9p = False
        self.enable_context_switch_stats_dump = None
        self.lpae = True
        self.virtualisation = None
        self.tlm_memory = None
        self.abs_max_tick=None
        self.rel_max_tick=None
        self.maxtime=None
        self.standard_switch = None
        self.repeat_switch = None
        self.disable_listeners = True


def add_options(parser):

    parser.add_argument("--config-file",  type=str, default=None, help="Configuration file")
    #parser.add_argument("--config-key",   type=str, default=None, help="Configuration file key")

    #parser.add_argument("--se-mode", action='store_true', default=False, help="System Emulation mode")
    #parser.add_argument("--ruby",    action='store_true', default=False, help="Use Ruby")

    #parser.add_argument("--num-cpus",            type=int, default=1, help="Number CPUs to instantiate")
    #parser.add_argument("--sve-length",          type=int, default=None,  help="SVE Length")
    #parser.add_argument("--use-l2-prefetcher",   type=str, default=None,  help="Prefetcher Model")

    parser.add_argument("--dtb-filename",   type=str, default=None,       help="DTB file to load")
    parser.add_argument("--kernel",         type=str, default=None,       help="Linux kernel")
    parser.add_argument("--disk",           action="append", type=str, default=None,       help="Disks to instantiate")
    parser.add_argument("--bootloader",     type=str, default=None,       help="Bootloader path")
    parser.add_argument("--root-partition", type=str, default="/dev/vda1", help="Root partition")
    parser.add_argument("--bootscript",     type=str, default=None,       help="Linux bootscript")

    parser.add_argument("--checkpoint-mode",          action='store_true', default=False, help="Instantiate Checkpoint Parameters")
    parser.add_argument("--checkpoint-restore", "-r", type=int, help="restore from checkpoint <N>")
    parser.add_argument("--checkpoint-directory",     type=str, default=None, help="Checkpoint directory")

    parser.add_argument("--cmd",        type=str, default="", help="The command to run in syscall emulation mode.")
    parser.add_argument("--cmd-env",    type=str, default="", help="Initialize command environment from text file.")
    parser.add_argument("--cmd-input",  type=str, default="", help="Read stdin from a file.")
    parser.add_argument("--cmd-output", type=str, default="", help="Redirect stdout to a file.")
    parser.add_argument("--cmd-outerr", type=str, default="", help="Redirect stderr to a file.")

    return parser

options = Options()
