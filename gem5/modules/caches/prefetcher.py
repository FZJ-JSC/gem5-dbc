
import m5

class AMPM_Object(m5.objects.AccessMapPatternMatching):
    def __init__(self, parameters, **kwargs):
        super().__init__(**kwargs)
        
        # Cacheline size used by the prefetcher using this object
        # self.block_size = Param.Unsigned(Parent.block_size,"")
        
        # Limit the strides checked up to -X/X, if 0, disable the limit
        self.limit_stride = parameters.get('limit_stride',0)
        # Initial degree (Maximum number of prefetches generated
        self.start_degree = parameters.get('start_degree',4)
        # Memory covered by a hot zone
        self.hot_zone_size = parameters.get('hot_zone_size',"2KiB")
        # Number of entries in the access map table
        self.access_map_table_entries = parameters.get('access_map_table_entries',"256")
        # Associativity of the access map table
        self.access_map_table_assoc = parameters.get('access_map_table_assoc',8)
        # Indexing policy of the access map table
        self.access_map_table_indexing_policy = m5.objects.SetAssociative(
            entry_size = 1,
            assoc = self.access_map_table_assoc,
            size  = self.access_map_table_entries
        )
        # Replacement policy of the access map table
        self.access_map_table_replacement_policy = m5.objects.LRURP()
        # A prefetch coverage factor bigger than this is considered high
        self.high_coverage_threshold = parameters.get('high_coverage_threshold',0.25)
        # A prefetch coverage factor smaller than this is considered low
        self.low_coverage_threshold = parameters.get('low_coverage_threshold',0.125)
        # A prefetch accuracy factor bigger than this is considered high
        self.high_accuracy_threshold = parameters.get('high_accuracy_threshold',0.5)
        # A prefetch accuracy factor smaller than this is considered low
        self.low_accuracy_threshold = parameters.get('low_accuracy_threshold',0.25)
        # A cache hit ratio bigger than this is considered high
        self.high_cache_hit_threshold = parameters.get('high_cache_hit_threshold',0.875)
        # A cache hit ratio smaller than this is considered low
        self.low_cache_hit_threshold = parameters.get('low_cache_hit_threshold',0.75)
        # Cycles in an epoch period
        self.epoch_cycles = parameters.get('epoch_cycles', 256000)
        # Memory latency used to compute the required memory bandwidth
        self.offchip_memory_latency = parameters.get('offchip_memory_latency',"30ns")

class Stride(m5.objects.StridePrefetcher):
    def __init__(self, parameters, **kwargs):
        super().__init__(**kwargs)

        # Number of bits of the confidence counter
        self.confidence_counter_bits = parameters.get('confidence_counter_bits',3)
        # Starting confidence of new entries
        self.initial_confidence = parameters.get('initial_confidence',4)
        # Prefetch generation confidence threshold
        self.confidence_threshold = parameters.get('confidence_threshold',50)
        # Use requestor id based history
        self.use_requestor_id = parameters.get('use_requestor_id', True)
        # Number of prefetches to generate
        self.degree = parameters.get('degree', 4)
        # Associativity of the PC table
        self.table_assoc = parameters.get('table_assoc', 4)
        # Number of entries of the PC table
        self.table_entries = parameters.get('table_entries' ,"64")
        # Replacement policy of the PC table
        self.table_replacement_policy = m5.objects.RandomRP()
        # [lnghrdntcr]: Error: "proxy cannot unproxy properties"
        self.prefetch_on_access = parameters.get("prefetch_on_access", True)
        self.prefetch_on_pf_hit = parameters.get("prefetch_on_pf_hit", False)


class Tagged(m5.objects.TaggedPrefetcher):
    def __init__(self, parameters, **kwargs):
        super().__init__(**kwargs)
        # Number of prefetches to generate
        self.degree     = parameters.get('degree', 2)
        # Queued Prefetcher
        # Latency for generated prefetches
        self.latency    = parameters.get('latency', 1)
        # Maximum number of queued prefetches
        self.queue_size = parameters.get('queue_size', 32)
        # Maximum number of queued prefetches that have a missing translation
        self.max_prefetch_requests_with_pending_translation = parameters.get('max_prefetch_requests_with_pending_translation', 32)
        # Squash queued prefetch on demand access
        self.queue_squash = parameters.get('queue_squash', True)
        # Don't queue redundant prefetches
        self.queue_filter = parameters.get('queue_filter', True)
        # Snoop cache to eliminate redundant request
        self.cache_snoop  = parameters.get('cache_snoop', False)
        # Tag prefetch with PC of generating access
        self.tag_prefetch = parameters.get('tag_prefetch', True)
        # Percentage of requests that can be throttled depending on the accuracy of the prefetcher.
        self.throttle_control_percentage = parameters.get('throttle_control_percentage', 0)
        # [lnghrdntcr]: Error: "proxy cannot unproxy properties"
        self.prefetch_on_access = parameters.get("prefetch_on_access", True)
        self.prefetch_on_pf_hit = parameters.get("prefetch_on_pf_hit", False)


class IndirectMemory(m5.objects.IndirectMemoryPrefetcher):
    def __init__(self, parameters, **kwargs):
        super().__init__(**kwargs)
        # Number of entries of the Prefetch Table
        self.pt_table_entries = parameters.get('pt_table_entries', "16")
        # Associativity of the Prefetch Table
        self.pt_table_assoc = parameters.get('pt_table_assoc', 16)
        # Replacement policy of the pattern table
        self.pt_table_replacement_policy = m5.objects.LRURP()
        # Maximum prefetch distance
        self.max_prefetch_distance = parameters.get('max_prefetch_distance', 16)
        # Number of bits of the indirect counter
        self.num_indirect_counter_bits = parameters.get('num_indirect_counter_bits', 3)
        # Number of entries of the Indirect Pattern Detector
        self.ipd_table_entries = parameters.get('ipd_table_entries', "4")
        # Associativity of the Indirect Pattern Detector
        self.ipd_table_assoc = parameters.get('ipd_table_assoc', 4)
        # Replacement policy of the Indirect Pattern Detector
        self.ipd_table_replacement_policy = m5.objects.LRURP()
        # Shift values to evaluate
        self.shift_values = parameters.get('shift_values', [2, 3, 4, -3])
        # Number of misses tracked
        self.addr_array_len = parameters.get('addr_array_len', 4)
        # Counter threshold to start the indirect prefetching
        self.prefetch_threshold = parameters.get('prefetch_threshold', 2)
        # Counter threshold to enable the stream prefetcher
        self.stream_counter_threshold = parameters.get('stream_counter_threshold', 4)
        # Number of prefetches to generate when using the stream prefetcher
        self.streaming_distance = parameters.get('streaming_distance', 4)


class SignaturePath(m5.objects.SignaturePathPrefetcher):
    def __init__(self, parameters, **kwargs):
        super().__init__(**kwargs)
        self.latency    = parameters.get('latency', 1)
        # Maximum number of queued prefetches
        self.queue_size = parameters.get('queue_size', 32)
        # Maximum number of queued prefetches that have a missing translation
        self.max_prefetch_requests_with_pending_translation = parameters.get('max_prefetch_requests_with_pending_translation', 32)
        # Squash queued prefetch on demand access
        self.queue_squash = parameters.get('queue_squash', True)
        # Don't queue redundant prefetches
        self.queue_filter = parameters.get('queue_filter', True)
        # Snoop cache to eliminate redundant request
        self.cache_snoop  = parameters.get('cache_snoop', False)
        # Tag prefetch with PC of generating access
        self.tag_prefetch = parameters.get('tag_prefetch', True)
        # Percentage of requests that can be throttled depending on the accuracy of the prefetcher.
        self.throttle_control_percentage = parameters.get('throttle_control_percentage', 0)
        # Number of bits to shift when calculating a new signature
        self.signature_shift = parameters.get('signature_shift', 3)
        # Size of the signature, in bits
        self.signature_bits = parameters.get('signature_bits',12)
        # Number of entries of the signature table
        self.signature_table_entries = parameters.get('signature_table_entries',"1024")
        # Associativity of the signature table
        self.signature_table_assoc = parameters.get('signature_table_assoc',2)
        # Indexing policy of the signature table
        # self.signature_table_indexing_policy
        # Replacement policy of the signature table
        self.signature_table_replacement_policy = m5.objects.LRURP()
        # Number of bits of the saturating counters
        self.num_counter_bits = parameters.get('num_counter_bits',3)
        # Number of entries of the pattern table
        self.pattern_table_entries = parameters.get('pattern_table_entries',"4096")
        # Associativity of the pattern table
        self.pattern_table_assoc = parameters.get('pattern_table_assoc',1)
        # Number of strides stored in each pattern entry
        self.strides_per_pattern_entry = parameters.get('strides_per_pattern_entry',4)
        # Indexing policy of the pattern table
        # self.pattern_table_indexing_policy
        # Replacement policy of the pattern table
        self.pattern_table_replacement_policy = m5.objects.LRURP()
        # Minimum confidence to issue prefetches
        self.prefetch_confidence_threshold = parameters.get('prefetch_confidence_threshold',0.5)
        # Minimum confidence to continue exploring lookahead entries
        self.lookahead_confidence_threshold = parameters.get('lookahead_confidence_threshold',0.75)


class SignaturePath2(m5.objects.SignaturePathPrefetcherV2):
    def __init__(self, parameters, **kwargs):
        super().__init__(**kwargs)
        self.latency    = parameters.get('latency', 1)
        # Maximum number of queued prefetches
        self.queue_size = parameters.get('queue_size', 32)
        # Maximum number of queued prefetches that have a missing translation
        self.max_prefetch_requests_with_pending_translation = parameters.get('max_prefetch_requests_with_pending_translation', 32)
        # Squash queued prefetch on demand access
        self.queue_squash = parameters.get('queue_squash', True)
        # Don't queue redundant prefetches
        self.queue_filter = parameters.get('queue_filter', True)
        # Snoop cache to eliminate redundant request
        self.cache_snoop  = parameters.get('cache_snoop', False)
        # Tag prefetch with PC of generating access
        self.tag_prefetch = parameters.get('tag_prefetch', True)
        # Percentage of requests that can be throttled depending on the accuracy of the prefetcher.
        self.throttle_control_percentage = parameters.get('throttle_control_percentage', 0)

        # Number of entries of global history register
        self.global_history_register_entries = parameters.get('strides_per_pattern_entry',"8")
        # Indexing policy of the global history register
        # elf.global_history_register_indexing_policy
        # Replacement policy of the global history register
        self.global_history_register_replacement_policy = m5.objects.LRURP()


class AMPM(m5.objects.AMPMPrefetcher):
    def __init__(self, parameters, **kwargs):
        super().__init__(
            ampm = AMPM_Object(parameters, **kwargs),
            **kwargs
        )
        # Latency for generated prefetches
        self.latency    = parameters.get('latency',1)
        # Maximum number of queued prefetches
        self.queue_size = parameters.get('queue_size',32)
        # Maximum number of queued prefetches that have a missing translation
        self.max_prefetch_requests_with_pending_translation = parameters.get('max_prefetch_requests_with_pending_translation',32)
        # Squash queued prefetch on demand access
        self.queue_squash = parameters.get('queue_squash', True)
        # Don't queue redundant prefetches
        self.queue_filter = parameters.get('queue_filter', True)
        # Snoop cache to eliminate redundant request
        self.cache_snoop  = parameters.get('cache_snoop', False)
        # Tag prefetch with PC of generating access
        self.tag_prefetch = parameters.get('tag_prefetch', True)
        # Percentage of requests that can be throttled depending on the accuracy of the prefetcher.
        self.throttle_control_percentage = parameters.get('throttle_control_percentage', 0)


class DCPT(m5.objects.DCPTPrefetcher):
    def __init__(self, parameters, **kwargs):
        super().__init__(
            # Delta Correlating Prediction Tables object
            dcpt = m5.objects.DeltaCorrelatingPredictionTables(
                deltas_per_entry = parameters.get('deltas_per_entry',20),
                delta_bits = parameters.get('delta_bits',12),
            ),
            **kwargs
        )
        self.latency    = parameters.get('latency', 1)
        # Maximum number of queued prefetches
        self.queue_size = parameters.get('queue_size', 32)
        # Maximum number of queued prefetches that have a missing translation
        self.max_prefetch_requests_with_pending_translation = parameters.get('max_prefetch_requests_with_pending_translation', 32)
        # Squash queued prefetch on demand access
        self.queue_squash = parameters.get('queue_squash', True)
        # Don't queue redundant prefetches
        self.queue_filter = parameters.get('queue_filter', True)
        # Snoop cache to eliminate redundant request
        self.cache_snoop  = parameters.get('cache_snoop', False)
        # Tag prefetch with PC of generating access
        self.tag_prefetch = parameters.get('tag_prefetch', True)
        # Percentage of requests that can be throttled depending on the accuracy of the prefetcher.
        self.throttle_control_percentage = parameters.get('throttle_control_percentage', 0)


class IrregularStreamBuffer(m5.objects.IrregularStreamBufferPrefetcher):
    def __init__(self, parameters, **kwargs):
        super().__init__(**kwargs)
        self.latency    = parameters.get('latency', 1)
        # Maximum number of queued prefetches
        self.queue_size = parameters.get('queue_size', 32)
        # Maximum number of queued prefetches that have a missing translation
        self.max_prefetch_requests_with_pending_translation = parameters.get('max_prefetch_requests_with_pending_translation', 32)
        # Squash queued prefetch on demand access
        self.queue_squash = parameters.get('queue_squash', True)
        # Don't queue redundant prefetches
        self.queue_filter = parameters.get('queue_filter', True)
        # Snoop cache to eliminate redundant request
        self.cache_snoop  = parameters.get('cache_snoop', False)
        # Tag prefetch with PC of generating access
        self.tag_prefetch = parameters.get('tag_prefetch', True)
        # Percentage of requests that can be throttled depending on the accuracy of the prefetcher.
        self.throttle_control_percentage = parameters.get('throttle_control_percentage', 0)

        # Number of bits of the confidence counter
        self.num_counter_bits = parameters.get('num_counter_bits',2)
        # Maximum number of addresses in a temporal stream
        self.chunk_size = parameters.get('chunk_size',256)
        # Number of prefetches to generate
        self.degree = parameters.get('degree',4)
        # Associativity of the training unit
        self.training_unit_assoc = parameters.get('training_unit_assoc',128)
        # Number of entries of the training unit
        self.training_unit_entries = parameters.get('training_unit_entries',"128")
        # Indexing policy of the training unit
        # self.training_unit_indexing_policy
        # Replacement policy of the training unit
        self.training_unit_replacement_policy = m5.objects.LRURP()
        # Number of prefetch candidates stored in a SP-AMC entry
        self.prefetch_candidates_per_entry = parameters.get('prefetch_candidates_per_entry',16)
        # Associativity of the PS/SP AMCs
        self.address_map_cache_assoc = parameters.get('address_map_cache_assoc',128)
        # Number of entries of the PS/SP AMCs
        self.address_map_cache_entries = parameters.get('address_map_cache_entries',"128")
        # Indexing policy of the Physical-to-Structural Address Map Cache
        # self.ps_address_map_cache_indexing_policy
        # Replacement policy of the Physical-to-Structural Address Map Cache
        self.ps_address_map_cache_replacement_policy = m5.objects.LRURP()
        # Indexing policy of the Structural-to-Physical Address Mao Cache
        # self.sp_address_map_cache_indexing_policy
        # Replacement policy of the Structural-to-Physical Address Map Cache
        self.sp_address_map_cache_replacement_policy = m5.objects.LRURP()


class SlimAMPM(m5.objects.SlimAMPMPrefetcher):
    def __init__(self, parameters, **kwargs):
        super().__init__(
            # Access Map Pattern Matching object
            ampm = m5.objects.SlimAccessMapPatternMatching(),
            # Delta Correlating Prediction Tables object
            dcpt = m5.objects.SlimDeltaCorrelatingPredictionTables(),
            **kwargs
        )
        self.latency    = parameters.get('latency', 1)
        # Maximum number of queued prefetches
        self.queue_size = parameters.get('queue_size', 32)
        # Maximum number of queued prefetches that have a missing translation
        self.max_prefetch_requests_with_pending_translation = parameters.get('max_prefetch_requests_with_pending_translation', 32)
        # Squash queued prefetch on demand access
        self.queue_squash = parameters.get('queue_squash', True)
        # Don't queue redundant prefetches
        self.queue_filter = parameters.get('queue_filter', True)
        # Snoop cache to eliminate redundant request
        self.cache_snoop  = parameters.get('cache_snoop', False)
        # Tag prefetch with PC of generating access
        self.tag_prefetch = parameters.get('tag_prefetch', True)
        # Percentage of requests that can be throttled depending on the accuracy of the prefetcher.
        self.throttle_control_percentage = parameters.get('throttle_control_percentage', 0)


class BOP(m5.objects.BOPPrefetcher):
    def __init__(self, parameters, **kwargs):
        super().__init__(**kwargs)
        self.latency    = parameters.get('latency', 1)
        # Maximum number of queued prefetches
        self.queue_size = parameters.get('queue_size', 32)
        # Maximum number of queued prefetches that have a missing translation
        self.max_prefetch_requests_with_pending_translation = parameters.get('max_prefetch_requests_with_pending_translation', 32)
        # Squash queued prefetch on demand access
        self.queue_squash = parameters.get('queue_squash', True)
        # Don't queue redundant prefetches
        self.queue_filter = parameters.get('queue_filter', True)
        # Snoop cache to eliminate redundant request
        self.cache_snoop  = parameters.get('cache_snoop', False)
        # Tag prefetch with PC of generating access
        self.tag_prefetch = parameters.get('tag_prefetch', True)
        # Percentage of requests that can be throttled depending on the accuracy of the prefetcher.
        self.throttle_control_percentage = parameters.get('throttle_control_percentage', 0)

        # Max. score to update the best offset
        self.score_max = parameters.get('score_max',31)
        # Max. round to update the best offset
        self.round_max               = parameters.get('round_max',100)
        # Score at which the HWP is disabled
        self.bad_score               = parameters.get('bad_score',10)
        # Number of entries of each RR bank
        self.rr_size                 = parameters.get('rr_size',64)
        # Bits used to store the tag
        self.tag_bits                = parameters.get('tag_bits',12)
        # Number of entries in the offsets list
        self.offset_list_size        = parameters.get('offset_list_size',46)
        # Initialize the offsets list also with negative values
        # The table will have half of the entries with positive offsets and the other half with negative ones
        self.negative_offsets_enable = parameters.get('negative_offsets_enable', True)
        # Enable the delay queue
        self.delay_queue_enable      = parameters.get('delay_queue_enable', True)
        # Number of entries in the delay queue
        self.delay_queue_size        = parameters.get('delay_queue_size', 15)
        # Cycles to delay a write in the left RR table from the delay queue
        self.delay_queue_cycles      = parameters.get('delay_queue_cycles', 60)
        # [lnghrdntcr]: Error: "proxy cannot unproxy properties"
        self.prefetch_on_access = parameters.get("prefetch_on_access", True)
        self.prefetch_on_pf_hit = parameters.get("prefetch_on_pf_hit", False)


class SBOOE(m5.objects.SBOOEPrefetcher):
    def __init__(self, parameters, **kwargs):
        super().__init__(**kwargs)
        self.latency    = parameters.get('latency', 1)
        # Maximum number of queued prefetches
        self.queue_size = parameters.get('queue_size', 32)
        # Maximum number of queued prefetches that have a missing translation
        self.max_prefetch_requests_with_pending_translation = parameters.get('max_prefetch_requests_with_pending_translation', 32)
        # Squash queued prefetch on demand access
        self.queue_squash = parameters.get('queue_squash', True)
        # Don't queue redundant prefetches
        self.queue_filter = parameters.get('queue_filter', True)
        # Snoop cache to eliminate redundant request
        self.cache_snoop  = parameters.get('cache_snoop', False)
        # Tag prefetch with PC of generating access
        self.tag_prefetch = parameters.get('tag_prefetch', True)
        # Percentage of requests that can be throttled depending on the accuracy of the prefetcher.
        self.throttle_control_percentage = parameters.get('throttle_control_percentage', 0)

        # Entries in the latency buffer
        self.latency_buffer_size = parameters.get('latency_buffer_size',32)
        # Number of sequential prefetchers
        self.sequential_prefetchers = parameters.get('sequential_prefetchers',9)
        # Size of the address buffer
        self.sandbox_entries = parameters.get('sandbox_entries',1024)
        # Min. threshold to issue a prefetch. The value is the percentage of sandbox entries to use
        self.score_threshold_pct = parameters.get('score_threshold_pct',25)


class STeMS(m5.objects.STeMSPrefetcher):
    def __init__(self, parameters, **kwargs):
        super().__init__(**kwargs)
        self.latency    = parameters.get('latency', 1)
        # Maximum number of queued prefetches
        self.queue_size = parameters.get('queue_size', 32)
        # Maximum number of queued prefetches that have a missing translation
        self.max_prefetch_requests_with_pending_translation = parameters.get('max_prefetch_requests_with_pending_translation', 32)
        # Squash queued prefetch on demand access
        self.queue_squash = parameters.get('queue_squash', True)
        # Don't queue redundant prefetches
        self.queue_filter = parameters.get('queue_filter', True)
        # Snoop cache to eliminate redundant request
        self.cache_snoop  = parameters.get('cache_snoop', False)
        # Tag prefetch with PC of generating access
        self.tag_prefetch = parameters.get('tag_prefetch', True)
        # Percentage of requests that can be throttled depending on the accuracy of the prefetcher.
        self.throttle_control_percentage = parameters.get('throttle_control_percentage', 0)

        # Memory covered by a hot zone
        self.spatial_region_size = parameters.get('sequential_prefetchers',"2KiB")
        # Number of entries in the active generation table
        self.active_generation_table_entries = parameters.get('sequential_prefetchers',"64")
        # Associativity of the active generation table
        self.active_generation_table_assoc = parameters.get('sequential_prefetchers',64)
        # Indexing policy of the active generation table
        # self.active_generation_table_indexing_policy
        # Replacement policy of the active generation table
        self.active_generation_table_replacement_policy = m5.objects.LRURP()
        # Number of entries in the pattern sequence table
        self.pattern_sequence_table_entries = parameters.get('sequential_prefetchers',"16384")
        # Associativity of the pattern sequence table
        self.pattern_sequence_table_assoc = parameters.get('sequential_prefetchers',16384)
        # Indexing policy of the pattern sequence table
        # self.pattern_sequence_table_indexing_policy
        # Replacement policy of the pattern sequence table
        self.pattern_sequence_table_replacement_policy = m5.objects.LRURP()
        # Number of entries of the Region Miss Order Buffer
        self.region_miss_order_buffer_entries = parameters.get('sequential_prefetchers',131072)
        # Add duplicate entries to RMOB
        self.add_duplicate_entries_to_rmob = parameters.get('sequential_prefetchers',True)
        # Number of reconstruction entries
        self.reconstruction_entries = parameters.get('sequential_prefetchers',256)


class PIF(m5.objects.PIFPrefetcher):
    def __init__(self, parameters, **kwargs):
        super().__init__(**kwargs)
        self.latency    = parameters.get('latency', 1)
        # Maximum number of queued prefetches
        self.queue_size = parameters.get('queue_size', 32)
        # Maximum number of queued prefetches that have a missing translation
        self.max_prefetch_requests_with_pending_translation = parameters.get('max_prefetch_requests_with_pending_translation', 32)
        # Squash queued prefetch on demand access
        self.queue_squash = parameters.get('queue_squash', True)
        # Don't queue redundant prefetches
        self.queue_filter = parameters.get('queue_filter', True)
        # Snoop cache to eliminate redundant request
        self.cache_snoop  = parameters.get('cache_snoop', False)
        # Tag prefetch with PC of generating access
        self.tag_prefetch = parameters.get('tag_prefetch', True)
        # Percentage of requests that can be throttled depending on the accuracy of the prefetcher.
        self.throttle_control_percentage = parameters.get('throttle_control_percentage', 0)

        # Number of preceding addresses in the spatial region
        self.prec_spatial_region_bits = parameters.get('sequential_prefetchers',2)
        # Number of subsequent addresses in the spatial region
        self.succ_spatial_region_bits = parameters.get('sequential_prefetchers',8)
        # Entries in the temp. compactor
        self.compactor_entries = parameters.get('sequential_prefetchers',2)
        # Entries in the SAB
        self.stream_address_buffer_entries = parameters.get('sequential_prefetchers',7)
        # Entries in the history buffer
        self.history_buffer_size = parameters.get('sequential_prefetchers',16)
        # Number of entries in the index
        self.index_entries = parameters.get('sequential_prefetchers',"64")
        # Associativity of the index
        self.index_assoc = parameters.get('sequential_prefetchers',64)
        # Indexing policy of the index
        #self.index_indexing_policy
        # Replacement policy of the index
        self.index_replacement_policy = m5.objects.LRURP()
