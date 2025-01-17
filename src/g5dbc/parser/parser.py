from abc import ABC, abstractmethod
from pathlib import Path
import re
import yaml

from ..util.parser import stats_line_generator, parse_number_text
from ..config import Config

class StatsParser(ABC):
    """
    Statistics Parser
    """
    def __init__(self, parser_re_dir: Path):

        parser_conf = [f for f in parser_re_dir.iterdir() if f.suffix == ".yaml"]

        self.regexes = []

        for file in parser_conf:
            with file.open('r') as stream:
                self.regexes.extend(yaml.safe_load(stream))


    def parse_stats(self, stats_params: dict, parsed_output: dict, stats_file: Path) -> list[dict[str,int|float|list]]:
        max_roi_id=5

        parsed_rois = [dict(**stats_params, roi_id=roi_id) for roi_id in range(max_roi_id)]
        for roi_id, path, key, val in stats_line_generator(stats_file):
            s = '.'.join(path)
            for r,labels in self.regexes:
                m = re.fullmatch(r, s)
                if m:
                    for l in labels:
                        g = [parse_number_text(k) for k in m.groups()]
                        c = l.format(*g)
                        self.update_column(parsed_rois[roi_id], c, key, val)

        for roi_id, parsed_roi in enumerate(parsed_rois):
            self.normalize_network(parsed_roi, parsed_output)

        return parsed_rois


    def normalize_network(self, r: dict, parsed_output:dict) -> dict:
        if 'simTicks' in r:
        
            ruby_cycles   = float(r['simTicks'])/r['interconnect_clock']

            links = parsed_output["output_log"]["network"]["links"]
            rtp_node = r.setdefault("router_topology", dict())

            int_node = rtp_node.setdefault("internal", dict())
            exo_node = rtp_node.setdefault("ext_out", dict())
            exi_node = rtp_node.setdefault("ext_in", dict())

            for link in links:
                nxt_node = None
                if link['linkType'] == 'Internal':
                    nxt_node = int_node
                elif link['linkType'] == 'ExtIn':
                    nxt_node = exi_node
                elif link['linkType'] == 'ExtOut':
                    nxt_node = exo_node
                else:
                    continue
                linkId = link['linkId']
                src_node = nxt_node.setdefault(link['srcId'], dict())
                dst_node = src_node.setdefault(link['dstId'], dict())

                # Append to Link List
                rt_links = dst_node.setdefault("link", list())
                rt_links.append(linkId)
                # Find Link Traffic statistics
                dst_node.setdefault("total_packets", 0)
                stats = sorted([c for c in r if re.search(fr"network_network_latencies_vnet(\d+)_link{linkId}_total", c)])
                for s in stats:
                    m = re.match(fr"network_network_latencies_vnet(\d+)_link{linkId}_total", s)
                    vnetId = int(m.group(1))
                    vnet_t = dst_node.setdefault("vnet", dict())
                    link_t = vnet_t.setdefault(vnetId, list())
                    link_t.append(dict(linkId=linkId, samples=r[s], traffic=float(r[s])/ruby_cycles ))
                    dst_node["total_packets"] += r[s]
                    dst_node["total_traffic"] = float(dst_node["total_packets"]) / ruby_cycles

    @abstractmethod
    def update_column(self, r:dict, c: str, key, val) -> dict:
        """
        Update column
        """
