import m5
import math

from modules.options import CacheOptions

class Versions:
    '''
    Helper class to obtain unique ids for a given controller class.
    These are passed as the 'version' parameter when creating the controller.
    '''
    _seqs = 0
    @classmethod
    def getSeqId(cls):
        val = cls._seqs
        cls._seqs += 1
        return val

    _version = {}
    @classmethod
    def getVersion(cls, tp):
        if tp not in cls._version:
            cls._version[tp] = 0
        val = cls._version[tp]
        cls._version[tp] = val + 1
        return val

class TriggerMessageBuffer(m5.objects.MessageBuffer):
    '''
    MessageBuffer for triggering internal controller events.
    These buffers should not be affected by the Ruby tester randomization
    and allow poping messages enqueued in the same cycle.
    '''
    randomization = 'disabled'
    allow_zero_latency = True

class OrderedTriggerMessageBuffer(TriggerMessageBuffer):
    ordered = True


class CacheMemory(m5.objects.RubyCache):
    def __init__(self, options: CacheOptions, **kwargs):
        super(CacheMemory, self).__init__(
            dataAccessLatency = options.latencies.data,
            tagAccessLatency  = options.latencies.tag,
            size  = options.size,
            assoc = options.assoc,
            is_icache = options.is_icache,
            **kwargs
        )

class Sequencer(m5.objects.RubySequencer):
    def __init__(self, ruby_system, **kwargs):
        super(Sequencer, self).__init__(
            version = Versions.getSeqId(),
            ruby_system = ruby_system,
            **kwargs
        )

class CHI_Cache_Controller(m5.objects.Cache_Controller):
    '''
    Default parameters for a Cache controller
    The Cache_Controller can also be used as a DMA requester or as
    a pure directory if all cache allocation policies are disabled.
    '''

    def __init__(self, ruby_system):
        super(CHI_Cache_Controller, self).__init__(
            version = Versions.getVersion(m5.objects.Cache_Controller),
            ruby_system = ruby_system,
            mandatoryQueue = m5.objects.MessageBuffer(),
            prefetchQueue = m5.objects.MessageBuffer(),
            triggerQueue = TriggerMessageBuffer(),
            retryTriggerQueue = OrderedTriggerMessageBuffer(),
            replTriggerQueue  = OrderedTriggerMessageBuffer(),
            reqRdy = TriggerMessageBuffer(),
            snpRdy =TriggerMessageBuffer()
        )
        # Set somewhat large number since we really a lot on internal
        # triggers. To limit the controller performance, tweak other
        # params such as: input port buffer size, cache banks, and output
        # port latency
        self.transitions_per_cycle = 1024 
        # This should be set to true in the data cache controller to enable
        # timeouts on unique lines when a store conditional fails
        self.sc_lock_enabled = False



class CHI_Memory_Controller(m5.objects.Memory_Controller):
    '''
    Default parameters for a Memory controller
    '''

    def __init__(self, ruby_system):
        super(CHI_Memory_Controller, self).__init__(
                          version = Versions.getVersion(m5.objects.Memory_Controller),
                          ruby_system = ruby_system,
                          triggerQueue = TriggerMessageBuffer(),
                          responseFromMemory = m5.objects.MessageBuffer(),
                          requestToMemory = m5.objects.MessageBuffer(ordered = True),
                          reqRdy = TriggerMessageBuffer()
                          )


        self._cntrl = m5.objects.Memory_Controller


class CHI_L1Controller(CHI_Cache_Controller):
    '''
    Default parameters for a L1 Cache controller
    '''

    def __init__(self, ruby_system, sequencer, options: CacheOptions, prefetcher=m5.objects.NULL):
        super(CHI_L1Controller, self).__init__(ruby_system)

        cache_line_size = ruby_system.block_size_bytes.value
        block_size_bits = int(math.log(cache_line_size, 2))

        self.cache     = CacheMemory(options, start_index_bit = block_size_bits)
        self.sequencer = sequencer

        self.use_prefetcher = prefetcher != m5.objects.NULL 
        self.prefetcher = prefetcher

        self.is_HN = False
        self.send_evictions = True
        self.enable_DMT = False
        self.enable_DCT = False
        # Strict inclusive MOESI
        #  Allow receiving data in SD state.
        self.allow_SD = options.controller.allow_SD
        # Allocate if CHIRequestType = Load, Store
        self.alloc_on_seq_acc_load  = options.controller.alloc_on_seq_acc_load
        self.alloc_on_seq_acc_store = options.controller.alloc_on_seq_acc_store
        # Allocate if CHIRequestType = StoreLine
        self.alloc_on_seq_line_write = options.controller.alloc_on_seq_line_write
        # Allocate if CHIRequestType = ReadShared, ReadNotSharedDirty
        self.alloc_on_readshared = options.controller.alloc_on_readshared
        # Allocate if CHIRequestType = ReadUnique
        self.alloc_on_readunique = options.controller.alloc_on_readunique
        # Allocate if CHIRequestType = ReadOnce
        self.alloc_on_readonce = options.controller.alloc_on_readonce
        # Allocate if CHIRequestType = WriteBackFull, WriteCleanFull, WriteEvictFull
        # Allocate if HN and CHIRequestType = WriteUniqueFull
        self.alloc_on_writeback = options.controller.alloc_on_writeback
        # Deallocate if CHIRequestType = ReadUnique, CleanUnique
        self.dealloc_on_unique = options.controller.dealloc_on_unique
        # Deallocate if CHIRequestType = ReadShared, ReadNotSharedDirty
        self.dealloc_on_shared = options.controller.dealloc_on_shared
        # follwing triggers Local_Eviction + back-invalidate line in all upstream requesters
        self.dealloc_backinv_unique = options.controller.dealloc_backinv_unique
        self.dealloc_backinv_shared = options.controller.dealloc_backinv_shared
        # Some reasonable default TBE params
        self.number_of_TBEs       = options.controller.number_of_TBEs
        self.number_of_repl_TBEs  = options.controller.number_of_repl_TBEs
        self.number_of_snoop_TBEs = options.controller.number_of_snoop_TBEs
        # DVM
        self.number_of_DVM_TBEs = 16
        self.number_of_DVM_snoop_TBEs = 4

        self.unify_repl_TBEs      = options.controller.unify_repl_TBEs

class CHI_L2Controller(CHI_Cache_Controller):
    '''
    Default parameters for a L2 Cache controller
    '''

    def __init__(self, ruby_system, options: CacheOptions, prefetcher=m5.objects.NULL):
        super(CHI_L2Controller, self).__init__(ruby_system)

        cache_line_size = ruby_system.block_size_bytes.value
        block_size_bits = int(math.log(cache_line_size, 2))

        self.cache = CacheMemory(options, start_index_bit = block_size_bits)
        self.sequencer = m5.objects.NULL

        # self.use_prefetcher = False
        self.use_prefetcher = prefetcher != m5.objects.NULL
        self.prefetcher = prefetcher
        self.is_HN = False
        self.send_evictions = False
        self.enable_DMT = False
        self.enable_DCT = False
        self.allow_SD   = options.controller.allow_SD
        # Strict inclusive MOESI
        self.alloc_on_seq_acc_load   = options.controller.alloc_on_seq_acc_load
        self.alloc_on_seq_acc_store  = options.controller.alloc_on_seq_acc_store
        self.alloc_on_seq_line_write = options.controller.alloc_on_seq_line_write
        self.alloc_on_readshared     = options.controller.alloc_on_readshared
        self.alloc_on_readunique     = options.controller.alloc_on_readunique
        self.alloc_on_readonce       = options.controller.alloc_on_readonce
        self.alloc_on_writeback      = options.controller.alloc_on_writeback
        self.dealloc_on_unique       = options.controller.dealloc_on_unique
        self.dealloc_on_shared       = options.controller.dealloc_on_shared
        self.dealloc_backinv_unique  = options.controller.dealloc_backinv_unique
        self.dealloc_backinv_shared  = options.controller.dealloc_backinv_shared
        # Some reasonable default TBE params
        self.number_of_TBEs       = options.controller.number_of_TBEs
        self.number_of_repl_TBEs  = options.controller.number_of_repl_TBEs
        self.number_of_snoop_TBEs = options.controller.number_of_snoop_TBEs
        self.number_of_DVM_TBEs = 1 # should not receive any dvm
        self.number_of_DVM_snoop_TBEs = 1 # should not receive any dvm
        self.unify_repl_TBEs      = options.controller.unify_repl_TBEs


class CHI_HNFController(CHI_Cache_Controller):
    '''
    Default parameters for a coherent home node (HNF) cache controller
    '''

    def __init__(self, ruby_system, addr_ranges, options: CacheOptions, prefetcher=m5.objects.NULL):
        super(CHI_HNFController, self).__init__(ruby_system)

        cache_line_size = ruby_system.block_size_bytes.value
        block_size_bits = int(math.log(cache_line_size, 2))

        self.cache = CacheMemory(options, start_index_bit = block_size_bits)
        self.sequencer = m5.objects.NULL

        self.use_prefetcher = prefetcher != m5.objects.NULL
        self.prefetcher = prefetcher
 
        self.addr_ranges = addr_ranges
        self.is_HN = True
        self.send_evictions = False
        self.enable_DMT = options.controller.enable_DMT
        self.enable_DCT = options.controller.enable_DCT
        self.allow_SD   = options.controller.allow_SD
        # MOESI / Mostly inclusive for shared / Exclusive for unique
        self.alloc_on_seq_acc_load   = options.controller.alloc_on_seq_acc_load
        self.alloc_on_seq_acc_store  = options.controller.alloc_on_seq_acc_store
        self.alloc_on_seq_line_write = options.controller.alloc_on_seq_line_write
        self.alloc_on_readshared     = options.controller.alloc_on_readshared
        self.alloc_on_readunique     = options.controller.alloc_on_readunique
        self.alloc_on_readonce       = options.controller.alloc_on_readonce
        self.alloc_on_writeback      = options.controller.alloc_on_writeback
        self.dealloc_on_unique       = options.controller.dealloc_on_unique
        self.dealloc_on_shared       = options.controller.dealloc_on_shared
        self.dealloc_backinv_unique  = options.controller.dealloc_backinv_unique
        self.dealloc_backinv_shared  = options.controller.dealloc_backinv_shared
        # Some reasonable default TBE params
        self.number_of_TBEs       = options.controller.number_of_TBEs
        self.number_of_repl_TBEs  = options.controller.number_of_repl_TBEs
        self.number_of_snoop_TBEs = options.controller.number_of_snoop_TBEs
        self.number_of_DVM_TBEs = 1 # should not receive any dvm
        self.number_of_DVM_snoop_TBEs = 1 # should not receive any dvm
        self.unify_repl_TBEs      = options.controller.unify_repl_TBEs

class CHI_MNController(m5.objects.MiscNode_Controller):
    '''
    Default parameters for a Misc Node
    '''

    def __init__(self, ruby_system, addr_range, l1d_caches, early_nonsync_comp):
        super(CHI_MNController, self).__init__(
            version = Versions.getVersion(m5.objects.MiscNode_Controller),
            ruby_system = ruby_system,
            mandatoryQueue = m5.objects.MessageBuffer(),
            triggerQueue = TriggerMessageBuffer(),
            retryTriggerQueue = TriggerMessageBuffer(),
            schedRspTriggerQueue = TriggerMessageBuffer(),
            reqRdy = TriggerMessageBuffer(),
            snpRdy = TriggerMessageBuffer(),
        )
        # Set somewhat large number since we really a lot on internal
        # triggers. To limit the controller performance, tweak other
        # params such as: input port buffer size, cache banks, and output
        # port latency
        self.transitions_per_cycle = 1024
        self.addr_ranges = [addr_range]
        # 16 total transaction buffer entries, but 1 is reserved for DVMNonSync
        self.number_of_DVM_TBEs = 16
        self.number_of_non_sync_TBEs = 1
        self.early_nonsync_comp = early_nonsync_comp

        # "upstream_destinations" = targets for DVM snoops
        self.upstream_destinations = l1d_caches

class CHI_DMAController(CHI_Cache_Controller):
    '''
    Default parameters for a DMA controller
    '''

    def __init__(self, ruby_system, sequencer):
        super(CHI_DMAController, self).__init__(ruby_system)
        self.sequencer = sequencer
        class DummyCache(m5.objects.RubyCache):
            dataAccessLatency = 0
            tagAccessLatency = 1
            size = "128"
            assoc = 1
        self.use_prefetcher = False
        self.prefetcher = m5.objects.NULL
        self.cache = DummyCache()
        self.sequencer.dcache = m5.objects.NULL
        # All allocations are false
        # Deallocations are true (don't really matter)
        self.allow_SD = False
        self.is_HN = False
        self.enable_DMT = False
        self.enable_DCT = False
        self.alloc_on_seq_acc_load   = False
        self.alloc_on_seq_acc_store  = False
        self.alloc_on_seq_line_write = False
        self.alloc_on_readshared = False
        self.alloc_on_readunique = False
        self.alloc_on_readonce = False
        self.alloc_on_writeback = False
        self.dealloc_on_unique = False
        self.dealloc_on_shared = False
        self.dealloc_backinv_unique = False
        self.dealloc_backinv_shared = False
        self.send_evictions = False
        self.number_of_TBEs = 16
        self.number_of_repl_TBEs = 1
        self.number_of_snoop_TBEs = 1 # should not receive any snoop
        self.number_of_DVM_TBEs = 1 # should not receive any dvm
        self.number_of_DVM_snoop_TBEs = 1 # should not receive any dvm
        self.unify_repl_TBEs = False
