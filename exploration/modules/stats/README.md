# EPI-gem5 statistics parsing

## Simulation Clocks
```python
# System clocks
r['system_clock'] = parse_number(d['system.clk_domain.clock'])
r['cpu_clock']    = parse_number(d['system.cpu_clk_domain.clock'])
if 'system.ruby.clk_domain.clock' in d:
    r['ruby_clock'] = parse_number(d['system.ruby.clk_domain.clock'])

# simulation ticks
r['simTicks'] = parse_number(d['simTicks'])
r['simFreq']  = parse_number(d['simFreq'])
r['simOps']   = parse_number(d['simOps'])
# Time
r['time']    = float(r['simTicks'])/r['simFreq']
r['cycles']  = float(r['simTicks'])/r['cpu_clock']
```

## CPU instructions
```python
r"system\.cpu([0-9]*)\.commit.(\w+)$"
r"system\.cpu([0-9]*)\.commit\.committedInstType_0::(Int)(\w+)"
r"system\.cpu([0-9]*)\.commit\.committedInstType_0::(Simd|Float)(\w+)"
r"system\.cpu([0-9]*)\.commit\.committedInstType_0::(Float)?(Mem)(\w+)"
r"system\.cpu([0-9]*)\.fetch\.(\w+)$"
r"system\.cpu([0-9]*)\.(\w+)$"
r"system\.cpu([0-9]*)\.statIssuedInstType_0::(Int|Simd|Float)(\w+)"
r"system\.cpu([0-9]*)\.statIssuedInstType_0::(Float)?(Mem)(\w+)"
r"system\.cpu([0-9]*)\.(cpi|ipc)$"
r"system\.cpu([0-9]*)\.(cpi_total|ipc_total|committedInsts|committedOps|idleCycles|numCycles|quiesceCycles|timesIdled)"
r"system\.cpu([0-9]*)\.(misc|pred|vec|cc)_regfile_(reads|writes)"
```

## Memory
```python
# Data bus utilization in percentage
r"system\.mem_ctrls(\d+)(.dram)?\.(busUtil)$"
# Data bus utilization in percentage
r"system\.mem_ctrls(\d+)(.dram)?\.(busUtilRead|busUtilWrite)$"
# Memory bandwidth
r"system\.mem_ctrls(\d+)(.dram)?\.(avgRdBW|avgWrBW|peakBW|pageHitRate)$"
# Memory bandwidth and bytes transfered
r"system\.mem_ctrls(\d+)(.dram)?\.(bwRead|bwWrite|bwTotal|numReads|numWrites|bytesRead|bytesWritten|bytesPerActivate)::total"
r"system\.cpu(\d*)\.MemDepUnit__(\d*)\.(conflicting|inserted)(Loads|Stores)"
```

## Ruby caches
```python
r"system\.cpu(\d+)\.(l1d|l1i|l2)\.cache\.m_(demand)_(accesses|hits|misses)"
r"system\.cpu(\d+)\.(l1d|l1i|l2)\.cache\.num(Data|Tag)Array(Reads|Writes)"
r"system\.cpu(\d+)\.(l1d|l1i|l2)\.(dat|req|rsp|snp)(In|Out|Rdy)\.m_(buf_msgs|stall_time)"
r"system\.ruby\.hnf(\d+)\.cntrl\.cache\.m_(demand)_(accesses|hits|misses)"
r"system\.ruby\.hnf(\d+)\.cntrl\.cache\.num(Data|Tag)Array(Reads|Writes)"
r"system\.ruby\.hnf(\d+)\.cntrl\.(dat|req|rsp|snp)(In|Out)\.avg_(buf_msgs|stall_time)"
```

## Ruby Network
```python
r"system\.ruby\.network\.int_links(\d+)\.(dst|src)_node\.buffer_(reads|writes)"
# Average Flit/Packet latency
r"system\.ruby\.network\.average_(flit|packet)_?(network|queueing)?_latency"
r"system\.ruby\.network\.(average_hops|avg_link_utilization)"
r"system\.ruby\.network\.(ext_in|ext_out|int)_link_utilization"
r"system\.ruby\.network\.(avg_vc_load|flits_injected|flits_received)::total"
r"system\.ruby\.network\.(histogram_hops)_vnet(\d+)$"
r"system\.ruby\.network\.(routers|net_ifs)_vnet(\d+)_src_dst$"
```