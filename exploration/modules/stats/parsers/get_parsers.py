from modules.stats.parsers.parse_memory import parse_memory
from modules.stats.parsers.parse_cpu import parse_cpu
from modules.stats.parsers.parse_ruby_cache import parse_ruby_cache
from modules.stats.parsers.parse_classic_cache import parse_classic_cache
from modules.stats.parsers.parse_ruby_network import parse_ruby_network
from modules.stats.parsers.parse_prefetcher import parse_prefetcher
from modules.stats.parsers.parse_ruby_protocol import parse_ruby_protocol
from modules.stats.parsers.parse_ruby_routers import parse_ruby_routers
from modules.stats.parsers.parse_clocks import parse_clocks
from modules.stats.parsers.parse_ruby_network_sparse_histogram import parse_ruby_network_sparse_histogram

def get_parsers(conf_dict: dict):
    links_dict = conf_dict["output_log"]["links"]
    sve_vl     = conf_dict['cpu']['sve_vl']
    simdw      = sve_vl/64

    parsers = [
        lambda r,k,v: parse_clocks(k, v, r),
        lambda r,k,v: parse_memory(k, v, r),
        lambda r,k,v: parse_cpu(k, v, r, simdw),
        lambda r,k,v: parse_ruby_cache(k, v, r),
        lambda r,k,v: parse_ruby_network(k, v, r),
        lambda r,k,v: parse_ruby_protocol(k, v, r),
        lambda r,k,v: parse_classic_cache(k, v, r),
        lambda r,k,v: parse_prefetcher(k, v, r),
        lambda r,k,v: parse_ruby_routers(k, v, r, links_dict),
        lambda r,k,v: parse_ruby_network_sparse_histogram(k,v,r),
    ]

    return parsers
