from dataclasses import asdict, dataclass


@dataclass
class CacheCtrlConf:
    # Default TBE params
    number_of_TBEs: int = 256
    number_of_repl_TBEs: int = 256
    number_of_snoop_TBEs: int = 64
    unify_repl_TBEs: bool = False

    number_of_DVM_TBEs: int = 16
    number_of_DVM_snoop_TBEs: int = 4

    is_HN: bool = False
    enable_DMT: bool = False
    enable_DCT: bool = False

    send_evictions: bool = False

    allow_SD: bool = True
    # Allocate if CHIRequestType = Load, Store
    alloc_on_seq_acc: bool = False
    # Allocate if CHIRequestType = StoreLine
    alloc_on_seq_line_write: bool = False

    sc_lock_enabled: bool = False

    # Allocate on Atomic
    alloc_on_atomic: bool = False
    # Allocate if CHIRequestType = ReadShared, ReadNotSharedDirty
    alloc_on_readshared: bool = True
    # Allocate if CHIRequestType = ReadUnique
    alloc_on_readunique: bool = True
    # Allocate if CHIRequestType = ReadOnce
    alloc_on_readonce: bool = True
    # Allocate if CHIRequestType = WriteBackFull, WriteCleanFull, WriteEvictFull
    # Allocate if HN and CHIRequestType = WriteUniqueFull
    alloc_on_writeback: bool = True
    # Deallocate if CHIRequestType = ReadUnique, CleanUnique
    dealloc_on_unique: bool = False
    # Deallocate if CHIRequestType = ReadShared, ReadNotSharedDirty
    dealloc_on_shared: bool = False
    # follwing triggers Local_Eviction + back-invalidate line in all upstream requesters
    dealloc_backinv_unique: bool = True
    dealloc_backinv_shared: bool = True

    # Wait for cache data array write to complete before executing next action
    wait_for_cache_wr: bool = False

    mandatory_queue_latency: int = 1
    request_latency: int = 1
    response_latency: int = 1
    snoop_latency: int = 1
    data_latency: int = 1
    stall_recycle_lat: int = 1
    sc_lock_base_latency_cy: int = 4

    read_hit_latency: int = 0
    read_miss_latency: int = 0
    write_fe_latency: int = 0
    write_be_latency: int = 0
    # Fill latency
    fill_latency: int = 0
    # Applied before handling any snoop
    snp_latency: int = 0
    # Additional latency for invalidating snoops
    snp_inv_latency: int = 0

    # State machine transitions per cycle
    transitions_per_cycle: int = 1024
    # Atomic Operation Policy
    policy_type: int = 0

    data_channel_size: int = 64

    def to_dict(self) -> dict:
        return asdict(self)
